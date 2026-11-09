<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R28 → R27A Dependency Contract — P0 review package

**Status: PROPOSED / INDEPENDENT OWNER REVIEW REQUIRED.** Đây là dependency package cho Core/Helpdesk two-service split, không phải toàn bộ R28, OpenAPI hoàn chỉnh hay quyền triển khai runtime.

**Disposition:** 0 hợp đồng P0 đạt READY FOR IMPLEMENTATION trong gói này. Các hướng đã được xác nhận chỉ được kế thừa đúng phạm vi; không nâng recommendation, COMMENTED hoặc ACCEPT WITH CONDITIONS thành approval. ADR-010/ADR-015 vẫn PROPOSED; G0-CONTRACT BLOCKED; G0-DESIGN và G0-IMPLEMENT/RUNTIME NOT ACCEPTED; R27 Step 03 IN PROGRESS.

## 1. Source register và preflight

Kiểm tra GitHub ngày 2026-11-09: HEAD của cả bốn PR không đổi so với baseline bên dưới; không có delta HEAD mới cần review lại. Review/comments cũng không thay đổi so với đợt assessment trước. Nếu bất kỳ nguồn nào đổi sau snapshot này, so sánh exact old→new SHA và review lại các P0/Q/test phụ thuộc trước khi sử dụng; không tự chuyển approval sang SHA mới.

