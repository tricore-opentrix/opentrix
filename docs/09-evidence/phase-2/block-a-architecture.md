<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Khối A — Kiến trúc, hợp đồng, bảo mật và tài liệu / Block A — Architecture, contracts, security and documentation

## 1. Thông tin báo cáo / Report metadata

| Trường / Field | Giá trị / Value |
|---|---|
| Khối / Block | A |
| Issue | [#183](https://github.com/tricore-opentrix/opentrix/issues/183) · parent [#182](https://github.com/tricore-opentrix/opentrix/issues/182) |
| Owner | @phanyen06ym-ien (Yến) |
| Reviewer độc lập / Independent reviewers | @lexuanbao258-collab (Bảo — kiến trúc / architecture) · @ngang02012007-crypto (Ánh — tài liệu / documentation) |
| Baseline SHA (`main`) | [`832c75fc3164cf170eed3bb8f1e380d24dd65aba`](https://github.com/tricore-opentrix/opentrix/commit/832c75fc3164cf170eed3bb8f1e380d24dd65aba) |
| Thời điểm baseline / Baseline snapshot (UTC) | `2026-11-10T18:35Z` (ghi trong / recorded in #182) |
| Mốc R24 lịch sử / Historical R24 freeze | `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e` — không phải baseline audit / not the audit baseline |
| Phương pháp / Method | Đọc Git tree tại đúng SHA, mã nguồn và tài liệu chọn lọc, metadata GitHub Actions; biên dịch và chạy `jdeps` trên worktree tách riêng tại SHA. Không chạy runtime, DB, browser. / Exact-SHA tree, selected sources and docs, Actions metadata; compile + `jdeps` on a detached worktree. No runtime, DB or browser execution. |
| Phạm vi SHA / SHA scope | Mọi finding được ghi tại `main@832c75f` trừ khi ghi khác. Kiểm kê nhánh/PR (mục 9.1) là snapshot thời điểm `2026-11-11T00:41Z`. / All findings are at `main@832c75f` unless stated; the branch/PR inventory (9.1) is a `2026-11-11T00:41Z` snapshot. |
| Kết luận chung / Overall verdict | `PARTIAL — KIỂM KÊ CÓ BẰNG CHỨNG, CHƯA PHẢI NGHIỆM THU KIẾN TRÚC / EVIDENCE-BASED INVENTORY, NOT ARCHITECTURE ACCEPTANCE` |

Báo cáo này kiểm kê hiện trạng (as-is). Nó **không** phê duyệt kiến trúc đích, không merge ADR, không sửa mã, không xác nhận release và không đóng issue quyền nguồn [#138](https://github.com/tricore-opentrix/opentrix/issues/138). / This report inventories the as-is state only. It does **not** approve the target architecture, merge ADRs, change code, certify a release or close [#138](https://github.com/tricore-opentrix/opentrix/issues/138).

## 2. Từ vựng và thang ưu tiên chung cho #182 / Shared vocabulary and priority scale for #182

Khối A đề xuất bộ dưới đây làm chuẩn chung cho cả ba khối A, B, C. Sau khi reviewer đồng ý, bộ này được chép vào #182 và Khối B, C đổi theo. / Block A proposes the following as the common standard for Blocks A, B and C. Once approved, it is copied to #182 and Blocks B and C align to it.

### 2.1 Hai chiều trạng thái / Two status dimensions

Mục "Evidence contract" của #182 cho phép một thành phần có nhiều chiều trạng thái. Mỗi finding ghi **cả hai chiều** dưới đây, ví dụ `IMPLEMENTED / OBSERVED_SOURCE` = có trong mã, chưa chứng minh đã chạy. `BLOCKED` dùng kèm được ở cả hai chiều. / Per the #182 evidence contract, each finding records both dimensions; `BLOCKED` may accompany either.

**Chiều hiện thực (giữ nguyên theo #182) / Implementation dimension**

| Mã / Code | Nghĩa / Meaning |
|---|---|
| `IMPLEMENTED` | Có mã hiện thực. / Implemented in code. |
| `TESTED` | Có test tự động cho phần này. / Covered by automated tests. |
| `INTEGRATED` | Đã nối với các thành phần liên quan qua luồng thật. / Wired end-to-end with related components. |
| `PARTIAL` | Hiện thực một phần. / Partially implemented. |
| `DESIGNED_ONLY` | Mới có thiết kế, tài liệu hoặc fixture MOCK. / Design, docs or MOCK fixtures only. |
| `MISSING` | Bắt buộc nhưng không có. / Required but absent. |

**Chiều bằng chứng (bổ sung) / Evidence dimension**

| Mã / Code | Nghĩa / Meaning |
|---|---|
| `RUNTIME_VERIFIED` | Đã chạy tại đúng SHA, có lệnh, log hoặc báo cáo lưu lại. / Executed at the exact SHA with retained command, log or report. |
| `CI_BUILD_PASS_AT_BASELINE` | Job CI tại đúng SHA thành công, nhưng không lưu kết quả từng test. / CI job passed at the exact SHA; no per-test report retained. |
| `EVIDENCE_CAPTURED` | Đã thu dữ liệu thô tại đúng SHA, chưa phân tích xong. / Raw evidence captured at the exact SHA; analysis pending. |
| `OBSERVED_SOURCE` | Có trong mã nguồn tại SHA; chưa chứng minh đã chạy. / Present in source at the SHA; execution not proven. |
| `OBSERVED_METADATA` | Quan sát từ metadata GitHub (PR, issue, run, release). / Observed from GitHub metadata (PRs, issues, runs, releases). |
| `UNKNOWN` | Chưa xác lập được bằng chứng. / Evidence not established. |

`BLOCKED` — bị chặn bởi một phụ thuộc hoặc quyết định; dùng kèm một trong hai chiều. / Blocked by a dependency or decision; used alongside either dimension.

Có class hoặc tên test trong repo **không** đồng nghĩa với test đã chạy thành công: `TESTED` ở chiều hiện thực phải đi cùng một mã ở chiều bằng chứng cho biết test đã chạy hay chưa. / A class or test name alone never means a successful run: `TESTED` must be paired with an evidence code.

Ghi chú cho báo cáo này: các bảng ở mục 3–9 được viết trước khi chốt hai chiều, nên chủ yếu ghi chiều bằng chứng; `PARTIAL`, `DESIGNED_ONLY`, `MISSING` trong các bảng đó là chiều hiện thực. / Tables in sections 3–9 predate the two-dimension rule and mostly record the evidence dimension.

### 2.2 Thang ưu tiên / Priority scale

| Mức / Level | Định nghĩa / Definition |
|---|---|
| **P0** | Chặn việc nộp bài, làm mất điểm PoF, hoặc là quyết định đang chặn việc của người khác. Phải xong trước release dự thi. / Blocks submission, loses PoF points, or is a decision blocking others. Must be done before the competition release. |
| **P1** | Cần cho buổi trình diễn chung kết hoặc điểm sản phẩm (50 điểm). / Needed for the final demo or product score. |
| **P2** | Cải thiện chất lượng, làm nếu còn thời gian trước hạn nộp. / Quality improvement if time allows. |
| **P3** | Ngoài phạm vi trước hạn nộp; giữ làm định hướng phát triển. / Out of scope before the deadline; kept as roadmap. |

## 3. Kiến trúc mã nguồn hiện tại / Current (as-is) source architecture

| Khu vực / Area | Quan sát tại SHA / Observed at SHA | Giới hạn / Limit | Trạng thái / Status |
|---|---|---|---|
| Backend | `backend/settings.gradle` có một project `dxos-backend`; entry point `DxosApplication`; Java 21, Spring Boot 3.5.16 | Một project không chứng minh môi trường triển khai / One project does not prove a deployment | `OBSERVED_SOURCE` |
| Core logic | `core.identity`, `core.workflow`, `core.data` chứa type, port và logic domain/runtime dùng chung | Năng lực logic, không phải service triển khai riêng / Logical capabilities, not separate services | `OBSERVED_SOURCE` |
| Application | Có `application.authorization`, `application.identity`; `application.helpdesk` và `application.facility` chỉ có `.gitkeep` | Nghiệp vụ Helpdesk đang nằm ở `infrastructure.workflow.HelpdeskService` | `OBSERVED_SOURCE` |
| Gateway/HTTP | Controller health và Helpdesk (có điều kiện); `WorkflowController` chung không được đăng ký | Có annotation không chứng minh route đang sống / Annotations do not prove a live route | `OBSERVED_SOURCE` |
| Persistence | `PostgresWorkflowPersistence`, JDBC, Flyway V1–V4, SQL Helpdesk | Cấu hình và runtime PostgreSQL thuộc Khối B | `OBSERVED_SOURCE` |
| Portal BFF | `portal-bff` là Spring Boot riêng: OIDC session, CSRF, chuyển tiếp Helpdesk có allowlist | Luồng browser thật chưa xác lập (xem Khối C) | `OBSERVED_SOURCE` |
| Frontend | React, TypeScript, Vite, Vitest, Playwright | MOCK, integration-local và E2E thật phải tách riêng | `OBSERVED_SOURCE` |
| Object storage | Có `core.data.ObjectStoragePort` và bản in-memory cho test | **Không có** adapter S3/MinIO/SeaweedFS chạy thật | `MISSING` (adapter) |
| Facility | Chỉ có fixture MOCK ở frontend; backend trống | Chưa có tái sử dụng ứng dụng thứ hai | `DESIGNED_ONLY` |

**Topology thực tế / Actual topology:** hiện trạng đã có **ba thành phần chạy riêng** — `backend`, `portal-bff`, `frontend` — cộng Keycloak là nhà cung cấp định danh bên ngoài. Nhóm đã chốt backend là Modular Monolith (mục 7); ADR cần ghi rõ `portal-bff` tiếp tục là deployable riêng hay không. / The as-is already has **three deployables** plus external Keycloak. The team chose a Modular Monolith backend (section 7); the ADR must state whether `portal-bff` stays a separate deployable.

**Luồng dự kiến theo mã / Code-level intended flow (chưa phải bằng chứng E2E):** React Portal → Portal BFF (OIDC session, CSRF, Bearer forwarding) → `HelpdeskController` → `HelpdeskService` → PostgreSQL.

## 4. Ranh giới Core/Application và quy tắc phụ thuộc / Core/Application boundaries and dependency rules

Nguồn quy tắc đích / Normative target rules: [`docs/01-architecture/dependency-rules.md`](../../01-architecture/dependency-rules.md), DR-01–DR-16. Phân biệt quy tắc đích với phần mã đang thực thi quy tắc.

| ID | Quan sát / Finding | Hệ quả / Implication | Trạng thái / Status | Priority |
|---|---|---|---|---|
| BND-01 | `gateway.helpdesk.HelpdeskController` import trực tiếp `infrastructure.workflow.HelpdeskService` và các record lồng `RequestView`, `HistoryView`, `Page` (xác nhận bằng `jdeps` mức class, mục 4.1) | Gateway phụ thuộc hạ tầng cụ thể thay vì use case Application công khai; mô hình phản hồi API nằm trong lớp hạ tầng | `OBSERVED_SOURCE` | P1 |
| BND-02 | `HelpdeskService` gộp phân quyền nghiệp vụ, điều phối và JDBC | Ranh giới Application chưa tách; mọi refactor phải giữ nguyên tính nguyên tử của transaction | `OBSERVED_SOURCE` | P1 |
| BND-03 | `core.workflow.WorkflowRuntime` phụ thuộc `WorkflowPersistencePort` của Core; `PostgresWorkflowPersistence` hiện thực port này | Điểm đảo ngược phụ thuộc tốt, giữ nguyên | `OBSERVED_SOURCE` | — |
| BND-04 | `WorkflowController` không có `@RestController`/`@Component`; mã ghi rõ cấm đăng ký production khi chưa có guard | Không quảng bá Workflow HTTP chung là đang chạy | `OBSERVED_SOURCE` | — |
| BND-05 | `CoreDependencyRulesTest` (ArchUnit) kiểm quy tắc Core và giữa các capability, có canary âm/dương; quy tắc Application/Gateway chưa có | Thực thi kiến trúc tự động mới **một phần** | `CI_BUILD_PASS_AT_BASELINE` | P1 |
| BND-06 | Chỉ một Gradle project `dxos-backend`; không có `core-service`/`helpdesk-service` | Khớp hướng Modular Monolith nhóm đã chốt (mục 7); đề xuất tách R27 trước đây chỉ còn là lịch sử. Ranh giới module chưa được cưỡng chế ở tầng Application/Gateway (BND-05) | `OBSERVED_SOURCE` | P1 |
| BND-07 | `jdeps` mức package trên mã biên dịch tại SHA (mục 4.1): **đúng một** cạnh vào `infrastructure` từ tầng trên (`gateway.helpdesk → infrastructure.workflow`, xác nhận BND-01); `core` không phụ thuộc tầng nào khác; `application` chỉ phụ thuộc `core` | Đồ thị tĩnh khớp phần lớn quy tắc phân tầng; ngoại lệ là BND-01, BND-08, BND-10. `portal-bff` xem BND-11 | `OBSERVED_SOURCE` (jdeps, package + class level) | P1 |
| BND-08 | Hai module gateway phụ thuộc lẫn nhau. Mức class: `HelpdeskExceptionHandler → WorkflowExceptionHandler`; `gateway.workflow.WorkflowJsonConfiguration → HelpdeskController` và các record request `Assign`, `Create`, `Resolve`, `Version` | Vòng ở mức module (không phải vòng package trực tiếp). Cấu hình JSON của phần Workflow chung biết tới DTO của ứng dụng Helpdesk — chiều phụ thuộc bị đảo: phần dùng chung không nên biết ứng dụng cụ thể | `OBSERVED_SOURCE` | P1 |
| BND-09 | `core.data` không có cạnh vào nào từ mã main; chỉ phụ thuộc chính nó | Năng lực lưu trữ phi cấu trúc chưa có bên dùng nào ở runtime, khớp với adapter `MISSING` (mục 3, 6.1) | `OBSERVED_SOURCE` | P0 (gộp với adapter storage) |
| BND-10 | `gateway` phụ thuộc thẳng `core` qua 4 cạnh package. Mức class: phần lớn là type giá trị và ngoại lệ (`ActorReference`, `ResourceReference`, `TransitionRecord`, `WorkflowInstance`, `WorkflowErrorCode`, `WorkflowException`, `AuthenticatedPrincipal`, `Authority`…); riêng `WorkflowController → WorkflowRuntime` là gọi thẳng engine | Type giá trị có thể hợp lệ nếu được công bố là API công khai của Core — hiện Core chưa tách phần công khai/nội bộ. Cạnh `→ WorkflowRuntime` bỏ qua tầng Application và gắn gateway vào engine cụ thể; tuy controller chưa được đăng ký (BND-04), cạnh này sẽ cản việc thay engine bằng Flowable (RISK-02) | `OBSERVED_SOURCE` | P2 (P1 nếu controller được bật) |
| BND-11 | `portal-bff` chỉ có cạnh nội bộ `com.tricore.dxos.portal → com.tricore.dxos.portal`; không phụ thuộc compile-time vào package nào của backend | BFF tách khỏi backend ở mức mã nguồn, chỉ giao tiếp qua HTTP | `OBSERVED_SOURCE` | — |

### 4.1 Bằng chứng `jdeps` / `jdeps` evidence

Chạy ngày 2026-11-11 trên worktree tách riêng, detached HEAD tại `832c75f`. / Run on 2026-11-11 on a detached worktree at `832c75f`.

```powershell
git -C $REPO worktree add --detach $AUDIT 832c75fc3164cf170eed3bb8f1e380d24dd65aba
cd $AUDIT\backend
.\gradlew.bat clean compileJava
jdeps --ignore-missing-deps -verbose:package -filter:none build\classes\java\main | Out-File -Encoding utf8 $AUDIT\backend-package-deps.txt
jdeps --ignore-missing-deps -verbose:class   -filter:none build\classes\java\main | Out-File -Encoding utf8 $AUDIT\backend-class-deps.txt

# Lọc cạnh nội bộ / internal edges only
Select-String -Path $AUDIT\backend-package-deps.txt -Pattern '->' |
  Where-Object { $_.Line -notmatch '-> (java|javax|jakarta|org\.springframework|com\.fasterxml|org\.slf4j|lombok)\.' } |
  ForEach-Object { $_.Line } | Out-File -Encoding utf8 $AUDIT\deps-internal.txt

# portal-bff — dùng wrapper backend như CI (bản clone làm việc, HEAD 832c75f)
cd $REPO
.\backend\gradlew.bat -p portal-bff clean compileJava
jdeps --ignore-missing-deps -verbose:package -filter:none portal-bff\build\classes\java\main | Out-File -Encoding utf8 $AUDIT\bff-package-deps.txt
```

| Mục / Item | Giá trị / Value |
|---|---|
| OS | Windows 11 10.0 amd64, PowerShell |
| JDK | Temurin OpenJDK 21.0.12.1+1-LTS |
| Gradle | 8.14.3 (wrapper), Kotlin 2.0.21, Groovy 3.0.24 |
| Phạm vi / Scope | `backend` main classes (worktree tại `832c75f`); `portal-bff` main classes (bản clone làm việc, HEAD `832c75f`, không có thay đổi trên file được track) / Backend and BFF main classes at `832c75f` |
| Build `portal-bff` | Bằng wrapper backend (Gradle 8.14.3), đúng như job CI `portal-bff`: `backend\gradlew.bat -p portal-bff clean compileJava`. Kết quả `jdeps` giống lần chạy trước bằng wrapper 9.6.0 lạc (chỉ có cạnh `portal → portal`) |
| Lọc / Filter | Bỏ cạnh tới `java`, `javax`, `jakarta`, `org.springframework`, `com.fasterxml`, `org.slf4j`, `lombok`; chỉ giữ cạnh `com.tricore.dxos → com.tricore.dxos` |
| Output | `backend-package-deps.txt`, `backend-class-deps.txt`, `deps-internal.txt`, `bff-package-deps.txt` — đính kèm tại [#183](https://github.com/tricore-opentrix/opentrix/issues/183#issuecomment-6783378923) / attached on #183 |

#### Ma trận tầng → tầng (số cạnh package, bỏ cạnh trong cùng tầng) / Layer → layer matrix (package edges, intra-layer excluded)

| Từ ↓ / Đến → | `core` | `application` | `common` | `infrastructure` | `gateway` |
|---|---:|---:|---:|---:|---:|
| `core` | — | 0 | 0 | 0 | 0 |
| `application` | 3 | — | 0 | 0 | 0 |
| `infrastructure` | 3 | 3 | 1 | — | 0 |
| `gateway` | 4 | 3 | 2 | **1** | — |
| `common` | 0 | 0 | — | 0 | 0 |

Đọc ma trận: không có cạnh nào đi ngược vào `gateway`; `application` và `core` không phụ thuộc `infrastructure`; `infrastructure → application` là adapter hiện thực port của Application (hợp lệ trong hexagonal). Ngoại lệ duy nhất đi vào hạ tầng là `gateway → infrastructure` (BND-01). / No edge points back into `gateway`; `application` and `core` never depend on `infrastructure`; the only edge into infrastructure from above is BND-01.

#### Cạnh cần xử lý / Edges to act on

| Cạnh package / Package edge | Class nguồn → đích / Source → target classes | Finding | Đánh giá / Assessment |
|---|---|---|---|
| `gateway.helpdesk → infrastructure.workflow` | `HelpdeskController → HelpdeskService`, `HelpdeskService$RequestView`, `$HistoryView`, `$Page` | BND-01 | Vi phạm phân tầng. Ngoài lời gọi service, các record lồng trong lớp hạ tầng đang đóng vai mô hình phản hồi HTTP, nên hợp đồng API bị gắn vào `infrastructure` |
| `gateway.helpdesk → gateway.workflow.controller` | `HelpdeskExceptionHandler → WorkflowExceptionHandler` | BND-08 | Helpdesk dùng lại xử lý lỗi nằm trong package controller Workflow chung |
| `gateway.workflow → gateway.helpdesk` | `WorkflowJsonConfiguration → HelpdeskController`, `$Assign`, `$Create`, `$Resolve`, `$Version` | BND-08 | Cấu hình dùng chung tham chiếu DTO của ứng dụng cụ thể, tạo vòng ở mức module |
| `gateway.workflow.controller → core.workflow` | `WorkflowController → WorkflowRuntime`, `TransitionCommand`, `TransitionResult`, `WorkflowInstance`… | BND-10 | Gọi thẳng engine, bỏ qua Application; controller chưa được đăng ký |
| `gateway.helpdesk`, `gateway.workflow.dto`, `gateway.workflow.security → core.*` | `HelpdeskExceptionHandler → WorkflowErrorCode`, `WorkflowException`; các DTO `Workflow*Response` → type giá trị `core.workflow`; `WorkflowGatewayPrincipalGate → AuthenticatedPrincipal`, `Authority`, `RequiredAuthority` | BND-10 | Type giá trị và ngoại lệ; hợp lệ nếu Core công bố chúng là API công khai |
| (không có cạnh vào) `core.data` | — | BND-09 | Năng lực storage chưa được dùng |

**Hướng xử lý gợi ý (không thuộc phạm vi audit, để owner quyết) / Suggested direction (outside audit scope):**

- **BND-01:** đưa use case và các view model Helpdesk lên `application.helpdesk` (đang trống); gateway chỉ phụ thuộc Application.
- **BND-08:** tách phần xử lý lỗi và cấu hình JSON dùng chung ra khỏi package của controller Workflow (ví dụ vào `common` hoặc gói gateway dùng chung); để module Helpdesk tự đăng ký cấu hình của mình thay vì phần dùng chung tham chiếu tới nó.
- Sau khi sửa, thêm quy tắc ArchUnit tương ứng để chặn tái phát (BND-05).

Giới hạn: `jdeps` không thấy Spring bean wiring, reflection hay phân quyền runtime; `--ignore-missing-deps` không phải kết luận "sạch". / `jdeps` cannot see bean wiring, reflection or runtime authorization; `--ignore-missing-deps` is not an all-clear.

**CI checkpoint:** [Actions run 42866668592](https://github.com/tricore-opentrix/opentrix/actions/runs/42866668592) — `push` tại đúng SHA, 5/5 job PASS (`backend`, `portal-bff`, `frontend`, `r23-compliance`, `repo-hygiene`). Bước *Upload test reports* của backend bị `skipped`, nên chỉ ghi được `CI_BUILD_PASS_AT_BASELINE`. Việc test PostgreSQL Golden Path có bị skip trong CI hay không thuộc Khối B.

## 5. ADR, hợp đồng API, định danh và bảo mật / ADR, API contracts, identity and security

| ID | Quan sát / Finding | Trạng thái / Status | Priority |
|---|---|---|---|
| ADR-01 | `ADR-007` chọn **MinIO** cho object storage, adapter runtime chờ nghiệm thu; xung đột với hướng SeaweedFS của nhóm | `OBSERVED_SOURCE` · `BLOCKED` | P0 (quyết định) |
| ADR-02 | `ADR-008` chọn **Apache Superset**; triển khai, nhúng, tenant chưa kiểm; nhóm từng cân nhắc Metabase | `OBSERVED_SOURCE` | P2 |
| ADR-03 | Nhiều tài liệu thiết kế ghi `PROPOSED / REVIEW REQUIRED`; không coi là đã hiện thực | `OBSERVED_SOURCE` | — |
| ADR-04 | PR #159, #160, #165 **đã đóng, không merge** — chỉ là tham chiếu thiết kế lịch sử | `OBSERVED_METADATA` | — |
| API-01 | `HelpdeskController` có **chín** thao tác tại `/api/v1/mvp/requests`, chỉ đăng ký khi `dxos.helpdesk.enabled=true` | `OBSERVED_SOURCE` | — |
| API-02 | Health GET và proxy BFF có trong mã; Workflow controller chung cố ý không đăng ký | `OBSERVED_SOURCE` | — |
| API-03 | Không có file OpenAPI YAML/JSON trong tree; chưa có spec công bố (theo dõi ở #112, Khối C) | `MISSING` (spec công bố) | P1 |
| SEC-01 | Backend là OAuth2 JWT Resource Server stateless, kiểm issuer, thời gian, audience, subject, token type; chỉ health là anonymous | `OBSERVED_SOURCE` | — |
| SEC-02 | `SpringSecurityCurrentPrincipal` lấy principal từ JWT đã xác thực, chuẩn hóa issuer+subject | `OBSERVED_SOURCE` | — |
| SEC-03 | `WorkflowGatewayPrincipalGate` kiểm ở mức thao tác, **chưa** có ACL theo tenant/tài nguyên; ACL V3 chưa đạt | `PARTIAL` | P1 |
| SEC-04 | BFF: OIDC Code + PKCE, session phía server, CSRF, Bearer forwarding tới route allowlist | `PARTIAL` (chưa E2E thật) | P1 |

## 6. Đối chiếu đề thi và tiêu chí PoF / Competition requirements and PoF mapping

### 6.1 Yêu cầu bắt buộc của đề / Mandatory requirements

Nguồn: Đề thi PMNM OLP 2026, mục 3 "Mục đích yêu cầu đề thi". Đề liệt kê bốn dịch vụ lõi bắt buộc (Identity/SSO, API Gateway, dữ liệu cấu trúc/phi cấu trúc, Workflow), yêu cầu lõi không cung cấp UI, và ít nhất một ứng dụng minh họa ở Tầng 2. Bảng công nghệ ở mục 4 (APISIX, Flowable, MinIO…) chỉ là giải pháp tham chiếu; đề ghi các đội có toàn quyền chọn công nghệ. / Source: competition brief, section 3. Section 4's technology table is a reference solution only.

| Yêu cầu / Requirement | Nguồn / Source | Hiện trạng tại SHA / As-is | Trạng thái / Status | Priority |
|---|---|---|---|---|
| Lõi Tầng 1 headless, không UI, hoạt động như PaaS | Đề thi mục 3 | Core không có UI. Theo hướng Modular Monolith, Helpdesk cùng deployable với core, nên ranh giới chỉ được bảo vệ bằng ArchUnit; hiện gateway gọi thẳng infrastructure (BND-01/02) | `PARTIAL` | P0 |
| Định danh bảo mật (Identity/SSO) | Đề thi mục 3 | Keycloak + JWT Resource Server + BFF OIDC/PKCE trong mã; chưa có bằng chứng chạy thật tại SHA | `PARTIAL` | P1 |
| Cổng API (API Gateway) | Đề thi mục 3 (năng lực); APISIX chỉ ở bảng tham chiếu mục 4 | Không có gateway chuyên dụng (APISIX) tại SHA; định tuyến bằng controller Spring và allowlist BFF | `PARTIAL` | P0 (quyết định DEC-04) |
| Dữ liệu có cấu trúc | Đề thi mục 3 | PostgreSQL, JDBC, Flyway V1–V4 | `OBSERVED_SOURCE` | — |
| Dữ liệu phi cấu trúc | Đề thi mục 3 | Chỉ có port và bản in-memory cho test | `MISSING` | P0 |
| Động cơ luồng công việc (Workflow) | Đề thi mục 3 | `WorkflowRuntime` tự viết với port persistence đang có trong mã. Flowable là đích đã chốt (mục 7), chưa có trong mã | `OBSERVED_SOURCE` (engine hiện tại) · `DESIGNED_ONLY` (Flowable) | P1 |
| Ít nhất một ứng dụng Tầng 2 có giao diện | Đề thi mục 3 | Helpdesk: React Portal + BFF + backend; E2E thật chưa xác lập (Khối C, #118) | `PARTIAL` | P1 |

### 6.2 Sáu tiêu chí PoF (50 điểm, chấm trước chung kết) / Six PoF criteria

Nguồn: Thể lệ OLP PMNM 2026, bảng "Các tiêu chí chấm điểm", nhóm I (tiêu chí 1–6). Cột "Điểm trừ liên quan" chép ý các dòng trừ điểm trong bảng đó. / Source: OLP PMNM 2026 rules, scoring table, group I (criteria 1–6).

| # | Tiêu chí / Criterion | Điểm trừ liên quan / Relevant deductions (Thể lệ) | Hiện trạng / As-is | Trạng thái / Status | Việc cần làm / Action | Priority |
|---|---|---|---|---|---|---|
| 1 | Quản lý mã nguồn trên Internet (5) | Không có web viewer −3; không truy cập mở −3; không thực sự sử dụng −5 | Repo GitHub công khai, có web viewer, đang dùng thực tế | `OBSERVED_METADATA` | — | — |
| 2 | Giấy phép OSI-approved (10) | Không ghi giấy phép trong từng tệp −5; giấy phép không tương thích −5; không có thông báo mục đích giấy phép −5; không có bản sao toàn văn −5 | Tại SHA có `LICENSE`, `LICENSES/Apache-2.0.txt`, `NOTICE`, `REUSE.toml`. Job `repo-hygiene` chạy `fsfe/reuse-action@v5` (REUSE lint toàn repo) và PASS tại baseline (run 42866668592). Job `r23-compliance` chạy canary từ chối giấy phép, sinh SBOM CycloneDX cho backend, BFF, frontend, kiểm giấy phép và đối chiếu `THIRD-PARTY-NOTICES.md` | `CI_BUILD_PASS_AT_BASELINE` | Giữ gate; Khối C đổi `NOASSERTION` để thống nhất người giữ bản quyền | — |
| 3 | Có bản release (5) | Không có phát hành −5; không phát hành theo phiên bản −3; dùng định dạng không mở (zip, rar, arj…) −3. Thể lệ ghi bản release đầu tiên phải tạo trước thời điểm nộp bài | Có một tag `v0.1.0` (`98530b9`, 2026-11-04). Release công bố "DX-OS Open-Core v0.1.0 — MVP Pre-release" là **Pre-release**, đính kèm `dxos-open-core-0.1.0.tar.gz` (563 495 byte, sha256 `32d8ae81…a5be710`) và `SHA256SUMS`. Có thêm một bản **Draft** trùng tag. GitHub luôn tự sinh thêm "Source code (zip)" | `OBSERVED_METADATA` | Yêu cầu "ít nhất một release có phiên bản, định dạng mở" đã có. Còn: release dự thi từ mã mới (version mới, nên là bản chính thức), đính kèm `.tar.gz`, `SHA256SUMS` và SBOM; dọn bản Draft trùng; ghi chú phát hành chỉ rõ tệp `.tar.gz`. Tên tệp vẫn là `dxos-open-core`, cần thống nhất với tên OpenTrix | P1 |
| 4 | Build từ mã nguồn (10) | Không có hướng dẫn −5; cấu hình bằng sửa tay −5; không cấu hình được trước khi dịch −5; dịch bằng công cụ nguồn đóng −5; không chạy được ngoài thư mục mã nguồn −5 | Backend có Gradle wrapper (CI kiểm bằng `wrapper-validation`). `portal-bff` không có wrapper riêng; job CI `portal-bff` ghi rõ "uses the backend Gradle wrapper" và chạy `./backend/gradlew -p portal-bff build` — xem HYG-01. Compose một lệnh chưa xác minh | `PARTIAL` | Xác nhận README hướng dẫn đúng lệnh `backend/gradlew -p portal-bff`; Khối B chạy build sạch theo README trên máy mới | P1 |
| 5 | Thư viện và gói đính kèm (10) | Không dùng thư viện sẵn có −5; phát hành kèm gói của dự án khác −5; mã gói đính kèm bị sửa −5. Yêu cầu có thông tin làm rõ thư viện sử dụng | Có `package-lock.json`, khai báo Gradle; `THIRD-PARTY-NOTICES.md` được track và CI đối chiếu với dependency đã resolve; SBOM CycloneDX cho ba thành phần được sinh trong CI nhưng chỉ lưu dạng artifact 30 ngày | `CI_BUILD_PASS_AT_BASELINE` | Đính kèm SBOM vào release dự thi để bằng chứng không hết hạn trước ngày chấm; xác nhận không vendor/sửa thư viện | P1 |
| 6 | Tài liệu và giao tiếp (10) | Không có bug tracker −5; không có changelog −5; không có readme và hướng dẫn −5 | Có README, CHANGELOG, Issues làm bug tracker (21 issue mở ngày 11/11); nhiều link hỏng và mô tả lỗi thời (mục 8) | `PARTIAL` | Sửa DOC-001, DOC-002, DOC-004 | P1 |

Mức ưu tiên ở bảng trên theo thang ở mục 2.2 ("làm mất điểm PoF" là P0). Bảo đã đồng ý thang này trên [#182](https://github.com/tricore-opentrix/opentrix/issues/182#issuecomment-6783205953); chờ Ánh. / Priorities follow the 2.2 scale; agreed by Bảo on #182, pending Ánh.

**Hạn nộp:** **17:00 Chủ Nhật 06/12/2026** (đề thi in nhầm năm 2025; owner xác nhận ngày 2026-11-11). Release dự thi (PoF mục 3) phải được tạo trước mốc này; từ baseline còn khoảng 25 ngày. / Submission deadline: **17:00 Sunday 06/12/2026** (the brief misprints 2025; confirmed by the owner on 2026-11-11). The competition release must exist before this time.

## 7. Quyết định kiến trúc đích / Architecture target decisions

### 7.1 Quyết định nhóm đã chốt (chưa có ADR merge trong `main`) / Team-decided targets (no merged ADR in `main`)

Trạng thái `TEAM_DECIDED — ADR_NOT_MERGED`: nhóm đã thống nhất, Yến xác nhận ngày 2026-11-11, nhưng chưa có ADR được review và merge. Không dòng nào dưới đây là bằng chứng mã đã hiện thực. / The team has agreed (confirmed by Yến on 2026-11-11), but no reviewed ADR is merged yet. Nothing below is evidence of implementation.

**Nguồn ghi nhận quyết định / Decision record:** `DEFERRED` — chưa có văn bản ghi nhận; sẽ được lập trong giai đoạn ADR (DEC-01). Cho tới khi đó, các dòng dưới đây chỉ có giá trị là xác nhận của owner. / No written record yet; to be created in the ADR phase (DEC-01). Until then, rows below rest on the owner's confirmation only.

| Lĩnh vực / Domain | Quyết định đã chốt / Decided target | Hiện trạng tại SHA / As-is at SHA | Khoảng cách / Gap |
|---|---|---|---|
| Backend | Spring Boot **Modular Monolith** | Một project `dxos-backend` (BND-06) | Khớp topology; ranh giới module chưa cưỡng chế đủ (BND-01/02/05) |
| Workflow | **Flowable** engine | `WorkflowRuntime` tự viết + `WorkflowPersistencePort` | Cần ADR chuyển đổi, migration dữ liệu và regression test cho Golden Path |
| Application modules | **Hybrid manifest-driven** | `application.helpdesk` trống; nghiệp vụ ở `infrastructure.workflow` | Chưa có manifest hay cơ chế đăng ký module |
| Dữ liệu / Data ownership | **Shared database, module-owned schemas** | PostgreSQL, Flyway V1–V4 | Cần bằng chứng schema/role theo module, không chỉ cấu trúc thư mục |
| Hợp đồng / Contracts | **Dual contract + capability-driven**: Java interface nội bộ, HTTP/OpenAPI bên ngoài | Chưa có OpenAPI công bố (API-03) | Thiếu hợp đồng ngoài đã công bố |
| Ranh giới module / Module boundary | **Strict public module APIs + ArchUnit** | ArchUnit chỉ cho Core (BND-05) | Thiếu quy tắc Application/Gateway |
| Quản trị hợp đồng / Contract governance | **Documentation + CI** | Chưa có kiểm tra tương thích hợp đồng trong CI | Thiếu gate CI |
| Identity | **Keycloak**, chuyển đổi tenant/permission | JWT Resource Server, BFF OIDC; ACL V3 chưa đạt (SEC-03) | Thiếu mô hình tenant/permission đã nghiệm thu |
| Internal module APIs | **Java interfaces** | Có port ở Core (BND-03) | Chưa có cho Application |
| Object storage | **S3-compatible API**; provider chưa cố định chỉ bởi giao thức | Chỉ có port + in-memory | Thiếu adapter; provider chờ DEC-03 |

**Lịch sử / History:** đề xuất ngày 2026-11-05 (R27) tách hai service (`core-service` + `helpdesk-service`) và dùng engine tự viết trước, Flowable sau, nay **đã được thay thế** bởi các quyết định trên. Giữ làm tham chiếu lịch sử, không còn là phương án ngang hàng. / The 2026-11-05 R27 two-service / in-house-engine proposal is **superseded** and kept as history only.

### 7.2 Rủi ro của quyết định đã chốt / Risks of the decided targets

| ID | Rủi ro / Risk | Hệ quả / Consequence | Priority |
|---|---|---|---|
| RISK-01 | Đề yêu cầu lõi Tầng 1 headless tách khỏi ứng dụng Tầng 2. Trong một deployable, ranh giới này chỉ được bảo vệ bằng quy tắc module và ArchUnit | Nếu BND-01/02 chưa sửa và ArchUnit chưa phủ Application/Gateway, giám khảo khó thấy ranh giới lõi/ứng dụng | P0 |
| RISK-02 | Chuyển từ engine tự viết sang Flowable khi còn khoảng 25 ngày tới hạn nộp | Có thể làm hỏng Golden Path đang có test; ADR phải nói rõ Flowable là điều kiện của bản dự thi hay đích sau dự thi | P0 (quyết định phạm vi) |
| RISK-03 | `portal-bff` đã là deployable riêng trên thực tế | Mô tả "một deployable" phải nói rõ backend, không phải toàn hệ thống | P2 |

### 7.3 Quyết định còn treo và người quyết đề xuất / Pending decisions and proposed deciders

| ID | Quyết định / Decision | Người quyết đề xuất / Proposed decider | Reviewer | Priority |
|---|---|---|---|---|
| DEC-01 | Ghi các quyết định 7.1 thành ADR và merge vào `main` | Yến | Bảo, Ánh | P0 |
| DEC-02 | Phạm vi Flowable cho bản dự thi (RISK-02): bắt buộc trước hạn nộp hay sau | Yến | Bảo | P0 |
| DEC-03 | Object storage provider: cập nhật ADR-007 MinIO → SeaweedFS hay giữ | Bảo | Yến | P0 |
| DEC-04 | API Gateway: triển khai APISIX hay dùng năng lực gateway hiện có | Yến | Bảo | P0 |
| DEC-05 | BI: Superset (ADR-008) hay Metabase | Ánh | Yến | P2 |

## 8. Tài liệu so với mã hiện tại / Documentation versus current code

Kiểm tĩnh **15 file Markdown chính**, **67 lần xuất hiện link tương đối**; **28 lần** trỏ tới đường dẫn không có trong tree tại SHA (là số lần xuất hiện, không phải 28 file đích khác nhau). Link ngoài, anchor và toàn bộ Markdown chưa được kiểm.

| ID | Sai lệch / Drift | Owner | Trạng thái / Status | Priority |
|---|---|---|---|---|
| DOC-001 | `docs/README.md` trỏ tới index không tồn tại: `docs/architecture/`, `docs/contracts/`, `docs/evidence/`, `docs/poc/` | Yến | `OBSERVED_SOURCE` | P1 |
| DOC-002 | `dependency-rules.md` §9 vẫn ghi chưa có ArchUnit, trong khi `build.gradle` đã pin ArchUnit và có test Core | Yến | `OBSERVED_SOURCE` | P1 |
| DOC-003 | `frontend/README.md` ghi HTTP transport bị chặn, trong khi đã có `sameOriginTransport.ts`, `HelpdeskApiClient.ts` | Ánh | `PARTIAL` | P1 |
| DOC-004 | `system-architecture`, `core-application-boundary`, `identity-architecture`, `gateway-architecture` dựa trên SHA/PR cũ | Yến | `OBSERVED_SOURCE` | P1 |
| DOC-005 | Nhiều thư mục `docs/` chỉ là placeholder | Yến | `OBSERVED_SOURCE` | P2 |
| DOC-006 | Mô tả ownership, provider, bảo mật workflow chồng chéo giữa nhiều tài liệu | Yến | `PARTIAL` | P2 |
| DOC-007 | README và tài liệu R24 mô tả v0.1.0 lịch sử, v0.2.0 dự kiến; chưa có sổ theo dõi release hiện tại | Bảo | `PARTIAL` | P1 |
| DOC-008 | Flowable, APISIX, MinIO/SeaweedFS, Facility E2E, Superset được mô tả là đích, chưa nghiệm thu | Owner từng capability | `DESIGNED_ONLY` | P1 |
| DOC-009 | Chưa kiểm toàn bộ link, anchor, URL ngoài | Yến | `UNKNOWN` | P2 |

Ví dụ link hỏng: `docs/00-project/scope-and-mvp.md` → `docs/contracts/{workflow-core,identity-core,data-core}.md`; `system-architecture.md` → `docs/architecture/*`, `docs/contracts/*`; `frontend/README.md` → `docs/application/issue39-mvp-readiness-20261027.md`.

## 9. Vệ sinh repo quan sát được / Observed repository hygiene

Quan sát ngày 2026-11-11 qua `git status --short` trong bản clone làm việc; HYG-01 được đối chiếu thêm với `main` bằng `git ls-files`:

| ID | Quan sát / Observation | Rủi ro / Risk | Priority |
|---|---|---|---|
| HYG-01 | `main` không có wrapper riêng cho `portal-bff` (`git ls-files portal-bff` chỉ có `build.gradle`, `settings.gradle`). Đây là thiết kế có chủ đích: job CI `portal-bff` và `r23-compliance` đều build BFF bằng wrapper backend (`./backend/gradlew -p portal-bff`). Bản clone làm việc từng có một wrapper BFF **untracked** dùng Gradle 9.6.0 (đã xóa ngày 2026-11-11) | Không commit wrapper riêng cho BFF. README phải ghi rõ cách build BFF bằng wrapper backend | P2 |
| HYG-02 | Thư mục audit, `R27_Step2_*.zip` và file `*-deps.txt` nằm trong thư mục gốc repo | Dễ bị commit nhầm bằng `git add .`; `.zip` là định dạng bị trừ điểm | P2 |

### 9.1 Kiểm kê nhánh và PR (P2-GOV-03) / Branch and PR inventory

Snapshot `2026-11-11T00:41Z` sau `git fetch --prune origin` và `gh pr list --state open`. Không dùng lại số liệu của #171/#172. / Fresh snapshot; #171/#172 figures are not reused.

**Nhánh remote / Remote branches** (`origin/HEAD` → `main`)

| Nhánh / Branch | Commit cuối / Last commit | PR mở / Open PR | Ghi chú / Note |
|---|---|---|---|
| `main` | 2026-11-10 | — | Baseline `832c75f` |
| `gh-pages` | 2026-11-11 | — | Nhánh xuất bản trang tĩnh / static site publishing |
| `docs/portal-phase2-block-c` | 2026-11-11 | [#187](https://github.com/tricore-opentrix/opentrix/pull/187) (Ánh) | Báo cáo Khối C |
| `docs/infra-phase2-audit-template` | 2026-11-11 | [#186](https://github.com/tricore-opentrix/opentrix/pull/186) (Yến, **draft**) | Template báo cáo Phase 2 |
| `docs/infra-r21-compose-plan` | 2026-11-05 | **không có / none** | Nhánh mồ côi / orphan branch |

`fetch --prune` gỡ 5 ref đã bị xóa phía remote: `docs/r16-mobile-reflow`, `docs/r31-112-helpdesk-api-crosswalk`, `feature/r29-typed-usecase-contract-20261107`, `feature/r33-bff-transport-integration-20261107`, `revert/pr-158`. / Five stale remote-tracking refs removed.

| ID | Quan sát / Observation | Hệ quả / Implication | Trạng thái / Status | Priority | Owner | Reviewer |
|---|---|---|---|---|---|---|
| GOV-01 | Chỉ còn 5 nhánh remote, 2 PR mở; các nhánh R16, R29, R31, R33 và revert PR #158 đã bị xóa | Việc dọn nhánh theo #171 có hiệu lực; repo gọn | `OBSERVED_METADATA` | — | — | — |
| GOV-02 | `docs/infra-r21-compose-plan` không có PR mở, commit cuối 2026-11-05 | Nhánh mồ côi: hoặc mở PR, hoặc lưu kết quả vào issue rồi xóa nhánh | `OBSERVED_METADATA` | P2 | Yến | Bảo |
| GOV-03 | Template báo cáo Phase 2 nằm ở PR [#186](https://github.com/tricore-opentrix/opentrix/pull/186) còn **draft**, chưa có trong `main`; #183 yêu cầu báo cáo "dùng template trong cùng thư mục" | Báo cáo các khối chưa đối chiếu được với một template đã nghiệm thu; nên merge #186 trước hoặc cùng lúc với các PR báo cáo | `OBSERVED_METADATA` | P1 | Yến | Bảo |
| GOV-04 | Tại thời điểm snapshot chưa có nhánh remote nào cho báo cáo Khối A và Khối B. Sau snapshot, Khối A đã có nhánh `docs/arch-phase2-block-a` và PR chứa chính báo cáo này | Khối A: đã xử lý. Khối B: chưa có sản phẩm để hợp nhất | `OBSERVED_METADATA` | P1 | Bảo (B) | Yến (B) |
| GOV-05 | Các nhánh nguồn của PR đã đóng #145 (R29), #156 (R33) đã bị xóa; báo cáo Khối C vẫn dẫn permalink tới SHA `5d577dd`, `181e559` | Commit của PR đã đóng vẫn truy cập được qua PR trên GitHub, nên permalink chưa hỏng; nên dẫn kèm số PR để giữ truy vết | `OBSERVED_METADATA` | P3 | Ánh | Yến |

## 10. Phát hiện tổng hợp và phân luồng rủi ro / Consolidated findings and risk routing

| Finding | Priority | Owner | Reviewer | Điều kiện đóng / Acceptance |
|---|---|---|---|---|
| DEC-01, DEC-02: ghi ADR cho quyết định đã chốt; chốt phạm vi Flowable | P0 | Yến | Bảo | ADR được Bảo và Ánh review, merge vào `main` |
| RISK-01: ranh giới headless trong Modular Monolith | P0 | Bảo | Yến | BND-01/02 được sửa; ArchUnit phủ Application/Gateway |
| ADR-01 / DEC-03, adapter storage `MISSING` và BND-09 | P0 | Bảo | Yến | ADR cập nhật; adapter S3 có contract test với provider thật; có ít nhất một use case dùng `core.data` |
| DEC-04: năng lực API Gateway | P0 | Yến | Bảo | Quyết định ghi trong ADR; nếu dùng APISIX thì có route chạy thật |
| PoF 3 và DOC-007: release dự thi (đã có `v0.1.0` pre-release kèm `.tar.gz`) | P1 | Bảo | Yến | Release từ mã mới, có version mới, `.tar.gz`, `SHA256SUMS` và SBOM đính kèm; ghi chú phát hành; dọn Draft trùng của `v0.1.0`; sổ theo dõi release trong README |
| PoF 4 và HYG-01: build từ mã nguồn | P1 | Bảo | Yến | README ghi đúng lệnh build cả backend và BFF; build sạch trên máy mới |
| BND-01/02: Helpdesk ghép với infrastructure | P1 | Bảo | Yến | Use case và view model ở `application.helpdesk`; giữ tính nguyên tử; có review |
| BND-08: vòng phụ thuộc giữa module gateway Helpdesk và Workflow | P1 | Bảo | Yến | Phần dùng chung không tham chiếu DTO Helpdesk; xử lý lỗi dùng chung ra khỏi package controller |
| BND-05/10: ArchUnit mới phủ Core; gateway gọi thẳng `WorkflowRuntime` | P1 | Yến | Bảo | Quy tắc ArchUnit cho Application/Gateway chặn BND-01, BND-08 và cạnh tới `WorkflowRuntime`; Core công bố danh sách type công khai |
| SEC-03, SEC-04: ACL tenant và E2E bảo mật | P1 | Bảo | Yến | Negative test 401/403/scoped-404 và CSRF có log |
| API-03: chưa có OpenAPI công bố | P1 | Ánh | Yến | Theo #112 |
| DOC-001/002/004 | P1 | Yến | Bảo | Link đúng, nội dung khớp baseline |
| GOV-03: template #186 chưa merge | P1 | Yến | Bảo | #186 chuyển ready và merge |
| GOV-04: Khối B chưa có PR | P1 | Bảo | Yến | Khối B có PR báo cáo theo template |
| GOV-02: nhánh mồ côi `docs/infra-r21-compose-plan` | P2 | Yến | Bảo | Mở PR hoặc ghi kết quả vào issue rồi xóa nhánh |

## 11. Việc còn lại và bàn giao review / Pending work and review handoff

- [x] Ghi JDK/Gradle version và ma trận layer→layer mức package (mục 4.1).
- [x] Lấy tên class cho BND-01, BND-08 từ `backend-class-deps.txt`.
- [x] Trích mức class cho BND-10; chạy `jdeps` cho `portal-bff` (BND-11).
- [x] Đính kèm 4 file output `jdeps` vào [#183](https://github.com/tricore-opentrix/opentrix/issues/183#issuecomment-6783378923).
- [x] Kiểm kê nhánh và PR tại snapshot 2026-11-11 (mục 9.1, P2-GOV-03).
- [x] Mở PR báo cáo Khối A từ nhánh `docs/arch-phase2-block-a` (`Refs #183`; #183 chỉ đóng sau bước hợp nhất).
- [ ] Lập văn bản ghi nhận quyết định ở mục 7.1 — hoãn sang giai đoạn ADR (DEC-01).
- [ ] Chép bộ từ vựng và thang ưu tiên (mục 2) vào #182 sau khi Ánh đồng ý (Bảo đã đồng ý: [#182](https://github.com/tricore-opentrix/opentrix/issues/182#issuecomment-6783205953)).
- [ ] Mở ADR cho DEC-01 đến DEC-04; không thay đổi ADR-007 hồi tố.
- [x] Kiểm file giấy phép, job `r23-compliance` và `repo-hygiene`, tag và release (mục 6.2).
- [x] Kiểm tệp đính kèm của release `v0.1.0`; xác nhận job `portal-bff` trong CI build BFF bằng wrapper backend.
- [x] Xác nhận hạn nộp: 17:00 Chủ Nhật 06/12/2026.
- [ ] Review độc lập Khối B (Bảo) và Khối C ([PR #187](https://github.com/tricore-opentrix/opentrix/pull/187), Ánh).
- [ ] Gộp một danh sách rủi ro đã khử trùng vào #182; chỉ đánh dấu #183 hoàn tất sau khi có sign-off của reviewer.
- [ ] Sửa tham chiếu #159, #160, #165 trong #182 thành "đã đóng, không merge, chỉ là thiết kế lịch sử" (cần đồng ý trước khi sửa).

**Hạn đóng pha audit đề xuất:** hết ngày **2026-11-12**. Sau mốc này #182 chỉ còn danh sách rủi ro đã gộp và nhóm chuyển sang xử lý các mục P0. / Proposed audit close: end of 2026-11-12, then the team moves to P0 work.

**Yêu cầu review / Review request:**

- **Bảo:** kiểm ranh giới module, quyền sở hữu transaction, các tuyên bố về CI/runtime, phương án 7.2 và các mức P0.
- **Ánh:** kiểm các tuyên bố về frontend/BFF/tài liệu, kết quả link hỏng và owner ở mục 8.

Mỗi nhận xét ghi mức `BLOCKER`, `MAJOR`, `MINOR` hoặc `SUGGESTION`, kèm đường dẫn và bằng chứng cụ thể.

## 12. Kết luận audit / Audit verdict

| Bước / Step | Kết quả / Result |
|---|---|
| 1 — Kiểm kê mã nguồn | `PARTIAL` — tree và entry point tại SHA đã xem; chưa chạy kiểm chứng đầy đủ |
| 2 — Ranh giới Core/Application | `PARTIAL` — `CI_BUILD_PASS_AT_BASELINE` cho ArchUnit Core; `jdeps` mức package và class hoàn tất cho backend, mức package cho `portal-bff`; chưa đối chiếu từng cạnh với văn bản DR-01–DR-16 |
| 3 — ADR/API/Identity/Security | `PARTIAL` — mã và metadata đã lấy mẫu; chưa chạy lại kiểm thử bảo mật runtime |
| 4 — Tài liệu và mã | `PARTIAL` — đã chứng minh sai lệch lớn và link hỏng; chưa quét toàn bộ |
| 5 — Đề thi/PoF/hợp nhất | `PARTIAL` — đã map yêu cầu đề và 6 tiêu chí PoF; chờ Khối B, C để hợp nhất |

**Trạng thái cuối / Final status:** `AUDIT_IN_PROGRESS — NO ACCEPTANCE / NO RIGHTS_CLEARANCE / NO RELEASE_AUTHORIZATION`

## 13. Nguồn chính / Primary source pointers

Tiền tố / Base prefix: `https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/`

- `backend/settings.gradle`, `backend/build.gradle`, `backend/src/main/java/com/tricore/dxos/DxosApplication.java`
- `backend/src/main/java/com/tricore/dxos/core/workflow/{WorkflowRuntime,WorkflowPersistencePort}.java`
- `backend/src/main/java/com/tricore/dxos/infrastructure/workflow/{PostgresWorkflowPersistence,HelpdeskService,HelpdeskConfiguration}.java`
- `backend/src/main/java/com/tricore/dxos/gateway/helpdesk/HelpdeskController.java`, `gateway/workflow/controller/WorkflowController.java`
- `backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/{SecurityConfig,SpringSecurityCurrentPrincipal}.java`
- `backend/src/test/java/com/tricore/dxos/architecture/CoreDependencyRulesTest.java`
- `portal-bff/src/main/java/com/tricore/dxos/portal/{PortalSecurity,PortalBackendClient,PortalSessionController}.java`
- `frontend/package.json`, `frontend/src/services/mvp/http/{HelpdeskApiClient,sameOriginTransport}.ts`
- `docs/01-architecture/{system-architecture,dependency-rules,core-application-boundary}.md`
- `docs/02-core/{identity/identity-architecture,gateway/gateway-architecture,data/data-architecture}.md`
- `docs/08-decisions/{ADR-007-data-storage,ADR-008-dashboard-tool}.md`
- [GitHub Actions run tại SHA / exact-SHA CI run](https://github.com/tricore-opentrix/opentrix/actions/runs/42866668592)
- Đề thi PMNM OLP 2026 (mục 3–5) và Thể lệ OLP PMNM 2026 (bảng tiêu chí PoF)
