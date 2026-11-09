# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""Supplemental disposable-only evidence. Contract probes are not owner decisions."""
import json
import re


EXECUTOR = 'core_acl_exec_rt'
READER = 'core_authz_reader_rt'
SIG = '(text,text,text,text,text,bigint,bigint)'


def checked(r, sql):
    result = r.sql('postgres', sql)
    if result.returncode:
        raise RuntimeError('offline fixture operation failed: ' + result.stderr)
    # Persist offline SQL too; bootstrap/superuser is never runtime isolation evidence.
    r.metadata.setdefault('offline_operations', []).append(
        {'actor': 'postgres (offline fixture publisher)', 'command': r.psql_command('postgres'),
         'sql': sql, 'stdout': result.stdout, 'stderr': result.stderr})
    return result


def position(snapshot):
    return (next(x['acl_revision'] for x in snapshot['tenant_guards'] if x['tenant_id'] == 'T1'),
            next(x['accepted_fence'] for x in snapshot['resource_fence'] if x['tenant_id'] == 'T1'))


def same_business(before, after):
    return before == after


def one_effect(before, after, key):
    """No count-only oracle: require complete matching receipt/audit and actual final state."""
    receipts = [x for x in after['receipt'] if x not in before['receipt']]
    audits = [x for x in after['policy_audit'] if x not in before['policy_audit']]
    if len(receipts) != 1 or len(audits) != 1:
        return False
    receipt, audit = receipts[0], audits[0]
    g, fence = position(before)
    return (receipt['command_key'] == key and receipt['audit_id'] == audit['audit_id']
            and receipt['recorded_xid'] == audit['recorded_xid']
            and receipt['request'] == audit['request']
            and receipt['change_digest'] == audit['change_digest']
            and receipt['expected_g'] == g and receipt['resulting_g'] == g + 1
            and audit['previous_g'] == g and audit['resulting_g'] == g + 1
            and position(after) == (g + 1, fence + 1)
            and all(x['granted'] == (x['actor_id'] == receipt['request']['assignee'])
                    for x in after['resource_acl'] if x['tenant_id'] == 'T1')
            and all(before[t] == after[t] for t in ('authority', 'admission', 'tenant_memberships',
                                                    'resource_registry', 'workflow_definition_bindings')))


def session_case(r, Session, name, body, expected):
    before = r.snapshot()
    sessions, observations = [], {}
    status, reason = 'FAIL', 'case did not complete'
    try:
        body(before, sessions, observations)
        after = r.snapshot()
        if not expected(before, after, sessions, observations):
            raise AssertionError('snapshot/SQLSTATE/transaction oracle mismatch')
        status, reason = 'PASS', 'controlled barriers, traces and before/after matched oracle'
    except Exception as exc:
        reason = str(exc)
    finally:
        for session in reversed(sessions):
            session.close()
        after = r.snapshot()
    r.record({'name': name, 'actor': [s.command[s.command.index('-U') + 1] for s in sessions],
              'status': status, 'reason': reason, 'before': before, 'after': after,
              'expected': body.__doc__, 'observations': observations,
              'sessions': [{'command': s.command, 'pid': s.pid, 'sql': s.sent,
                            'trace': ''.join(s.lines)} for s in sessions],
              'sqlstates': re.findall(r'(?:ERROR|FATAL):\s+([0-9A-Z]{5}):',
                                     ''.join(''.join(s.lines) for s in sessions))})


