-- SPDX-FileCopyrightText: 2026 TRICORE contributors
-- SPDX-License-Identifier: Apache-2.0
-- EXPLORATORY Q02 fixture: not the accepted M5 receipt contract or a migration.
BEGIN;
CREATE SCHEMA m5_probe AUTHORIZATION core_acl_owner;
SET LOCAL ROLE core_acl_owner;
CREATE TABLE m5_probe.rejection (
    tenant_id text NOT NULL, service_id text NOT NULL, operation text NOT NULL,
    command_key text NOT NULL, request jsonb NOT NULL, result jsonb NOT NULL,
    PRIMARY KEY(tenant_id,service_id,operation,command_key),
    CHECK(result->>'outcome'='REJECTED_TERMINAL'),
    CHECK(result->>'reason' IN ('STALE_POLICY_GENERATION','FENCE_NOT_ADVANCING')));
CREATE TRIGGER immutable BEFORE UPDATE OR DELETE ON m5_probe.rejection
    FOR EACH ROW EXECUTE FUNCTION m5.deny_change();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON m5_probe.rejection
    FOR EACH STATEMENT EXECUTE FUNCTION m5.deny_change();
ALTER TABLE m5_probe.rejection ENABLE ALWAYS TRIGGER immutable;
ALTER TABLE m5_probe.rejection ENABLE ALWAYS TRIGGER no_truncate;
CREATE FUNCTION m5_probe.reject(p_key text,p_g bigint,p_fence bigint) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE g bigint; f bigint; request jsonb; old m5_probe.rejection; result jsonb; reason text;
BEGIN
    IF session_user<>'core_acl_exec_rt' OR p_key IS NULL OR p_key !~ '^[a-zA-Z0-9_-]{1,64}$'
        OR p_g IS NULL OR p_g<0 OR p_fence IS NULL OR p_fence<=0 THEN
        RAISE EXCEPTION 'invalid probe caller/request' USING ERRCODE='22023';
    END IF;
    SELECT acl_revision INTO STRICT g FROM m5.tenant_guards WHERE tenant_id='T1' FOR UPDATE;
    IF NOT EXISTS(SELECT 1 FROM m5.authority WHERE tenant_id='T1' AND principal='admin'
        AND resource_id='R1' AND service_id='synthetic-core' AND can_execute AND can_lookup)
        OR NOT EXISTS(SELECT 1 FROM m5.tenant_memberships WHERE tenant_id='T1' AND actor_id='admin' AND active)
        OR (SELECT count(*) FROM m5.admission WHERE tenant_id IN ('GLOBAL','T1') AND is_open)<>2 THEN
        RAISE EXCEPTION 'not available' USING ERRCODE='42501';
    END IF;
    request:=jsonb_build_object('tenant','T1','service','synthetic-core','operation','ACL_ASSIGN_REPLACE',
        'principal','admin','resource','R1','assignee','new','expected_g',p_g,'fence',p_fence,'version',1);
    SELECT * INTO old FROM m5_probe.rejection WHERE tenant_id='T1' AND service_id='synthetic-core'
        AND operation='ACL_ASSIGN_REPLACE' AND command_key=p_key;
    IF FOUND THEN
        IF old.request<>request THEN RAISE EXCEPTION 'key conflict' USING ERRCODE='23505'; END IF;
        RETURN old.result;
    END IF;
    SELECT accepted_fence INTO STRICT f FROM m5.resource_fence WHERE tenant_id='T1' AND resource_id='R1';
    IF p_g<g THEN reason:='STALE_POLICY_GENERATION';
    ELSIF p_fence<=f THEN reason:='FENCE_NOT_ADVANCING';
    ELSE RAISE EXCEPTION 'probe supports monotone rejection only' USING ERRCODE='22023'; END IF;
    result:=jsonb_build_object('outcome','REJECTED_TERMINAL','reason',reason,'key',p_key,
        'original_request',request);
    INSERT INTO m5_probe.rejection VALUES('T1','synthetic-core','ACL_ASSIGN_REPLACE',p_key,request,result);
    RETURN result;
END $$;
REVOKE ALL ON SCHEMA m5_probe FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA m5_probe FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA m5_probe FROM PUBLIC;
GRANT USAGE ON SCHEMA m5_probe TO core_acl_exec_rt,core_observer;
GRANT SELECT ON m5_probe.rejection TO core_observer;
GRANT EXECUTE ON FUNCTION m5_probe.reject(text,bigint,bigint) TO core_acl_exec_rt;
COMMIT;
