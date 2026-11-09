<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R28 — Core ACL-admin command và idempotency design

**Status:** PROPOSED DESIGN — PENDING OWNER/CORE REVIEW.
**Scope:** D-02 command boundary và D-03 ledger/reconciliation; logical contract, không API schema/migration.
**Source SHA:** ADR-015/#163 `35ab10a7fff600b1b2e48afd776d15c6834bdedd`; documentation base `5618091dc205b196b551465d2c52def9313ed1fb`; R29 #145 `b3d80254459269deb5071e52e59e1bda6954b5c7`.
**Owner/reviewer:** Bảo Core design, Yến security/owner decisions, Ánh Helpdesk compatibility; chưa có approval tài liệu này.
**Decisions confirmed:** OD-06 atomic replacement với observable lag; identity/version separation và authoritative Core boundary theo [source register](r28-g0-design-readiness-review.md#1-nguồn-và-git-safety-xác-minh-ngày-2026-11-09).
**Recommendations pending approval:** single transaction + terminal receipts, envelope/canonicalization/status semantics dưới đây.
**Open blockers:** D-01, normalized identity, managed grant slice, canonical version, rejection replay, expiry, auth/wire/status/error mapping.
**Verification status:** C-03/04/07..13/24 và T07/T08 NOT RUN hoặc BLOCKED theo nguồn; không có runtime evidence.
**Next actions:** Bảo/Ánh/Yến freeze open decisions §7 trước implementation.

ADR-015 **PROPOSED**, G0-CONTRACT **BLOCKED**, G0-DESIGN/IMPLEMENT/RUNTIME **NOT ACCEPTED**, R27 STEP 03 **IN PROGRESS**.

## 1. D-02 — command envelope (logical proposal)

[ADR-015 §§7–9](../../08-decisions/ADR-015-core-workflow-acl-v3-g0.md) đã mô tả **candidate** envelope; review #163 xác nhận hướng contract, không phê duyệt exact wire schema. Bảng này là envelope đề xuất, không JSON/OpenAPI production và không định nghĩa endpoint mới.

`Required` nghĩa là yêu cầu trong đề xuất design; chỉ cột provenance cho biết trường đã xuất hiện trong ADR. Không trường nào dưới đây được tự tuyên bố là API approved.

| Thành phần | Required / optional | Provenance | Validation / semantic binding |
| --- | --- | --- | --- |
| Authenticated service principal | Required trusted context, không body field | ADR §7, INV-01 | Core verifier establish canonical principal; credential không tự mang arbitrary ACL-admin authority. |
| `tenantId` | Required | ADR §7 | Must be within current service admin scope, match authoritative resource tenant; body không chọn trusted tenant. |
| Exact resource identity (`resourceId` và type/namespace nếu key yêu cầu) | Required | `resourceId` ADR §7; composite shape R28 proposal/OD-03 | Resolve Core registry; ID uniqueness/incarnation/normalization OPEN; không map alias tùy caller. |
| Command type | Required logical discriminator | operationType trong scope ADR §9; wire field R28 proposal | Server allowlist/class-specific checks; không cho client chọn weaker preconditions bằng flag. |
| Initiating actor identity | Optional audit context; required nếu business delegation policy đòi | ADR §7 phân biệt identities; encoding R28 proposal | Chỉ verified delegation được đánh dấu verified; untrusted supplied value không thay principal. |
| `affectedActors` | Required explicit set cho replacement | ADR §7 | Canonical IDs, eligible Core membership; không lẫn initiator/service principal. |
| `grantOperations`, `revokeOperations` / requested replacement | Required complete intended delta/set theo approved slice | ADR §7; exact replacement representation R28 proposal | Operations allowed cho service/resource; reject contradictory delta trên cùng actor/operation, còn revoke Uold và grant Unew cùng operation là replacement bình thường. Không delete toàn ACL khi chưa chốt managed slice. |
| Helpdesk assignment version / `helpdeskVersionToken` | Required với assignment | ADR §§7–8 | Opaque correlation; Helpdesk CAS authority, không parse business semantics tại Core. |
| Incoming `fencingSequence` | Required với assignment execution mới | ADR §§7–8 | Strictly increasing per exact tenant/resource stream, `incoming > lastAccepted`; atomic check/advance. |
| Expected resource fence (last accepted value) | Optional **proposal**, chưa required trong ADR | R28 only | Nếu chọn exact CAS, phân biệt `expectedAcceptedFence == current` với incoming sequence. CAS reject command cao hơn nếu predecessor khác; không thay luật monotonic ngầm. |
| `expectedPolicyGeneration` | Required theo baseline candidate ADR; conditional chỉ nếu D-01 approved | ADR §7; optionality là D-01 proposal | Không tự bỏ khỏi dispatcher. Có/không và value đều bind fingerprint. Không cập nhật G trong cùng key khi retry. |
| `idempotencyKey` | Required | ADR §§7–9 | Scope tenant + verified service principal + operation type + key; length/format/transport OPEN (256 của R29 chỉ candidate). |
| Canonical payload fingerprint | Required **server-derived** | ADR §9; representation R28 proposal | Client digest nếu có chỉ diagnostic; Core tính lại, không tin hash do caller gửi. |
| `correlationId` / trace context | Correlation required theo đề xuất; trace optional | `correlationId` ADR §7; trace shape R28 proposal | Validate bounded safe format, excluded from semantic fingerprint/uniqueness; record retries without rewriting original receipt. |
| Protocol/canonicalization version | Required nếu owner chọn versioned wire/canonical rules | R28 proposal | Tránh replay khác nghĩa khi canonicalization đổi; version persisted cùng receipt. |
| Authoritative outcome | Required response/receipt, không request authority | ADR §§7–9 | Exact scope/key, resource, business token, accepted fence, commit generation, semantic result và fingerprint identity; không assertion current permission. |

Expected resource fence chưa được chọn: baseline ADR chỉ require incoming > accepted. Ví dụ accepted=5; command 7 đến trước 6 thì 7 được accept và 6 stale. Nếu thêm expected=6, command 7 phải đợi/reconcile predecessor. Đây là thay đổi throughput/order semantics cần Ánh/Bảo quyết định, không đồng nhất assignmentVersion với expected fence.

### 1.1 Authentication/authorization sequence

1. Core ingress xác minh credential bằng approved issuer/audience/signature/expiry và service identity mapping; mechanism (service JWT/mTLS hoặc lựa chọn khác) còn OPEN. Không tin actor/tenant headers hoặc tự tạo principal từ body.
2. Validate shape/size, canonical identity và command class. Resource thuộc tenant khác được xử lý theo non-disclosure contract, không “sửa tenant” rồi chạy tiếp. Helpdesk eligibility check không thay Core authorization.
3. Trong Core transaction, acquire tenant guard rồi đọc current service-admin authority và exact registry/lifecycle, applicable membership/operations/binding. Missing guard/facts → fail closed. Dedicated service policy quyết định tenant, resource namespace/slice và operation set được quản lý. Ordinary READ/TRANSITION/JWT role không cho GRANT/REVOKE.
4. Chỉ sau current replay/status authorization mới expose ledger. Same-key replay không bypass authorization; credential đã mất tenant scope không được đọc receipt cũ. Quyền lookup có thể hẹp hơn quyền mutation nhưng phải explicit, same original scope; không arbitrary principal override trong request.
5. Resolve key/fingerprint. Với receipt cùng payload, trả historical outcome; không re-run execution precondition vốn đã stale do chính command cũ advance G/fence. Với execution mới, check all current execution authority và G/fence theo class. Không cho service tự sửa owner, membership hoặc binding ngoài allowlist.
6. Replace approved managed grant slice, update fence/generation/audit/outcome trong một Core transaction. Current independent admin grants/deny phải được preserve/enforce; scope slice/invalidation là D-01 blocker, không có implementation assumption.

### 1.2 Authoritative outcome đủ cho CAS đến mức nào?

Receipt đề xuất bind immutable scope/key + fingerprint/canonical version + exact resource + operation + Helpdesk token + accepted fence + resulting policy generation + outcome kind + audit/receipt reference. Response chỉ sau commit; trace/commit timestamp nếu có là diagnostic, không chứng minh currentness.

Helpdesk đối chiếu receipt với durable intent/outbox, rồi CAS `(current assignmentVersion, command identity, incoming fence, expected pending state)` trong transaction của mình. CAS fail do superseded intent: không finalize current, không tự rollback Core/regrant old actor; reconcile attempt cũ và latest desired intent riêng. CAS fail tạm thời trên same current intent: retry local finalize sau đối soát. Status `COMMITTED` một mình, không matching identifiers, là thiếu evidence.

**Ba facts độc lập:** (1) receipt chứng minh command từng commit; (2) current effective ACL có thể đã đổi sau đó; (3) Helpdesk CAS có thể chưa/không bao giờ finalize version ấy. `SYNCHRONIZED` mô tả finalized assignment attempt, không credential cấp quyền vĩnh viễn. Các action sau đó vẫn cần current Core ACL; Resolve/Confirm còn có prerequisites của R29.

### 1.3 Error taxonomy đề xuất

| Condition | Semantic outcome | Mutation/retry behavior | Transport status |
| --- | --- | --- | --- |
| Invalid/missing verified credentials | `AUTHENTICATION_REQUIRED` | No mutation/receipt disclosure | 401 candidate ADR §§7/11 |
| Hidden/missing/wrong-tenant resource | `RESOURCE_NOT_FOUND` / external `NOT_FOUND` | No mutation; avoid existence oracle | 404 candidate; exact mapping OPEN |
| Visible resource, no dedicated admin authority | `ACL_ADMIN_FORBIDDEN` | No mutation, unchanged request không retry | 403 candidate |
| Invalid command/identity/set/version shape | Validation outcome (name TBD) | Reject before writes | R28 OPEN; không tự đặt production code |
| Stale required generation | `STALE_POLICY_GENERATION` | No ACL change, reconcile then authorized new intent nếu cần | 409 candidate |
| Incoming fence ≤ accepted | `STALE_ASSIGNMENT_COMMAND` | New execution denied; replay match vẫn historical receipt | 409 candidate |
| Exact expected resource fence mismatch nếu field được chọn | Resource fence conflict (name TBD) | No mutation; không hạ incoming fence | R28 OPEN |
| Same scope/key, different fingerprint | `IDEMPOTENCY_PAYLOAD_CONFLICT` | Không trả nhầm prior result hoặc sửa receipt | 409 candidate |
| Expired/tombstoned identity | Expired replay rejection (name TBD) | Không coi key là fresh | R28 OPEN; C-24 BLOCKED |
| Lock/statement timeout, deadlock, unavailable facts | `ACL_UNAVAILABLE` / `AUTHORIZATION_UNAVAILABLE` | Fail closed/full rollback nếu known; status nếu outcome uncertain | 503 candidate |
| Commit ACK lost | Client `OUTCOME_UNKNOWN` / `COMMIT_OUTCOME_UNKNOWN` | Reconcile same key, không suy rollback | 503 candidate khi có thể response; không persistent state |
| Definite semantic rejection | Stable specific rejection; optional committed no-op receipt | Không mutation; durable rejection semantics §3.3 chưa approved | R28 OPEN |

HTTP/auth error visibility precedence cần freeze; không trả fingerprint/fence/G cho caller không có quyền xem scope. Candidate names bám ADR, tên TBD không phải code mới đã approved.

## 2. D-03 — canonical identity và fingerprint

Recommendation pending approval: tenant/principal/operation/key scope giống ADR §9; resource và mọi semantic field nằm trong fingerprint để cùng key không đổi resource. Database unique identity phải non-null; opaque key không trim/case-fold tùy ý. Credential rotation giữ canonical service principal ổn định; đổi principal/issuer mapping không được dùng để lách dedup mà không có approved identity migration.

Canonicalization proposal cần freeze và có golden vectors trước implementation:

- Versioned semantic object, strict UTF-8; reject duplicate JSON keys, unknown semantic fields và ambiguous numeric forms theo approved wire schema. Không dùng hash raw JSON vì whitespace/ordering khác nhau.
- Include tenant, canonical service scope, resource/type/incarnation nếu được chọn, command class, verified initiating actor nếu có ảnh hưởng semantics, affected actors/operation sets, business token, incoming/expected fence, expected G và explicit presence rules. Delegation credentials/token bytes không vào fingerprint; trusted actor identity có thể vào. Correlation/trace excluded.
- Sets có deterministic order và reject duplicates theo rule frozen; array có thứ tự semantic thì giữ thứ tự. Identity không tự Unicode-normalize/case-fold/trim nếu canonical identity authority chưa quy định. Phân biệt omitted/null/default bằng một rule duy nhất, không tùy client.
- Integer fences/G dùng exact range/representation, không qua floating-point làm mất precision; overflow fail closed. Hash algorithm (đề xuất SHA-256), canonical version, hash encoding và storage constraint đều **PENDING REVIEW**. Fingerprint chứng minh equality, không authentication.
- Bind versioned canonical bytes/digest với receipt; test alternate field/set ordering, unicode, omitted/null, large integers, changed actor/resource/operation/version/fence/G, changed correlation-only và malicious supplied digest. Không thay canonical rules của old keys khi nâng version.

### 2.1 P1-02 — candidate canonical test vectors

Đây là **semantic vectors để owner chọn profile**, không approved wire JSON/canonical bytes. Fixture P: tenant T1, verified principal S1, operation ASSIGN, key K6, resource `(type=ticket,id=R1,incarnation=I1 nếu selected)`, affected set `{Uold,Unew}`, revoke `{Uold:READ}`, grant `{Unew:READ}`, token V6, incoming fence6, expected G10, correlation C1. Key là lookup identity; server-derived fingerprint bind semantic scope/payload, không dùng caller digest. Profile/version, identity types, ordered serialization và hash encoding chưa freeze nên chưa công bố fabricated golden digests.

| Vector so với P | Candidate expected result / oracle | Decision dependency |
| --- | --- | --- |
| V-01: đổi JSON property order/whitespace, đảo order affected set | Same canonical bytes/digest và historical replay, zero new mutation | Profile định nghĩa đây là set, không array có ordered semantics. |
| V-02: chỉ correlation C1→C2 hoặc rotate credential vẫn canonical S1 | Same semantic fingerprint; original receipt immutable, retry trace riêng | Principal mapping và trace exclusion đã đề xuất; issuer migration không tự alias principal. |
| V-03: lần lượt đổi tenant/principal/type/resource/actor/grant/revoke/token/fence/G | Different semantic identity; same scoped key/different fingerprint conflict nếu scope không đổi. Đổi tenant/principal/operation tạo khác lookup scope, vẫn current authorization | Không assert conflict giữa hai scopes khác nhau; không cho scope mới lách service/issuer admission policy. |
| V-04: duplicate JSON key, unknown semantic field, duplicate set item | Reject trước mutation theo candidate strict profile; không silently pick last value/dedup | Owner chốt rejection/key-binding boundary; malformed input không reserve key mặc định. |
| V-05: omitted G vs null vs G10; omitted actor vs supplied verified actor | G10 khác absence; null invalid cho required G baseline A. Omitted/null/default không tự coi equivalent; verified actor khác nếu ảnh hưởng semantics | Freeze field presence/default/delegation rule; C optional G cần version/class-specific vectors. |
| V-06: fence `9007199254740993` vs `9007199254740992`; fractional/exponent/overflow variants | Exact distinct integers nếu range cho phép; otherwise explicit range rejection. Không round qua binary floating point; fractional/ambiguous form reject theo schema | Wire numeric/string shape, range và canonical integer encoding OPEN. |
| V-07: resource/actor Unicode composed vs decomposed, case/leading space | Candidate exact identity: khác hoặc invalid theo identity authority, không tự normalize thành same key | Chốt normalized canonical IDs trước expected bytes; không dùng fixture để chọn identity authority. |
| V-08: cùng fake client digest nhưng đổi Unew hoặc resource | Server recompute; conflict/denial đúng scope, không prior result substitution | Current visibility authorization precedes fingerprint disclosure. |
| V-09: canonical version mới với old key | Dùng persisted old version để compare/replay hoặc reject unsupported version theo approved policy; không reinterpret old payload | Version compatibility và upgrade admission cần owner chọn. |

Trước implementation acceptance, Bảo/Ánh phải thay các conditional rows bằng exact input bytes, canonical bytes, digest và expected outcome cho từng selected profile; assert cả malformed/unauthorized no-write. X-11 dùng V-01..09, trạng thái golden execution NOT RUN/BLOCKED đến khi profile freeze.

## 3. Ledger recommendation và lifecycle

### 3.1 Một Core transaction, không persistent progress rows mặc định

Recommendation: reservation unique key + execution + durable **COMMITTED** receipt cùng transaction. Trong transaction có thể có reservation chưa commit; đó là uncommitted data, không durable `IN_PROGRESS`/`OUTCOME_UNKNOWN`. Sau rollback không có reservation tồn tại để recovery worker “dọn”. Không cần lease/sweeper cho crash trước commit trong model này.

Lifecycle: verify → guard/current authority → canonical scope + key reservation → duplicate check hoặc current execution preconditions → atomic replacement/fence/G/audit/receipt → commit → response. Mọi failure trước commit rollback toàn bộ. Process chết giữa transaction: PostgreSQL rollback khi connection được đóng/phát hiện; có thể còn lock cho đến lúc phát hiện, vì vậy connection/transaction deadlines cần vận hành. Process chết sau commit: ledger giữ receipt, client status lookup phục hồi. Commit connection bị đứt: client uncertainty, không tự đoán rollback.

Under READ COMMITTED, unique insert có thể block trên competing uncommitted key; `ON CONFLICT DO NOTHING` có thể không insert dù conflicting row chưa visible trong statement snapshot. Vì vậy cần **statement SELECT mới** sau conflict để lấy committed receipt, không suy “không RETURNING = NOT_FOUND = chạy lần nữa” trong cùng CTE. Các quy tắc này dựa trên [PostgreSQL INSERT](https://www.postgresql.org/docs/17/sql-insert.html) và [READ COMMITTED](https://www.postgresql.org/docs/17/transaction-iso.html); protocol cụ thể là inference thiết kế chưa test.

Vì ACL writer lấy exclusive tenant guard trước reservation, same-tenant duplicates thông thường chờ guard trước khi chạm unique index. Unique constraint vẫn cần cho mọi entrypoint/correctness; không lấy ledger lock trước guard ở retry/cleanup path. Không giữ Core transaction trong khi gọi Helpdesk hoặc chờ network ACK.

### 3.2 Duplicate/replay decision table

| Situation | Durable Core evidence | Decision đề xuất | Helpdesk action |
| --- | --- | --- | --- |
| First eligible command | No prior receipt, admissible identity | Reserve + execute atomically once | Pending đến ACK/status + matching CAS. |
| Concurrent same scope/key/payload | First tx uncommitted | Wait guard/key bounded; after commit read receipt, after rollback recheck execution preconditions | Timeout stays reconciliation; không key mới. |
| Same key/same payload after commit | COMMITTED receipt | Current lookup auth, replay historical result, no new audit/G/fence/ACL mutation | Match exact intent then CAS; current ACL separately. |
| Same key/different payload after/concurrent commit | Existing fingerprint differs | Conflict, no mutation; không overwrite ledger | Fix client; payload correction là new authorized intent, không retry cũ. |
| First tx abort/crash before commit | No committed receipt | Reservation gone; same-key retry serialize and reauthorize | Absence không chứng minh never-in-flight; follow status rules §5. |
| Mutation failure after reservation | All tx writes roll back | No committed success receipt/audit | Reconcile if commit outcome not known. |
| ACK lost after commit | COMMITTED receipt survives | Return original outcome from authorized status/replay | No second replacement; local CAS once. |
| Old receipt, later assignment/admin revoke | Historical COMMITTED only | Replay original receipt; do not regrant | Do not infer current ACL or synchronize superseded version. |
| Deleted/expired receipt | Missing full outcome, tombstone/admission rule may remain | Reject replay unless proven admissible under approved retention | Never treat absence/expiry as fresh command. |
| Unauthenticated/cross-tenant status/replay | Caller lacks scope | Deny without receipt disclosure or execution | No cross-tenant reconciliation. |
| Stable semantic rejection | Depends on §3.3 owner choice | Repeat stable result if durable receipt; no implied persistence if rollback | Record definitive failure only from authoritative rejection. |

### 3.3 Rejections: simplification có giới hạn cần owner quyết định

Chỉ lưu successful COMMITTED outcomes là ít state nhất nhưng **không** bind key đã bị rollback/reject. Sau auth/policy thay đổi, cùng key có thể trở nên executable; cùng key/different payload sau rollback cũng không thể bị database phát hiện nếu fingerprint không còn. Vì vậy không hứa durable rejection replay/identity reservation across rollback từ model này.

Đề xuất để review: với command đã authenticate/authorize scope và canonicalize hợp lệ, lưu terminal receipt có transaction status **COMMITTED**, result kind `REJECTED` cho deterministic domain rejection, như committed no-op decision; không bump generation/fence và không success ACL audit. Đây là outcome kind, không state machine recovery mới. Nó cho phép replay rejection ổn định; exact rejection set và audit loại rejection còn OPEN. Unexpected SQL error/deadlock/full rollback không được fabricate committed rejection. Authentication failures/malformed requests không tự reserve key hoặc expose receipt; denial telemetry riêng, không success audit.

Owner có thể chọn success-only ledger với protocol cấm retry terminal failures và chấp nhận giới hạn key binding trên rolled-back attempts. Cần ghi rõ semantics trước acceptance. Không thêm persistent `REJECTED`, `IN_PROGRESS` hoặc `OUTCOME_UNKNOWN` state chỉ vì tên xuất hiện trong ADR candidate response table.

### 3.4 P1-02 — attempt identity và commit completeness

| Prior attempt | Same key/same payload | Same key/different payload | Required evidence |
| --- | --- | --- | --- |
| Committed success | Replay historical outcome sau current lookup auth, không recheck stale execution G/fence | Conflict trong cùng scope | One immutable receipt; no new ACL/G/fence/audit. |
| Committed deterministic no-op rejection, nếu selected | Replay exact rejection dù policy sau đó cho phép mutation | Conflict trong cùng scope | Receipt terminal-complete, outcome kind REJECTED; no success policy delta. |
| Known full rollback/crash trước commit | Retry qua cùng serialization và current authority/preconditions, nếu admissible và không terminal-failure no-resend | Không còn persisted fingerprint để detect conflict; không hứa durable attempt binding | Absence không chứng minh never-in-flight. Success-only lựa chọn phải công khai giới hạn; corrected intent theo business policy, không blind retry. |
| Commit uncertain / connection chết chưa được server phát hiện | Status rồi selected recovery protocol §5.1; có thể chờ guard/deadline | Không thay payload của uncertain intent; key mới không giải quyết uncertainty | Chờ server transaction end hoặc terminal receipt; không fabricate rollback/rejection. |
| Cleanup full outcome, identity tombstone còn | Explicit expired history/rejection theo selected policy; không execute mới | Reject reuse; có thể detect mismatch nếu tombstone giữ fingerprint | Cần giữ scoped identity và admission protection theo §4. |
| Identity đã bị xóa | Chỉ admit nếu approved epoch/floor chứng minh request không thuộc retired identity; không coi absence là fresh | Cùng giới hạn admission, không hứa compare old fingerprint không còn | TTL-only + reuse là unsafe counterexample, kể cả sau restore. |

**Completeness proposal, PENDING OWNER DECISION; không DDL:** nếu giữ early INSERT reservation, review deferred validation tại transaction commit trên mọi inserted/updated ledger identity. Validator phải đọc final row theo immutable key và reject commit khi missing/nonterminal hoặc thiếu scope/fingerprint/canonical version/resource/command/outcome và applicable fence/G/intent references. Runtime không có DELETE, trigger-disable (kể cả SET `session_replication_role`), function-replace hoặc owner/SET ROLE escape; queued validation và rejection không được swallow qua savepoint rồi commit mutation. Một attempted partial commit phải abort ACL/G/fence/audit/ledger cùng transaction. Cơ chế candidate là AFTER ROW constraint trigger DEFERRABLE INITIALLY DEFERRED, theo [PostgreSQL CREATE TRIGGER](https://www.postgresql.org/docs/17/sql-createtrigger.html), với reviewed fixed SQL/least-privilege owner; schema/trigger/function signature và exact required fields chưa chọn. SET CONSTRAINTS IMMEDIATE có thể kiểm sớm, không được bypass final completeness; X-25 kiểm cả timing modes. Đây là inference thiết kế cần test, chỉ enforce completeness trong T1, không chứng minh row nội dung truthful trước compromised trusted writer/T2.

Alternative: chỉ INSERT complete terminal receipt ở cuối, nhưng acquire approved scoped-key transaction serialization **trước mọi execution** và read existing receipt sau lock; tenant UPDATE guard có thể đủ cho assignment, shared Workflow paths cần proof riêng. Không được mutate trước rồi dựa unique violation như external exactly-once guarantee. Recommendation để review là deferred commit validation nếu giữ reservation flow hiện tại; owner có thể chọn final-only sau proof. X-25 phải thử commit incomplete reservation, skip finalization, delete/alter/disable probes và positive complete receipt. Chưa chọn/enforce mechanism thì receipt-completeness acceptance BLOCKED.

## 4. Retention / expired-key alternatives

| Alternative | Replay safety | Cost / limit | Recommendation pending |
| --- | --- | --- | --- |
| Retain full receipt indefinitely | Known key/fingerprint/outcome always available | Storage/privacy/audit growth; backup/restore must preserve identity | Đơn giản cho verification ban đầu, duration không tự chọn. |
| Retain full outcome qua supported reconciliation window, then minimal tombstone | Tombstone bind scope/key/fingerprint và reject reuse; historical payload có thể unavailable | Nếu tombstone bị xóa mà không admission floor, old key trở thành mới | Ưu tiên review cho vận hành; tombstone không là processing state. |
| Versioned issuer epoch/admission floor + bounded receipts | Reject toàn command thuộc retired epoch trước reservation | Cần authenticated epoch ownership/rotation; fence resource không đủ cho commands khác | Chỉ chọn nếu có recovery/retention requirement cụ thể, không thêm field mặc định. |
| TTL delete only / permit key reuse | Không an toàn: old signed request/key có thể execute lại sau delete; assignment fence không cứu Create | Dễ duplicate/regrant, outcome không còn recover | Không khuyến nghị. |

Retention window phải lớn hơn supported offline retry/reconciliation/backup recovery budget theo owner; không tự đặt ngày/SLA. Resource identity/fence tombstone phải sống đủ lâu để ID reuse hoặc reset counter không resurrect command cũ. Cleanup cùng guard/order với execution; không race delete receipt giữa conflict và SELECT. Lookup khi full outcome expired trả explicit expired/unknown-history, không giả `NOT_FOUND` chứng minh chưa commit. Data retention của audit và ledger là hai quyết định riêng; xóa full payload không được xóa dedup identity mà vẫn cho phép replay.

### 4.1 Cleanup/restore oracle chưa chọn policy

Trong supported replay window: same-key replay phải giữ historical outcome và một mutation. Sau window: full retained receipt có thể replay nếu policy cho; tombstoned/retired epoch phải reject execution, có thể không trả full history. Chưa chọn expiry response name/duration. X-23 phải dispatch lại original Create và assignment sau cleanup, không chỉ SELECT status: no second instance/ACL mutation/audit/G/fence advance. Thử khác payload cùng retired identity cũng không admit mới. Nếu thử TTL-only rồi Create execute lần hai thì ghi **FAIL counterexample**, không chọn branch đó làm passing policy.

Cleanup và execution đều guard→key; barrier trước cleanup commit và giữa conflict/new SELECT để chứng minh identity không biến mất. Restore fixture phải capture admission floor/tombstone/principal mapping/resource incarnation/fence cùng supported recovery policy. Nếu restore làm mất dedup identity hoặc reset fence nhưng request cũ vẫn admissible, giữ recovery/admission closed và escalate; không declare replay-safe. Retention/restore policy OPEN, X-23 BLOCKED cho đến selected oracle/fixtures; không tự chọn ngày, schema hay backup atomicity giữa hai dịch vụ.

## 5. Lost-ACK reconciliation và authenticated status

Status request bind verified original service principal (hoặc recovery authority được approve riêng), tenant, operation type, key; resource/fingerprint expectation phải khớp, không tenant header override. Reauthorize current lookup quyền, filter response; status không tự cấp quyền READ/HISTORY.

1. Helpdesk persist intent/version/fence/key/payload trước dispatch. Timeout/disconnect sau send → `RECONCILIATION_REQUIRED`, giữ original payload/key, gate synchronized-only actions.
2. Lookup committed receipt trong authoritative Core store; không đọc replica có lag như bằng chứng absence. `COMMITTED`: verify identity/fingerprint/outcome/fence/G; current intent CAS finalize. Receipt cũ/superseded không hoàn tất intent mới.
3. Definitive durable rejection (nếu được chọn) → failure của exact attempt. Unavailable/ambiguous/expired → remain reconciling + approved escalation; không new-key retry.
4. **No visible receipt ≠ not executing.** Một request còn mở transaction không visible cho lookup. Single-transaction design không hứa status `IN_PROGRESS`. Response có thể là “no committed receipt observed” (wire name OPEN), không tuyên bố never committed. Không cần persistent progress state để biết điều này.
5. Nếu retention/admission bảo đảm key chưa expired và policy cho resend, same-key/same-payload retry đi qua **cùng guard/unique transaction path**, không execute ngoài serialization. Nó sẽ đợi winner và replay hoặc execute sau known rollback với current checks. Lookup absence một mình không đủ authorize blind/new-key retry. Nếu cần definitive “not committed” API, protocol phải serialize với in-flight execution/admission; owner phải define/test, không suy từ SELECT rỗng.
6. Core commit + Helpdesk local CAS failure → giữ commit; nếu same current intent thì retry local finalize, nếu superseded thì reconcile latest desired state với new authorized command khi cần. Không reapply old receipt để “repair” current ACL.

Future E2E phải tách lost ACK trước commit (lookup không false success), sau commit (replay once), transport uncertainty và local finalize failure. Persistent recovery states chỉ xem xét nếu có separately committed reservation/long-running operation được chứng minh cần thiết.

### 5.1 P1-03 — đối chiếu R29 HEAD và thống nhất resend

Rechecked [R29 PR #145 HEAD `5d577dd4a0a8efa830459cf35cb1868e52a9de2f`](https://github.com/tricore-opentrix/opentrix/blob/5d577dd4a0a8efa830459cf35cb1868e52a9de2f/docs/03-applications/helpdesk/r29-use-case-contract.md#L60-L75): shared recovery chỉ cho retry same key/payload với authoritative non-commit evidence. So với `b3d8025…`, HEAD chỉ cập nhật CI evidence, không sửa requirement đó. R28 §5 bước 5 cho phép serialized same-key retry khi identity còn admissible mà không đòi definitive non-commit; đồng thời không cung cấp definitive API mặc định. Đây là **contract discrepancy**, không phải đã tương thích nhờ cùng cấm new-key retry. Request đầu rollback nhưng status chỉ biết absence có thể khiến R29 kẹt reconciling.

| Protocol, PENDING OWNER DECISION | Required mechanism / oracle | Trade-off |
| --- | --- | --- |
| N: definitive non-commit trước resend | Serialize status với in-flight execution **và admission của delayed original**; authoritative closed/cancelled attempt hoặc permit protocol chứng minh original không thể commit sau response. Chỉ SELECT dưới guard rồi release chưa đủ nếu original chưa tới | Giữ R29 hiện tại nhưng cần define permit/reopen/expiry và fencing của transport attempts, liveness/recovery proof; không tự thêm persistent reservation/state ở đây. |
| S: safe same-key resend sau lookup | Authenticated lookup trước resend; khi không có terminal receipt, retry exact persisted payload/scope/key chỉ nếu unexpired/admissible. Cùng guard→unique path waits/replays winner hoặc execute sau rollback/current checks; không cần absence là non-commit proof | Ít protocol hơn, hợp single transaction; cần R29 owner amendment, stable identity/canonicalization/retention, timeout/backoff và terminal-rejection rules. Status unavailable/expired hoặc admission không chứng minh được thì giữ reconciling. |

**Recommendation: S — PENDING OWNER DECISION (Ánh/Bảo, Yến contract).** Quy tắc chung đề xuất: lookup trước; terminal success/rejection xử lý exact intent; otherwise chỉ same-key/same-payload serialized resend nếu Core reachable và approved admission/replay policy cho phép; không mutate G/fence trong original payload và không new-key retry. Lựa chọn S chưa thay R29 source hay ADR-015. Trước owner alignment, integration của discrepant branch vẫn BLOCKED, không suy R29 đã cho phép resend này.

Acceptance oracle X-12/X-13: original đang giữ guard → S resend waits rồi một mutation/receipt sau commit, hoặc execute một lần sau rollback; original đến muộn sau resend cũng replay. N phải có closed/admission evidence, original delayed không thể commit ngoài permit mới; nếu chưa có mechanism thì N branch BLOCKED. Crash/disconnect không tự release local business reservation khi outcome unknown. Prerequisite/convergence của Resolve/Confirm xem [readiness §4.1](r28-g0-design-readiness-review.md#41-p1-06--resolveconfirm-khi-reassignment-cạnh-tranh), X-16/X-26.

## 6. SQL transaction pseudocode

**NON-EXECUTABLE DESIGN PSEUDOCODE.** Angle-bracket operations là logical placeholders; relation/columns/constraints chưa approved. Không copy block này thành migration, function hoặc SQL harness. Tên logical theo ADR §5; không DDL/GRANT.

```text
-- NON-EXECUTABLE DESIGN PSEUDOCODE: ACL replacement + ledger
BEGIN ISOLATION LEVEL READ COMMITTED;
SET LOCAL lock_timeout = <approved transaction lock budget>;
SET LOCAL statement_timeout = <approved statement budget>;
<lock Core tenant_guards[verified tenant] FOR UPDATE, fail if absent>;
<read current service scope and exact resource/lifecycle facts under guard>;
<require current mutation/replay authority before exposing any receipt>;
INSERT INTO <Core command ledger> (<scope>, <key>, <fingerprint>, <private tx reservation>)
  VALUES (<verified tenant/principal/type>, <key>, <server fingerprint>, <not yet durable>)
  ON CONFLICT (<unique scoped key>) DO NOTHING
  RETURNING <reservation identity>;
IF <no inserted row>:
  <in a NEW statement SELECT committed receipt under the same scope>;
  <missing receipt => fail closed/reconcile, never execute as fresh by inference>;
  <different fingerprint => payload conflict, no overwrite>;
  <same fingerprint => return historical receipt after ending transaction; no ACL writes>;
ELSE:
  <check accepted/incoming fence, generation per APPROVED class, current eligibility>;
  <on semantic rejection: rollback OR finalize committed no-op receipt per owner choice>;
  <lock affected facts/ACL rows in deterministic identity order>;
  <replace ONLY approved managed ACL slice, preserve/enforce independent admin policy>;
  <advance accepted fence and increment policy generation per frozen batch/no-op rule>;
  <append policy audit with exact actor/service/source, key, old/new G and fence>;
  <finalize receipt COMMITTED with exact immutable outcome/fingerprint/G/fence>;
  <assert no unfinished reservation can be committed; enforcement mechanism TBD>;
COMMIT;
<only now emit authoritative success response>;
ON <pre-commit exception>: ROLLBACK <all effects including reservation/audit>;
ON <uncertain commit response>: <client reconciliation, no fabricated Core state>;
```

Final receipt completeness phải enforced/tested trước schema acceptance (ví dụ constrained write protocol, không tự chọn nullable schema). Không commit reservation “để poll”; không gọi Helpdesk trong transaction; không use `ON CONFLICT DO UPDATE` để thay fingerprint/outcome cũ.

## 7. Open schema/contract decisions và next actions

| Decision | Cần đóng băng | Owner / dependency |
| --- | --- | --- |
| Resource and command identity | Global/tenant key, type/namespace/incarnation, canonical principal rotation, ID reuse | Bảo + Yến; ADR OD-03 |
| Assignment/class preconditions | D-01 G optionality, incoming vs expected fence, admin invalidation/managed slice | Yến + Bảo + Ánh |
| Canonical payload | Version/encoding/hash, set/null/numeric rules, trusted actor fields, size bounds | Bảo + Ánh; golden vectors NOT RUN |
| Receipt schema/invariant | Unique non-null scope/key, completeness at commit, no partial success audit | Bảo; C-07..12/C-21 NOT RUN |
| Rejected-command semantics | Success-only vs committed no-op rejected decision, which failures bind keys | Bảo + Ánh; không default recovery states |
| Status transport | Visibility/auth scope, absence vs in-flight/expired, service recovery delegation | Yến + Bảo + Ánh |
| Retention | Full receipt window, tombstone/admission floor, restore/cleanup safety | Bảo + Ánh; C-24 BLOCKED |
| R29 finalize/recovery | CAS fields, current-vs-historical checks, Resolve/Confirm prerequisites; resend N vs S (§5.1) | Ánh + Yến; **PENDING R28/R29 PROTOCOL DECISION**; #145 HEAD có scoped review |

Next: review các lựa chọn ở bảng, sửa candidate contract qua owner process sau review; triển khai test từ [T07/T08 plan](r28-postgresql-locking-privilege-t07-t08-plan.md) ở task riêng sau gate. Chưa chạy database, không có API/schema mới được approve.