| ID | PR / full source commit SHA | Đường dẫn và phạm vi |
| --- | --- | --- |
| S1 | [#159](https://github.com/tricore-opentrix/opentrix/pull/159), ef4b9484369c94ed7e5674e4b056b0d8f673e1ba | [ADR-010](https://github.com/tricore-opentrix/opentrix/blob/ef4b9484369c94ed7e5674e4b056b0d8f673e1ba/docs/08-decisions/ADR-010-core-helpdesk-service-boundary.md), [HTTP candidate](https://github.com/tricore-opentrix/opentrix/blob/ef4b9484369c94ed7e5674e4b056b0d8f673e1ba/docs/01-architecture/r27-core-workflow-http-contract.md), [authorization boundary](https://github.com/tricore-opentrix/opentrix/blob/ef4b9484369c94ed7e5674e4b056b0d8f673e1ba/docs/01-architecture/r27-core-authorization-boundary.md). Open, chưa accepted. |
| S2 | [#160](https://github.com/tricore-opentrix/opentrix/pull/160), 5618091dc205b196b551465d2c52def9313ed1fb | [ADR-015](https://github.com/tricore-opentrix/opentrix/blob/5618091dc205b196b551465d2c52def9313ed1fb/docs/08-decisions/ADR-015-core-workflow-acl-v3-g0.md), [C-01..C-30 matrix](https://github.com/tricore-opentrix/opentrix/blob/5618091dc205b196b551465d2c52def9313ed1fb/docs/verification/r27/adr015-g0-contract-verification-matrix.md). Open Draft; logical model, chưa schema/grants approval. |
| S3 | [#165](https://github.com/tricore-opentrix/opentrix/pull/165), 2335a0858b6eafeacdff82bf157b44df116145bc | [Readiness/Q register](https://github.com/tricore-opentrix/opentrix/blob/2335a0858b6eafeacdff82bf157b44df116145bc/docs/verification/r28/r28-g0-design-readiness-review.md), [command/idempotency design](https://github.com/tricore-opentrix/opentrix/blob/2335a0858b6eafeacdff82bf157b44df116145bc/docs/verification/r28/r28-core-acl-command-and-idempotency-design.md), [PostgreSQL X-01..X-26 plan](https://github.com/tricore-opentrix/opentrix/blob/2335a0858b6eafeacdff82bf157b44df116145bc/docs/verification/r28/r28-postgresql-locking-privilege-t07-t08-plan.md). Open Draft; ba Markdown files, không runtime/HTTP/migration change. |
| S4 | [#145](https://github.com/tricore-opentrix/opentrix/pull/145), 5d577dd4a0a8efa830459cf35cb1868e52a9de2f | [R29 contract](https://github.com/tricore-opentrix/opentrix/blob/5d577dd4a0a8efa830459cf35cb1868e52a9de2f/docs/03-applications/helpdesk/r29-use-case-contract.md). Six typed input contracts, chưa handlers/idempotency runtime. Open Draft. |
| S5 | [#163 review](https://github.com/tricore-opentrix/opentrix/pull/163#pullrequestreview-5821754766), 35ab10a7fff600b1b2e48afd776d15c6834bdedd | OD-06 Option A và contract-remediation direction được xác nhận; squash vào S2. [Owner record](https://github.com/tricore-opentrix/opentrix/pull/163#issuecomment-6731860971) reviewed af7506d26fbe33f4e634012389bde9c6553c31ab; [Bảo reconfirm](https://github.com/tricore-opentrix/opentrix/pull/163#issuecomment-6732338208) tại full S5 SHA. Không ADR/G0 acceptance. |
| S6 | [Yến #165 review](https://github.com/tricore-opentrix/opentrix/pull/165#pullrequestreview-5822299893), 2335a0858b6eafeacdff82bf157b44df116145bc | COMMENTED; Q01/Q06/Q08/Q09 recommendations, documentation package only. |
| S7 | [Ánh #165 review](https://github.com/tricore-opentrix/opentrix/pull/165#pullrequestreview-5822334086), 2335a0858b6eafeacdff82bf157b44df116145bc | COMMENTED; Q02..Q06/Q08 recommendations, chưa chọn contract. |
| S8 | [Core/PostgreSQL assessment](https://github.com/tricore-opentrix/opentrix/pull/165#issuecomment-6734047293), 2335a0858b6eafeacdff82bf157b44df116145bc | AI-assisted assessment cho Bảo review; không human owner signature hoặc GitHub APPROVE. |
| S9 | [R29 scoped APPROVE](https://github.com/tricore-opentrix/opentrix/pull/145#pullrequestreview-5821940340), 5d577dd4a0a8efa830459cf35cb1868e52a9de2f | Yến chỉ approve pre-integration documentation/contract scope; [Bảo COMMENT](https://github.com/tricore-opentrix/opentrix/pull/145#pullrequestreview-5822217339) giữ runtime integration blocked. |

S1..S9 là định danh dẫn chứng: mỗi lần dùng bên dưới trỏ về đúng PR/path/full SHA ở bảng này, không phải mutable main. Các nguồn S2/matrix còn nhắc R29 cũ là historical evidence; S4 là consumer HEAD đã đối chiếu, vẫn còn Q06 discrepancy.

Preflight local: origin https://github.com/tricore-opentrix/opentrix.git; worktree gốc docs/r28-g0-design-readiness-review tại a8190b14a7678cef71600820fb1e92c8f5b12953, không tracked diff, có portal-bff/bin/ untracked được giữ nguyên. Gói mới được soạn trên branch riêng docs/r28-r27a-p0-dependency-contract-20261109 trong worktree riêng từ exact S3 SHA. Không merge/cherry-pick S1/S4 vào base.

## 2. Status vocabulary và approval boundary

| Contract status | Ý nghĩa |
| --- | --- |
| APPROVED — CONTRACT DIRECTION ONLY | Chỉ hướng có explicit owner/reviewer evidence và đúng scope/SHA, hiện là OD-06 Option A qua S5. Không có nghĩa exact API/schema hoặc gate approved. |
| PROPOSED | Candidate có nguồn nhưng cần owner lựa chọn; không normative production contract. |
| OPEN / BLOCKED | Thiếu quyết định/proof hoặc producer-consumer mâu thuẫn; không implement theo giả định. |

[Decision Closure Matrix](r28-r27a-decision-closure-matrix.md) giữ Q01..Q09 PENDING. [Mandatory Verification Plan](r28-r27a-mandatory-verification-plan.md) định nghĩa oracle; không có PostgreSQL/runtime PASS trong gói này.

## 3. P0-01 — Core HTTP/OpenAPI

**Sources:** S1 HTTP candidate §§routes/errors/A1–A4; S2 §§6/11/16; S3 command design §§1/7; S4 cross-service contract. **Owner/reviewer:** Yến Core/API và architecture; Bảo Core security; Ánh consumer compatibility.

**Confirmed baseline facts:** chỉ có method/path và named DTO candidate bên dưới; routes specified, not registered. S1 nói CoreWorkflowHttpContract.java là local uncommitted work. Không có exact Core OpenAPI/DTO đó được phê duyệt trong các nguồn này.

| Operation / Core ownership | Exact candidate method/path | Input → successful response | Freeze disposition / prerequisite |
| --- | --- | --- | --- |
| CREATE — Core Workflow | POST /api/v1/core/workflow-instances | CreateRequest → 201 InstanceView + Location | PROPOSED surface; BLOCKED full schema/idempotency; A1 chọn composite Create+Activate hay two-step recovery. Duplicate chosen instance ID → 409 chưa phải idempotency. |
| ACTIVATE — Core Workflow | POST /api/v1/core/workflow-instances/{id}/activate | ActivateRequest → 200 InstanceView | PROPOSED; expectedVersion mandatory trong candidate nhưng runtime activateInstance chưa nhận version. BLOCKED enforcement + stale-version tests. |
| TRANSITION — Core Workflow | POST /api/v1/core/workflow-instances/{id}/transitions | TransitionRequest → 200 TransitionView | PROPOSED; expectedVersion mandatory, trusted actor server-side. Exact schema/status/recovery và Q06/Q08 chưa freeze. |
| READ — Core Workflow | GET /api/v1/core/workflow-instances/{id} | Không body → 200 InstanceView | PROPOSED; current authorization + consistent materialization; exact view và visibility precedence chưa duyệt. |
| HISTORY — Core Workflow | GET /api/v1/core/workflow-instances/{id}/history | Không body → 200 HistoryView; required operation READ | PROPOSED; không thêm HISTORY authority; collection/order/pagination/snapshot wire chưa freeze. |
| ACL-admin / command-status — Core policy/ledger | Method/path chưa được nguồn chốt | Logical envelope/receipt ở P0-03/04, không DTO mới | BLOCKED; không phát minh route/status schema để R27A client dùng. |

**Request/response/schema gaps:** tên CreateRequest/ActivateRequest/TransitionRequest/InstanceView/TransitionView/HistoryView không đủ định nghĩa JSON. Chưa có approved required-field set, limits, numeric representation/range, null/default/unknown/duplicate-field rule hoặc response collection shape. Chỉ version requirement nêu trên là candidate constraint cụ thể; field set của legacy adapter không tự trở thành Core DTO.

**Legacy evidence only:** tại S2, [WorkflowController](https://github.com/tricore-opentrix/opentrix/blob/5618091dc205b196b551465d2c52def9313ed1fb/backend/src/main/java/com/tricore/dxos/gateway/workflow/controller/WorkflowController.java) dùng /api/v1/workflow-instances (không /core), chưa registered. Create DTO có instanceId/definitionId/definitionVersion/resourceType/resourceId; transition có transitionId/expectedVersion; legacy history trả list. Không chép chúng sang candidate mới rồi tuyên bố frozen. Runtime registration vẫn bị chặn.

| Condition | Candidate HTTP/code từ S1/S2 | Exact semantics còn OPEN |
| --- | --- | --- |
| Missing/invalid verified authentication | 401 AUTHENTICATION_REQUIRED | Service/delegation scheme và error-body/precedence. |
| Visible resource, thiếu operation permission | 403 FORBIDDEN | Visibility policy và ACL-admin-specific mapping. |
| Hidden/missing instance/resource/definition | 404 NOT_FOUND | Hidden và nonexistent phải indistinguishable, không lộ tenant/receipt/G/fence. |
| Duplicate instance / stale Workflow version | 409 INSTANCE_ALREADY_EXISTS / VERSION_CONFLICT | Precedence khi nhiều conflicts, replay success khác fresh stale execution. |
| Unknown Workflow transition | 422 INVALID_TRANSITION | Phân biệt unknown transition với known-but-disallowed state; full mapping chưa freeze. |
| Authoritative ACL unavailable / uncertain commit | 503 AUTHORIZATION_UNAVAILABLE / COMMIT_OUTCOME_UNKNOWN | Known rollback khác uncertain commit; retry/status policy phụ thuộc Q06. |

ApiError(status,code,message,errors) là legacy implementation shape ở S2, không approved Core error schema. Validation 400/415, headers/content types, no-disclosure message/details và precedence phải được chốt trong OpenAPI; không tự bổ sung vào production contract. Candidate precedence để review: verified auth → shape/current scope/visibility → authorized ledger lookup → replay/conflict hoặc fresh execution preconditions. Thứ tự shape/visibility và stale G/fence/state khi đồng thời sai vẫn BLOCKED, không cho caller không có quyền đọc conflict metadata.

| Version / owner | Required separation |
| --- | --- |
| Workflow runtimeVersion — Core | expectedVersion của ACTIVATE/TRANSITION so với Workflow version; không dùng assignment version thay thế. |
| assignmentVersion — Helpdesk | Business CAS/token; Core coi opaque, không thể chứng minh Helpdesk current version. |
| policyGeneration — Core | expectedPolicyGeneration theo D-01 A trong ACL command; batch/no-op increment OPEN; không tự thêm required G vào mọi Workflow route. |
| fencingSequence — approved Helpdesk stream / Core accepted value | Incoming > last accepted theo exact tenant/resource; atomic compare/advance. Expected-accepted-fence CAS field là proposal chưa chọn. |

**R27A dependency:** chỉ dùng bảng làm interface planning; trước client/handler chính thức cần owner-approved exact OpenAPI/security/errors, A1, Q01..Q06 liên quan và applicable G0 approvals. Hiện không endpoint nào READY FOR IMPLEMENTATION.

## 4. P0-02 — Service Authentication & Authorization

**Sources:** S1 D3–D5/authorization boundary; S2 INV-01..07/§7; S3 command §1.1; S4 Authority; S6/S8. **Owner/reviewer:** Yến trust boundary; Bảo Core authorization; Ánh Helpdesk identity/intent mapping.

**Confirmed direction:** Helpdesk xác minh business actor; Core xác minh caller độc lập qua trusted ingress/CurrentPrincipal.requireVerified(), resolve exact resource + tenant + lifecycle + definition binding và current membership/grant. Operation authority không bằng resource permission. Existing user adapter tại S2 dùng canonical issuer+subject; credential rotation không tự định nghĩa canonical service identity. Không có approved Helpdesk→Core credential/delegation wire scheme.

| Boundary | Contract proposal / mandatory constraint | OPEN/BLOCKED + required test |
| --- | --- | --- |
| Helpdesk → Core authentication | Verified issuer/audience/signature/expiry/token type và canonical service principal; JWT/mTLS/other mechanism chưa chọn | Bảo/Yến/Ánh phải freeze credential/pool/audience và rotation mapping. Test wrong issuer/audience/type/expiry, forged/absent credential, principal rotation/replay. |
| Tenant/resource | Body tenantId không chọn trusted tenant; resolve authoritative exact resource within service scope, no cross-tenant alias | X-08/C-13/C-14: T1 credential + T2 resource/header/body không mutate/disclose; authorized T2 control chứng minh resource tồn tại. |
| Delegated actor | Tách initiating business user, verified service principal, affected actors và audit actor/source | Delegation proof/encoding/requiredness OPEN. Body/X-User/X-Role/X-Tenant không tạo verified identity; unverified audit context không thành authority. |
| Workflow authorization | Current exact operation grant/membership/binding dưới concurrency boundary | Ordinary role/scope/token hoặc historical receipt không đủ; test denied no instance/history/data write, READ/HISTORY vs revoke. |
| ACL-admin authorization | Dedicated tenant/resource/operation-set/service authority; same current authority boundary trước mutation/replay disclosure | Ordinary READ/TRANSITION credential không cấp GRANT/REVOKE. Test valid service thiếu admin, revoked service scope và wrong status principal. |

**R27A dependency:** exact service authentication/delegation contract và authority policy cần approval trước transport adapter activation; không truyền user token/header như delegated trust bằng giả định. Mandatory tests X-08/X-09/X-13/X-18/X-19, real ingress security tests; mocked principal tests không chứng minh JWT verification.

## 5. P0-03 — Atomic Assignment

**Sources:** S2 §§7–8; S3 readiness §§3–4 và command §§1/6; S4 Assign/Reassign; S5–S8. **Owner/reviewer:** Yến policy; Bảo atomicity/invalidation; Ánh intent/fence issuance/CAS.

**APPROVED — CONTRACT DIRECTION ONLY:** OD-06 Option A qua S5: revoke-old + grant-new cùng Core commit; old grant có thể còn effective tới replacement commit; Helpdesk pending/gating và local finalize tách biệt. Không approved exact DDL/API.

**D-01 Option A baseline được giữ nguyên:** mandatory expectedPolicyGeneration cộng monotonic incoming resource fence, cho đến approved amendment. D-01 A (generation precondition) khác OD-06 A (observable lag). Không bỏ G hoặc đổi G trong payload cùng key khi retry.

**Proposed single Core transaction:** tenant guard → current dedicated authority/exact facts → scoped key/replay resolution → fresh G/fence checks → replace approved assignment-owned slice → accepted fence + generation + audit + complete authoritative receipt → commit → ACK. Known pre-commit error rollback tất cả; không chờ Helpdesk/network trong DB transaction. Same-key historical replay không chạy lại fresh stale-G/fence check hoặc apply lại grant.

Logical envelope kế thừa S2/S3, chưa wire schema: tenantId/exact resource, authenticated service context, affectedActors, grantOperations/revokeOperations hoặc approved replacement representation, opaque Helpdesk version token, incoming fencingSequence, expectedPolicyGeneration, idempotencyKey/correlationId; fingerprint do Core tính. Resource type/namespace/incarnation shape, optional verified initiator và protocol version, numeric limits, empty/duplicate/contradictory-set rules đều cần freeze; không phát minh JSON field mới.

**BLOCKED Q01:** managed assignment grant slice so với independent admin grants/deny; resource incarnation/issuer/fence reset; admin invalidate/cancel pending intent và clear authority. Baseline schedule G10/fence5 → admin revoke commit G11/fence5 → queued command G10/fence6 phải reject, zero policy delta. Refresh G/key mới không tự authorize regrant; managed slice riêng không đủ emergency-deny proof. Higher fence có thể tới trước lower fence; không tự yêu cầu contiguous sequence hoặc expected-accepted-fence CAS.

**R27A dependency:** freeze identity/slice/invalidation, no-op/batch G increment, stale-G/fence error precedence và exact receipt trước ACL adapter implementation. X-03/X-04/X-10/X-14/X-15/X-23/X-25 phải match lựa chọn đã duyệt; không chọn option theo kết quả test.

## 6. P0-04 — Idempotency & Recovery

**Sources:** S2 §9; S3 command §§2–5.1; S4 Recovery and concurrency; S6–S8. **Owner/reviewer:** Bảo producer/ledger; Ánh consumer/recovery; Yến contract/security. **Status:** PROPOSED; Q02..Q06 PENDING, Q06 BLOCKED BY DECISION.

| Area | Candidate contract | Missing freeze dependency |
| --- | --- | --- |
| Scoped identity | (tenantId, authenticatedServicePrincipal, operationType, idempotencyKey); resource và semantic payload bind fingerprint | Non-null exact identity/issuer migration/incarnation, key encoding/length/transport. R29 256 là candidate internal limit. |
| Canonical fingerprint | Server-derived, versioned strict semantic representation; correlation/trace excluded; client digest không trusted | Presence/null/default/unknown/duplicate-key/set/Unicode/integer rules, algorithm/encoding và golden V-01..V-09 chưa chọn. |
| Duplicate/conflict | Same scope/key + same semantics → immutable historical outcome, no second mutation; khác semantics → conflict, không overwrite receipt | Current lookup auth trước disclosure; exact conflict/error/response headers chưa frozen. |
| Terminal rejection | Ưu tiên committed no-op cho authorized deterministic domain rejection | Q02 chưa chọn errors bind key/rejection audit. Infrastructure/crash/full SQL rollback/malformed/invalid-auth không fabricated terminal receipt; no ACL/G/fence/success-audit mutation cho no-op rejection. |
| Receipt completeness | Early reservation + mutation + complete terminal receipt cùng transaction; deferred validator là candidate | Q03 exact schema/validator/writer coverage/grants; application assert không database enforcement. Final-only cần prove key serialization trước mọi mutation. X-25. |
| Retention/restore | Full receipt qua approved window, sau đó retained identity/tombstone hoặc authenticated admission floor | Q05 duration/expiry response/cleanup order/restore principal/resource/fence/admission mapping; TTL-only reuse không an toàn. X-23 dispatch lại Create và Assign. |
| Status | Authenticated authoritative lookup theo original scope; reauthorize current visibility; historical outcome khác current ACL/local finalize | Method/path/body, absent vs expired/in-flight, recovery delegation còn OPEN. No committed row ≠ never executing; không mặc định persistent IN_PROGRESS/OUTCOME_UNKNOWN. |

**Protocol S — RECOMMENDED, NOT APPROVED:** persist exact intent/key/payload/G/fence/version trước send; lost ACK → lookup trước; terminal outcome → match exact intent rồi local CAS; nếu chưa terminal, chỉ resend same scope/key/exact persisted semantics khi approved admission/replay window cho phép. Original đang mở transaction, resend và delayed original đều qua cùng guard/unique-key path; một winner, các arrival còn lại replay hoặc execution sau rollback/current checks. Không đổi G/fence/key để giải uncertainty. Unavailable/ambiguous/expired status giữ reconciling + escalation.

**Contract conflict:** S4 hiện chỉ cho resend khi có authoritative non-commit evidence. Q06 chỉ freeze sau Ánh/Bảo thống nhất, Yến review và R29 sửa/review đúng owner process tại new exact SHA. Nếu giữ Protocol N, cần closure/admission proof bảo đảm delayed original không thể commit sau non-commit response; SELECT rỗng hoặc lock rồi release không đủ. Không sửa S4/ADR trong gói này.

**R27A dependency:** exact status/retry/retention/rejection contract và consumer amendment trước reconciliation worker/transport behavior chính thức. X-12/X-13/X-23/X-24, Q03 X-25; không tuyên bố exactly-once từ typed key hay unit tests.

## 7. P0-05 — PostgreSQL Ownership & Isolation

**Sources:** S1 D1–D8/lock order/Flyway; S2 §§5–6/10/16; S3 PostgreSQL §§1–3; S8. **Owner/reviewer:** Bảo DB/security; Yến architecture/privilege approval; Ánh Helpdesk cutover. **Status:** proposed ownership/lock target; Q07/Q09 BLOCKED, không deployed-catalog proof.

| Target owner | Relations/capabilities trong logical model | Isolation requirement |
| --- | --- | --- |
| Core | Workflow definitions/states/transitions/instances/history; effective tenant memberships, registry/ACL/guard/binding/policy audit; future ledger/accepted fence | Core-only migration owner/runtime roles/history/location; definition business content do Helpdesk author, controlled registration/provisioning authority vẫn OPEN. Không Core query Helpdesk. |
| Helpdesk | helpdesk_actors/helpdesk_requests/business membership, assignee/resolution/assignmentVersion; future intents/outbox/reservations/CAS | Own DB/schema/roles/history; không Core table/function grants/JDBC/JOIN/FK/trigger. Opaque remote IDs + authenticated API/reconciliation. |

Không đồng nhất Helpdesk business membership với Core effective membership authority. Physical schemas/DDL/receipt/fence storage chưa được chọn; bảng trên không tạo table mới. Internal Core binding→definition FK có thể giữ nếu cùng owner; không xóa toàn bộ FK để đạt split.

**Candidate lock order:** READ COMMITTED; tenant guard trước current facts → key/fence/policy rows theo deterministic identity → instance lock nếu cần → history/audit/receipt → commit. READ/HISTORY và Workflow-only lấy shared guard; policy writer lấy exclusive ngay đầu, không SHARE→UPDATE upgrade. Workflow writes còn instance UPDATE + expected runtime version; Workflow-only không tự bump policy G. READ/HISTORY materialize protected data trước release guard; multi-statement/pagination/streaming consistency chưa được chứng minh. Admin/membership/binding/registry/service-authority/maintenance/cleanup writer phải tuân thủ cùng protocol.

**Least privilege:** request reader và Workflow writer không có direct guard-generation/ACL UPDATE; ACL-admin executor và migration owner tách credentials/pools/role inheritance. Không cấp UPDATE(acl_revision) để reader chạy FOR SHARE. PostgreSQL [SELECT privilege](https://www.postgresql.org/docs/17/sql-select.html) yêu cầu UPDATE trên ít nhất một column cho row-lock: vấn đề này cần mechanism thật, không đổi tên role.

**Q07 candidate:** narrow lock-only SECURITY DEFINER, NOLOGIN/non-superuser owner, fixed typed signature/mode, qualified fixed SQL, trusted search_path với pg_temp cuối; no dynamic relation/SQL. CREATE + REVOKE PUBLIC EXECUTE + exact GRANT trong một DB transaction theo [PostgreSQL safe definer guidance](https://www.postgresql.org/docs/17/sql-createfunction.html#SQL-CREATEFUNCTION-SECURITY). Advisory transaction shared/exclusive locks là alternative chưa chọn, cần namespace/mapping/all-writer proof; không session-lock pool leak. T1 trusted Core không trở thành T2 chống compromised Core bằng helper.

### Legacy coupling inventory — source evidence, not exhaustive live inventory

Tất cả source links sau tại S2 full SHA 5618091dc205b196b551465d2c52def9313ed1fb:

| Observed path | Coupling/writer cần loại khỏi target Helpdesk | Closure evidence cần có |
| --- | --- | --- |
| [HelpdeskService.java](https://github.com/tricore-opentrix/opentrix/blob/5618091dc205b196b551465d2c52def9313ed1fb/backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskService.java) | Direct PostgresWorkflowPersistence; create registry/ACL/instance, assignment revoke/grant, tenant locks và cross-domain reads | Replace qua approved API + local intents/CAS; source/package inventory tất cả callers/admin/jobs, không copy nguyên monolithic transaction. |
| [schema.sql](https://github.com/tricore-opentrix/opentrix/blob/5618091dc205b196b551465d2c52def9313ed1fb/backend/src/main/resources/db/helpdesk/schema.sql) | helpdesk actor/requester/assignee FK→tenant_memberships, instance_id FK→workflow_instances; helpdesk_policy_lock và actor/membership/ACL/registry/binding triggers→tenant_guards | Catalog dependency traversal + function bodies; target H local mutation không chờ Core guard. |
| [runtime-grants.sql](https://github.com/tricore-opentrix/opentrix/blob/5618091dc205b196b551465d2c52def9313ed1fb/backend/src/main/resources/db/helpdesk/runtime-grants.sql) | H legacy SELECT/INSERT/UPDATE Core facts, UPDATE(acl_revision), resource_acl grant writes và Workflow DML | Actual target grants/defaults/memberships/helper signatures chứng minh H không Core access. |
| [policy-schema.sql](https://github.com/tricore-opentrix/opentrix/blob/5618091dc205b196b551465d2c52def9313ed1fb/backend/src/main/resources/db/helpdesk/policy-schema.sql) | Core authority model, immutability/audit triggers/functions và internal FKs | Assign Core owner, inspect implicit locks/dependencies/maintenance; immutability trigger không thay mutation authorization. |

**Removal plan, not migration:** inventory actual catalogs/source writers → approve ownership/identity mappings/Flyway locations → design separate cutover/reconciliation/rollback assets → disposable X-17/T07/T08/least-privilege proof → independent cutover approval → controlled activation. V1–V4 unchanged; Core/Helpdesk migrations không cùng backend classpath:db/migration/history. Không áp dụng grants/DDL hoặc gỡ legacy edges trong task này.

## 8. P0-06 — Reconciliation & Operations

**Sources:** S2 §8/INV-10; S3 readiness §4.1/command §5/PostgreSQL X-16/X-26; S4 Resolve/Confirm; S5–S8. **Owner/reviewer:** Ánh recovery/business protocol; Yến operations/cancellation/emergency authority; Bảo Core feasibility/security.

**Confirmed direction:** Core commit/history/receipt tồn tại độc lập với Helpdesk finalize; old receipt không overwrite new business intent. OD-06 A cho phép old-grant authorization lag; timeout không revoke và không biến unknown thành failure. Current Core ACL luôn quyết định access.

| Existing candidate Helpdesk state | Meaning / disposition | OPEN point |
| --- | --- | --- |
| PENDING_SYNCHRONIZATION | Durable current intent chờ exact Core outcome; pending observable; synchronized-only actions blocked | Wire/UI/error mapping và dispatch/backoff chưa freeze. |
| SYNCHRONIZED | Matching committed receipt + successful Helpdesk current-intent CAS | Không bằng current perpetual access; future action reauthorize tại Core. |
| RECONCILIATION_REQUIRED | Lost ACK/uncertainty, unavailable status hoặc Core commit + local finalize failure | Same-current intent: retry local finalize sau authoritative match. Superseded: old CAS=0, preserve Core commit và durable recovery disposition, không reverse/regrant tùy tiện. |
| SYNCHRONIZATION_FAILED | Definitive rejection durably recorded cho exact current attempt | Unknown không được timeout-convert thành terminal; nếu ghi local failure chưa thành công vẫn reconciling. |

**Q08 proposal:** durable Helpdesk prerequisite reservation bind exact resource/intent/business-assignment versions trước Resolve/Confirm dispatch, short local transaction, không DB lock qua network. Competing reassignment không silent supersede; lost ACK/restart/timeout không tự release reservation. Confirm cần matching finalized resolution, synchronized prerequisites và authoritative current Core RESOLVED/version cùng authorization; historical receipt một mình không đủ.

**BLOCKED:** authority/cancellation/release rules, superseded Resolve convergence và forward recovery; alternative explicit supersede/reconciliation chưa được chọn. X-16/X-26 phải có durable terminal/conflict disposition, không chỉ CAS=0. Retry/backoff/alert thresholds/on-call/manual recovery/restore và emergency revoke authority chưa approved; không tự đặt SLA/timeout. Emergency revoke phải Core-enforced invalidation/deny chống pending assignment regrant, chỉ authority được duyệt mới clear; không suy từ Helpdesk pause hoặc OD-06 A.

**R27A dependency:** Q06 + Q08 shared recovery contract trước worker/finalization semantics; Q09 operational/cutover controls trước activation. C-27/C-28 và X-15/X-16/X-26 vẫn BLOCKED theo decision prerequisites.

## 9. R27A Implementation Permission Matrix

Đây là phân loại hợp đồng, không thay quyết định người có thẩm quyền. READY chỉ dùng khi explicit owner approval đủ scope/SHA và applicable gates đã clear; hiện **không có row nào READY FOR IMPLEMENTATION**.

| Area | Permission classification | R27A được dựa vào / dependency trước implementation |
| --- | --- | --- |
| Six P0 contract package và interface/test planning | CANDIDATE ONLY | Dùng làm review/design inputs, lập dependency/test fixtures trên giấy; không coi là chuẩn chính thức hay quyền viết runtime. |
| OD-06 Option A direction | CANDIDATE ONLY | Preserve confirmed lag/pending/gating direction S5; complete wire/DB/operations vẫn thiếu approval. |
| Core HTTP client/controllers, activation/version behavior | BLOCKED | P0-01 exact schema/A1/security/errors + applicable approvals; route registration giữ OFF. |
| Service credential/delegation/ACL-admin policy | BLOCKED | P0-02 exact scheme/current authority/visibility approval và ingress negatives. |
| Atomic ACL persistence/generation/fence/ledger | BLOCKED | P0-03/04 + Q01..Q07, approved schema/privilege/transaction design và G0 prior gates. |
| Protocol S dispatcher/reconciliation/reservation | BLOCKED | Q06 owner agreement + R29 amendment/review; Q08 recovery/cancellation closure. |
| Migration/grants/coupling removal/cutover | BLOCKED | ADR-010 architecture decision, Q07/Q09, reviewed migration/Flyway/identity/rollback plan và disposable runtime proof trước activation. |
| Core Gradle extraction/build-only scaffolding | OUT OF P0 SCOPE | S1 có conditional plan review, không approval từ gói này. R27A owner phải dùng authorization riêng đúng plan/SHA; không bị diễn giải là mọi R27A work bị cấm. |
| Full File/Identity REST, IAM provisioning, resource-lock optimization, release/source-rights clearance | OUT OF P0 SCOPE | Chỉ service auth/identity boundary cần cho P0; không thêm endpoint/feature, không clear rights/gates/release. |

## 10. R27A Handoff Checklist

- [ ] Yến review exact package commit/diff và xác nhận scope; owner/reviewers ghi closure evidence từng Q, không approve bằng account/name của người khác.
- [ ] Dùng ngay cho planning: S1 candidate endpoint inventory, version/ownership separation, S5 confirmed OD-06 direction, explicit blocked dependencies và verification oracles; không dùng làm approved production schema.
- [ ] Trước runtime implementation: approved exact P0-01/02 OpenAPI/security, A1 choice; Q01..Q07 schema/transaction/privileges/canonicalization/retention; G0-CONTRACT/G0-ARCH/G0-DESIGN theo S2 §16, không suy từ merge tài liệu.
- [ ] Trước recovery handlers: Q06 chọn S/N và review R29 new SHA; Q08 reserve/release/cancel/convergence authority, statuses và current-intent CAS criteria; six-use-case producer/consumer contract tests.
- [ ] Trước migration execution: ownership/Flyway/role/credential manifests, complete source/catalog writer-edge inventory, ID/incarnation/fence/receipt/admission reconciliation, approved migration/restore/rollback sequence; separate authorization cho disposable verification và cutover.
- [ ] Trước activation/cutover: T07/T08, C-20..C-23/C-25/C-26 và mandatory X evidence; Q09 timeout/escalation/emergency-revoke authority; source rights/release gates vẫn riêng. Không claim immediate revoke hoặc distributed ACID.
- [ ] Trước quay lại R27 Step 03 acceptance: record tested source+spec+schema SHAs, independent approvals, current remaining blockers và gate decisions đúng owner; không sửa lịch sử matrix/ADR để giả PASS.
- [ ] Khi source HEAD đổi: record old/new full SHA + changed paths, rerun affected contract/doc verification và request lại owner review đúng scope. Không auto-transfer R29 scoped APPROVE sang R28 runtime.

**Next owner action:** ưu tiên Q06, Q01, Q03/Q07 và Q08; close exact API/security alongside schema/ops decisions. Gói tài liệu hoàn thành để review không đồng nghĩa dependency đã approved cho R27A.
