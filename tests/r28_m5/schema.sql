-- SPDX-FileCopyrightText: 2026 TRICORE contributors
-- SPDX-License-Identifier: Apache-2.0
-- TEST ONLY. Loaded exclusively by run.py into its fresh, networkless container.
BEGIN;
CREATE ROLE core_acl_owner NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE core_migrator LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE core_acl_exec_rt LOGIN NOINHERIT NOSUPERUSER;
CREATE ROLE core_authz_reader_rt LOGIN NOINHERIT NOSUPERUSER;
CREATE ROLE core_workflow_rt LOGIN NOINHERIT NOSUPERUSER;
CREATE ROLE helpdesk_rt LOGIN NOINHERIT NOSUPERUSER;
CREATE ROLE core_observer LOGIN NOINHERIT NOSUPERUSER;
-- Migrator membership is deliberately absent while admission is OPEN.
REVOKE ALL ON DATABASE m5_disposable FROM PUBLIC;
GRANT CONNECT ON DATABASE m5_disposable TO core_acl_exec_rt, core_authz_reader_rt,
    core_workflow_rt, helpdesk_rt, core_observer, core_migrator;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA m5 AUTHORIZATION core_acl_owner;
SET LOCAL ROLE core_acl_owner;
-- Schema-local REVOKE cannot remove PostgreSQL's global PUBLIC EXECUTE default.
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
CREATE TABLE m5.tenant_guards (tenant_id text PRIMARY KEY, acl_revision bigint NOT NULL CHECK (acl_revision >= 0));
CREATE TABLE m5.tenant_memberships (tenant_id text REFERENCES m5.tenant_guards, actor_id text,
    active boolean NOT NULL, PRIMARY KEY(tenant_id,actor_id));
CREATE TABLE m5.resource_registry (tenant_id text REFERENCES m5.tenant_guards, resource_id text,
    lifecycle text NOT NULL CHECK(lifecycle IN ('ACTIVE','TOMBSTONED')), PRIMARY KEY(tenant_id,resource_id));
CREATE TABLE m5.workflow_definition_bindings (tenant_id text REFERENCES m5.tenant_guards,
    definition_id text, active boolean NOT NULL, PRIMARY KEY(tenant_id,definition_id));
CREATE TABLE m5.authority (tenant_id text, principal text, resource_id text, service_id text NOT NULL,
    can_execute boolean NOT NULL, can_lookup boolean NOT NULL, PRIMARY KEY(tenant_id,principal,resource_id),
    FOREIGN KEY(tenant_id,resource_id) REFERENCES m5.resource_registry);
CREATE TABLE m5.admission (tenant_id text PRIMARY KEY, is_open boolean NOT NULL);
CREATE TABLE m5.resource_acl (tenant_id text, resource_id text, actor_id text, operation text,
    granted boolean NOT NULL, PRIMARY KEY(tenant_id,resource_id,actor_id,operation),
    CHECK(operation IN ('workflow:read','workflow:transition')),
    FOREIGN KEY(tenant_id,resource_id) REFERENCES m5.resource_registry,
    FOREIGN KEY(tenant_id,actor_id) REFERENCES m5.tenant_memberships);
CREATE TABLE m5.resource_fence (tenant_id text, resource_id text, accepted_fence bigint NOT NULL CHECK(accepted_fence>=0),
    PRIMARY KEY(tenant_id,resource_id), FOREIGN KEY(tenant_id,resource_id) REFERENCES m5.resource_registry);
CREATE TABLE m5.policy_audit (audit_id uuid PRIMARY KEY, tenant_id text NOT NULL, resource_id text NOT NULL,
    principal text NOT NULL, service_id text NOT NULL, command_key text NOT NULL,
    operation text NOT NULL CHECK(operation='ACL_ASSIGN_REPLACE'),
    previous_g bigint NOT NULL, resulting_g bigint NOT NULL CHECK(resulting_g=previous_g+1),
    accepted_fence bigint NOT NULL, request jsonb NOT NULL, changes jsonb NOT NULL,
    change_digest bytea NOT NULL CHECK(octet_length(change_digest)=32), recorded_xid xid8 NOT NULL,
    UNIQUE(tenant_id,resulting_g));
