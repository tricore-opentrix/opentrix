# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""Offline harness checks only; these are never PostgreSQL/X-25 PASS evidence."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('m5_runner', Path(__file__).with_name('run.py'))
m5 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m5)


class HarnessChecks(unittest.TestCase):
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
                checksums=json.loads((folder/'checksums.json').read_text())
                self.assertEqual(checksums['result.json'],m5.digest(folder/'result.json'))


if __name__=='__main__':
    unittest.main()
