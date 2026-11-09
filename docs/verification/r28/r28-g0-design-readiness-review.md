<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R28 / G0-DESIGN — Core ACL V3 design-readiness review

**Status:** RECOMMENDED — PENDING OWNER/CORE REVIEW; documentation readiness only.
**Scope:** D-01..D-06, threat review, decision analysis và kế hoạch kiểm chứng; không triển khai runtime/database.
**Source SHA:** ADR-015/#163 `35ab10a7fff600b1b2e48afd776d15c6834bdedd`; base tài liệu `5618091dc205b196b551465d2c52def9313ed1fb`.
**Owner/reviewer:** Bảo chịu trách nhiệm Core/PostgreSQL design; Yến quyết định owner/gate; Ánh review R29. Đây là phân công cần review, không phải chữ ký APPROVE.
**Decisions confirmed:** OD-06 Option A là hướng hợp đồng; xem nguồn dưới đây.
**Recommendations pending approval:** D-01 Option C có điều kiện, envelope/ledger và lock/privilege trong hai tài liệu đi kèm.
**Open blockers:** ADR-010, D-01 invalidation, wire/error/retention, privileges, PR #145 alignment, timeout/emergency procedure.
**Verification status:** T07/T08 và runtime E2E NOT RUN; các quyết định chưa chốt BLOCKED; kiểm tra tài liệu ở §7.
**Next actions:** Yến/Bảo/Ánh review decision register §6 trước khi đóng băng contract hoặc viết implementation.

ADR-015 = **PROPOSED**; G0-CONTRACT = **BLOCKED**; G0-DESIGN = **NOT ACCEPTED**;
G0-IMPLEMENT = **NOT ACCEPTED**; G0-RUNTIME = **NOT ACCEPTED**; R27 STEP 03 = **IN PROGRESS**.

## 1. Nguồn và Git safety (xác minh ngày 2026-11-09)