CREATE TABLE m5.receipt (receipt_id uuid PRIMARY KEY, tenant_id text NOT NULL, service_id text NOT NULL,
    principal text NOT NULL, command_key text NOT NULL CHECK(command_key ~ '^[a-zA-Z0-9_-]{1,64}$'),
    operation text NOT NULL CHECK(operation='ACL_ASSIGN_REPLACE'), resource_id text NOT NULL,
    outcome text NOT NULL CHECK(outcome='APPLIED'), fingerprint_version int NOT NULL CHECK(fingerprint_version=1),
    request jsonb NOT NULL, fingerprint bytea NOT NULL CHECK(octet_length(fingerprint)=32),
    expected_g bigint NOT NULL, resulting_g bigint NOT NULL CHECK(resulting_g=expected_g+1),
    accepted_fence bigint NOT NULL, audit_id uuid NOT NULL REFERENCES m5.policy_audit,
    change_digest bytea NOT NULL CHECK(octet_length(change_digest)=32), recorded_xid xid8 NOT NULL,
    UNIQUE(tenant_id,service_id,operation,command_key));
CREATE TABLE m5.mutation_log (event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recorded_xid xid8 NOT NULL, relation_name text NOT NULL, tenant_id text NOT NULL,
    action text NOT NULL, old_row jsonb, new_row jsonb);

-- Synthetic fixture. Bootstrap precedes trigger installation and admission opening.
INSERT INTO m5.tenant_guards VALUES ('T1',10),('T2',10);
INSERT INTO m5.tenant_memberships SELECT t,a,true FROM (VALUES('T1'),('T2')) x(t),
    (VALUES('admin'),('old'),('new')) y(a);
INSERT INTO m5.resource_registry VALUES ('T1','R1','ACTIVE'),('T2','R2','ACTIVE');
INSERT INTO m5.workflow_definition_bindings VALUES ('T1','D1',true),('T2','D2',true);
INSERT INTO m5.authority VALUES ('T1','admin','R1','synthetic-core',true,true),
    ('T2','admin','R2','synthetic-other-service',true,true);
INSERT INTO m5.admission VALUES ('GLOBAL',true),('T1',true),('T2',true);
INSERT INTO m5.resource_acl SELECT r.tenant_id,r.resource_id,a,o,a='old'
    FROM m5.resource_registry r CROSS JOIN (VALUES('old'),('new')) x(a)
    CROSS JOIN (VALUES('workflow:read'),('workflow:transition')) y(o);
INSERT INTO m5.resource_fence VALUES ('T1','R1',5),('T2','R2',5);

CREATE FUNCTION m5.deny_change() RETURNS trigger LANGUAGE plpgsql
SET search_path=pg_catalog,pg_temp AS $$
BEGIN
    RAISE EXCEPTION 'immutable evidence or unsupported operation' USING ERRCODE='23514';
END $$;

CREATE FUNCTION m5.capture_delta() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,pg_temp AS $$
BEGIN
    INSERT INTO m5.mutation_log(recorded_xid,relation_name,tenant_id,action,old_row,new_row)
    VALUES(pg_current_xact_id(),TG_TABLE_NAME,coalesce(NEW.tenant_id,OLD.tenant_id),TG_OP,
        CASE WHEN TG_OP <> 'INSERT' THEN to_jsonb(OLD) END,
        CASE WHEN TG_OP <> 'DELETE' THEN to_jsonb(NEW) END);
    RETURN NULL;
END $$;

CREATE FUNCTION m5.actual_changes(x xid8) RETURNS jsonb LANGUAGE sql VOLATILE
SET search_path=pg_catalog,pg_temp AS $$
    SELECT coalesce(jsonb_agg(jsonb_build_object('table',relation_name,'action',action,
        'old',old_row,'new',new_row) ORDER BY relation_name,old_row::text,new_row::text),'[]'::jsonb)
    FROM m5.mutation_log WHERE recorded_xid=x
        AND relation_name IN ('resource_acl','tenant_guards','resource_fence')
$$;

