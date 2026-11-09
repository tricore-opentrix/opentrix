# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""Offline harness checks only; these are never PostgreSQL/X-25 PASS evidence."""
import importlib.util
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('m5_runner', Path(__file__).with_name('run.py'))
m5 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m5)
LAUNCH_SPEC = importlib.util.spec_from_file_location('m5_launch', Path(__file__).with_name('launch.py'))
launcher = importlib.util.module_from_spec(LAUNCH_SPEC)
LAUNCH_SPEC.loader.exec_module(launcher)
ACCEPTANCE_SPEC = importlib.util.spec_from_file_location('m5_acceptance', Path(__file__).with_name('acceptance.py'))
acceptance = importlib.util.module_from_spec(ACCEPTANCE_SPEC)
ACCEPTANCE_SPEC.loader.exec_module(acceptance)


class HarnessChecks(unittest.TestCase):
    def test_new_effect_oracle_rejects_tampering(self):
        path = m5.ROOT/'docs/verification/r28/evidence/X-25/20261109-m5-isolated-05/normal-multirow-assignment.json'
        saved = json.loads(path.read_text(encoding='utf-8'))
        before, after = saved['before'], saved['after']
        self.assertTrue(acceptance.one_effect(before, after, 'normal'))
        for field in ('audit_id', 'principal', 'command_key', 'recorded_xid', 'resulting_g'):
            changed = copy.deepcopy(after)
            changed['receipt'][0][field] = 'forged'
            self.assertFalse(acceptance.one_effect(before, changed, 'normal'), field)
        changed = copy.deepcopy(after)
        changed['receipt'] = []
        self.assertFalse(acceptance.one_effect(before, changed, 'normal'))

    def test_session_counterexample_remains_fail(self):
        class FakeRunner:
            def __init__(self): self.records=[]
            def snapshot(self): return {'receipt': [], 'acl': ['receipt-less committed effect']}
            def record(self, result): self.records.append(result)
        runner=FakeRunner()
        acceptance.session_case(runner,None,'counterexample',lambda *args: None,lambda *args: False)
        self.assertEqual(runner.records[0]['status'],'FAIL')
        self.assertIn('receipt-less committed effect',runner.records[0]['after']['acl'])

    def test_harness_manifest_includes_nested_source(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(m5,'ROOT',Path(temp)), \
             patch.object(m5,'git',return_value='synthetic-base'):
            runner=m5.Runner('nested-source')
            source=runner.folder('HARNESS')/'source'/'synthetic.py'
            source.parent.mkdir(parents=True)
            source.write_bytes(b'# synthetic source\n')
            runner.finish('offline only')
            manifest=json.loads((runner.folder('HARNESS')/'checksums.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['source/synthetic.py'],m5.digest(source))

    def test_launcher_starts_new_process_without_inherited_credentials(self):
        with patch.dict(launcher.os.environ, {'PATH':'os-path','CART_DB_PASSWORD':'service-secret',
                         'ORDER_DB_PASSWORD':'other-secret','PGSERVICE':'external',
                         'DOCKER_HOST':'remote','PYTHONPATH':'injected','HOME':'host-home'}, clear=True), \
             patch.object(launcher.subprocess,'run',return_value=subprocess.CompletedProcess([],7)) as child:
            self.assertEqual(launcher.main(),7)
            command=child.call_args.args[0]
            env=child.call_args.kwargs['env']
            self.assertEqual(command[1:3],['-I','-B'])
            self.assertEqual(set(env),{'PATH','HOME','USERPROFILE'})
            self.assertEqual(env['PATH'],'os-path')
            self.assertNotEqual(env['HOME'],'host-home')
            self.assertEqual(env['HOME'],env['USERPROFILE'])
            self.assertFalse(Path(env['HOME']).exists())
            self.assertEqual(launcher.os.environ['CART_DB_PASSWORD'],'service-secret')

    def test_fresh_credentials_and_network_rejection_before_sql(self):
        passwords=[]
        for mismatch in ('network','password'):
            with patch.object(m5,'git',return_value='synthetic-base'), patch.dict(m5.os.environ,{},clear=True):
                runner=m5.Runner('offline-isolation')
                container='a'*64
                def command(args,sql=None,timeout=30):
                    self.assertIn('POSTGRES_PASSWORD',args)
                    self.assertNotIn('synthetic-unused-network-rejected',' '.join(args))
                    passwords.append(runner.env['POSTGRES_PASSWORD'])
                    self.assertNotIn(passwords[-1],' '.join(args))
                    return subprocess.CompletedProcess(args,0,container,'')
                def docker_json(*args):
                    if args[0]=='version': return {'Version':'synthetic'}
                    if args[0]=='image':
                        return [{'Id':'image-id','Os':'linux','RepoDigests':['postgres@sha256:'+'b'*64],
                                 'Config':{'Env':['PG_MAJOR=17']}}]
                    return [{'Id':container,'Name':'/'+runner_name[0],'Image':'image-id',
                             'Config':{'Labels':{'opentrix.r28.m5.disposable':'true','opentrix.r28.m5.run':runner.run_id},
                                       'Env':['POSTGRES_PASSWORD='+('wrong' if mismatch=='password' else passwords[-1]),
                                              'POSTGRES_DB=m5_disposable','POSTGRES_HOST_AUTH_METHOD=reject',
                                              'POSTGRES_INITDB_ARGS=--auth-local=trust --auth-host=reject']},
                             'HostConfig':{'NetworkMode':'bridge'}}]
                runner_name=[]
                def capture(args,sql=None,timeout=30):
                    runner_name.append(args[args.index('--name')+1])
                    return command(args,sql,timeout)
                try:
                    with patch.object(runner,'command',side_effect=capture), \
                         patch.object(runner,'docker_json',side_effect=docker_json), \
                         patch.object(runner,'inventory',return_value=[]), \
                         patch.object(runner,'sql') as sql:
                        with self.assertRaisesRegex(RuntimeError,'isolation proof failed' if mismatch=='network' else 'credentials/database/auth'):
                            runner.prepare()
                        sql.assert_not_called()
                    self.assertNotIn('POSTGRES_PASSWORD',runner.env)
                    self.assertNotIn(passwords[-1],json.dumps(runner.metadata))
                    self.assertGreaterEqual(len(passwords[-1]),43)
                finally:
                    runner.temp.cleanup()
        self.assertNotEqual(*passwords)

    def test_faults_modify_only_offline_copy(self):
        original = m5.executor_sql()
        for kind in ('omit','insert_failure','malformed','wrong_digest','wrong_xid','remove',
                     'change','extra_membership','wrong_actual_acl','wrong_audit'):
            with self.subTest(kind=kind):
                faulty = m5.fault_sql(kind)
                self.assertNotEqual(original, faulty)
                self.assertIn('CREATE FUNCTION m5.assign_fault(', faulty)
                self.assertNotIn('CREATE FUNCTION m5.assign_replace(', faulty)
                self.assertIn('FOR UPDATE', faulty)
        self.assertNotIn('INSERT INTO m5.receipt', m5.fault_sql('omit'))
        self.assertIn("'BROKEN',1", m5.fault_sql('insert_failure'))
        self.assertEqual(original, m5.executor_sql())

    def test_source_boundary_manifest(self):
        sql = (m5.HERE/'schema.sql').read_text(encoding='utf-8')
        self.assertIn('DEFERRABLE INITIALLY DEFERRED', sql)
        self.assertIn('a.changes<>m5.actual_changes(x)', sql)
        self.assertIn('ENABLE ALWAYS TRIGGER receipt_required', sql)
        for prohibited in ('EXCEPTION WHEN','ON CONFLICT','EXECUTE format'):
            self.assertNotIn(prohibited, m5.executor_sql())
        self.assertNotIn('GRANT core_acl_owner TO', sql)

    def test_credentials_fail_before_docker(self):
        with patch.object(m5,'git',return_value='synthetic-base'), \
             patch.dict(m5.os.environ, {'PGPASSWORD':'synthetic'}, clear=True), \
             patch.object(m5.Runner,'docker_json') as docker:
            runner = m5.Runner('offline-selfcheck')
            try:
                with self.assertRaisesRegex(RuntimeError,'PGPASSWORD'):
                    runner.prepare()
                docker.assert_not_called()
                self.assertNotIn('PGPASSWORD',runner.env)
            finally:
                runner.temp.cleanup()

    def test_unknown_environment_fails_before_docker(self):
        with patch.object(m5,'git',return_value='synthetic-base'), \
             patch.dict(m5.os.environ, {'UNREVIEWED_VARIABLE':'synthetic'}, clear=True), \
             patch.object(m5.Runner,'docker_json') as docker:
            runner=m5.Runner('offline-environment')
            try:
                with self.assertRaisesRegex(RuntimeError,'uncontrolled environment'):
                    runner.prepare()
                docker.assert_not_called()
            finally:
                runner.temp.cleanup()

    def test_fault_publication_preserves_case_evidence(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(m5,'ROOT',Path(temp)), \
             patch.object(m5,'git',return_value='synthetic-base'):
            runner=m5.Runner('offline-publication')
            try:
                with patch('builtins.print'):
                    runner.record({'name':'fault-insert_failure','status':'PASS','reason':'original trace'})
                with patch.object(runner,'sql',return_value=subprocess.CompletedProcess([],0,'published','')):
                    runner.publish_fault('insert_failure')
                result=json.loads((runner.folder()/'fault-insert_failure.json').read_text())
                self.assertEqual(result['reason'],'original trace')
                self.assertTrue((runner.folder()/'publication-insert_failure.json').is_file())
            finally:
                runner.temp.cleanup()

    def test_function_defaults_are_globally_private(self):
        sql=(m5.HERE/'schema.sql').read_text(encoding='utf-8')
        self.assertIn('ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;',sql)
        self.assertNotIn('ALTER DEFAULT PRIVILEGES IN SCHEMA m5 REVOKE EXECUTE',sql)

    def test_container_command_has_no_remote_connection(self):
        runner=m5.Runner('offline-selfcheck')
        try:
            runner.container='synthetic-container'
            command=runner.psql_command('core_workflow_rt')
            self.assertEqual(command[command.index('-U')+1],'core_workflow_rt')
            self.assertEqual(command[command.index('-h')+1],'/var/run/postgresql')
            self.assertNotIn('SET ROLE',' '.join(command))
            self.assertIn('--config',command)
        finally:
            runner.temp.cleanup()

    def test_blocked_records_zero_executions(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(m5,'ROOT',Path(temp)), \
             patch.object(m5,'git',return_value='synthetic-base'):
            runner=m5.Runner('blocked-selfcheck')
            runner.finish('synthetic unavailable environment')
            for group in m5.EVIDENCE_IDS:
                folder=Path(temp)/'docs/verification/r28/evidence'/group/'blocked-selfcheck'
                result=json.loads((folder/'result.json').read_text())
                self.assertEqual(result['status'],'BLOCKED')
                self.assertEqual(result['database_cases_executed'],0)
                env=json.loads((folder/'environment.json').read_text())
                self.assertEqual(env['preflight_status'],'BLOCKED')
                checksums=json.loads((folder/'checksums.json').read_text())
                self.assertEqual(checksums['result.json'],m5.digest(folder/'result.json'))


if __name__=='__main__':
    unittest.main()