| Nguồn | SHA / trạng thái quan sát | Ý nghĩa và giới hạn |
| --- | --- | --- |
| [PR #163](https://github.com/tricore-opentrix/opentrix/pull/163) | Reviewed `35ab10a7fff600b1b2e48afd776d15c6834bdedd`; merged bằng squash `5618091dc205b196b551465d2c52def9313ed1fb` vào nhánh #160 | Chưa nằm trên main; diff phần docs giữa reviewed SHA và squash rỗng. |
| [Bảo re-confirm](https://github.com/tricore-opentrix/opentrix/pull/163#issuecomment-6732338208) | Đúng reviewed SHA #163 | Contract direction only; ghi nhận generation false conflict, C-25/C-26 và ledger đơn transaction. |
| [Ánh APPROVE](https://github.com/tricore-opentrix/opentrix/pull/163#pullrequestreview-5821754766) | Đúng reviewed SHA #163 | Chỉ documentation/contract remediation; không chấp thuận G0 hoặc runtime/security. |
| [Yến OD-06](https://github.com/tricore-opentrix/opentrix/pull/163#issuecomment-6731860971) | `af7506d26fbe33f4e634012389bde9c6553c31ab`; được ghi nhận trong reviewed #163 | Atomic replacement, quyền cũ có thể tồn tại đến Core commit, pending/action gating; không hard revocation bound. |
| [ADR-015](../../08-decisions/ADR-015-core-workflow-acl-v3-g0.md) | §§4–10, 13–16 tại reviewed #163; có trên base này | Logical relations/envelope còn là candidate; không phải DDL/API đã duyệt. |
| [Verification matrix](../r27/adr015-g0-contract-verification-matrix.md) | C-01..C-30 tại reviewed #163 | Giữ nguyên nghĩa ID và trạng thái nguồn. |
| [R29 amendment](../../03-applications/helpdesk/r29-pr145-contract-amendment.md) | Tại reviewed #163; mô tả #145 cũ `6e6e91e2e0f1f68f196eeb492dec371c52f402db` | Historical baseline; cập nhật #145 mới ở hàng dưới, không sửa amendment hoặc nhánh của Ánh. |
| [PR #160](https://github.com/tricore-opentrix/opentrix/pull/160) | Open Draft; head `5618091dc205b196b551465d2c52def9313ed1fb`, base main `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e` | Base riêng để review stacked docs; chưa merge main. |
| [PR #159](https://github.com/tricore-opentrix/opentrix/pull/159) / [ADR-010](https://github.com/tricore-opentrix/opentrix/blob/ef4b9484369c94ed7e5674e4b056b0d8f673e1ba/docs/08-decisions/ADR-010-core-helpdesk-service-boundary.md) | Open; head `ef4b9484369c94ed7e5674e4b056b0d8f673e1ba`, chưa merge | ADR-010 PROPOSED, absent trên base #160; đọc trực tiếp bằng Git object, không copy/merge vào đây. |
| [Core HTTP candidate](https://github.com/tricore-opentrix/opentrix/blob/ef4b9484369c94ed7e5674e4b056b0d8f673e1ba/docs/01-architecture/r27-core-workflow-http-contract.md) / [authorization boundary](https://github.com/tricore-opentrix/opentrix/blob/ef4b9484369c94ed7e5674e4b056b0d8f673e1ba/docs/01-architecture/r27-core-authorization-boundary.md) | Cùng SHA #159 | Routes specified, not registered; HISTORY dùng READ authority trong candidate, không phát minh operation mới. |
| [PR #145](https://github.com/tricore-opentrix/opentrix/pull/145) / [R29 contract](https://github.com/tricore-opentrix/opentrix/blob/5d577dd4a0a8efa830459cf35cb1868e52a9de2f/docs/03-applications/helpdesk/r29-use-case-contract.md) | Rechecked HEAD `5d577dd4a0a8efa830459cf35cb1868e52a9de2f`, Open Draft; Yến APPROVED đúng HEAD, pre-integration documentation/contract only | Từ reviewed `b3d80254459269deb5071e52e59e1bda6954b5c7`: một Markdown file +6/-1, chỉ sửa CI evidence. Không đổi business contract/Java. Approval không giải quyết recovery/prerequisite decisions của R28. |
| [Issue #110](https://github.com/tricore-opentrix/opentrix/issues/110) | Kết quả tìm issues “R28” | R28 Windows fixture/CI legacy (#93/#94), không chứng minh Core ACL acceptance. Không đổi nghĩa backlog hoặc gộp gate. |

Tìm PR/issue R28 trả các dependency #145/#159/#160/#163 và legacy #110; không tìm thấy tài liệu G0-DESIGN R28 riêng trên base. Dùng `docs/verification/r28/` cạnh matrix R27. Không tạo ADR mới.

Ban đầu: nhánh `docs/r28-g0-design-20261109` tại main SHA `187dbd2…`; có untracked `portal-bff/bin/` được giữ nguyên. Nhánh mới `docs/r28-g0-design-readiness-review` được tạo trực tiếp từ verified #160 head, không sửa main/#145/#163, không merge/cherry-pick. Git metadata nằm ở worktree chung ngoài workspace nên fetch/branch/commit cần quyền filesystem riêng. Chỉ commit local; chưa xác minh quyền publish nên không push/mở PR.

## 2. Thuật ngữ và invariants phải giữ

| Khái niệm | Định nghĩa đối chiếu nguồn | Không được suy diễn |
| --- | --- | --- |
| Tenant guard | Core synchronization point theo tenant, generation được đọc/đổi dưới cùng protocol; ADR-015 §§5–6 | Bỏ expected generation không đồng nghĩa bỏ tenant lock. |
| Effective ACL | Membership + authoritative resource/lifecycle + exact operation grant + definition binding khi cần; §§4–6 | JWT role, owner flag, Helpdesk intent hoặc ACK cũ không đủ. |
| Policy generation | Revision của policy tenant, khác Workflow runtime version và business assignment version; §§4,6,8 | Không phải phiên bản riêng của ticket; batch/no-op increment còn OPEN. |
| Resource identity | Exact Core registry binding với tenant; candidate legacy có resource type; §§4–5 | Không tự chọn globally unique hay tenant-scoped key, normalization hoặc cho tái sử dụng ID. |
| Assignment version | Helpdesk business CAS token; Core coi opaque correlation; §8 | Không dùng làm expected Workflow version hoặc mặc nhiên là fence. |
| Resource fence | `fencingSequence` tăng trong stream tenant/resource, gắn Helpdesk intent; check và advance nguyên tử; §8.2 | Reject ≤ last accepted cho execution mới; không biết business intent chưa đến Core, không tự order mọi admin revoke. |
| Command identity | Scope đề xuất `(tenant, verified service principal, operation type, idempotency key)`; §9 | Correlation ID không cung cấp uniqueness/authority. |
| Ledger | Historical authoritative outcome + fingerprint/commit generation; §9 | Không chứng minh ACL hiện hành hoặc Helpdesk đã finalize. |
| READ/HISTORY | Authorize hiện hành, cùng Core transaction với dữ liệu trả về và revoke ordering; §6.4 | Detached ACL SELECT/TTL cache không đủ; HISTORY không được dùng historical grant. |
| Atomic replacement | Revoke-old + grant-new + generation + audit + outcome + fence cùng Core commit; §§7–8 | Chưa quy định thay toàn bộ resource ACL hay managed assignment slice; không xóa grant admin ngoài phạm vi. |
| Service boundary | Helpdesk intent/CAS và Core commit tách transaction; §9.1, ADR-010 D3–D6 | Không distributed rollback, cross-service FK/trigger/query. |

## 3. D-01 — generation precondition và resource fencing

**D-01 STATUS: RECOMMENDED — PENDING OWNER/CORE REVIEW**

Tên Option A/B/C dưới đây chỉ là **D-01**, không phải các lựa chọn authorization-lag OD-06. OD-06 Option A vẫn giữ nguyên.

### 3.1 Decision matrix

| Tiêu chí | D-01 A: required tenant generation | D-01 B: assignment resource fence authoritative | D-01 C: command classes / conditional generation |
| --- | --- | --- | --- |
| Safety | Reject mọi policy change kể từ snapshot, nếu mọi mutation bump generation. Vẫn cần current authorization và fence. | An toàn có điều kiện: current authority, exact managed slice, admin/revoke invalidation. Fence assignment đơn độc không đủ. | Giữ generation với command phụ thuộc snapshot rộng; assignment bỏ precondition chỉ sau proof invalidation. |
| Isolation | Tenant-wide logical conflicts + tenant lock. | Tenant-wide lock vẫn giữ; chỉ giảm logical false conflict. | Cùng lock protocol; không giảm tenant isolation. |
| Stale-command rejection | Fence chống delayed assignment; generation chống policy stale. | Fence reject older accepted command, không phát hiện admin change không advance fence. | Quy định riêng stale assignment, policy snapshot và admin invalidation. |
| False conflict | Cao: unrelated R2 bump G khiến R1 stale. | Không reject chỉ vì R2 đổi G; relevant policy changes vẫn phải được xét. | Thấp ở assignment đủ điều kiện; intentional conflicts ở policy/binding/membership batch. |
| Operational complexity | Ít contract modes; retry amplification, outbox backlog và reconciliation khi tenant bận. | Ít fields cần cho assignment nhưng phải giải quyết revoke/admin ownership và resync. | Nhiều class rules, invalid combinations và contract vectors; không cho caller chọn chế độ tùy ý. |
| SQL locking | Exclusive guard cho ACL replacement; compare G/fence trong transaction. | Vẫn exclusive guard; current facts đọc sau lock. | Như A/B; server xác định preconditions từ command type đã duyệt. |
| ADR-015 compatibility | Khớp §§7/9 hiện tại. | Cần amendment rõ bỏ required G cho assignment; không tự sửa ADR ở task này. | Cần owner đóng băng classes/amendment; giữ A làm baseline chưa đổi. |
| R29 compatibility | #145 mới đang giữ cả G và fence pending D-01; nhiều retry có thể kéo dài PENDING. | Ánh phải cập nhật dispatch/fingerprint/recovery; không được tự thay G trong cùng key. | R29 assignment chỉ dùng lớp được duyệt, không tùy chọn downgrade precondition. |
| Testability | Unrelated-generation conflict tái lập dễ; đo accepted/rejected và retry count. | Phải test revoke-before/after, admin same-resource và external deny, không chỉ stale fence. | Thêm full class/field matrix + mixed concurrent commands; coverage lớn hơn. |
| Recommendation | Baseline hiện hành cho đến owner quyết định; ưu tiên nếu chưa chứng minh invalidation. | Chưa khuyến nghị standalone fence như security boundary. | **Khuyến nghị hướng review có điều kiện**, không approved policy. |

### 3.2 Invariants và counterexamples

1. **Giữ tenant guard.** Mọi effective mutation (grant/revoke, membership, registry lifecycle, binding, service-admin authority) phải theo cùng serialization và generation/audit protocol. Không writer nào đi tắt bằng JDBC/trigger cũ. Resource fence là logical precondition, không thay tenant synchronization (§6.5 vẫn defer resource-level lock optimization).
2. **Current authorization.** Sau guard, Core recheck service authority, tenant/resource binding, recipient membership/lifecycle và allowed operation set. Bỏ G không bỏ các kiểm tra này. Policy deny/membership revoke phải thắng grant; không auto-reactivate resource.
3. **Assignment ordering.** Chỉ Helpdesk có thẩm quyền phát fence của stream đã đăng ký; persist intent trước dispatch. Core compare/advance cùng replacement; Helpdesk CAS chỉ finalize đúng version/key/fence. Command cao hơn chưa đến Core không thể chặn command thấp hơn bằng thông tin mà Core chưa biết.
4. **Admin ownership/invalidation còn BLOCKED.** Cần quyết định assignment chỉ replace grant slice do stream sở hữu hay toàn resource. Admin revoke/tombstone/emergency policy phải làm pending assignment không thể phục hồi quyền bị cấm. Các khả năng để review: persistent deny/current eligibility; invalidate stream bằng resource policy epoch; hoặc thủ tục admin pause/invalidate pending commands. Đây là thiết kế đề xuất, không thêm field/schema đã duyệt. Admin không tự tăng fence Helpdesk nếu chưa có protocol đồng bộ issuer.
5. **Replay là historical.** Same-key replay trả receipt sau current lookup authorization; không apply lại grant hoặc nâng fence. Nếu cần new authorized intent, cấp version/key mới theo business policy, không lách bằng retry.

Counterexample false conflict: R1 có fence 5, G=10. R2 đổi ACL → G=11; R1 command fence 6/G=10 bị A reject dù R1 không đổi. Nếu unrelated policy write rate là λ và intent-to-Core latency là Δ, mô hình Poisson minh họa xác suất conflict `1-exp(-λΔ)`; không phải benchmark. Retry lại snapshot dưới tải có thể khuếch đại hàng đợi. Đổi G trong payload cùng key sẽ conflict fingerprint; phải reconcile outcome cũ và tạo intent mới được kiểm soát, không rewrite outbox.

Counterexample unsafe B: pending assignment fence 6 được lập trước admin revoke trên R1; admin revoke chỉ bump G, fence vẫn 5. B chấp nhận 6 và regrant actor vừa bị revoke. Current service authority và recipient membership vẫn hợp lệ nên hai check đó **không** đủ chống resource-specific revoke. A reject G cũ trong lần gửi này; nhưng nếu client tự refresh G và gửi lại với key mới, A cũng không thay được emergency-deny policy. Không phương án nào tự bảo đảm immediate revocation.

Counterexample non-conflict: REVOKE membership đã commit trước assignment. Với guard/current facts đầy đủ, mọi option deny recipient không eligible; nếu grant row vẫn tồn tại, effective ACL phải deny theo membership. Test riêng trường hợp revoke grant nhưng membership còn active để không che lỗi B.

### 3.3 Command classes đề xuất cho C

| Class (logical, chưa là operation enum) | Preconditions đề xuất | Điều kiện khóa contract |
| --- | --- | --- |
| Assignment-owned replacement | Required monotonic incoming fence; proposed expected accepted fence nếu chọn CAS; expected G không required **chỉ sau** invariant 4 được chứng minh | Không overwrite unrelated admin grants; current authorization; admin invalidation protocol. Nếu chưa giải quyết, dùng baseline A. |
| Snapshot-derived admin/batch/binding/membership edits | Required expected G + current authority; resource-specific guard nếu contract quy định | G chống lost update của snapshot; batch increment/no-op semantics owner chốt. |
| Emergency revoke | Chưa cho execution class; separate owner/security procedure | Không downgrade qua assignment mode; define deny/invalidation/recovery trước runtime acceptance. |
| Workflow CREATE/ACTIVATE/TRANSITION/READ/HISTORY | Theo ADR-010/015 current ACL + guard; expected Workflow version khi cần | Không áp assignment envelope tùy tiện; không thêm G field bắt buộc cho routes ngoài contract nguồn. |

Đề xuất C tránh required tenant generation cho assignment độc lập **khi** các invariant đã được chứng minh. Chi phí class matrix có thật; nếu owner không cần mode khác nhau, A là phương án nhỏ hơn và hợp đồng chưa thay đổi. Không kết luận C được phép triển khai.

### 3.4 P1-01 — stale regrant và lựa chọn invalidation

Schedule bắt buộc: Helpdesk persist Q6 tại G10/fence5 → admin revoke grant của Unew trên R1, membership/service authority vẫn active, commit G11/fence5 → Q6/fence6 đến Core. Baseline A phải reject `STALE_POLICY_GENERATION`, không ACL/fence/G/success-audit mutation. Bare B và C bỏ G nhưng chưa có invalidation có thể grant lại Unew: **counterexample FAIL**, không phải authorization lag đã được OD-06 chấp nhận. Retry Q6 bằng key mới/G11 cũng không biến stale business intent thành authorized correction.

Invariant cần owner freeze: (a) assignment chỉ thay slice được đăng ký cho stream; (b) independent admin grant/deny được preserve; (c) resource-specific revoke phải xác định có invalidate pending intents không; (d) urgent deny tồn tại qua retry/replay và chỉ được clear bởi authority riêng; (e) stream/fence/epoch không reset do resource-ID reuse hoặc restore. Managed slice một mình không thỏa (c)/(d).

| Invalidation option, đều PENDING | Stale-regrant oracle | Trade-off / acceptance consequence |
| --- | --- | --- |
| Managed ACL slice + baseline required G (A) | Schedule trên reject G cũ; independent admin slice unchanged | Giữ ADR-015 hiện tại; unrelated R2 update vẫn gây logical false conflict. New intent sau refresh cần business authorization, không phải emergency deny proof. |
| Managed slice + resource policy epoch (B hoặc assignment class của C) | Admin invalidation advances epoch; pending command với old epoch reject dù incoming fence cao và membership active | Giảm unrelated-G conflict; thêm authenticated epoch precondition, issuer/recovery/restore rules và fingerprint field. Cần amendment ADR/R29; epoch không tự order admin với Helpdesk fence. |
| Managed slice + durable deny/eligibility fence | Admin deny thắng assignment và protected operation; command bị reject hoặc grant không effective theo contract được chọn | Có thể đáp ứng urgent removal sau Core commit; cần deny scope/clear authority và explicit response semantics. Không đồng nhất với assignment incoming fence hoặc OD-06 Option B đã không chọn. |
| Pause stream + invalidate/cancel pending intents | Sau revoke ACK, old queued/in-flight intent không execute; resume chỉ từ explicit new authorized intent | Thêm cross-service recovery; pause ở Helpdesk đơn độc không chặn request đã gửi. Phải có Core-enforced admission/invalidation và failure handling. |
| Bare assignment fence (B/C không invalidation) | Q6 regrants sau admin revoke → FAIL | Không đề xuất để freeze security contract. |

Recommendation **PENDING OWNER DECISION**: giữ A; review managed slice + epoch cho C nếu thật sự cần giảm logical conflicts, cùng persistent deny/procedure riêng cho urgent revoke. Yến quyết định ý nghĩa revoke, Bảo kiểm Core enforcement, Ánh kiểm intent refresh/resume. Không chọn epoch/deny/schema tại đây. X-14/X-15 và X-23 phải chạy đúng selected option; một safety FAIL không được đổi sang branch khác để PASS. Tenant guard vẫn serialize R1/R2 ở mọi option: giảm logical rejection không đồng nghĩa giảm physical wait hoặc có revocation deadline.

## 4. D-02..D-06 — assessment và compatibility

Chi tiết D-02/D-03: [command và idempotency design](r28-core-acl-command-and-idempotency-design.md).
Chi tiết D-04/D-05: [PostgreSQL và T07/T08 plan](r28-postgresql-locking-privilege-t07-t08-plan.md).

| D-06 use case | Core contract requirement | Helpdesk business requirement | Open design / runtime requirement | Assessment |
| --- | --- | --- | --- | --- |
| Create+Activate | Exact binding, current CREATE/ACTIVATE ACL; activation expected Workflow version; durable command outcome | Durable ticket/create intent + stable resource correlation; local finalize sau activation | Composite Core command hay two-step; idempotency cho cả hai dịch vụ, orphan recovery | #145 mới nêu cả hai lựa chọn, tương thích hướng; chưa endpoint/schema approved. |
| Assign/Reassign | Dedicated admin authorization; atomic replacement/G/audit/ledger/fence | CAS expected assignment version, durable intent/outbox trước send; pending gate | D-01/classes, managed grant slice và admin invalidation | #145 giữ generation baseline, không âm thầm bỏ; target proposal cần Ánh review lại. |
| Resolve | Current exact transition ACL, locked Workflow version, transition/history Core atomic | Eligible worker/current synchronized assignment; durable resolution intent; finalize resolution text bằng CAS | Prerequisite protocol giữa current assignment và remote transition, retry/status/error mapping | #145 bỏ distributed atomicity; chưa chứng minh concurrent reassignment không làm local finalize stale. |
| Confirm | Current authorized RESOLVED check + expected Workflow version; confirm transition vẫn tồn tại | Requester-only, synchronized assignment, matching resolution đã finalize; versioned confirmation intent + CAS | Đóng race read/check/transition và Helpdesk edits; không tin receipt cũ | #145 mới nêu confirm transition và prerequisites; chưa runtime E2E. |
| Core commit + Helpdesk CAS fail | Commit giữ nguyên, replay chỉ historical | Reconcile same intent; superseded attempt không overwrite current; không báo success | Recover current attempt khác superseded; compensation chỉ khi có approved business rule | C-02/C-04/C-16 và plan X-16; NOT RUN. |
| Pending / lost ACK | Authenticated status theo đúng scope; current ACL riêng | `PENDING_SYNCHRONIZATION` / `RECONCILIATION_REQUIRED`; same-key only sau reconcile | Status NOT_FOUND không chứng minh rollback; retention + in-flight safety | #145 mới tương thích hướng; D-03 còn blocker. |
| Timeout/escalation | Fail closed ở authorization; timeout không revoke | Observable pending, cảnh báo và escalation | Owner quyết định threshold/on-call/manual recovery, không tự đặt SLA | C-27 BLOCKED. |
| Emergency revocation | Current effective deny/revoke + prevent stale regrant, ACK sau commit | Không thông báo immediate revoke từ timeout/PENDING | Separate procedure/authority; invalidation của pending assignment | C-28 BLOCKED; Option A vẫn có lag không hard bound. |

**D-06 dependency: PENDING R28/R29 PROTOCOL DECISION.** #145 đã được Yến review tại HEAD mới; còn resend/prerequisite protocol cần thống nhất, không phải thiếu toàn bộ independent review. Không ghi đè nhánh/tài liệu của Ánh. ADR-010 vẫn proposed; approval #163/#145 không giải quyết service-boundary gate.

### 4.1 P1-06 — Resolve/Confirm khi reassignment cạnh tranh

Counterexample: H xác nhận V6 synchronized rồi commit resolution intent Z6; H tiếp nhận reassignment V7/pending; Core serialize Resolve Z6 trước ACL replacement Q7 và commit RESOLVED/W+1 dưới quyền còn effective; H CAS Z6 theo assignment V6 fail. Core commit hợp lệ theo revoke ordering/OD-06 nhưng không chứng minh local resolution hoặc V7 đã hoàn tất. Workflow expectedVersion không phát hiện Helpdesk V7, còn historical receipt không chứng minh current prerequisites. Confirm có race tương tự giữa local prerequisite check, Core read/transition và local CAS.

| Alternative, PENDING OWNER DECISION | Oracle và trạng thái hội tụ đề xuất | Trade-off / acceptance consequence |
| --- | --- | --- |
| H durable reservation cho assignment/resolution prerequisites | Trong local transaction, reserve exact resource/business versions + command ID; competing reassignment/Resolve/Confirm không được supersede reservation. Chỉ release sau authoritative outcome + matching local finalize/rejection | Recommendation để review: giữ local tx ngắn, không giữ DB lock qua network. Lost ACK/outage giữ reservation và observable reconciling; expiry đơn độc không release khi outcome unknown. Cần authority cho recovery/cancellation, restart và failover tests. |
| Cho supersede + explicit reconciliation decision | Preserve committed Core transition; old attempt không overwrite latest H. Resource vào unresolved conflict/reconciling và gate synchronized-only actions cho đến owner-authorized recovery | Ít blocking lúc nhận intent nhưng có thể cần manual resolution. Cần quyết định dùng resolution cũ, ghi corrective business record, hay forward transition được phép; không implicit reverse transition/regrant. |
| Core-enforced prerequisite token/epoch | Core reject stale business prerequisite token theo authoritative admission protocol | Core không tự biết H version. Cần protocol publish/invalidate và crash ordering, không coi opaque token gửi kèm là proof; mở rộng contract nên chưa ưu tiên MVP. |

Convergence acceptance, bất kể option: Core history/receipt giữ nguyên; mỗi H attempt có disposition riêng; current business state chỉ complete khi matching current intent và prerequisites được finalize. Superseded Core success phải có durable recovery disposition, không tự báo resolved/synchronized và không để unknown thành terminal failure. Confirm bị chặn khi matching resolution chưa finalize hoặc conflict chưa xử lý. Owner cần chọn invariant có cấm supersede hay không, recovery authority và result/UI/error mapping. X-16/X-26 tách same-current transient failure, superseded success và Confirm gating; chưa chốt option thì branch tương ứng BLOCKED, không runtime PASS.

## 5. Security threat review

Tất cả mitigation dưới đây là requirement/recommendation cần kiểm chứng; residual risk chưa được loại bỏ.

| THREAT | INVARIANT | MITIGATION | VERIFICATION | RESIDUAL RISK |
| --- | --- | --- | --- | --- |
| Cross-tenant ACL mutation | Verified principal chỉ có authority cho exact tenant/resource | Resolve registry tại Core, tenant composite predicates, fail closed hidden resource | C-13/C-14; X-08 | Normalization/resource key và service-scope policy chưa frozen. |
| Service-principal impersonation | Body/header không tạo principal | Core verifier kiểm signature/issuer/audience/expiry, approved service credential lifecycle; delegated user context riêng | X-08 authentication negatives + future HTTP contract tests | Credential theft thuộc T1 trust boundary; mechanism chưa chọn. |
| Stale assignment command | Fence và replacement commit cùng nhau | Strict > accepted fence cho execution mới; Helpdesk CAS | C-10/C-11; X-03/X-04/X-15 | Fence không biết intent chưa tới, admin invalidate chưa chốt. |
| Idempotency replay abuse | Historical replay không mutation/authority | Current auth cho replay/status; scoped key, retention/tombstone; no new-key blind retry | C-07/C-09/C-24; X-10/X-13 | Rejection/expiry policy cần owner, storage có thể tăng mãi. |
| Payload substitution | Cùng scope/key bind một canonical semantic payload | Core tự canonicalize/fingerprint, include resource/actor/operation/fence/version; reject ambiguous encoding | C-08; X-11 | Canonical version/hash chưa đóng băng. |
| Lost ACK / unsafe retry | Unknown khác rollback | Authenticated status + serialize retry same key; durable outcome cùng transaction | C-03/C-04; X-12/X-13 | NOT_FOUND lúc in-flight/expired không đủ; outage kéo dài reconciliation. |
| Old grant during lag | Option A không immediate revoke | UI pending/action gating + current Core ACL; separate approved emergency control | C-05/C-27/C-28/C-30 | Không hard revocation bound, quyền cũ có thể tồn tại vô hạn nếu không đồng bộ. |
| PostgreSQL role/function escalation | Request role không arbitrary ACL/G write | Role separation; nếu narrow definer: fixed qualified SQL, trusted owner/search_path, EXECUTE allowlist | C-25; X-09 | T1 trusted execution code compromise chưa được ngăn hoàn toàn. |
| Deadlock/timeout bypass | Failure không permission/success | Full rollback, no fallback grant/cache; status nếu commit uncertain | C-21..C-23; X-05..X-07 | DoS/tenant contention; lock budget chưa owner duyệt. |
| Audit gaps | Effective ACL delta và success audit cùng commit | Atomic audit + scoped command/fence/G; safe operational denial logs riêng | C-12/C-21; X-05/X-10 | Audit retention/denial export chưa chốt; logs không thay durable audit. |
| Inconsistent policy generation | Mọi effective policy writer cùng protocol | Guard first, generation/audit atomic, batch/no-op explicit; no direct Helpdesk writes | X-03/X-05/X-14; C-26 | Missed writer/legacy trigger có thể phá proof. |
| Emergency revoke bypass | Pending assignment không hồi sinh quyền khẩn cấp đã cấm | Approved deny/invalidation policy phải thắng assignment, revoke ACK only after Core commit | C-28; X-15 extended revoke case | Procedure OPEN; resource fence hoặc G riêng lẻ chưa chứng minh đủ. |

## 6. Owner decision register và readiness

| ID | Recommendation pending approval | Owner/reviewer cần quyết định | Blocker / next evidence |
| --- | --- | --- | --- |
| D-01 | Review C conditional; giữ A baseline cho đến quyết định | Yến quyết định, Bảo security, Ánh dispatch/CAS | Admin invalidation/managed slice; mixed-command counterexamples. |
| D-02 | Explicit service authority, exact scope, server fingerprint và historical outcome | Bảo + Yến + Ánh | Auth mechanism, normalization/resource incarnation, field/operation classes, HTTP/status visibility. |
| D-03 | Single transaction, only durable terminal receipt; no persistent progress/unknown default | Bảo + Ánh | Rejected-command receipts, retention/tombstone/admission expiry, key/canonical versions, status absence semantics. |
| D-04 | Guard first; shared readers/exclusive policy writers; request-role không UPDATE G | Bảo + Yến | Chọn trusted execution/definer/advisory protocol và actual role matrix; T1 limitation explicit. |
| D-05 | Disposable deterministic two-session plan, exact-SHA artifacts | Bảo; independent reviewer Yến/Ánh theo scope | Target schema/API chưa có; C-20..23 NOT RUN; C-25/26 BLOCKED. |
| D-06 | #145 HEAD `5d577dd…` đã có scoped approval; freeze prerequisite/CAS protocol §4.1 | Ánh + Yến; Bảo Core boundary | PENDING R28/R29 PROTOCOL DECISION; approval pre-integration không đóng race. |
| OPS | Observable lag escalation và emergency-revoke riêng | Yến + Ánh; Bảo feasibility | C-27/C-28 BLOCKED; không tự đặt duration hoặc runbook. |
| ARCH | Resolve ADR-010 và service ownership/cutover | Yến + Bảo + Ánh | #159 open/proposed; cutover chỉ lập kế hoạch. |

Readiness kết luận: đã có analysis và test specification để review; **chưa đủ design acceptance**. Các lựa chọn schema/privilege/wire và các security proof ở register vẫn chưa được owner chốt. Không sửa ADR-015, matrix R27, code hoặc nhánh #145/#163 để thể hiện approval.

### 6.1 P1 remediation disposition (documentation scope)

`FIXED` = thiếu sót test/document specification đã bổ sung; `CLARIFIED` = giới hạn/alternatives/oracle đã rõ, không chọn policy; `BLOCKED BY DECISION` = chưa thể thống nhất contract nếu owner chưa chọn. Không status nào nghĩa runtime PASS.

| Review group | Disposition | Evidence / quyết định còn mở |
| --- | --- | --- |
| P1-01 D01 | CLARIFIED | §3.4; A baseline, epoch/deny/slice và X-14/X-15/X-23; chọn invalidation còn mở. |
| P1-02 D03 | CLARIFIED | Command design §§2.1,3.4,4.1; X-11/X-23..25; rejection, canonical profile, completeness mechanism và retention chưa chọn. |
| P1-03 Recovery | BLOCKED BY DECISION | Command design §5.1; R29 HEAD checked; hai protocol có oracle, recommendation chưa là shared contract. |
| P1-04 Privileges | CLARIFIED | Lock plan §§2.2–2.3; atomic helper publication, effective role/lock selection và X-09/X-25 chưa verified. |
| P1-05 T07/T08 | FIXED | Sửa X-03/05/06/09/16/17, thêm X-18..26; giữ ID cũ và C-ID meanings. Harness/database execution NOT RUN/BLOCKED. |
| P1-06 Resolve/Confirm | CLARIFIED | §4.1 và X-16/X-26; reservation vs supersede/recovery cần owner quyết định. |

### 6.2 Owner decision package — tất cả PENDING OWNER DECISION

| Question / owner | Options | Recommendation để review | Trade-offs và acceptance consequences |
| --- | --- | --- | --- |
| Q-01: assignment/admin revoke invalidates gì? Yến, Bảo/Ánh review | A + managed slice; C + epoch; durable deny; Core-enforced pause | Giữ A; đánh giá epoch nếu giảm false conflict cần thiết (§3.4) | C cần amendment ADR-015/R29 + class/fingerprint/invalidation tests; chưa có proof thì không bỏ G. Urgent revoke cần policy riêng. |
| Q-02: failure nào bind key? Bảo + Ánh | Success-only + terminal-failure no-resend; committed no-op deterministic rejection | Review terminal no-op cho authenticated deterministic domain rejections | Thêm rejection classification/audit; SQL rollback không tạo receipt. Success-only phải công khai giới hạn binding/replay và reconcile promise của ADR-015 §9 qua owner process; X-24 phải match lựa chọn. |
| Q-03: receipt completeness enforced thế nào? Bảo, Yến security | Deferred commit validation; final-only receipt sau approved serialization | Review deferred validation nếu giữ early reservation (§3.4 command design) | Cần schema/privilege review, reject incomplete commit X-25; T1 không thành T2. Final-only cần prove key lock trước mutation ở mọi path. |
| Q-04: canonical profile/version? Bảo + Ánh | Strict presence/exact canonical IDs/reject unknown-null; hoặc schema-approved normalization/default equivalence; cả hai versioned | Review strict profile để ít implicit transforms, server-derived digest | Tương thích client/identity authority khác nhau; chốt bytes/hash/limits trước golden digest tests. Approved defaults cần vectors riêng; version migration giữ old-key semantics, không chỉ chọn SHA-256. |
| Q-05: retention/admission/restore? Bảo + Ánh, Yến policy | Full receipts; full window + tombstone; authenticated epoch/admission floor | Review window + retained identity, không chọn duration | Tombstone không được mất khi old request còn admissible; restore/issuer/resource incarnation phải đồng bộ. X-23 còn BLOCKED tới khi chọn. |
| Q-06: unknown outcome có được resend? Ánh + Bảo, Yến contract | Definitive non-commit barrier; safe same-key serialized resend | Review safe same-key resend sau lookup, retention/admission check (§5.1 command design) | Cần cập nhật R29 qua owner process; nếu giữ R29 hiện tại phải cung cấp definitive admission/closure protocol. Không new-key retry; chưa thống nhất thì BLOCKED. |
| Q-07: reader lock/privilege boundary? Bảo + Yến | Narrow definer; transaction advisory locks; separate trusted executor | Review narrow lock-only definer nếu giữ row lock | Atomic create/revoke transaction + actual role matrix/X-09; advisory cần all-writer proof/key namespace. Không broad UPDATE hoặc ngầm chọn T2. |
| Q-08: reassignment có được supersede Resolve/Confirm đang pending? Ánh + Yến, Bảo Core | H durable reservation; explicit supersede/recovery; Core prerequisite admission | Review durable local reservation (§4.1) | Gate competitors tới definitive outcome; owner chọn recovery/abandon authority. Nếu cho supersede cần durable conflict disposition, X-16/X-26 và approved forward recovery. |
| Q-09: cutover và operational recovery khi nào được phép? Yến + Bảo + Ánh | Separate approved cutover + owner runbook; tiếp tục BLOCKED | Giữ separate approval, no migration trong remediation | ADR-010/#159, catalog/ID/receipt reconciliation và X-17; timeout/emergency thresholds/authority chưa chọn, không suy SLA từ SQL timeout. |

Traceability: ADR-015/#160 `5618091…` là baseline; #163 `35ab10a7…` xác nhận hướng OD-06/ledger, không approve các recommendation mới; #159 `ef4b9484…` là proposed service boundary; #145 `5d577dd…` chỉ scoped pre-integration approval. Immutable source links ở §1; chi tiết recovery ở command design §5.1. Decision owner phải ghi selected option, reviewed SHA, reviewers và acceptance consequences trước contract freeze; remediation không sửa ADR status/G0 gates.

## 7. Verification và next actions

Kết quả local ngày 2026-11-09 (documentation-only):

| Check | Kết quả / evidence |
| --- | --- |
| Markdown links | 37 links kiểm tra; relative targets/anchors tồn tại, immutable GitHub blob paths có Git object tại source SHA; GitHub PR/comment/review và PostgreSQL references đã đọc qua connected GitHub/official docs. Không blanket HTTP crawl toàn repo. |
| Changed-file SPDX/REUSE | `python -m reuse lint-file` trên đúng ba file, REUSE 6.3.0, exit 0; SPDX Apache-2.0/TRICORE headers đầy đủ. Tool cài ngoài repo, không thêm dependency runtime. |
| Repository-wide REUSE | `python -m reuse lint`, exit 1: invalid expression trong unchanged `scripts/r23-compliance.py` và 11 class files trong untracked `portal-bff/bin/` có sẵn thiếu SPDX. Không sửa/xóa các file này. |
| Baseline reproduction | Archive riêng của base `5618091…` vào disposable temp directory: `reuse lint` exit 1, cùng invalid expression `Apache-2.0", "-->", "",` trong `scripts/r23-compliance.py`; 338/338 tracked baseline files có copyright/license. Lỗi không phát sinh từ ba tài liệu. |
| Scope/semantic assertions | Chỉ ba Markdown R28 mới; SQL blocks đều text pseudocode có NON-EXECUTABLE label; không thêm ADR, runtime, database hoặc gate approval; future case statuses NOT RUN/BLOCKED. |

Whitespace và staged/committed scope được kiểm tra lại bằng `git diff --check` trước/sau local commit; exact commit/exit kết quả trong final task report. Những check tài liệu này không suy ra runtime result.

T07/T08: **NOT RUN**. Runtime E2E: **NOT RUN**. Schema/role selection và owner controls: **BLOCKED**. CI trên nhánh tài liệu mới: **NOT RUN / NOT VERIFIED**.

Next actions: review local documentation commit với Yến (owner/gate scope), Ánh (R29), Bảo (Core/PostgreSQL); đóng register trước contract freeze. Chỉ sau các gate áp dụng được phê duyệt mới viết riêng implementation/migrations/harness và chạy disposable verification. Không push, merge, chạy grants, SQL hoặc cutover trong task này.

### 7.1 P1 documentation remediation validation — 2026-11-09

Working base trước sửa: branch `docs/r28-g0-design-readiness-review`, HEAD `d70a82117a978c22950e39d984286a996341d769`, merge-base với #160 là `5618091dc205b196b551465d2c52def9313ed1fb`; chỉ untracked `portal-bff/bin/` có sẵn, giữ nguyên. Chỉ ba tài liệu R28 được sửa; final local commit SHA báo riêng sau commit, không tự ghi self-referential SHA trong nội dung.

| Check | Remediation evidence / limit |
| --- | --- |
| Diff/whitespace | `git diff --check` exit 0; scoped diff chỉ ba file trong `docs/verification/r28/`. |
| Links | Python read-only path/heading assertions exit 0: 39 Markdown links, 16 relative targets/anchors hợp lệ; immutable GitHub blob targets kiểm bằng local Git objects hoặc connected fetch. R29 HEAD fetched blob `8e299ff927a92a3fce47af43fcc0fddb8ef42a53`, lines 60–75 xác nhận resend discrepancy. Không blanket HTTP crawl 23 external link occurrences hoặc coi tồn tại link là approval. |
| Semantic/scope checks | Read-only assertions exit 0: X-01..17 headings giữ nguyên; X-01..26 unique/in order; original pseudocode code blocks unchanged. Manual diff review: baseline A và OPEN decisions giữ nguyên, không ADR/R29/runtime/grant/route/gate modification. |
| REUSE changed files | REUSE 6.3.0 `lint-file` đúng ba file, exit 0; tool installed ngoài repo. Không chạy lại repository-wide REUSE; failure baseline ở §7 là historical evidence, không claim toàn repo PASS. |
| Runtime/CI | PostgreSQL/T07/T08/E2E NOT RUN; actual schema/SQL/roles/privilege graph và conditional oracles BLOCKED đến decisions/harness. Không CI/runtime security PASS suy từ documentation checks. |

Documentation remediation chuẩn bị đủ analysis/specification/decision questions cho review, không giải quyết các owner choices bằng suy diễn. Next review: Yến chọn policy/acceptance scope Q-01/06/08/09; Ánh review R29 resend, prerequisites, recovery và canonical/retention interoperability; Bảo review invalidation, receipt completeness, lock/privileges và executable test feasibility. Ghi disposition từng Q tại exact remediation SHA trước contract freeze; mọi implementation/runtime acceptance vẫn qua các gate hiện hành.