CREATE FUNCTION m5.validate_commit() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,pg_temp AS $$
DECLARE
    x xid8 := pg_current_xact_id(); r m5.receipt; a m5.policy_audit;
    g m5.mutation_log; f m5.mutation_log; n integer;
BEGIN
    -- Re-query final rows; NEW is only a queued event image, not final transaction state.
    SELECT count(*) INTO n FROM m5.receipt WHERE recorded_xid=x;
    IF n <> 1 THEN
        RAISE EXCEPTION 'one complete final receipt required' USING ERRCODE='23514';
    END IF;
    SELECT * INTO STRICT r FROM m5.receipt WHERE recorded_xid=x;
    SELECT count(*) INTO n FROM m5.policy_audit WHERE recorded_xid=x;
    IF n <> 1 THEN RAISE EXCEPTION 'one audit required' USING ERRCODE='23514'; END IF;
    SELECT * INTO STRICT a FROM m5.policy_audit WHERE recorded_xid=x;
    IF EXISTS (SELECT 1 FROM m5.mutation_log WHERE recorded_xid=x AND
        (tenant_id<>r.tenant_id OR relation_name NOT IN
        ('resource_acl','tenant_guards','resource_fence','policy_audit','receipt'))) THEN
        RAISE EXCEPTION 'out-of-scope effective policy mutation' USING ERRCODE='23514';
    END IF;
    IF (SELECT count(*) FROM m5.mutation_log WHERE recorded_xid=x AND relation_name='tenant_guards')<>1
        OR (SELECT count(*) FROM m5.mutation_log WHERE recorded_xid=x AND relation_name='resource_fence')<>1
        OR (SELECT count(*) FROM m5.mutation_log WHERE recorded_xid=x AND relation_name='policy_audit')<>1
        OR (SELECT count(*) FROM m5.mutation_log WHERE recorded_xid=x AND relation_name='receipt')<>1 THEN
        RAISE EXCEPTION 'wrong effect cardinality' USING ERRCODE='23514';
    END IF;
    SELECT * INTO STRICT g FROM m5.mutation_log WHERE recorded_xid=x AND relation_name='tenant_guards';
    SELECT * INTO STRICT f FROM m5.mutation_log WHERE recorded_xid=x AND relation_name='resource_fence';
    IF g.action<>'UPDATE' OR f.action<>'UPDATE'
        OR (g.old_row->>'acl_revision')::bigint<>r.expected_g
        OR (g.new_row->>'acl_revision')::bigint<>r.resulting_g
        OR (g.old_row-'acl_revision')<>(g.new_row-'acl_revision')
        OR (f.old_row-'accepted_fence')<>(f.new_row-'accepted_fence')
        OR f.new_row->>'resource_id'<>r.resource_id
        OR (f.new_row->>'accepted_fence')::bigint<>r.accepted_fence
        OR (f.old_row->>'accepted_fence')::bigint>=r.accepted_fence
        OR (SELECT acl_revision FROM m5.tenant_guards WHERE tenant_id=r.tenant_id) IS DISTINCT FROM r.resulting_g
        OR (SELECT accepted_fence FROM m5.resource_fence WHERE tenant_id=r.tenant_id AND resource_id=r.resource_id)
            IS DISTINCT FROM r.accepted_fence THEN
        RAISE EXCEPTION 'generation/fence mismatch' USING ERRCODE='23514';
    END IF;
    IF EXISTS(SELECT 1 FROM m5.mutation_log WHERE recorded_xid=x AND relation_name='resource_acl'
        AND (action<>'UPDATE' OR old_row-'granted'<>new_row-'granted'
            OR new_row->>'resource_id'<>r.resource_id))
        OR NOT EXISTS(SELECT 1 FROM m5.resource_acl WHERE tenant_id=r.tenant_id AND resource_id=r.resource_id)
        OR EXISTS(SELECT 1 FROM m5.resource_acl WHERE tenant_id=r.tenant_id AND resource_id=r.resource_id
            AND granted IS DISTINCT FROM (actor_id=r.request->>'assignee')) THEN
        RAISE EXCEPTION 'ACL replacement mismatch' USING ERRCODE='23514';
    END IF;
    IF ROW(a.audit_id,a.tenant_id,a.resource_id,a.principal,a.service_id,a.command_key,a.operation,
            a.previous_g,a.resulting_g,a.accepted_fence,a.request,a.change_digest)
        IS DISTINCT FROM ROW(r.audit_id,r.tenant_id,r.resource_id,r.principal,r.service_id,r.command_key,r.operation,
            r.expected_g,r.resulting_g,r.accepted_fence,r.request,r.change_digest)
        OR a.changes<>m5.actual_changes(x)
        OR a.change_digest<>sha256(convert_to(a.changes::text,'UTF8'))
        OR r.fingerprint<>sha256(convert_to(r.request::text,'UTF8'))
        OR r.request<>jsonb_build_object('version',1,'tenant',r.tenant_id,'service',r.service_id,
            'principal',r.principal,'operation',r.operation,'resource',r.resource_id,
            'assignee',r.request->>'assignee','expected_g',r.expected_g,'fence',r.accepted_fence)
        OR (SELECT count(*) FROM m5.resource_acl WHERE tenant_id=r.tenant_id AND resource_id=r.resource_id
            AND actor_id=r.request->>'assignee' AND granted)<>2 THEN
        RAISE EXCEPTION 'receipt/audit/actual delta mismatch' USING ERRCODE='23514';
    END IF;
    RETURN NULL;