def unique_conflict(r, Session, executor_source):
    r.group = 'X-25'
    source = executor_source().replace('m5.assign_replace(', 'm5.assign_fault(', 1)
    start = source.index('    SELECT * INTO v_receipt')
    end = source.index('    IF NOT EXISTS', start)
    source = source[:start] + source[end:]
    checked(r, 'BEGIN; SET LOCAL ROLE core_acl_owner; ' + source +
            f' GRANT EXECUTE ON FUNCTION m5.assign_fault{SIG} TO {EXECUTOR}; COMMIT;')
    key = 'autonomous-unique'

    def body(before, sessions, observations):
        """First actual executor commits; independent faulty executor reaches same-key UNIQUE: 23505, no second effect."""
        g, f = position(before)
        a, b = Session(r, EXECUTOR), Session(r, EXECUTOR)
        sessions.extend((a, b))
        a.send('BEGIN; ' + r.assignment(key, g, f + 1) + '\n\\echo STAGED\n')
        a.until('STAGED')
        if before != r.snapshot():
            raise AssertionError('uncommitted winner visible')
        b.send('\\set ON_ERROR_STOP off\nBEGIN; ' + r.assignment(key, g + 1, f + 2, 'assign_fault', 'old') +
               '\nCOMMIT;\n\\echo FOLLOWER_END\n')
        observations['lock_edge'] = r.blocked_on(b.pid, a.pid)
        a.send('COMMIT;\n\\echo WINNER_COMMITTED\n')
        a.until('WINNER_COMMITTED')
        b.until('FOLLOWER_END')

    session_case(r, Session, key, body,
                 lambda b, a, ss, o: one_effect(b, a, key) and '23505' in ''.join(ss[1].lines)
                 and 'receipt_tenant_id_service_id_operation_command_key_key' in ''.join(ss[1].lines))
    r.remove_fault()


def direct_and_forged(r, executor_source):
    r.group = 'X-25'
    g, f = position(r.snapshot())
    for name, old, new in (
            ('principal', 'v_service,p_principal,p_key,', "v_service,'forged',p_key,"),
            ('resource', "'ACL_ASSIGN_REPLACE',p_resource,'APPLIED'", "'ACL_ASSIGN_REPLACE','R2','APPLIED'"),
            ('key', 'v_service,p_principal,p_key,', "v_service,p_principal,'forged-key',")):
        source = executor_source().replace('m5.assign_replace(', 'm5.assign_fault(', 1)
        start = source.index('    INSERT INTO m5.receipt')
        source = source[:start] + source[start:].replace(old, new, 1)
        checked(r, 'BEGIN; SET LOCAL ROLE core_acl_owner; ' + source +
                f' GRANT EXECUTE ON FUNCTION m5.assign_fault{SIG} TO {EXECUTOR}; COMMIT;')
        r.case('forged-' + name, EXECUTOR, 'BEGIN; ' + r.assignment('forge-' + name, g, f + 1, 'assign_fault') +
               ' COMMIT;', '23514')
        r.remove_fault()
    checked(r, 'GRANT SELECT,UPDATE ON m5.resource_acl,m5.tenant_guards,m5.resource_fence TO helpdesk_rt;'
            'GRANT SELECT,INSERT ON m5.receipt TO helpdesk_rt;')
    r.case('direct-multirow-multitable-omission', 'helpdesk_rt', "BEGIN; "
           "UPDATE m5.resource_acl SET granted=NOT granted WHERE tenant_id='T1';"
           "UPDATE m5.tenant_guards SET acl_revision=acl_revision+1 WHERE tenant_id='T1';"
           "UPDATE m5.resource_fence SET accepted_fence=accepted_fence+1 WHERE tenant_id='T1'; COMMIT;", '23514')
    r.case('direct-savepoint-partial-rollback', 'helpdesk_rt', "BEGIN; "
           "UPDATE m5.resource_acl SET granted=NOT granted WHERE tenant_id='T1'; SAVEPOINT s;"
           "UPDATE m5.tenant_guards SET acl_revision=acl_revision+1 WHERE tenant_id='T1';"
           'ROLLBACK TO s; COMMIT;', '23514')
    columns = ('tenant_id,service_id,principal,operation,resource_id,outcome,fingerprint_version,request,'
               'fingerprint,expected_g,resulting_g,accepted_fence,audit_id,change_digest')
    r.case('direct-forged-existing-audit', 'helpdesk_rt',
           f"BEGIN; INSERT INTO m5.receipt(receipt_id,command_key,recorded_xid,{columns}) "
           f"SELECT gen_random_uuid(),'forged-existing',pg_current_xact_id(),{columns} "
           "FROM m5.receipt WHERE command_key='normal'; COMMIT;", '23514')
    checked(r, 'REVOKE ALL ON m5.resource_acl,m5.tenant_guards,m5.resource_fence,m5.receipt FROM helpdesk_rt;')


