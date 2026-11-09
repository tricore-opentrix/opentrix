#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""M5 test-only runner. No external DSN, mounts, ports, remote engine or credentials accepted."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import runpy
import secrets
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ROLES = ('core_acl_exec_rt', 'core_authz_reader_rt', 'core_workflow_rt', 'helpdesk_rt', 'core_observer')
TABLES = ('tenant_guards', 'tenant_memberships', 'resource_registry', 'workflow_definition_bindings',
          'authority', 'admission', 'resource_acl', 'resource_fence', 'policy_audit', 'receipt', 'mutation_log')
EVIDENCE_IDS = ('X-25', 'T07', 'T08-X-09', 'X-12', 'X-13', 'X-23', 'X-24', 'X-16-X-26')
ASSIGN_SIG = '(text,text,text,text,text,bigint,bigint)'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def git(*args):
    return subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}', *args],
                                   cwd=ROOT, text=True, encoding='utf-8').strip()


def executor_sql():
    source = (HERE / 'schema.sql').read_text(encoding='utf-8')
    start = source.index('CREATE FUNCTION m5.assign_replace(')
    return source[start:source.index('END $assign$;', start) + len('END $assign$;')]


def fault_sql(kind):
    """Offline publication of one faulty definer, never a parameter on the reviewed executor."""
    source = executor_sql().replace('m5.assign_replace(', 'm5.assign_fault(', 1)
    start = source.index('    INSERT INTO m5.receipt VALUES(')
    end = source.index('    RETURN jsonb_build_object', start)
    insert = source[start:end]
    if kind == 'omit':
        replacement = ''
    elif kind == 'insert_failure':
        replacement = insert.replace("'APPLIED',1", "'BROKEN',1")
    elif kind == 'malformed':
        replacement = insert.replace("'APPLIED',1,v_request,v_digest", "'APPLIED',1,v_request,NULL")
    elif kind == 'wrong_digest':
        replacement = insert.replace('sha256(convert_to(v_changes::text,\'UTF8\'))', "sha256('forged'::bytea)")
    elif kind == 'wrong_xid':
        replacement = insert.replace(',v_xid);', ",'1'::xid8);")
    elif kind == 'remove':
        replacement = insert + '    DELETE FROM m5.receipt WHERE audit_id=v_audit;\n'
    elif kind == 'change':
        replacement = insert + "    UPDATE m5.receipt SET principal='forged' WHERE audit_id=v_audit;\n"
    elif kind == 'extra_membership':
        replacement = insert + "    UPDATE m5.tenant_memberships SET active=false WHERE tenant_id=p_tenant AND actor_id='old';\n"
    elif kind == 'wrong_actual_acl':
        replacement = insert + "    UPDATE m5.resource_acl SET granted=false WHERE tenant_id=p_tenant AND actor_id=p_assignee;\n"
    elif kind == 'wrong_audit':
        source = source.replace('v_request,v_changes,\n        sha256', "v_request,'[]'::jsonb,\n        sha256")
        return source
    else:
        raise ValueError(kind)
    return source[:start] + replacement + source[end:]


class Session:
    """Interactive psql for controlled barriers; EOF/error/timeouts are failures, never success."""
    def __init__(self, runner, role):
        self.runner = runner
        self.command = runner.psql_command(role, interactive=True)
        self.proc = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, text=True, encoding='utf-8', env=runner.env, bufsize=1)
        self.lines, self.sent, self.pending = [], [], queue.Queue()
        def read():
            for line in self.proc.stdout:
                self.lines.append(line)
                self.pending.put(line)
            self.pending.put(None)
        threading.Thread(target=read, daemon=True).start()
        self.send("SELECT 'PID='||pg_backend_pid(); SELECT 'ACTOR='||session_user||'/'||current_user; SHOW transaction_isolation;\n\\echo READY\n")
        self.until('READY')
        match = re.search(r'PID=(\d+)', ''.join(self.lines))
        require(match is not None, 'missing backend PID')
        self.pid = int(match[1])
        require(f'ACTOR={role}/{role}' in ''.join(self.lines), 'session actor mismatch')

    def send(self, sql):
        self.sent.append(sql)
        self.proc.stdin.write(sql + '\n')
        self.proc.stdin.flush()

    def until(self, marker, timeout=20):
        deadline = time.monotonic() + timeout
        while True:
            line = self.pending.get(timeout=max(0.01, deadline-time.monotonic()))
            require(line is not None, 'psql exited before barrier ' + marker)
            if line.strip() == marker:
                return
            require(time.monotonic() < deadline, 'barrier timeout ' + marker)

    def close(self):
        if self.proc.poll() is None:
            self.proc.stdin.close()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)