END $$;

-- Table set is explicit and identical to the harness catalog allow-list.
DO $$ DECLARE t text; BEGIN
    FOREACH t IN ARRAY ARRAY['tenant_guards','tenant_memberships','resource_registry',
        'workflow_definition_bindings','authority','admission','resource_acl','resource_fence','policy_audit','receipt'] LOOP
        EXECUTE format('CREATE TRIGGER capture AFTER INSERT OR UPDATE OR DELETE ON m5.%I
            FOR EACH ROW EXECUTE FUNCTION m5.capture_delta()',t);
        EXECUTE format('CREATE CONSTRAINT TRIGGER receipt_required AFTER INSERT OR UPDATE OR DELETE ON m5.%I
            DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION m5.validate_commit()',t);
        EXECUTE format('CREATE TRIGGER no_truncate BEFORE TRUNCATE ON m5.%I
            FOR EACH STATEMENT EXECUTE FUNCTION m5.deny_change()',t);
        EXECUTE format('ALTER TABLE m5.%I ENABLE ALWAYS TRIGGER capture',t);
        EXECUTE format('ALTER TABLE m5.%I ENABLE ALWAYS TRIGGER receipt_required',t);
        EXECUTE format('ALTER TABLE m5.%I ENABLE ALWAYS TRIGGER no_truncate',t);
    END LOOP;
END $$;
CREATE TRIGGER immutable BEFORE UPDATE OR DELETE ON m5.receipt FOR EACH ROW EXECUTE FUNCTION m5.deny_change();
CREATE TRIGGER immutable BEFORE UPDATE OR DELETE ON m5.policy_audit FOR EACH ROW EXECUTE FUNCTION m5.deny_change();
CREATE TRIGGER immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON m5.mutation_log
    FOR EACH STATEMENT EXECUTE FUNCTION m5.deny_change();
ALTER TABLE m5.receipt ENABLE ALWAYS TRIGGER immutable;
ALTER TABLE m5.policy_audit ENABLE ALWAYS TRIGGER immutable;
ALTER TABLE m5.mutation_log ENABLE ALWAYS TRIGGER immutable;

CREATE FUNCTION m5.assign_replace(p_tenant text,p_principal text,p_resource text,p_key text,
    p_assignee text,p_g bigint,p_fence bigint) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $assign$
DECLARE
    v_service text; v_g bigint; v_fence bigint; v_request jsonb; v_digest bytea;
    v_receipt m5.receipt; v_audit uuid:=gen_random_uuid(); v_changes jsonb; v_xid xid8;
BEGIN
    IF session_user<>'core_acl_exec_rt' OR current_setting('transaction_isolation')<>'read committed'
        OR pg_current_xact_id_if_assigned() IS NOT NULL THEN
        RAISE EXCEPTION 'invalid executor context' USING ERRCODE='25001';
    END IF;
    IF p_key IS NULL OR p_key !~ '^[a-zA-Z0-9_-]{1,64}$' OR p_g IS NULL OR p_g<0
        OR p_fence IS NULL OR p_fence<=0 OR p_assignee IS NULL THEN
        RAISE EXCEPTION 'invalid request' USING ERRCODE='22023';
    END IF;
    SELECT service_id INTO v_service FROM m5.authority WHERE tenant_id=p_tenant
        AND principal=p_principal AND resource_id=p_resource AND can_lookup;
    IF NOT FOUND THEN RAISE EXCEPTION 'not available' USING ERRCODE='42501'; END IF;
    SELECT acl_revision INTO v_g FROM m5.tenant_guards WHERE tenant_id=p_tenant FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'not available' USING ERRCODE='42501'; END IF;
    -- Tenant-exclusive guard serializes every scoped key, no weaker hash/advisory identity.
    IF (SELECT count(*) FROM m5.admission WHERE tenant_id IN ('GLOBAL',p_tenant) AND is_open)<>2 THEN
        RAISE EXCEPTION 'admission closed' USING ERRCODE='55000';
    END IF;
    IF NOT EXISTS(SELECT 1 FROM m5.authority WHERE tenant_id=p_tenant AND principal=p_principal
        AND resource_id=p_resource AND service_id=v_service AND can_lookup)
        OR NOT EXISTS(SELECT 1 FROM m5.tenant_memberships WHERE tenant_id=p_tenant AND actor_id=p_principal AND active) THEN
        RAISE EXCEPTION 'not available' USING ERRCODE='42501';
    END IF;
    v_request:=jsonb_build_object('version',1,'tenant',p_tenant,'service',v_service,
        'principal',p_principal,'operation','ACL_ASSIGN_REPLACE','resource',p_resource,
        'assignee',p_assignee,'expected_g',p_g,'fence',p_fence);
    v_digest:=sha256(convert_to(v_request::text,'UTF8'));
    SELECT * INTO v_receipt FROM m5.receipt WHERE tenant_id=p_tenant AND service_id=v_service
        AND operation='ACL_ASSIGN_REPLACE' AND command_key=p_key;
    IF FOUND THEN
        IF v_receipt.fingerprint<>v_digest THEN
            RAISE EXCEPTION 'payload conflict' USING ERRCODE='23505';
        END IF;
        RETURN jsonb_build_object('status','REPLAY','receipt',to_jsonb(v_receipt));
    END IF;
    IF NOT EXISTS(SELECT 1 FROM m5.authority WHERE tenant_id=p_tenant AND principal=p_principal
        AND resource_id=p_resource AND can_execute)
        OR NOT EXISTS(SELECT 1 FROM m5.tenant_memberships WHERE tenant_id=p_tenant AND actor_id=p_principal AND active)
        OR NOT EXISTS(SELECT 1 FROM m5.tenant_memberships WHERE tenant_id=p_tenant AND actor_id=p_assignee AND active)
        OR NOT EXISTS(SELECT 1 FROM m5.resource_registry WHERE tenant_id=p_tenant AND resource_id=p_resource AND lifecycle='ACTIVE')
        OR (SELECT count(*) FROM m5.resource_acl WHERE tenant_id=p_tenant AND resource_id=p_resource AND actor_id=p_assignee)<>2 THEN
        RAISE EXCEPTION 'not available' USING ERRCODE='42501';
    END IF;
    SELECT accepted_fence INTO v_fence FROM m5.resource_fence
        WHERE tenant_id=p_tenant AND resource_id=p_resource FOR UPDATE;
    IF v_g<>p_g OR p_fence<=v_fence THEN
        -- Q02 is not frozen: rollback only; no fabricated terminal rejection receipt.
        RAISE EXCEPTION 'generation or fence conflict' USING ERRCODE='40001';
    END IF;
    UPDATE m5.resource_acl SET granted=(actor_id=p_assignee)
        WHERE tenant_id=p_tenant AND resource_id=p_resource AND granted IS DISTINCT FROM (actor_id=p_assignee);
    UPDATE m5.tenant_guards SET acl_revision=acl_revision+1 WHERE tenant_id=p_tenant;
    UPDATE m5.resource_fence SET accepted_fence=p_fence WHERE tenant_id=p_tenant AND resource_id=p_resource;
    v_xid:=pg_current_xact_id();
    v_changes:=m5.actual_changes(v_xid);
    INSERT INTO m5.policy_audit VALUES(v_audit,p_tenant,p_resource,p_principal,v_service,p_key,
        'ACL_ASSIGN_REPLACE',p_g,p_g+1,p_fence,v_request,v_changes,
        sha256(convert_to(v_changes::text,'UTF8')),v_xid);
    INSERT INTO m5.receipt VALUES(gen_random_uuid(),p_tenant,v_service,p_principal,p_key,
        'ACL_ASSIGN_REPLACE',p_resource,'APPLIED',1,v_request,v_digest,p_g,p_g+1,p_fence,v_audit,
        sha256(convert_to(v_changes::text,'UTF8')),v_xid);
    RETURN jsonb_build_object('status','APPLIED','audit',v_audit);
END $assign$;

CREATE FUNCTION m5.lookup_receipt(p_tenant text,p_principal text,p_resource text,p_key text)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE v_service text; v_result jsonb;
BEGIN
    IF session_user NOT IN ('core_acl_exec_rt','core_authz_reader_rt') THEN
        RAISE EXCEPTION 'not available' USING ERRCODE='42501';
    END IF;
    SELECT service_id INTO v_service FROM m5.authority WHERE tenant_id=p_tenant AND principal=p_principal
        AND resource_id=p_resource AND can_lookup;
    IF NOT FOUND OR NOT EXISTS(SELECT 1 FROM m5.tenant_memberships
        WHERE tenant_id=p_tenant AND actor_id=p_principal AND active)
        OR (SELECT count(*) FROM m5.admission
        WHERE tenant_id IN ('GLOBAL',p_tenant) AND is_open)<>2 THEN RETURN '{"status":"UNRESOLVED"}'; END IF;
    SELECT jsonb_build_object('status','COMMITTED','receipt',to_jsonb(r)) INTO v_result FROM m5.receipt r
        WHERE tenant_id=p_tenant AND service_id=v_service AND resource_id=p_resource AND command_key=p_key
        AND operation='ACL_ASSIGN_REPLACE';
    RETURN coalesce(v_result,'{"status":"UNRESOLVED"}'::jsonb);
END $$;

CREATE FUNCTION m5.reader_guard_share(p_tenant text) RETURNS void LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,pg_temp AS $$
BEGIN
    IF session_user NOT IN ('core_authz_reader_rt','core_workflow_rt') OR p_tenant IS DISTINCT FROM 'T1' THEN
        RAISE EXCEPTION 'not available' USING ERRCODE='42501';
    END IF;
    -- shortcut: synthetic T1 reader mapping only, replace after Q07 identity/reader contract approval.
    PERFORM 1 FROM m5.tenant_guards WHERE tenant_id=p_tenant FOR SHARE;
END $$;

REVOKE ALL ON ALL TABLES IN SCHEMA m5 FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA m5 FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA m5 FROM PUBLIC;
GRANT USAGE ON SCHEMA m5 TO core_acl_exec_rt,core_authz_reader_rt,core_workflow_rt,helpdesk_rt,core_observer;
GRANT SELECT ON m5.tenant_guards,m5.tenant_memberships,m5.resource_registry,m5.resource_acl,
    m5.workflow_definition_bindings TO core_authz_reader_rt,core_workflow_rt;
GRANT SELECT ON ALL TABLES IN SCHEMA m5 TO core_observer;
GRANT EXECUTE ON FUNCTION m5.assign_replace(text,text,text,text,text,bigint,bigint) TO core_acl_exec_rt;
GRANT EXECUTE ON FUNCTION m5.lookup_receipt(text,text,text,text) TO core_acl_exec_rt,core_authz_reader_rt;
GRANT EXECUTE ON FUNCTION m5.reader_guard_share(text) TO core_authz_reader_rt,core_workflow_rt;
COMMIT;