def kill_and_timeout(r, Session):
    r.group = 'T07'
    for stage in ('before-mutation', 'after-mutation', 'before-commit', 'commit-in-flight'):
        key = 'kill-' + stage

        def body(before, sessions, observations):
            """Terminate actual backend (SIGTERM/57P01) at observed barrier; full rollback; authenticated status before same-key retry."""
            g, f = position(before)
            holder = Session(r, READER)
            victim = Session(r, EXECUTOR)
            sessions.extend((holder, victim))
            if stage == 'before-mutation':
                holder.send("BEGIN; SELECT m5.reader_guard_share('T1');\n\\echo GUARD_HELD\n")
                holder.until('GUARD_HELD')
                victim.send('BEGIN; ' + r.assignment(key, g, f + 1))
                observations['barrier'] = r.blocked_on(victim.pid, holder.pid)
            else:
                victim.send('BEGIN; ' + r.assignment(key, g, f + 1) + '\n\\echo MUTATION_STAGED\n')
                victim.until('MUTATION_STAGED')
                if stage == 'before-commit':
                    victim.send('SET CONSTRAINTS ALL IMMEDIATE;\n\\echo VALIDATED_BEFORE_COMMIT\n')
                    victim.until('VALIDATED_BEFORE_COMMIT')
                if stage == 'commit-in-flight':
                    holder.send('SELECT pg_advisory_lock(280707);\n\\echo COMMIT_GATE_HELD\n')
                    holder.until('COMMIT_GATE_HELD')
                    victim.send('COMMIT;')
                    observations['barrier'] = r.blocked_on(victim.pid, holder.pid)
            if before != r.snapshot():
                raise AssertionError('staged mutation visible before termination')
            killed = checked(r, f'SELECT pg_terminate_backend({victim.pid},5000);')
            observations['kill'] = {'sql': f'SELECT pg_terminate_backend({victim.pid},5000);',
                                    'stdout': killed.stdout, 'stderr': killed.stderr}
            if stage in ('after-mutation', 'before-commit'):
                victim.send('SELECT 1;')
            victim.proc.wait(timeout=10)
            victim.close()
            if 't' not in killed.stdout.splitlines():
                raise AssertionError('backend termination not acknowledged')
            holder.send('ROLLBACK; SELECT pg_advisory_unlock_all();\n\\echo RELEASED\n')
            holder.until('RELEASED')
            observations['rollback_snapshot'] = r.snapshot()
            observations['status'] = r.case(key + '-authenticated-status', READER,
                f"SELECT m5.lookup_receipt('T1','admin','R1','{key}');", contains='UNRESOLVED')['status']
            observations['retry'] = r.case(key + '-retry', EXECUTOR,
                'BEGIN; ' + r.assignment(key, g, f + 1) + ' COMMIT;', effect='applied')['status']

        if stage == 'commit-in-flight':
            checked(r, "BEGIN; SET LOCAL ROLE core_acl_owner; "
                    "CREATE FUNCTION m5.commit_barrier() RETURNS trigger LANGUAGE plpgsql "
                    "SET search_path=pg_catalog,pg_temp AS $$ BEGIN PERFORM pg_advisory_xact_lock(280707); RETURN NULL; END $$;"
                    "CREATE CONSTRAINT TRIGGER zz_commit_barrier AFTER INSERT ON m5.receipt "
                    "DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION m5.commit_barrier(); COMMIT;")
        session_case(r, Session, key, body,
                     lambda b, a, ss, o: o.get('rollback_snapshot') == b and one_effect(b, a, key)
                     and o.get('status') == o.get('retry') == 'PASS' and '57P01' in ''.join(ss[1].lines))
        if stage == 'commit-in-flight':
            checked(r, 'DROP TRIGGER zz_commit_barrier ON m5.receipt; DROP FUNCTION m5.commit_barrier();')

    for timeout, state in (('lock_timeout', '55P03'), ('statement_timeout', '57014')):
        def body(before, sessions, observations):
            """Actual runtime waits on held guard then configured timeout; SQLSTATE and all business rows unchanged."""
            g, f = position(before)
            holder, victim = Session(r, READER), Session(r, EXECUTOR)
            sessions.extend((holder, victim))
            holder.send("BEGIN; SELECT m5.reader_guard_share('T1');\n\\echo HELD\n")
            holder.until('HELD')
            victim.send(f"\\set ON_ERROR_STOP off\nBEGIN; SET LOCAL {timeout}='5s'; " +
                        r.assignment(timeout, g, f + 1) + '\nROLLBACK;\n\\echo TIMEOUT_DONE\n')
            observations['barrier'] = r.blocked_on(victim.pid, holder.pid)
            victim.until('TIMEOUT_DONE')
            holder.send('COMMIT;\n\\echo RELEASED\n')
            holder.until('RELEASED')
        session_case(r, Session, timeout, body,
                     lambda b, a, ss, o: same_business(b, a) and state in ''.join(ss[1].lines))

    def deadlock(before, sessions, observations):
        """Executor waits on reader guard; reader waits on executor advisory lock; one 40P01, both rollback, no effects."""
        g, f = position(before)
        a, b = Session(r, EXECUTOR), Session(r, READER)
        sessions.extend((a, b))
        a.send('\\set ON_ERROR_STOP off\nBEGIN; SELECT pg_advisory_xact_lock(280701);\n\\echo HELD\n')
        a.until('HELD')
        b.send("\\set ON_ERROR_STOP off\nBEGIN; SELECT m5.reader_guard_share('T1');\n\\echo HELD\n")
        b.until('HELD')
        a.send(r.assignment('deadlock', g, f + 1) + '\nROLLBACK;\n\\echo DONE\n')
        observations['first_edge'] = r.blocked_on(a.pid, b.pid)
        b.send('SELECT pg_advisory_xact_lock(280701);\nROLLBACK;\n\\echo DONE\n')
        a.until('DONE')
        b.until('DONE')
    session_case(r, Session, 'actual-deadlock', deadlock,
                 lambda b, a, ss, o: same_business(b, a) and
                 ''.join(''.join(s.lines) for s in ss).count('40P01') == 1)
    r.metadata['acceptance_gaps'].append({'test_id': 'T07', 'case': 'actual-commit-ack-drop', 'status': 'BLOCKED',
        'reason': 'network none, host TCP reject, docker-exec Unix socket; no verified in-container transport proxy. '
                  'Isolation not changed; response discard is historical model only. SIGTERM in-flight COMMIT is not ACK-drop. '
                  'SIGKILL/postmaster crash and Java transport mapping also not exercised.'})