class Runner:
    def __init__(self, run_id):
        self.run_id = run_id
        self.container = None
        self.bootstrap_secret = None
        self.results = []
        self.group = 'X-25'
        self.temp = tempfile.TemporaryDirectory(prefix='r28-m5-docker-')
        # Empty Docker config prevents reuse of registry/service credentials.
        endpoint = 'npipe:////./pipe/dockerDesktopLinuxEngine' if os.name == 'nt' else 'unix:///var/run/docker.sock'
        self.docker = ['docker', '--config', self.temp.name, '--host', endpoint]
        self.env = {k: v for k, v in os.environ.items() if k.upper() in
                    ('PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'PATHEXT', 'COMSPEC', 'HOME', 'USERPROFILE')}
        self.metadata = {'run_id': run_id, 'source_commit': git('rev-parse', 'HEAD'),
                         'source_branch': git('branch', '--show-current'),
                         'source_status': git('status', '--short', '--', 'tests/r28_m5'),
                         'schema_sha256': digest(HERE / 'schema.sql'),
                         'grant_sha256': digest(HERE / 'schema.sql'),
                         'source_files_sha256': {p.name: digest(p) for p in HERE.iterdir() if p.is_file()},
                         'execution_command': subprocess.list2cmdline([sys.executable, *sys.argv]),
                         'database_tests_executed': 0,
                         'postgresql': None, 'image': None, 'container': None,
                         'credential_safety': 'NOT_ESTABLISHED until isolated-container preflight completes',
                         'connection': 'local container Unix socket; dbname=m5_disposable; no published port',
                         'fixture': 'synthetic T1/T2, R1/R2, admin/old/new; initial G10/fence5',
                         'sql_runtime_approved': False}
        self.metadata['preflight_status'] = 'NOT_RUN'
        self.metadata['process_environment_keys'] = sorted(os.environ)
        self.metadata['acceptance_gaps'] = []

    def folder(self, group=None):
        return ROOT / 'docs/verification/r28/evidence' / (group or self.group) / self.run_id

    def command(self, args, sql=None, timeout=30):
        return subprocess.run(args, input=sql, text=True, encoding='utf-8', capture_output=True,
                              timeout=timeout, env=self.env)

    def docker_json(self, *args):
        r = self.command([*self.docker, *args])
        require(r.returncode == 0, r.stderr.strip() or 'Docker unavailable')
        return json.loads(r.stdout)

    def prepare(self):
        unsafe = sorted(k for k, v in os.environ.items() if v and re.search(
            r'(^PG(HOST|HOSTADDR|PORT|DATABASE|USER|PASSWORD|PASSFILE|SERVICE|SERVICEFILE|SSLKEY|SSLCERT)$|'
            r'(DATABASE|JDBC|DATASOURCE|DB)_(URL|DSN|PASSWORD|PASS|TOKEN|USER|HOST)$|^DOCKER_(HOST|CONTEXT|TLS_VERIFY|CERT_PATH)$)', k, re.I))
        require(not unsafe, 'credential/target variables present (names only): ' + ', '.join(unsafe))
        require(all(k.upper() in ('PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'PATHEXT',
                                  'COMSPEC', 'HOME', 'USERPROFILE') for k in os.environ),
                'uncontrolled environment; use tests/r28_m5/launch.py')
        server = self.docker_json('version', '--format', '{{json .Server}}')
        require(server is not None, 'Docker daemon unavailable')
        image = self.docker_json('image', 'inspect', 'postgres:17')[0]
        require(any(re.fullmatch(r'(?:docker.io/library/)?postgres@sha256:[0-9a-f]{64}', d)
                    for d in image.get('RepoDigests', [])), 'official postgres image digest unavailable')
        self.metadata['docker_server'] = server
        self.metadata['image'] = {k: image.get(k) for k in ('Id', 'RepoDigests', 'Architecture', 'Os')}
        self.metadata['existing_containers_before'] = self.inventory()
        require(image['Os'] == 'linux' and 'PG_MAJOR=17' in image['Config']['Env'],
                'image is not PostgreSQL 17/Linux')
        name = 'r28-m5-' + uuid.uuid4().hex
        password = secrets.token_urlsafe(32)
        self.env['POSTGRES_PASSWORD'] = password
        try:
            r = self.command([*self.docker, 'run', '--detach', '--pull=never', '--name', name,
                          '--label', 'opentrix.r28.m5.disposable=true', '--network', 'none',
                          '--label', 'opentrix.r28.m5.run=' + self.run_id,
                          '--tmpfs', '/var/lib/postgresql/data:rw', '--env', 'POSTGRES_DB=m5_disposable',
                          '--env', 'POSTGRES_HOST_AUTH_METHOD=reject',
                          '--env', 'POSTGRES_INITDB_ARGS=--auth-local=trust --auth-host=reject',
                          '--env', 'POSTGRES_PASSWORD', image['Id']])
        finally:
            self.env.pop('POSTGRES_PASSWORD')
        require(r.returncode == 0, r.stderr)
        self.container = r.stdout.strip()
        require(re.fullmatch('[a-f0-9]{64}', self.container), 'unexpected container id')
        info = self.docker_json('inspect', self.container)[0]
        require(info['Id'] == self.container and info['Name'] == '/' + name
                and info['Image'] == image['Id']
                and info['Config']['Labels'].get('opentrix.r28.m5.disposable') == 'true'
                and info['Config']['Labels'].get('opentrix.r28.m5.run') == self.run_id,
                'container identity mismatch')
        config_env = dict(item.split('=', 1) for item in info['Config']['Env'])
        require(config_env.get('POSTGRES_PASSWORD') == password
                and config_env.get('POSTGRES_DB') == 'm5_disposable'
                and config_env.get('POSTGRES_HOST_AUTH_METHOD') == 'reject'
                and config_env.get('POSTGRES_INITDB_ARGS') == '--auth-local=trust --auth-host=reject',
                'test-only credentials/database/auth configuration mismatch')
        self.bootstrap_secret = password
        del password, config_env, info['Config']['Env']
        require(info['HostConfig']['NetworkMode'] == 'none' and not info['HostConfig'].get('Binds')
                and not info['HostConfig'].get('PortBindings') and not info['HostConfig'].get('Privileged')
                and all(m['Type']=='tmpfs' and m['Destination']=='/var/lib/postgresql/data'
                        for m in info.get('Mounts', []))
                and '/var/lib/postgresql/data' in info['HostConfig'].get('Tmpfs', {}),
                'isolation proof failed: mounts/ports/network/privilege')
        self.metadata['container'] = {'id': self.container, 'name': name, 'image': info['Image'], 'network': 'none',
                                      'mounts': info['Mounts'], 'tmpfs': info['HostConfig']['Tmpfs'], 'ports': {}}
        binary_version = self.command([*self.docker, 'exec', self.container, 'postgres', '--version'])
        require(binary_version.returncode == 0 and re.search(r'\b17\.', binary_version.stdout),
                'PostgreSQL binary version mismatch')
        self.metadata['postgres_binary_version'] = binary_version.stdout.strip()
        self.metadata['credentials'] = {'source': 'secrets.token_urlsafe(32), generated in this run',
                                       'bootstrap_password_matches_container': True,
                                       'password_in_command_or_evidence': False,
                                       'runtime_auth': 'container-local Unix socket trust; actual LOGIN roles; TCP reject'}
        self.metadata['dsn'] = {'host': '/var/run/postgresql', 'dbname': 'm5_disposable',
                                'transport': 'docker exec by verified new container ID; Unix socket',
                                'roles': ['postgres', *ROLES, 'core_migrator']}
        self.metadata['pre_sql_isolation_status'] = 'PASS'
        deadline = time.monotonic() + 30
        while True:
            ready = self.command([*self.docker, 'exec', self.container, 'pg_isready',
                                  '-h', '/var/run/postgresql', '-U', 'postgres', '-d', 'm5_disposable'])
            pid1 = self.command([*self.docker, 'exec', self.container, 'cat', '/proc/1/comm'])
            # The image's temporary init server can accept connections before bootstrap finishes.
            if ready.returncode == 0 and pid1.returncode == 0 and pid1.stdout.strip() == 'postgres':
                break
            require(time.monotonic() < deadline, 'disposable database startup failed')
            time.sleep(0.1)  # readiness probe, never a concurrency assumption
        hba = self.command([*self.docker, 'exec', self.container, 'cat', '/var/lib/postgresql/data/pg_hba.conf'])
        rules = [line.split() for line in hba.stdout.splitlines() if line.strip() and not line.lstrip().startswith('#')]
        require(hba.returncode == 0 and rules
                and any(rule[:3] == ['local', 'all', 'all'] for rule in rules)
                and any(rule[:4] == ['host', 'all', 'all', 'all'] for rule in rules)
                and all((rule[0] == 'local' and rule[-1] == 'trust')
                        or (rule[0] == 'host' and rule[-1] == 'reject') for rule in rules),
                'effective socket/host authentication rules mismatch')
        self.metadata['authentication_rules'] = rules
        filesystem = self.command([*self.docker, 'exec', self.container, 'stat', '-f', '-c', '%T', '/var/lib/postgresql/data'])
        require(filesystem.returncode == 0 and filesystem.stdout.strip() == 'tmpfs',
                'PGDATA is not on a live tmpfs filesystem')
        self.metadata['pgdata_filesystem'] = filesystem.stdout.strip()
        version = self.sql('postgres', "SELECT current_setting('server_version_num'); SELECT version(); SELECT current_database();")
        require(version.returncode == 0 and re.search(r'^17\d{4}$', version.stdout, re.M)
                and 'm5_disposable' in version.stdout, 'PostgreSQL 17/database identity check failed')
        self.metadata['postgresql'] = version.stdout
        connection = self.sql('postgres', "SELECT session_user||'/'||current_user||'/'||current_database(); SELECT inet_server_addr() IS NULL;")
        require(connection.returncode == 0 and 'postgres/postgres/m5_disposable' in connection.stdout
                and 't' in connection.stdout.splitlines(), 'Unix-socket positive control failed')
        self.metadata['socket_positive_control'] = {'stdout': connection.stdout, 'stderr': connection.stderr}
        self.metadata['credential_safety'] = 'isolated local socket; empty Docker config; no host credential mounts or external DSN'
        self.metadata['preflight_status'] = 'PASS'
        write_json(self.folder('HARNESS') / 'preflight.json', self.metadata)
        print('PASS PREFLIGHT: new PostgreSQL 17, network none, tmpfs, Unix socket, per-run bootstrap credential', flush=True)
        r = self.sql('postgres', (HERE / 'schema.sql').read_text(encoding='utf-8'))
        require(r.returncode == 0, 'schema bootstrap failed:\n' + r.stdout + r.stderr)
        for role in ROLES:
            r = self.sql(role, "SELECT session_user||'/'||current_user||'/'||rolsuper FROM pg_roles WHERE rolname=current_user;")
            require(f'{role}/{role}/false' in r.stdout and r.returncode == 0, 'not an actual non-owner login: ' + role)
        self.catalog()

    def psql_command(self, role, interactive=False):
        args = [*self.docker, 'exec', '-i', self.container, 'psql', '-X', '-q', '-A', '-t', '-U', role,
                '-h', '/var/run/postgresql', '-d', 'm5_disposable', '-v', 'ON_ERROR_STOP=1', '-v', 'VERBOSITY=verbose']
        if not interactive:
            args.append('--echo-all')
        return args

    def inventory(self):
        result = self.command([*self.docker, 'ps', '--all', '--no-trunc', '--format',
                               '{{json .}}'])
        require(result.returncode == 0, 'container inventory unavailable')
        return sorted(({k: item[k] for k in ('ID', 'Names', 'Image', 'State')}
                       for item in (json.loads(line) for line in result.stdout.splitlines())), key=lambda x: x['ID'])

    def sql(self, role, text):
        return self.command(self.psql_command(role), text)

    def snapshot(self):
        parts = [f"'{t}',(SELECT coalesce(jsonb_agg(to_jsonb(s) ORDER BY to_jsonb(s)::text),'[]'::jsonb) FROM m5.{t} s)"
                 for t in TABLES]
        r = self.sql('core_observer', 'SELECT jsonb_build_object(' + ','.join(parts) + ');')
        require(r.returncode == 0, 'snapshot failed: ' + r.stderr)
        return json.loads(next(line for line in r.stdout.splitlines() if line.startswith('{')))

    def case(self, name, role, sql, state=None, effect='unchanged', contains=None, recovered=False):
        before = self.snapshot()
        r = self.sql(role, "SELECT 'ACTOR='||session_user||'/'||current_user; SHOW transaction_isolation;\n" + sql)
        after = self.snapshot()
        states = re.findall(r'(?:ERROR|FATAL):\s+([0-9A-Z]{5}):', r.stderr)
        ok = ((r.returncode == (0 if recovered else 3) and state in states) if state else r.returncode == 0)
        ok = ok and f'ACTOR={role}/{role}' in r.stdout
        if effect == 'unchanged':
            ok = ok and before == after
        elif effect == 'applied':
            ok = ok and len(after['receipt']) == len(before['receipt'])+1
            ok = ok and len(after['policy_audit']) == len(before['policy_audit'])+1
            old_g = next(x['acl_revision'] for x in before['tenant_guards'] if x['tenant_id']=='T1')
            new_g = next(x['acl_revision'] for x in after['tenant_guards'] if x['tenant_id']=='T1')
            ok = ok and new_g == old_g+1
            receipt = after['receipt'][-1] if len(after['receipt']) == 1 else next(
                (x for x in after['receipt'] if x not in before['receipt']), {})
            ok = ok and receipt.get('resulting_g') == new_g
            ok = ok and any(x['accepted_fence'] == receipt.get('accepted_fence') for x in after['resource_fence'] if x['tenant_id']=='T1')
            ok = ok and all(x['granted'] == (x['actor_id'] == receipt.get('request', {}).get('assignee'))
                            for x in after['resource_acl'] if x['tenant_id']=='T1')
        if contains:
            ok = ok and contains in r.stdout
        result = {'name': name, 'actor': role, 'command': self.psql_command(role), 'sql': sql,
                  'expected': {'sqlstate': state or '00000', 'recovered_at_savepoint': recovered,
                               'effect': effect, 'output_contains': contains},
                  'observed': {'exit_code': r.returncode, 'sqlstates': states},
                  'status': 'PASS' if ok else 'FAIL', 'reason': 'expectations matched' if ok else 'expectation mismatch',
                  'before': before, 'after': after, 'stdout': r.stdout, 'stderr': r.stderr}
        self.record(result)
        return result

    def record(self, result):
        result['test_id'] = self.group
        result['provenance'] = {'source_commit': self.metadata['source_commit'],
                                'schema_sha256': self.metadata['schema_sha256'],
                                'grant_sha256': self.metadata['grant_sha256'],
                                'environment': 'environment.json',
                                'claim_scope': 'disposable prototype only; no deployed writer closure'}
        self.results.append(result)
        self.metadata['database_tests_executed'] += 1
        write_json(self.folder() / (result['name'] + '.json'), result)
        print(result['status'], self.group, result['name'], flush=True)

    def catalog(self):
        queries = {
            'roles': 'SELECT jsonb_agg(to_jsonb(r)) FROM (SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls FROM pg_roles ORDER BY rolname) r;',
            'memberships': 'SELECT jsonb_agg(to_jsonb(m)) FROM pg_auth_members m;',
            'objects': "SELECT jsonb_agg(to_jsonb(c)) FROM (SELECT relname,relkind,pg_get_userbyid(relowner) owner,relacl FROM pg_class WHERE relnamespace='m5'::regnamespace ORDER BY relname) c;",
            'functions': "SELECT jsonb_agg(to_jsonb(p)) FROM (SELECT proname,oid::regprocedure::text signature,pg_get_userbyid(proowner) owner,prosecdef,provolatile,proconfig,proacl,prosrc FROM pg_proc WHERE pronamespace='m5'::regnamespace ORDER BY proname) p;",
            'triggers': "SELECT jsonb_agg(to_jsonb(t)) FROM (SELECT tgrelid::regclass::text relation,tgname,tgenabled,tgdeferrable,tginitdeferred,pg_get_triggerdef(oid) definition FROM pg_trigger WHERE tgrelid IN (SELECT oid FROM pg_class WHERE relnamespace='m5'::regnamespace) AND NOT tgisinternal ORDER BY tgrelid,tgname) t;",
            'grants': "SELECT jsonb_agg(to_jsonb(g)) FROM (SELECT * FROM information_schema.table_privileges WHERE table_schema='m5' ORDER BY grantee,table_name,privilege_type) g;",
            'columns': "SELECT jsonb_agg(to_jsonb(g)) FROM (SELECT * FROM information_schema.column_privileges WHERE table_schema='m5' ORDER BY grantee,table_name,column_name,privilege_type) g;",
            'parameters': 'SELECT jsonb_agg(to_jsonb(p)) FROM pg_parameter_acl p;',
            'defaults': 'SELECT jsonb_agg(to_jsonb(d)) FROM pg_default_acl d;',
            'extensions': 'SELECT jsonb_agg(to_jsonb(e)) FROM pg_extension e;',
            'database_schema_acl': "SELECT datacl::text FROM pg_database WHERE datname=current_database(); SELECT nspname,nspacl::text FROM pg_namespace WHERE nspname IN ('m5','public');"
        }
        for name, sql in queries.items():
            r = self.sql('postgres', sql)
            require(r.returncode == 0, 'catalog capture failed')
            write_json(self.folder('T08-X-09') / ('catalog-' + name + '.json'),
                       {'actor': 'postgres (catalog observer only)', 'sql': sql,
                        'command': self.psql_command('postgres'), 'stdout': r.stdout, 'stderr': r.stderr})

    def assignment(self, key, g, fence, function='assign_replace', assignee='new'):
        return f"SELECT m5.{function}('T1','admin','R1','{key}','{assignee}',{g},{fence});"

    def publish_fault(self, kind):
        text = ('BEGIN; SET LOCAL ROLE core_acl_owner; ' + fault_sql(kind) +
                f' REVOKE ALL ON FUNCTION m5.assign_fault{ASSIGN_SIG} FROM PUBLIC;'
                f' GRANT EXECUTE ON FUNCTION m5.assign_fault{ASSIGN_SIG} TO core_acl_exec_rt; COMMIT;')
        r = self.sql('postgres', text)
        require(r.returncode == 0, 'fault publication failed: ' + r.stderr)
        write_json(self.folder() / ('publication-' + kind + '.json'),
                   {'actor': 'postgres/offline publisher; never runtime proof', 'sql': text, 'stdout': r.stdout, 'stderr': r.stderr})

    def remove_fault(self):
        r = self.sql('postgres', f'DROP FUNCTION m5.assign_fault{ASSIGN_SIG};')
        require(r.returncode == 0, 'fault removal failed')

    def x25(self):
        self.group = 'X-25'
        self.case('normal-multirow-assignment', ROLES[0], 'BEGIN; ' + self.assignment('normal',10,6) + ' COMMIT;', effect='applied', contains='APPLIED')
        for kind, state in [('omit','23514'),('insert_failure','23514'),('malformed','23502'),
                            ('wrong_digest','23514'),('wrong_xid','23514'),('remove','23514'),
                            ('change','23514'),('extra_membership','23514'),('wrong_actual_acl','23514'),('wrong_audit','23514')]:
            self.publish_fault(kind)
            self.case('fault-' + kind, ROLES[0], 'BEGIN; ' + self.assignment('fault-'+kind,11,7,'assign_fault','old') + ' COMMIT;', state)
            self.remove_fault()
        self.publish_fault('insert_failure')
        # psql continues only so the script can issue ROLLBACK TO SAVEPOINT after the expected error.
        self.case('savepoint-receipt-failure', ROLES[0], '\\set ON_ERROR_STOP off\nBEGIN; SAVEPOINT s;\n' +
                  self.assignment('savepoint',11,7,'assign_fault','old') + '\nROLLBACK TO s; COMMIT;\n\\set ON_ERROR_STOP on',
                  state='23514', recovered=True)
        self.remove_fault()
        self.case('savepoint-success-rollback', ROLES[0], 'BEGIN; SAVEPOINT s; ' + self.assignment('sp-success',11,7,assignee='old') + ' ROLLBACK TO s; COMMIT;')
        self.case('constraints-immediate-fail-closed', ROLES[0], 'BEGIN; SET CONSTRAINTS ALL IMMEDIATE; ' + self.assignment('immediate',11,7,assignee='old') + ' COMMIT;', '23514')
        self.case('repeatable-read-rejected', ROLES[0], 'BEGIN ISOLATION LEVEL REPEATABLE READ; ' + self.assignment('rr',11,7) + ' COMMIT;', '25001')
        self.case('forged-principal-rejected', ROLES[0], "BEGIN; SELECT m5.assign_replace('T1','unknown','R1','fake','old',11,7); COMMIT;", '42501')
        self.case('wrong-tenant-resource-rejected', ROLES[0], "BEGIN; SELECT m5.assign_replace('T2','admin','R1','cross','old',10,6); COMMIT;", '42501')
        # Legacy grants exist only for this negative probe; production Helpdesk remains untouched.
        r = self.sql('postgres', 'GRANT SELECT,UPDATE ON m5.resource_acl TO helpdesk_rt; GRANT SELECT,UPDATE(acl_revision) ON m5.tenant_guards TO helpdesk_rt;')
        require(r.returncode == 0, 'legacy grant setup failed')
        self.case('legacy-helpdesk-acl-layer2', 'helpdesk_rt', "BEGIN; UPDATE m5.resource_acl SET granted=false WHERE tenant_id='T1'; COMMIT;", '23514')
        self.case('legacy-helpdesk-generation-layer2', 'helpdesk_rt', "BEGIN; UPDATE m5.tenant_guards SET acl_revision=acl_revision+1000 WHERE tenant_id='T1'; COMMIT;", '23514')
        r = self.sql('postgres', 'REVOKE UPDATE(acl_revision) ON m5.tenant_guards FROM helpdesk_rt; REVOKE ALL ON m5.resource_acl,m5.tenant_guards FROM helpdesk_rt;')
        require(r.returncode == 0, 'legacy grant cleanup failed')

    def privileges(self):
        self.group = 'T08-X-09'
        for role in ROLES:
            for table in TABLES:
                for operation, sql in (
                    ('insert', f'INSERT INTO m5.{table} DEFAULT VALUES;'),
                    ('update', f'UPDATE m5.{table} SET ' + ('recorded_xid=recorded_xid' if table=='mutation_log' else 'tenant_id=tenant_id') + ' WHERE false;'),
                    ('delete', f'DELETE FROM m5.{table} WHERE false;'),
                    ('truncate', f'TRUNCATE m5.{table};'),
                    ('lock', f'LOCK TABLE m5.{table} IN EXCLUSIVE MODE;')):
                    self.case(f'{role}-{table}-{operation}', role, 'BEGIN; ' + sql + ' COMMIT;', '42501')
            attacks = {
                'set-owner': 'SET ROLE core_acl_owner;', 'set-migrator': 'SET ROLE core_migrator;',
                'session-owner': 'SET SESSION AUTHORIZATION core_acl_owner;',
                'disable-trigger': 'ALTER TABLE m5.resource_acl DISABLE TRIGGER ALL;',
                'replication': "SET session_replication_role=replica;",
                'create': 'CREATE TABLE m5.escape(id int);', 'temp': 'CREATE TEMP TABLE escape(id int);',
                'create-function': "CREATE FUNCTION m5.escape() RETURNS int LANGUAGE sql AS 'SELECT 1';",
                'grant-owner': 'GRANT core_acl_owner TO core_acl_exec_rt;',
                'owner-change': 'ALTER TABLE m5.resource_acl OWNER TO core_acl_exec_rt;',
                'generation-update': 'UPDATE m5.tenant_guards SET acl_revision=acl_revision+1000;',
                'raw-row-lock': 'SELECT * FROM m5.tenant_guards FOR UPDATE;',
                'copy-program': "COPY (SELECT 1) TO PROGRAM 'echo unexpected';",
            }
            for name, sql in attacks.items():
                self.case(f'{role}-{name}', role, 'BEGIN; ' + sql + ' COMMIT;', '42501')
            if role not in ROLES[:2]:
                self.case(role+'-lookup-execute', role, "SELECT m5.lookup_receipt('T1','admin','R1','normal');", '42501')
            if role != ROLES[0]:
                self.case(role+'-assign-execute', role, self.assignment('deny',11,7), '42501')
            if role != 'core_observer':
                self.case(role+'-receipt-select', role, 'SELECT * FROM m5.receipt;', '42501')
            # Actual-role catalog assertions, not just a dump from the bootstrap superuser.
            self.case(role+'-effective-catalog', role, """
DO $$ DECLARE p record; BEGIN
 IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname=current_user AND (rolsuper OR rolcreaterole OR rolcreatedb OR rolreplication OR rolbypassrls))
 OR has_column_privilege(current_user,'m5.tenant_guards','acl_revision','UPDATE')
 OR has_database_privilege(current_user,current_database(),'TEMP')
 OR has_schema_privilege(current_user,'m5','CREATE') THEN RAISE EXCEPTION 'unexpected runtime capability'; END IF;
 FOR p IN SELECT oid,rolname FROM pg_roles WHERE rolname IN ('core_acl_owner','core_migrator','pg_write_all_data','pg_execute_server_program','pg_write_server_files') OR rolsuper OR rolcreaterole LOOP
  IF pg_has_role(current_user,p.oid,'MEMBER') OR pg_has_role(current_user,p.oid,'SET') THEN RAISE EXCEPTION 'role reachable: %',p.rolname; END IF;
 END LOOP;
 IF EXISTS(SELECT 1 FROM pg_trigger WHERE NOT tgisinternal AND tgrelid IN
   (SELECT oid FROM pg_class WHERE relnamespace='m5'::regnamespace) AND tgenabled<>'A')
 OR (SELECT count(*) FROM pg_trigger WHERE tgname='receipt_required' AND tgdeferrable AND tginitdeferred
   AND tgrelid IN (SELECT oid FROM pg_class WHERE relnamespace='m5'::regnamespace))<>10 THEN RAISE EXCEPTION 'trigger manifest mismatch'; END IF;
 IF EXISTS(SELECT 1 FROM pg_proc WHERE pronamespace='m5'::regnamespace AND
  (pg_get_userbyid(proowner)<>'core_acl_owner' OR proconfig IS DISTINCT FROM ARRAY['search_path=pg_catalog, pg_temp']
    OR EXISTS(SELECT 1 FROM aclexplode(coalesce(proacl,acldefault('f',proowner))) e WHERE grantee=0 AND privilege_type='EXECUTE'))) THEN RAISE EXCEPTION 'definer publication mismatch'; END IF;
END $$;
""")
        self.case('reader-helper-no-write', ROLES[1], "BEGIN; SELECT m5.reader_guard_share('T1'); COMMIT;")
        self.case('workflow-helper-no-write', ROLES[2], "BEGIN; SELECT m5.reader_guard_share('T1'); COMMIT;")
        self.case('migrator-no-online-owner', 'core_migrator', 'SET ROLE core_acl_owner;', '42501')
        self.catalog()

    def blocked_on(self, waiter, blocker):
        deadline = time.monotonic()+15
        while True:
            r = self.sql('core_observer', f'SELECT {blocker}=ANY(pg_blocking_pids({waiter}));')
            require(r.returncode == 0, 'lock graph observation failed')
            if 't' in r.stdout.splitlines():
                return {'waiter_pid': waiter, 'blocker_pid': blocker, 'sql': f'SELECT pg_blocking_pids({waiter});',
                        'command': self.psql_command('core_observer'), 'stdout': r.stdout}
            require(time.monotonic()<deadline, 'expected lock edge absent')
            time.sleep(0.02)  # graph condition, never a fixed-delay success

    def concurrent(self, name, winner_commit=True, reader_first=False):
        self.group = 'T07' if reader_first else 'X-12'
        before = self.snapshot()
        a = b = None
        trace = {}
        try:
            a = Session(self, ROLES[1] if reader_first else ROLES[0])
            b = Session(self, ROLES[0])
            g = next(x['acl_revision'] for x in before['tenant_guards'] if x['tenant_id']=='T1')
            f = next(x['accepted_fence'] for x in before['resource_fence'] if x['tenant_id']=='T1')
            call = self.assignment(name,g,f+1,assignee='old' if g%2 else 'new')
            first = "SELECT m5.reader_guard_share('T1');" if reader_first else call
            a.send('BEGIN; ' + first + '\n\\echo HELD\n')
            a.until('HELD')
            # All staged changes must remain invisible while the winner holds its transaction.
            require(before == self.snapshot(), 'uncommitted mutation became visible')
            b.send('BEGIN; ' + call + '\n\\echo FOLLOWER_DONE\n')
            trace = self.blocked_on(b.pid,a.pid)
            a.send(('COMMIT;' if winner_commit else 'ROLLBACK;') + '\n\\echo RELEASED\n')
            a.until('RELEASED')
            b.until('FOLLOWER_DONE')
            b.send('COMMIT;\n\\echo COMMITTED\n')
            b.until('COMMITTED')
            after = self.snapshot()
            require(len(after['receipt'])==len(before['receipt'])+1 and
                    len(after['policy_audit'])==len(before['policy_audit'])+1, 'duplicate or missing effect')
            require(next(x['acl_revision'] for x in after['tenant_guards'] if x['tenant_id']=='T1')==g+1,
                    'wrong generation advance')
            if winner_commit and not reader_first:
                require('REPLAY' in ''.join(b.lines), 'waiter did not replay after fresh snapshot')
            status, reason = 'PASS', 'lock graph barrier and exactly-one committed effect matched'
        except Exception as exc:
            after = self.snapshot()
            status, reason = 'FAIL', str(exc)
        finally:
            for s in (a,b):
                if s:
                    s.close()
        self.record({'name':name, 'status':status, 'reason':reason,
                     'actor':ROLES[0], 'before':before,'after':after,'barrier':trace,
                     'expected':'one effect after observed blocking edge; no partial/uncommitted visibility',
                     'sessions':[{'command':s.command,'pid':s.pid,'sql':s.sent,'trace':''.join(s.lines)} for s in (a,b) if s],
                     'sqlstates':re.findall(r'ERROR:\s+([0-9A-Z]{5}):',''.join(''.join(s.lines) for s in (a,b) if s))})

    def status_tests(self, group):
        self.group = group
        if group == 'T07':
            # This response-discard model does not exercise an actual network ACK drop.
            before=self.snapshot()
            g=next(x['acl_revision'] for x in before['tenant_guards'] if x['tenant_id']=='T1')
            f=next(x['accepted_fence'] for x in before['resource_fence'] if x['tenant_id']=='T1')
            self.case('commit-response-discard-model',ROLES[0], 'BEGIN; '+self.assignment('lost-ack-model',g,f+1)+' COMMIT;',effect='applied')
            self.case('status-after-response-discard',ROLES[1], "SELECT m5.lookup_receipt('T1','admin','R1','lost-ack-model');",contains='COMMITTED')
            self.case('replay-after-response-discard',ROLES[0], 'BEGIN; '+self.assignment('lost-ack-model',g,f+1)+' COMMIT;',contains='REPLAY')
            return
        self.group='X-13'
        self.case('committed-status',ROLES[1], "SELECT m5.lookup_receipt('T1','admin','R1','normal');",contains='COMMITTED')
        self.case('hidden-status',ROLES[1], "SELECT m5.lookup_receipt('T1','unknown','R1','normal');",contains='UNRESOLVED')
        self.case('unknown-status',ROLES[1], "SELECT m5.lookup_receipt('T1','admin','R1','missing');",contains='UNRESOLVED')
        self.case('cross-resource-status',ROLES[1], "SELECT m5.lookup_receipt('T2','admin','R1','normal');",contains='UNRESOLVED')

    def finish(self, blocked=None):
        self.metadata['blocker'] = blocked
        if blocked and self.metadata['preflight_status'] != 'PASS':
            self.metadata['preflight_status'] = 'BLOCKED'
        for group in EVIDENCE_IDS:
            cases=[{'name':r['name'],'status':r['status'],'reason':r['reason']} for r in self.results if r['test_id']==group]
            summary={'test_id':group,'status': 'FAIL' if any(x['status']=='FAIL' for x in cases) else 'BLOCKED' if blocked else 'PARTIAL_NOT_ACCEPTED' if cases else 'NOT_RUN',
                     'reason':blocked or 'See coverage gaps; subcase PASS is not full test or gate acceptance.',
                     'database_cases_executed':len(cases),'cases':cases,
                     'remaining':['Full approved contracts, W-17 deployed/external inventory, privileged maintenance/restore proof',
                                  'X-13 revocation/security transport/latency mapping; X-23 retention/restore; X-24 terminal rejection',
                                  'T07 backend-kill stages, actual network ACK loss, timeouts/deadlock; X-12 all arrival schedules',
                                  'X-25 autonomous unique-conflict injection, owner bypass reconciliation; X-16/X-26 Helpdesk integration']}
            if self.metadata['acceptance_gaps']:
                gaps = [x for x in self.metadata['acceptance_gaps'] if x['test_id'] == group]
                summary['remaining'] = [x['reason'] for x in gaps]
                summary['remaining'].append('Independent review, owner decisions and deployed all-writer closure remain required.')
                if gaps and summary['status'] != 'FAIL':
                    summary['status'] = 'BLOCKED'
                summary['reason'] = blocked or 'Executed subcases only; exploratory probes do not approve contracts.'
            write_json(self.folder(group)/'result.json',summary)
            write_json(self.folder(group)/'environment.json',self.metadata)
            folder=self.folder(group)
            sums={p.name:digest(p) for p in sorted(folder.iterdir()) if p.is_file() and p.name!='checksums.json'}
            write_json(folder/'checksums.json',sums)
        if self.container:
            # Only remove the exact new container after validating its ID and task label again.
            info=self.docker_json('inspect',self.container)[0]
            require(info['Id']==self.container and info['Config']['Labels'].get('opentrix.r28.m5.disposable')=='true'
                    and info['Config']['Labels'].get('opentrix.r28.m5.run')==self.run_id,
                    'refusing cleanup: identity mismatch')
            r=self.command([*self.docker,'rm','--force',self.container])
            require(r.returncode==0,'disposable container cleanup failed')
        self.metadata['cleanup'] = 'PASS; only the verified new container removed' if self.container else 'NOT_NEEDED'
        if 'existing_containers_before' in self.metadata:
            after = self.inventory()
            self.metadata['existing_containers_after'] = after
            self.metadata['existing_containers_unchanged'] = after == self.metadata['existing_containers_before']
        self.temp.cleanup()
        files = [p for group in (*EVIDENCE_IDS, 'HARNESS') for p in self.folder(group).rglob('*') if p.is_file()]
        self.metadata['bootstrap_secret_scan'] = {
            'files_scanned': len(files), 'value_available': self.bootstrap_secret is not None,
            'matches': sum(self.bootstrap_secret.encode() in p.read_bytes() for p in files) if self.bootstrap_secret else 0}
        self.bootstrap_secret = None
        write_json(self.folder('HARNESS')/'completion.json',self.metadata)
        folder=self.folder('HARNESS')
        write_json(folder/'checksums.json',{p.name:digest(p) for p in sorted(folder.iterdir())
                                          if p.is_file() and p.name!='checksums.json'})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',default=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    parser.add_argument('--acceptance', action='store_true', help='Run supplemental enforcement cases and exploratory contract probes')
    parser.add_argument('--acceptance-only', action='store_true', help='Fresh fixture and supplemental cases only; does not rerun the historical 388-case suite')
    args=parser.parse_args()
    require(re.fullmatch('[A-Za-z0-9_-]{1,80}',args.run_id),'invalid run ID')
    require(not any((ROOT/'docs/verification/r28/evidence'/g/args.run_id).exists() for g in (*EVIDENCE_IDS,'HARNESS')),
            'run ID already exists; evidence must never be overwritten')
    runner=Runner(args.run_id)
    blocked=None
    try:
        for name, expected in runner.metadata['source_files_sha256'].items():
            data = (HERE / name).read_bytes()
            require(hashlib.sha256(data).hexdigest() == expected, 'source changed before capture: ' + name)
            target = runner.folder('HARNESS') / 'source' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        runner.prepare()
        if args.acceptance_only:
            runner.case('normal-multirow-assignment', ROLES[0], 'BEGIN; ' + runner.assignment('normal',10,6) + ' COMMIT;', effect='applied', contains='APPLIED')
        else:
            runner.x25()
            runner.concurrent('reader-first',reader_first=True)
            runner.status_tests('T07')
            runner.privileges()
            runner.concurrent('original-first')
            runner.concurrent('winner-rollback',winner_commit=False)
            runner.status_tests('X-13')
        if args.acceptance or args.acceptance_only:
            runpy.run_path(str(HERE / 'acceptance.py'))['run'](runner, Session, executor_sql)
    except (RuntimeError, OSError, subprocess.SubprocessError, ValueError, queue.Empty) as exc:
        blocked=str(exc)
        print('BLOCKED:',blocked,flush=True)
    finally:
        runner.finish(blocked)
    print('Database cases executed:',len(runner.results),flush=True)
    return 2 if blocked else 1 if any(x['status']=='FAIL' for x in runner.results) else 0


if __name__=='__main__':
    sys.exit(main())