def exact_privileges(r):
    r.group = 'T08-X-09'
    # Compare effective table/column/function privileges, including absence, for each actual role.
    sql = """
DO $$ DECLARE t record; c record; p text; f record; expected boolean; BEGIN
 FOR t IN SELECT relname FROM pg_class WHERE relnamespace='m5'::regnamespace AND relkind='r' LOOP
  FOREACH p IN ARRAY ARRAY['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER','MAINTAIN'] LOOP
   expected := p='SELECT' AND (current_user='core_observer' OR
     (current_user IN ('core_authz_reader_rt','core_workflow_rt') AND t.relname IN
      ('tenant_guards','tenant_memberships','resource_registry','resource_acl','workflow_definition_bindings')));
   IF has_table_privilege(current_user,'m5.'||t.relname,p) IS DISTINCT FROM expected THEN
    RAISE EXCEPTION 'table allow-list mismatch: % %',t.relname,p; END IF;
  END LOOP;
  FOR c IN SELECT attname FROM pg_attribute WHERE attrelid=('m5.'||t.relname)::regclass AND attnum>0 AND NOT attisdropped LOOP
   FOREACH p IN ARRAY ARRAY['SELECT','INSERT','UPDATE','REFERENCES'] LOOP
    expected := p='SELECT' AND (current_user='core_observer' OR
      (current_user IN ('core_authz_reader_rt','core_workflow_rt') AND t.relname IN
       ('tenant_guards','tenant_memberships','resource_registry','resource_acl','workflow_definition_bindings')));
    IF has_column_privilege(current_user,'m5.'||t.relname,c.attname,p) IS DISTINCT FROM expected THEN
     RAISE EXCEPTION 'column allow-list mismatch: % % %',t.relname,c.attname,p; END IF;
   END LOOP;
  END LOOP;
 END LOOP;
 FOR f IN SELECT oid,proname FROM pg_proc WHERE pronamespace='m5'::regnamespace LOOP
  expected := (f.proname='assign_replace' AND current_user='core_acl_exec_rt') OR
   (f.proname='lookup_receipt' AND current_user IN ('core_acl_exec_rt','core_authz_reader_rt')) OR
   (f.proname='reader_guard_share' AND current_user IN ('core_authz_reader_rt','core_workflow_rt'));
  IF has_function_privilege(current_user,f.oid,'EXECUTE') IS DISTINCT FROM expected THEN
   RAISE EXCEPTION 'function allow-list mismatch: %',f.proname; END IF;
 END LOOP;
 IF NOT has_schema_privilege(current_user,'m5','USAGE') OR has_schema_privilege(current_user,'m5','CREATE')
 OR has_schema_privilege(current_user,'public','USAGE') OR has_schema_privilege(current_user,'public','CREATE')
 OR has_database_privilege(current_user,current_database(),'CREATE')
 OR has_database_privilege(current_user,current_database(),'TEMP')
 OR EXISTS(SELECT 1 FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname=current_user))
 OR EXISTS(SELECT 1 FROM pg_class WHERE relnamespace='m5'::regnamespace AND pg_get_userbyid(relowner)<>'core_acl_owner')
 OR EXISTS(SELECT 1 FROM pg_namespace WHERE nspname='m5' AND pg_get_userbyid(nspowner)<>'core_acl_owner')
 OR EXISTS(SELECT 1 FROM pg_default_acl d, LATERAL aclexplode(d.defaclacl) e
           WHERE d.defaclrole='core_acl_owner'::regrole AND e.grantee<>d.defaclrole)
 OR NOT EXISTS(SELECT 1 FROM pg_default_acl WHERE defaclrole='core_acl_owner'::regrole
               AND defaclnamespace=0 AND defaclobjtype='f') THEN
  RAISE EXCEPTION 'schema/ownership/membership/default allow-list mismatch'; END IF;
 IF EXISTS(SELECT 1 FROM pg_class c, LATERAL aclexplode(coalesce(c.relacl,acldefault('r',c.relowner))) e
           WHERE c.relnamespace='m5'::regnamespace AND (e.grantee=0 OR (e.grantee<>c.relowner AND e.is_grantable)))
 THEN RAISE EXCEPTION 'PUBLIC or grant-option table access'; END IF;
END $$;
"""
    for role in (EXECUTOR, READER, 'core_workflow_rt', 'helpdesk_rt', 'core_observer'):
        r.case(role + '-exact-allow-list', role, sql)
    # Transactional function + grant publication: a failing GRANT must roll back the function too.
    r.case('atomic-publication-failure', 'postgres', "BEGIN; SET LOCAL ROLE core_acl_owner; "
           "CREATE FUNCTION m5.failed_publication() RETURNS int LANGUAGE sql SET search_path=pg_catalog,pg_temp AS 'SELECT 1';"
           'GRANT EXECUTE ON FUNCTION m5.failed_publication() TO no_such_r28_role; COMMIT;', '42704')
    r.case('failed-publication-absent', EXECUTOR, "DO $$ BEGIN IF to_regprocedure('m5.failed_publication()') IS NOT NULL "
           "THEN RAISE EXCEPTION 'publication leaked'; END IF; END $$;")
    r.case('migrator-publication-denied', 'core_migrator',
           "CREATE FUNCTION m5.failed_publication() RETURNS int LANGUAGE sql AS 'SELECT 1';", '42501')
    r.catalog()


def privileged_probes(r, Session):
    """Exploratory closed-admission maintenance/revoke; never grant-based protection against owner."""
    r.group = 'X-23'
    baseline = r.snapshot()
    close = "UPDATE m5.admission SET is_open=false;"
    def maintenance(sql, tables):
        toggles = lambda mode: ' '.join(f'ALTER TABLE m5.{t} {mode} TRIGGER USER;' for t in tables)
        return ('BEGIN; SET LOCAL ROLE core_acl_owner; ' + toggles('DISABLE') + sql +
                toggles('ENABLE ALWAYS') + ' COMMIT;')
    checked(r, maintenance(close, ['admission']))
    r.case('closed-admission-executor-denied', EXECUTOR,
           'BEGIN; ' + r.assignment('closed-admission', *position(baseline)) + ' COMMIT;', '55000')
    r.case('closed-admission-status-hidden', READER,
           "SELECT m5.lookup_receipt('T1','admin','R1','normal');", contains='UNRESOLVED')
    # Actual owner bypass: explicitly expected, not a runtime enforcement PASS or counterexample.
    before = r.snapshot()
    checked(r, maintenance("UPDATE m5.resource_acl SET granted=NOT granted WHERE tenant_id='T1';", ['resource_acl']))
    dirty = r.snapshot()
    detected = before['resource_acl'] != dirty['resource_acl'] and before['receipt'] == dirty['receipt']
    r.group = 'X-25'
    r.record({'name': 'owner-bypass-closed-admission', 'actor': 'postgres SET ROLE core_acl_owner (privileged)',
              'status': 'PASS' if detected else 'FAIL', 'reason': 'owner bypass observed; no superuser protection claimed',
              'before': before, 'after': dirty, 'expected': 'owner can disable triggers; reconciliation must detect receipt-less ACL drift',
              'observed': {'drift_detected': detected, 'admission_open': any(x['is_open'] for x in dirty['admission'])},
              'claim_scope': 'exploratory maintenance fixture; not approved deployed procedure'})
    r.group = 'X-23'
    r.case('unreconciled-admission-stays-closed', EXECUTOR,
           'BEGIN; ' + r.assignment('dirty-admission', *position(baseline)) + ' COMMIT;', '55000')
    checked(r, maintenance("UPDATE m5.resource_acl SET granted=NOT granted WHERE tenant_id='T1';", ['resource_acl']))
    if before != r.snapshot():
        raise AssertionError('reconciliation did not restore complete closed-admission snapshot')
    # Revoke-first: publish authority revoke under the tenant guard, then let the waiting executor read freshly.
    checked(r, maintenance('UPDATE m5.admission SET is_open=true;', ['admission']))
    r.group = 'T08-X-09'
    def revoke(before, sessions, observations):
        """Privileged offline revocation wins guard; actual executor rechecks can_lookup after wait: 42501, zero receipt/effect."""
        g, f = position(before)
        owner, executor = Session(r, 'postgres'), Session(r, EXECUTOR)
        sessions.extend((owner, executor))
        owner.send("BEGIN; SET LOCAL ROLE core_acl_owner; SELECT * FROM m5.tenant_guards WHERE tenant_id='T1' FOR UPDATE;"
                   'ALTER TABLE m5.authority DISABLE TRIGGER USER;'
                   "UPDATE m5.authority SET can_lookup=false,can_execute=false WHERE tenant_id='T1';"
                   'ALTER TABLE m5.authority ENABLE ALWAYS TRIGGER USER;\n\\echo REVOKE_STAGED\n')
        owner.until('REVOKE_STAGED')
        executor.send('\\set ON_ERROR_STOP off\nBEGIN; ' + r.assignment('revoke-first', g, f + 1) +
                      '\nROLLBACK;\n\\echo RECHECKED\n')
        observations['barrier'] = r.blocked_on(executor.pid, owner.pid)
        owner.send('COMMIT;\n\\echo REVOKED\n')
        owner.until('REVOKED')
        executor.until('RECHECKED')
    session_case(r, Session, 'revoke-first-fresh-authorization', revoke,
        lambda b, a, ss, o: '42501' in ''.join(ss[1].lines) and
        all(b[t] == a[t] for t in b if t != 'authority') and
        all(not x['can_lookup'] and not x['can_execute'] for x in a['authority'] if x['tenant_id'] == 'T1'))
    r.case('status-after-revoke-hidden', READER,
           "SELECT m5.lookup_receipt('T1','admin','R1','normal');", contains='UNRESOLVED')
    checked(r, maintenance("UPDATE m5.authority SET can_lookup=true,can_execute=true WHERE tenant_id='T1';", ['authority']))
    r.metadata['acceptance_gaps'].append({'test_id': 'X-23', 'status': 'BLOCKED',
        'reason': 'Closed-admission/drift/reconcile probes are exploratory; no approved retention duration, '
                  'durable retirement/tombstone/restore-reopen contract, actual backup restore or operational owner evidence.'})


def run(r, Session, executor_source):
    unique_conflict(r, Session, executor_source)
    direct_and_forged(r, executor_source)
    kill_and_timeout(r, Session)
    exact_privileges(r)
    privileged_probes(r, Session)
    r.group = 'X-12'
    r.concurrent('retry-first')
    r.concurrent('delayed-original')
    r.concurrent('rollback-replay', winner_commit=False)
    r.group = 'X-23'
    r.case('retention-delete-denied', EXECUTOR, 'DELETE FROM m5.receipt;', '42501')
    r.case('retention-privileged-delete-trigger', 'postgres', "DELETE FROM m5.receipt WHERE command_key='normal';", '23514')
    r.case('late-original-retained-replay', EXECUTOR, 'BEGIN; ' + r.assignment('normal', 10, 6) + ' COMMIT;', contains='REPLAY')
    r.group = 'X-24'
    g, f = position(r.snapshot())
    for attempt in (1, 2):
        r.case(f'deterministic-stale-generation-{attempt}', EXECUTOR,
               'BEGIN; ' + r.assignment('reject-stale', g - 1, f + 1) + ' COMMIT;', '40001')
        r.case(f'deterministic-nonadvancing-fence-{attempt}', EXECUTOR,
               'BEGIN; ' + r.assignment('reject-fence', g, f) + ' COMMIT;', '40001')
    r.case('applied-key-immutable-payload', EXECUTOR,
           'BEGIN; ' + r.assignment('normal', 10, 6, assignee='old') + ' COMMIT;', '23505')
    r.metadata['acceptance_gaps'].extend([
        {'test_id': 'X-24', 'status': 'BLOCKED', 'reason': 'Current contract only rolls back deterministic G/fence conflicts; '
         'no terminal rejection receipt exists. Rejection keyed immutability/replay requires Q02 owner confirmation. '
         'APPLIED replay is not terminal rejection replay.'},
        {'test_id': 'X-16-X-26', 'status': 'BLOCKED', 'reason': 'Consumer fixture prepared separately; '
         'no approved durable-reservation/CAS/manual-reconciliation integration contract or consumer environment.'}])
