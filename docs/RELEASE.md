<!--

SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0

-->

# Phát hành / Release

**Điều hướng / Navigation:** [Tài liệu](README.md) · [Development](DEVELOPMENT.md) · [Deployment](DEPLOYMENT.md) · [Release](RELEASE.md) · **Ngôn ngữ / Language:** [Tiếng Việt](#vi) | [English](#en)

> **Lịch sử tài liệu / Document history:** merged in #203, R23/R24/R26 added in #210; 16/11/2026 review update is **PROPOSED / NOT MERGED** · **Owner:** @lexuanbao258-collab · **Refs:** [#194](https://github.com/tricore-opentrix/opentrix/issues/194), [#197](https://github.com/tricore-opentrix/opentrix/issues/197), [#190](https://github.com/tricore-opentrix/opentrix/issues/190)

>
> **Baseline kỹ thuật / Technical baseline:** `main@e31497f364cc7e9d3cee03ee59b9e48db524ea77` (R24 scripts/workflow và CHANGELOG đã đối chiếu ngày 12/11/2026; **HISTORICAL**, không phải source freeze hiện tại). **Cập nhật bằng chứng / Evidence update: 16/11/2026:** #138 có quyết định nội bộ Q1–Q5 được ba maintainer xác nhận; R24 validation-only tái lập 3/3 tại `ac36d01091a42b7d4d82fbf2fb4f822014e98998`; B3 Golden Path integration-local 6/6 tại `8903c2ae85440cbc5365f5f0fc35e8c91940959c`. Các SHA phục vụ mục tiêu khác nhau, không được hoán đổi. / Separate SHA-bound rights, reproducibility, and demo evidence; none authorizes publication.

[Docs index](README.md) · [Open source and compliance](OPEN_SOURCE.md) · [Development](DEVELOPMENT.md) · [R24 canonical technical runbook](06-deployment/r24-release.md) · [R24 workflow](../.github/workflows/release.yml)

<a id="vi"></a>

## Tiếng Việt

### 1. Trạng thái bản phát hành (AS-IS / UNVERIFIED)

#### Bảng trạng thái tính năng / Feature status matrix (AS-IS / UNVERIFIED / PROPOSED)

| Thành phần | Nguồn có sẵn | Xác minh / giới hạn |
| --- | --- | --- |
| Identity / Keycloak | Backend [OIDC](../backend/src/main/resources/application.yml), BFF [OAuth client](../portal-bff/src/main/resources/application.yml) | **INTEGRATION-LOCAL VERIFIED** cùng Golden Path B3 ở `8903c2` với ba tài khoản demo; **production LIVE E2E / #118** vẫn chưa được xác nhận cho mọi SHA ([#225](https://github.com/tricore-opentrix/opentrix/issues/225)) |
| Workflow Core | `WorkflowRuntime`, `WorkflowPersistencePort`, PostgreSQL adapter và test source ([Backend](../backend/README.md)) | **SOURCE IMPLEMENTED / TEST-LEVEL**; không chứng minh Flowable/E2E |
| Helpdesk | `/api/v1/mvp/requests` khi bật `dxos.helpdesk.enabled`, authorization/version test | **INTEGRATION-LOCAL B3: 6/6 PASS** với ba tài khoản trên Windows `main@8903c2` (14/11/2026); không suy ra production LIVE, SHA mới hoặc B4 demo-ready ([bằng chứng B3](https://github.com/tricore-opentrix/opentrix/issues/225#issuecomment-6874592663)) |
| Portal Frontend | [Frontend](../frontend/package.json): MOCK và build `integration-local` | MOCK dùng dữ liệu giả; build bundle chưa chứng minh kết nối runtime |
| Portal BFF | [BFF](../portal-bff/README.md): OAuth/PKCE, session, CSRF, fixture test | Có bằng chứng **integration-local Golden Path B3** trên exact `8903c2`, thông qua APISIX; chưa suy ra production LIVE hoặc lần chạy SHA khác |
| PostgreSQL / Flyway | [Compose](../infra/compose.workflow-postgres.yml), migration Workflow V1–V4/Helpdesk SQL | **SOURCE IMPLEMENTED**; schema/ACL/restart cùng SHA cần kiểm chứng |
| Docker Compose | `infra/compose.workflow-postgres.yml` (đường lịch sử), `compose.demo.yml` và `compose.gateway.yml` phục vụ demo | **DEMO STACK IMPLEMENTED / INTEGRATION-LOCAL B3 VERIFIED** tại `8903c2`; tổng duyệt B4 ở máy thi vẫn cần nghiệm thu ([#119](https://github.com/tricore-opentrix/opentrix/issues/119), [#225](https://github.com/tricore-opentrix/opentrix/issues/225)) |
| APISIX | `compose.gateway.yml`, `gateway-smoke.ps1`; luồng browser Helpdesk B3 qua APISIX | **INTEGRATION-LOCAL VERIFIED** tại `8903c2`; gateway smoke **6 PASS / 1 BLOCKED** (mục browser được kiểm thủ công, không nhận 7/7 tự động) ([#116](https://github.com/tricore-opentrix/opentrix/issues/116), [#225](https://github.com/tricore-opentrix/opentrix/issues/225)) |
| Flowable | Workflow Golden Path đang chạy engine `internal` (ADR-009) | **NOT SHIPPED / PROPOSED**, không gộp trạng thái với APISIX ([#191](https://github.com/tricore-opentrix/opentrix/issues/191)) |

SOURCE IMPLEMENTED = có mã; TEST-LEVEL = chỉ các ca được ghi; UNVERIFIED ≠ FAIL. Nguồn: [Block B](09-evidence/phase-2/block-b-backend-infra.md) / [Block C](09-evidence/phase-2/block-c-application.md).

**Bảng phiên bản / Version status** (snapshot GitHub Releases ngày 12/11/2026; cập nhật bằng chứng kỹ thuật và #138 ngày 16/11, không phải xác minh release mới):

| Version | Trạng thái | Phạm vi và bằng chứng |
| --- | --- | --- |
| [`v0.1.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) | **Released — pre-release**, không phải bản ổn định | GitHub Release công khai ngày **04/11/2026**, 2 assets khi kiểm tra; MVP theo [README gốc](../README.md), không suy ra LIVE E2E |
| `v0.2.0` | **In development / Not released** | SOURCE-ONLY là phạm vi dự kiến theo [R24](06-deployment/r24-release.md). #138 đã có đồng thuận Q1–Q5; **Q3 PR, exact-SHA publishable archive, acceptance JSON, protection và #190** vẫn phải hoàn tất. Hai CI + một local build 16/11 chỉ **validation-only** |
| `v0.3.0+` | **Planned / PROPOSED** | Không có tag/phạm vi/cam kết phát hành đã nghiệm thu; tính năng tương lai chưa được ship |
| Đối tượng | Trạng thái có thể công bố | Không được suy diễn |
| --- | --- | --- |
| [`v0.1.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) | Bản công khai **pre-release lịch sử**, không phải bản dự thi ổn định ([#190](https://github.com/tricore-opentrix/opentrix/issues/190)) | Không phải `RELEASE_ACCEPTED` của giai đoạn hiện tại |
| R23, SPDX/REUSE | Có kiểm tra license-policy/SBOM/notices và metadata trong [`ci.yml`](../.github/workflows/ci.yml); bằng chứng kiểm kê ở [Block B](09-evidence/phase-2/block-b-backend-infra.md) | CI xanh không chứng minh sở hữu bản quyền hoặc quyền phân phối |
| R24 candidate | [`release.yml`](../.github/workflows/release.yml) và [`r24-release.py`](../scripts/r24-release.py) có lệnh tạo/kiểm archive và fail-closed gate | Candidate PASS không tự cho phép publish |
| `v0.2.0` | **Mục tiêu SOURCE-ONLY, chưa được xác nhận phát hành**; #138 đã có Q1–Q5 đồng thuận nhưng còn Q3/điều kiện đóng Issue; [#190](https://github.com/tricore-opentrix/opentrix/issues/190) vẫn OPEN tại lần kiểm tra | Không được nói đã phát hành, đã thông quyền, hoặc cho phép JAR/`frontend/dist`/GHCR |

Quy ước: `AS-IS` = source/workflow đã đối chiếu; `HISTORICAL` = quan sát của lần trước; `UNVERIFIED` = thiếu bằng chứng nghiệm thu đúng SHA; `PROPOSED` = việc còn theo dõi bằng Issue. **Không dùng kết quả Phase 2 hoặc R23 làm phiếu chấp thuận phát hành R24.**

### 2. Phiên bản, đường kích hoạt và phạm vi package

- Tag hợp lệ theo workflow: `vMAJOR.MINOR.PATCH` hoặc `vMAJOR.MINOR.PATCH-rc.N` với `N ≥ 1`; phần release notes tương ứng phải tồn tại trong [`CHANGELOG.md`](../CHANGELOG.md). [#190](https://github.com/tricore-opentrix/opentrix/issues/190) yêu cầu **bản dự thi mới không đánh dấu pre-release**.

- `pull_request` chạm các tệp R24 được theo dõi hoặc `workflow_dispatch` tạo **candidate không publish**. Với những sự kiện này, workflow kiểm tra cả binary-validation candidate và source-only candidate; **không có job publish**.

- `push` tag `v*` mới có thể đi vào job publish **nếu** candidate PASS, tag commit là tổ tiên của `main`, acceptance JSON của đúng tag đã nằm trên `main` và environment/permission gates được phê duyệt. Không được tự push tag để thử.

- `v0.2.0` có kiểm soát riêng: **chỉ mode `source-only`** được qua cổng phân phối. Candidate binary chạy để đánh giá CI không đồng nghĩa có quyền phát hành binary.

| Phạm vi R24 | Nội dung archive | Giới hạn |
| --- | --- | --- |
| `source-only` (mục tiêu `v0.2.0`) | Mã nguồn được Git theo dõi đủ điều kiện UTF-8, LICENSE, NOTICE, THIRD-PARTY-NOTICES, CHANGELOG, RELEASE-NOTES, ba CycloneDX SBOM, inventory và MANIFEST | Không đóng gói bootJAR, frontend dist hoặc images; SBOM liệt kê phụ thuộc đã resolve **không có nghĩa** nhị phân được phân phối |
| `binary` (phạm vi **chưa được phép**) | Backend/BFF bootJAR, frontend dist, SBOM/inventory/notices, upstream license texts, MANIFEST và release notes | Phải qua đánh giá upstream, source/relink, asset, JRE/OCI và các nghĩa vụ license riêng |

Nguồn chuẩn chi tiết: [R24 runbook](06-deployment/r24-release.md), [packager](../scripts/r24-release.py), [workflow](../.github/workflows/release.yml).

### 3. Cổng kiểm thử, pháp lý và chấp thuận độc lập

1. **Build và compliance:** CI dùng Java 21/Node 22, R24 contract tests (`test_r24_*.py`), R23 inventory/notices, REUSE; ghi SHA và PASS/FAIL/SKIPPED thực tế. Không coi các test không chạy là PASS.

2. **Quyền nguồn gốc:** ba maintainer đã xác nhận Q1–Q5 trong [biên bản #138](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6899613976) cho **source-only `v0.2.0`** trong phạm vi quyền của từng người, có công khai giới hạn AI/upstream; chưa phải kiểm chứng nguyên gốc toàn repo hay R24 release acceptance. `reuse lint` và policy allowlist **không chứng minh quyền**. Xem §3.3.

3. **Đóng băng source SHA:** xác định exact Git commit và package hash; kiểm hai ứng viên độc lập trên **cùng source SHA** nếu đang làm xác nhận tính tái lập. Không dùng checksum của SHA khác.

4. **Acceptance riêng trên `main`:** sau khi đóng băng source, PR khác có reviewer độc lập phải đưa `docs/06-deployment/r24-acceptances/<tag>.json` lên `main`. JSON cần `tag`, `source_sha`, `mode`, `archive_sha256`, `reviewed_by` và **giữ nguyên 5 evidence categories SOURCE-ONLY hiện hành**. **Technical hardening PR (chờ review):** thêm `review_url` và `candidate_run_ids` gồm **hai run ID độc lập**; gate đối chiếu bytes JSON với PR HEAD đã duyệt, merge/main, kiểm GitHub evidence comments và **tải thực tế cả hai candidate artifacts** để đối chiếu SHA256/MANIFEST/SBOM/member bytes cùng frozen SHA. Các phần này không giảm yêu cầu hai candidates; không tự coi checklists là bằng chứng quyền nguồn. Xem [R24 runbook](06-deployment/r24-release.md).

5. **Bảo vệ phát hành:** xác minh GitHub Environment `r24-release` cùng reviewer bắt buộc và quy tắc bảo vệ tag trước khi tạo tag. **Khai báo `environment: r24-release` trong YAML không tự chứng minh thiết lập bảo vệ đã có**.

6. **Đối chiếu trước công bố:** hash archive, MANIFEST file checksums, SHA256SUMS, release notes trong archive với file ngoài, source SHA/tag/mode, bằng chứng #138 và quyết định của reviewer. Nếu thiếu/bất đồng, **BLOCKED**.

Không tự tạo tag, release, phát hành GHCR hay chạy migration chỉ vì tài liệu hoặc CI đã được cập nhật.

#### 3.1 R23: tái tạo SBOM/NOTICE và bàn giao phân phối

Từ root repository của source đã chọn, có Java 21, Node 22 và dependencies; các lệnh sau tạo output build/compliance, **không công bố release**. Quy trình và lịch sử đầy đủ được giữ tại [R23](06-deployment/r23-plan.md).

~~~sh

set -e

./backend/gradlew -p backend cyclonedxBom --no-daemon

./backend/gradlew -p portal-bff cyclonedxBom --no-daemon

(cd frontend && npm ci && npx --yes @cyclonedx/cyclonedx-npm@6.0.1 --omit dev --output-format JSON --output-file ../frontend-sbom.json)

python3 scripts/r23-compliance.py \
  --backend backend/build/reports/cyclonedx/bom.json \
  --portal-bff portal-bff/build/reports/cyclonedx/bom.json \
  --frontend frontend-sbom.json --output build/r23

diff -u THIRD-PARTY-NOTICES.md build/r23/THIRD-PARTY-NOTICES.md

python3 -m unittest discover -s scripts -p 'test_r23_*.py'

~~~

Kiểm inventory trước khi bàn giao:

- Backend/BFF dùng Gradle **runtime classpath**; frontend dùng dependency **production**. `--omit dev` phải loại `vitest`, `jsdom`, `typescript` và `@vitest/*`, trừ khi có bằng chứng chúng thực sự là runtime dependencies. Giữ MIT-0/BlueOak nếu có trong graph runtime.

- Lịch sử cleanup [#133](https://github.com/tricore-opentrix/opentrix/pull/133), SHA `84a7ca9e5b5f1012b95f676c86c2ec1d95dd3ea7`: JDBC thay starter JPA. Kiểm BOM mới không còn `hibernate-core`, `jakarta.persistence-api`, `antlr4-runtime`, `hibernate-commons-annotations`; `hibernate-validator` không phải Hibernate ORM. Exception LGPL cho Hibernate 6.6.53.Final đã được bỏ; đưa ORM trở lại cần review mới.

- Policy xử lý toàn bộ biểu thức SPDX, `AND`/`OR`/ngoặc và `WITH` đã review; unknown/malformed declarations, `WITH` không được chấp nhận hoặc version ngoài exception đã pin phải fail closed. Giữ negative-canary evidence; không nới allow-list để vượt lỗi.

- Ba BOM, `build/r23/license-inventory.json`, notices sinh lại, lệnh/exit codes và verdict review phải cùng exact HEAD. Đối chiếu notices tracked bằng `diff`; kiểm đủ `backend`, `portal-bff`, `frontend`, `r23-compliance`, `repo-hygiene` của chính HEAD. Lưu run/artifact IDs và kiểm artifact còn tải được; `r23-sbom-and-notices` có retention 30 ngày.

**R23 implementation Done** yêu cầu #133 và [#131](https://github.com/tricore-opentrix/opentrix/pull/131) đã merge, inventory đúng scope, notices khớp, independent review/CI đúng HEAD và handoff R24 được owner chấp nhận. Đây không phải yêu cầu một archive tương lai đã được phát hành. Bảo phụ trách automation và bàn giao BOM/notices, pending-obligations matrix, commands, CI artifact IDs; Yến điều phối compliance/distribution acceptance, Ánh co-review. `release_distribution_owner=R24 / Yến` không chuyển ownership coding của workflow.

`license_policy_status=APPROVED` không đổi `release_distribution_status=PENDING`. Notices sinh tự động là inventory, không thay LICENSE/NOTICE upstream hoặc chứng nhận quyền. Với **nội dung thực sự phân phối**, R24 phải review các nghĩa vụ sau:

| Phạm vi | Evidence/disposition cần giữ |
| --- | --- |
| Logback classic/core (baseline R23 1.5.34, lựa chọn EPL-2.0) | Lựa chọn điều khoản, upstream texts, attribution/provenance và source availability áp dụng |
| Hibernate ORM LGPL-2.1, chỉ nếu thực sự được phân phối trở lại | Linking/packaging, license/source hoặc offer và replacement/relink rights; không mang nghĩa vụ ORM cũ sang BOM đã xác minh vắng ORM |
| MIT-0, BlueOak-1.0.0 có trong runtime graph | Text/attribution hoặc license link hợp lệ theo điều khoản áp dụng; không suy coverage từ BOM dev-only cũ |
| Dependencies và frontend assets khác | License/NOTICE bytes, provenance, dual-license choice, source/source-offer khi áp dụng; đối chiếu bundle thực |
| Service/base images được phân phối riêng, kể cả Superset/Grafana nếu có | Inventory/SBOM, license texts, attestations và OCI obligations riêng, ngoài ba BOM Gradle/npm |

#### 3.2 R24: evidence theo mode và approval độc lập

Sau source freeze, acceptance PR phải merge riêng lên `main`; tag được phép phát hành sẽ trỏ **source SHA đã đóng băng trước đó**, không trỏ acceptance commit mới hơn, tránh circular self-reference. Kiểm acceptance PR/review và HTTPS evidence thực tế, không chỉ đọc assertion trong JSON.

| Mode | Evidence bổ sung cho các trường chung ở trên |
| --- | --- |
| `source-only` | `source_provenance`, `source_license`, `sbom_source_boundary`, `archive_and_checksums`, `release_notes`; binary license groups không cấp clearance cho mode này |
| `binary` — chưa được phép | `eclipse-temurin:21-jre@sha256:<digest>` đã pin; permissive group `CLEARED` kèm evidence, từng exception `CLEARED` cho license ngoài nhóm; source/relink, upstream texts, assets, JRE/OCI, checksum/notes evidence |

Collector `scripts/r24-upstream.py` lấy LICENSE/NOTICE từ Gradle-cache JAR và LICENSE/COPYING/NOTICE từ npm; supplements đã review ở `docs/06-deployment/r24-upstream/<project>/<name>-<version>/`. Bytes được giữ/hash trong `upstream-index.json`: tìm thấy là `COLLECTED_UNREVIEWED`, thiếu là `MISSING`; Maven `type=pom` chỉ là metadata, license identifier trong `package.json` không thay actual texts. Khi chuẩn bị binary-validation inputs cho review, dùng `python3 scripts/r24-upstream.py --root . --inventory build/r23/license-inventory.json --output build/r24/upstream`.

Permissive group được chấp nhận độc lập chỉ có thể gộp Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC và 0BSD; archive vẫn cần upstream bytes. EPL, GPL+Classpath, OFL, CC0 và license ngoài nhóm cần disposition/choice riêng theo inventory, gồm Logback/jakarta.annotation-api nếu shipped. Thiếu texts hoặc còn source/NOTICE/asset/JRE/OCI obligations chưa xử lý thì **BLOCKED**.

Yến phải xác minh Environment `r24-release` có independent reviewers Yến/Ánh và ruleset bảo vệ `v*` trước tag. **R24 implementation Done** là review, CI và merge; **source-only release Done** còn cần #138 clearance, exact-source acceptance/review trong **PR mới** (PR lịch sử [#139](https://github.com/tricore-opentrix/opentrix/pull/139) đã CLOSED), protection, publication được phép và hash assets tải về được kiểm độc lập. Không miễn nghĩa vụ binary/JAR/GHCR.

#### 3.3 #138: biên bản quyền đóng góp và giới hạn AI (16/11/2026)

- **Phạm vi quyết định:** [biên bản Q1–Q5](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6899613976), [Bảo xác nhận](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6907781691), [Ánh xác nhận](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6907788256), Yến là người đăng biên bản. Ba maintainer đồng ý xét phát hành **source-only `v0.2.0`** chỉ trong phạm vi những đóng góp/quyền họ có thể cấp phép Apache-2.0. Quyết định nội bộ **không** thay thế clearance của upstream hoặc quyền bên thứ ba.
- **Giới hạn công khai:** không có lịch sử từng prompt; không khẳng định output AI độc lập hoàn toàn với nguồn ngoài; nhóm báo cáo không cố ý sao chép; chưa so sánh chi tiết từng file với upstream. Giữ nguyên `UNKNOWN` / `NOT_RECALLED` / `RIGHTS_PENDING` đối với nội dung chưa xác minh; không tuyên bố toàn repository `CLEARED`.
- **Điều kiện tài liệu Q3:** PR riêng cập nhật song ngữ `CONTRIBUTING.md` (AI disclosure và xử lý báo cáo trùng nguồn trong 7 ngày), `docs/OPEN_SOURCE.md`, `docs/RELEASE.md`, cùng giấy phép demo images Keycloak/PostgreSQL/APISIX trong `NOTICE`. Chỉ ghi **MERGED** sau khi PR và reviews có bằng chứng.
- **Q4/Q6:** đối chiếu chi tiết file/upstream được theo dõi trong Issue mới thuộc `v1.0.0`; tự kiểm tra khoảng năm file rủi ro Q6 là **tùy chọn** và kết quả không tìm thấy trùng không chứng minh tính độc lập.
- **Điều kiện phát hành độc lập:** #138 disposition ≠ R24 gate PASS. `v0.2.0.json` phải được tạo trong PR acceptance riêng sau khi đóng băng source, gắn evidence năm khóa và reviewer thật, rồi qua environment/tag protections. PR lịch sử [#139](https://github.com/tricore-opentrix/opentrix/pull/139) đã CLOSED, không phải approval hiện hành. Đừng đóng #138 trước khi các điều kiện đóng Issue được đáp ứng.

### 4. Artifact, checksum và kiểm tra không gây phát hành

| Kết quả | Nội dung / vị trí |
| --- | --- |
| Tệp ứng viên | `dxos-open-core-<version>.tar.gz`, `SHA256SUMS`, `RELEASE-NOTES.md` trong output packager |
| Trong archive | `MANIFEST.json` với `tag`, `source_sha`, `mode` và `files_sha256`; LICENSE, NOTICE, notes, SBOM/inventory theo mode |
| GitHub Actions candidate | `r24-candidate-<run_id>` và (với PR/manual) `r24-source-only-candidate-<run_id>`, retention 30 ngày |
| Khi publish đã được duyệt | Workflow gắn archive + `SHA256SUMS` lên GitHub Release; mode binary thêm `IMAGE-DIGESTS.txt`; SBOM/NOTICE nằm **trong archive**, không mặc định đính kèm độc lập |

**Khoảng trống cần review:** [#190](https://github.com/tricore-opentrix/opentrix/issues/190) yêu cầu đính kèm SBOM và NOTICE; đường publish hiện tại chỉ đính kèm archive, checksums và (binary) digests. Reviewer phải xác nhận việc chứa các tệp trong archive có đáp ứng yêu cầu hay phải bổ sung assets qua **PR riêng**; không tự tuyên bố Done.

Để **xác minh artifact đã có** (không tạo release), tải đúng cặp archive/checksum từ một run đã xác minh rồi chạy trong thư mục chứa hai tệp:

```sh

sha256sum -c SHA256SUMS

python3 /path/to/repository/scripts/r24-release.py verify \
  --archive dxos-open-core-0.2.0.tar.gz --checksums SHA256SUMS

```

Dùng version/tên archive đúng với run thực tế; ví dụ `0.2.0` **không xác nhận artifact đã tồn tại hoặc đã được phép phát hành**. Trên Windows, có thể chạy kiểm bằng Python `r24-release.py verify` với đường dẫn tương ứng; không nhập hash hoặc trạng thái PASS giả định. Sau đó mở `MANIFEST.json` trong archive và đối chiếu `tag`, `source_sha`, `mode`, `files_sha256`; kiểm `RELEASE-NOTES.md` trùng bytes trong archive.

#### 4.1 Chuỗi source-only candidate và reproducibility

Trong checkout sạch của **đúng source SHA đã đóng băng**, tạo các R23 inputs ở §3.1 và chạy contract tests trước khi package. Ví dụ dưới đây dùng shell Linux/CI và version `v0.2.0` có notes tương ứng trong CHANGELOG; nếu dùng version khác phải đổi cả tag và tên archive. Không tạo tag và không chứng minh Windows parity. Dừng khi bất kỳ bước nào lỗi:

~~~sh

set -e

python3 -m unittest discover -s scripts -p 'test_r24_*.py'

SOURCE_SHA="$(git rev-parse HEAD)"

TAG=v0.2.0

python3 scripts/r24-release.py package --mode source-only \
  --tag "$TAG" --sha "$SOURCE_SHA" --output dist/r24-source-only

python3 scripts/r24-release.py verify \
  --archive dist/r24-source-only/dxos-open-core-0.2.0.tar.gz \
  --checksums dist/r24-source-only/SHA256SUMS

(cd dist/r24-source-only && sha256sum -c SHA256SUMS)

~~~

1. Source-only cần tracked sources đủ điều kiện và R23 inputs; không cần binary upstream collector. Kiểm prefix `dxos-<tag>/`, `MANIFEST.json`, ba `compliance/*.cdx.json`, inventory và notices; đối chiếu archive members/hashes và standalone notes. Không sửa checksum hay normalize artifact để làm phép so sánh đạt.

2. PR/manual binary-validation candidate ở `dist/r24/`; source-only ở `dist/r24-source-only/`. Lấy đúng artifact/run/mode ở bảng trên, không trộn archive và checksum của hai candidate.

3. Sau freeze, chạy **hai workflow_dispatch candidates trên cùng source SHA** khi được phép; tải hai source-only artifacts riêng và so archive digest, MANIFEST tag/full SHA/mode/member hashes, SHA256SUMS và notes. Lưu cả run IDs/URLs và reviewer verdict; không dùng hai source SHA khác nhau để claim reproducibility.

4. Source-only packager lấy tracked source qua `git ls-files --cached`: sửa/rename docs cũng làm đổi member bytes/paths và archive hash. Không tái dùng acceptance/checksum cũ cho source mới. Frozen source và acceptance JSON phải được bảo toàn.

**Lịch sử R24:** target 06–07/11/2026 trong [runbook](06-deployment/r24-release.md) là có điều kiện, không phải ngày phát hành đã xác minh. `v0.2.0-rc.1` được giới hạn INTERNAL / NOT RELEASE-ACCEPTED, không công bố public tag/Release. Nếu gates chưa đủ, hoãn và chốt ngày thực tế trước source freeze; không backdate hoặc dùng lịch cũ của R26/#141 làm approval mới. Ngày 16/11 có **bằng chứng tái lập validation-only** tại `ac36d01` như §4.2; **publishable acceptance sequence vẫn UNVERIFIED/BLOCKED**.

#### 4.2 Bằng chứng tái lập validation-only tại `ac36d01` — 16/11/2026

Theo [báo cáo Bảo ở #225](https://github.com/tricore-opentrix/opentrix/issues/225#issuecomment-6907507813), hai candidate từ [CI run 43803840030](https://github.com/tricore-opentrix/opentrix/actions/runs/43803840030) và [43802505912](https://github.com/tricore-opentrix/opentrix/actions/runs/43802505912), cùng một lần tái lập độc lập trong Linux Ubuntu 24.04.5, sử dụng chính xác source `ac36d01091a42b7d4d82fbf2fb4f822014e98998`. **3/3 archive có SHA-256 trùng** `af9d5e71ced9b693d434a27e762cd4a1883a03444764954d2e1174ed397e8adc`; **421/421 thành viên trùng byte**. `verify`, `sha256sum -c`, R23/R24 checks được Bảo báo cáo PASS trong phạm vi thử nghiệm.

**Giới hạn bắt buộc:** mọi archive ở lượt này dùng `--validation-only`, MANIFEST có `validation_only=true`. Script release gate **từ chối** archive validation-only; hash nêu trên **không** được đưa vào `archive_sha256` cho publishable `v0.2.0.json` khi chưa kiểm chứng chính gói publishable. Bảo đã xác định metadata `vcs.url` của SBOM phụ thuộc cách viết Git remote; việc chuẩn hóa chỉ nằm trong clone Linux thử nghiệm, không phải sửa source. Sau mọi thay đổi source/CHANGELOG/docs, phải re-freeze và tái lập đúng SHA mới.

**B3 demo riêng biệt:** [#225](https://github.com/tricore-opentrix/opentrix/issues/225#issuecomment-6874592663) ghi Golden Path 6/6 integration-local tại **`8903c2`**, không phải `ac36d01` và không phải nghiệm thu release R24. B4 tổng duyệt máy thi và production LIVE không được suy ra từ B3.

### 5. Release notes, vận hành và quyết định cuối

- Release notes được packager sinh từ phần version tương ứng trong [`CHANGELOG.md`](../CHANGELOG.md). Trước khi chốt source SHA, review ngày phát hành, tính năng thực tế, giới hạn MOCK/LIVE, trạng thái #138, scope source-only và license notices; không tự chèn tuyên bố thành công.

- Với `v0.2.0`, không quảng cáo JAR, frontend build, GHCR, Flowable hoặc provider S3 như đã phát hành nếu chưa có chấp thuận. APISIX và Golden Path đã có **bằng chứng integration-local ở `8903c2`**, nhưng không suy thành **production LIVE** hay **thành phần nhị phân được phân phối** bởi source-only release.

- Nếu binary publish từng phần, GHCR tags và GitHub Release không phải thao tác atomic; ghi digest/trạng thái và dừng để đối soát, **không retry mù**.

- Lưu chứng cứ: source/tag/full SHA, run URLs, commit acceptance PR, reviewer, exact archive SHA-256, SHA256SUMS, MANIFEST, notes, mode, asset URLs và verdict `PASS / BLOCKED / UNVERIFIED`.

**Điều kiện được ghi `RELEASE_ACCEPTED`:** quyết định quyền nguồn trong phạm vi chấp thuận và ngoại lệ được xử lý minh bạch, reproducibility của **publishable** archive, manifest exact-SHA, review độc lập, tag/release được duyệt và xác minh lại tài sản tải về đã đạt. Trạng thái hiện tại của bản dự thi: **chưa đạt/UNVERIFIED**, theo [#190](https://github.com/tricore-opentrix/opentrix/issues/190).

#### 5.1 R26: lịch sử cutover, hậu kiểm và recovery

[R26 record](06-deployment/r26-repository-cutover.md), [#135](https://github.com/tricore-opentrix/opentrix/issues/135): **REPOSITORY RENAMED / POST-CUTOVER VERIFICATION INCOMPLETE**, snapshot **06/11/2026**. Repository hiện hữu được đổi từ `tricore-opentrix/dxos-open-core` thành `tricore-opentrix/opentrix`; không phải tạo repository thay thế. Owner Bảo, reviewers Yến/Ánh. Pre-rename freeze, availability checks và thứ tự PR/R16 trong record là lịch sử, không phải lệnh rename/merge lại.

| Snapshot lịch sử được giữ | Giới hạn bằng chứng |
| --- | --- |
| Repository ID `1398198415`; API aliases cũ trỏ cùng identity | PASS metadata identity; chưa xác minh HTTP 301/302 hoặc clean clone |
| `main@5daa145d3b5f20f2f16fe0799c6d0808fd6c3e33`; CODEOWNERS/collaborator metadata có mặt | Không chứng minh full protection/ruleset/review-policy equivalence |
| `gh-pages@a0e975dedb088d1aff5026636b6748ae731c9ad5`; metadata `protected:true` nhưng enforcement `off`, required checks rỗng | PENDING protection review; `https://tricore-opentrix.github.io/opentrix/` chỉ là candidate, chưa xác minh live content |
| `v0.1.0` tag object `98530b948c9200bcb43cec73759882a8750be5f4`; release ID `433767067`; archive 563495 bytes, SHA256SUMS 94 bytes | Giữ pre-release và hai assets; metadata không chứng minh đã tải lại/đối chiếu bytes |
| Pages/PR CI runs và exact-byte setup-script syntax/dry-run trong record | Chỉ evidence lịch sử theo SHA/fixture đó; không phải CI approval của HEAD mới hoặc deployed browser acceptance |

Hậu kiểm còn hiệu lực, phải ghi SHA/ngày, URLs, kết quả thực và reviewer:

1. Đối chiếu numeric ID, canonical name, HTTP redirects từ URL personal/Org cũ; kiểm `git ls-remote` và clean clone. API alias resolution không thay HTTP/network verification.

2. Kiểm README/NOTICE/CHANGELOG/docs/scripts và external links; giữ links pinned SHA. Tải đúng hai assets `v0.1.0`, kiểm SHA256SUMS và hash so với evidence gốc; không đổi tag hoặc bytes để sửa link.

3. Đối chiếu protections/rulesets, required checks, CODEOWNERS, quyền cả ba thành viên, workflows và integrations với snapshot trước cutover; không làm yếu review gates.

4. Xác minh URL Pages thực tế, homepage/blog/API/release links và deployed-HEAD desktop/mobile; Ánh xác nhận website/TikTok/external-channel updates, Yến/Ánh review. `has_pages=true` hoặc historical deploy SUCCESS không chứng minh content hiện hành.

5. Chỉ đánh dấu R26 Done khi đủ post-cutover checklist và independent sign-off; không lấy baseline R26 làm frozen R24 source, không hoàn tất #139 hoặc dùng lịch #141 khi thiếu kế hoạch publication mới được xác nhận.

**Recovery:** giữ repository ID, main/Pages SHAs, settings/protection snapshots, PR/tag/release refs và external-integration/Pages/DNS configuration trước thay đổi có liên quan. Khi hậu kiểm lệch, dừng và đối soát với owner từ snapshot; rename-back đơn thuần không chứng minh Pages, webhooks, external links hay DNS đã phục hồi. Giữ mọi trạng thái NOT VERIFIED/PENDING cho đến khi có evidence mới.

**Tài liệu giữ lại:** R23 giữ lịch sử policy và handoff; R24 giữ technical runbook, upstream/acceptance paths; R26 giữ exact snapshots, script blob hashes, run URLs và checklist lịch sử. `docs/06-deployment/r24-acceptances/<tag>.json` trên `main` và `docs/06-deployment/r24-upstream/…` vẫn là dependency được viện dẫn. Không đổi/xóa legacy, SQL evidence, upstream license bytes hoặc checksum khi hợp nhất phần hướng dẫn này.

### 6. Mục tiêu — PROPOSED

[#190](https://github.com/tricore-opentrix/opentrix/issues/190) theo dõi release dự thi; [#138](https://github.com/tricore-opentrix/opentrix/issues/138) theo dõi quyền nguồn gốc; [#119](https://github.com/tricore-opentrix/opentrix/issues/119) theo dõi demo stack đã có bằng chứng integration-local; các cổng này **độc lập** với việc merge tài liệu #194.

---

<a id="en"></a>

## English

### 1. Release status (AS-IS / UNVERIFIED)

#### Feature status matrix / Bảng trạng thái tính năng (AS-IS / UNVERIFIED / PROPOSED)

| Component | Existing source | Verification / limits |
| --- | --- | --- |
| Identity / Keycloak | Backend [OIDC](../backend/src/main/resources/application.yml), BFF [OAuth client](../portal-bff/src/main/resources/application.yml) | **INTEGRATION-LOCAL VERIFIED** in B3 at `8903c2` with three demo accounts; production LIVE E2E or any later SHA is **not verified** ([#225](https://github.com/tricore-opentrix/opentrix/issues/225)) |
| Workflow Core | `WorkflowRuntime`, `WorkflowPersistencePort`, PostgreSQL adapter and test sources ([Backend](../backend/README.md)) | **SOURCE IMPLEMENTED / TEST-LEVEL**; does not prove Flowable/E2E |
| Helpdesk | `/api/v1/mvp/requests` when `dxos.helpdesk.enabled` is enabled, authorization/version tests | **INTEGRATION-LOCAL B3: 6/6 PASS** with three accounts on Windows `main@8903c2` (2026-11-14); not production LIVE, a later SHA, or B4 demo readiness ([B3 evidence](https://github.com/tricore-opentrix/opentrix/issues/225#issuecomment-6874592663)) |
| Portal Frontend | [Frontend](../frontend/package.json): MOCK and `integration-local` build | MOCK uses synthetic data; bundle build is not proof of runtime integration |
| Portal BFF | [BFF](../portal-bff/README.md): OAuth/PKCE, session, CSRF, fixture test | **Integration-local B3 Golden Path evidence** through APISIX at exact `8903c2`; no production LIVE or later-SHA assertion |
| PostgreSQL / Flyway | [Compose](../infra/compose.workflow-postgres.yml), migration Workflow V1–V4/Helpdesk SQL | **SOURCE IMPLEMENTED**; same-SHA schema/ACL/restart evidence pending |
| Docker Compose | Historical `infra/compose.workflow-postgres.yml`; demo `compose.demo.yml` and `compose.gateway.yml` | **DEMO STACK IMPLEMENTED / INTEGRATION-LOCAL B3 VERIFIED** at `8903c2`; full B4 rehearsal on competition laptop remains pending ([#119](https://github.com/tricore-opentrix/opentrix/issues/119), [#225](https://github.com/tricore-opentrix/opentrix/issues/225)) |
| APISIX | `compose.gateway.yml`, `gateway-smoke.ps1` and B3 browser requests routed through gateway | **INTEGRATION-LOCAL VERIFIED** at `8903c2`; gateway smoke **6 PASS / 1 BLOCKED**, manual browser Golden Path evidence, not 7/7 automated ([#116](https://github.com/tricore-opentrix/opentrix/issues/116), [#225](https://github.com/tricore-opentrix/opentrix/issues/225)) |
| Flowable | Golden Path currently uses engine `internal` (ADR-009) | **NOT SHIPPED / PROPOSED**; do not conflate with APISIX ([#191](https://github.com/tricore-opentrix/opentrix/issues/191)) |

SOURCE IMPLEMENTED = source exists; TEST-LEVEL = recorded test scope only; UNVERIFIED ≠ FAIL. Sources: [Block B](09-evidence/phase-2/block-b-backend-infra.md) / [Block C](09-evidence/phase-2/block-c-application.md).

**Version status / Bảng phiên bản** (GitHub Releases snapshot from 2026-11-12; technical and #138 evidence updated 2026-11-16, not a new release verification):

| Version | Status | Scope and evidence |
| --- | --- | --- |
| [`v0.1.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) | **Released — pre-release**, not stable | Public GitHub Release **2026-11-04**, 2 assets at check; MVP scope in [root README](../README.md), not LIVE E2E acceptance |
| `v0.2.0` | **In development / Not released** | SOURCE-ONLY is the conditional scope under [R24](06-deployment/r24-release.md). #138 Q1–Q5 have maintainer agreement; **Q3 docs PR, exact-SHA publishable artifact, acceptance JSON, protection and #190** remain required. The 16 Nov three-way match is **validation-only** |
| `v0.3.0+` | **Planned / PROPOSED** | No accepted tag/scope/publication commitment; future features are not shipped |
| Item | Supportable status | Not implied |
| --- | --- | --- |
| [`v0.1.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) | Historical public **pre-release**, not the stable competition submission ([#190](https://github.com/tricore-opentrix/opentrix/issues/190)) | Not current `RELEASE_ACCEPTED` |
| R23, SPDX/REUSE | License-policy/SBOM/notices and metadata checks in [`ci.yml`](../.github/workflows/ci.yml); [Phase 2 Block B](09-evidence/phase-2/block-b-backend-infra.md) | Green CI does not establish source ownership or distribution permission |
| R24 candidate | [`release.yml`](../.github/workflows/release.yml) and [`r24-release.py`](../scripts/r24-release.py) create/verify archives with fail-closed gate | Candidate PASS does not authorize publishing |
| `v0.2.0` | **SOURCE-ONLY target, not verified as published**; #138 Q1–Q5 consent is recorded but Q3/closure conditions remain; [#190](https://github.com/tricore-opentrix/opentrix/issues/190) remains OPEN at inspection | No claim of release, rights clearance, JAR/`frontend/dist`/GHCR permission |

`AS-IS` means inspected source/workflow; `HISTORICAL` is prior evidence; `UNVERIFIED` lacks exact-SHA acceptance; `PROPOSED` is an issue-tracked target. **Phase 2/R23 results do not grant R24 distribution acceptance.**

### 2. Versioning, triggers and package scope

- The workflow accepts `vMAJOR.MINOR.PATCH` or `vMAJOR.MINOR.PATCH-rc.N` (`N ≥ 1`); [`CHANGELOG.md`](../CHANGELOG.md) must contain nonempty notes for that version. [#190](https://github.com/tricore-opentrix/opentrix/issues/190) requires the new competition version **not** to be marked pre-release.

- Relevant `pull_request` changes and `workflow_dispatch` build **nonpublishable** candidates. These runs validate a binary candidate and a separate source-only candidate; there is **no publish job** for those events.

- A `push` of a `v*` tag may reach publishing **only if** the candidate passed, the tagged source commit is an ancestor of `main`, an independently approved exact-tag acceptance JSON exists on `main`, and environment/permission gates are satisfied. Do not push a tag merely to test.

- `v0.2.0` has an additional gate: only `source-only` may be distributed. Binary CI validation is not permission to publish binary artifacts.

| R24 mode | Archive content | Boundary |
| --- | --- | --- |
| `source-only` (target for `v0.2.0`) | Eligible UTF-8 Git-tracked sources, LICENSE, NOTICE, THIRD-PARTY-NOTICES, CHANGELOG, RELEASE-NOTES, three CycloneDX SBOMs, inventory and MANIFEST | No bootJARs, frontend dist or images; a dependency SBOM is **not** shipped binary code |
| `binary` (**not authorized**) | Backend/BFF bootJARs, frontend dist, SBOM/inventory/notices, upstream license texts, MANIFEST and notes | Requires separate upstream, source/relink, assets, JRE/OCI and license obligations review |

Details: [R24 runbook](06-deployment/r24-release.md), [packager](../scripts/r24-release.py), [workflow](../.github/workflows/release.yml).

### 3. Test, legal and independent approval gates

1. **Build and compliance:** Java 21/Node 22, R24 contract tests (`test_r24_*.py`), R23 inventories/notices and REUSE. Capture actual SHA and PASS/FAIL/SKIPPED counts; skipped suites are not passes.

2. **Provenance:** all three maintainers have signed Q1–Q5 of the [#138 disposition record](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6899613976) for **source-only `v0.2.0`** only and within their respective rights, with AI/upstream limitations disclosed. This is neither repository-wide originality verification nor R24 distribution acceptance. `reuse lint` and an allowed dependency list are **not legal clearance**. See §3.3.

3. **Freeze source SHA:** bind the candidate digest to a full commit; two independently generated candidates must use the **same source SHA** before claiming reproducibility.

4. **Separate acceptance on `main`:** after source freeze, a separately reviewed PR must add `docs/06-deployment/r24-acceptances/<tag>.json` to `main`. Required fields include `tag`, `source_sha`, `mode`, `archive_sha256`, `reviewed_by`, and HTTPS evidence for that mode. Assertions in JSON alone are not proof of approval.

5. **Protected publishing:** verify configured `r24-release` Environment, required reviewers and tag protection **before** creating a tag. Declaring an environment in YAML does **not** prove its protection settings exist.

6. **Verify before publication:** exact archive/hash/MANIFEST member checksums/notes, tag/SHA/mode, #138 provenance and independent review. Missing or mismatching evidence means **BLOCKED**.

Updating documentation or passing CI does not authorize tag creation, GitHub Release, GHCR publishing or database migration.

#### 3.1 R23: reproduce SBOM/NOTICE and hand over distribution evidence

From the selected source checkout's repository root, with Java 21, Node 22 and dependencies; these commands generate build/compliance outputs and **do not publish a release**. The complete procedure and history remain in [R23](06-deployment/r23-plan.md).

~~~sh

set -e

./backend/gradlew -p backend cyclonedxBom --no-daemon

./backend/gradlew -p portal-bff cyclonedxBom --no-daemon

(cd frontend && npm ci && npx --yes @cyclonedx/cyclonedx-npm@6.0.1 --omit dev --output-format JSON --output-file ../frontend-sbom.json)

python3 scripts/r23-compliance.py \
  --backend backend/build/reports/cyclonedx/bom.json \
  --portal-bff portal-bff/build/reports/cyclonedx/bom.json \
  --frontend frontend-sbom.json --output build/r23

diff -u THIRD-PARTY-NOTICES.md build/r23/THIRD-PARTY-NOTICES.md

python3 -m unittest discover -s scripts -p 'test_r23_*.py'

~~~

Check the inventory before handoff:

- Backend/BFF use Gradle **runtime classpaths**; frontend uses **production** dependencies. `--omit dev` must exclude `vitest`, `jsdom`, `typescript` and `@vitest/*` unless independently shown to be actual runtime dependencies. Retain MIT-0/BlueOak whenever present in the runtime graph.

- Historical cleanup [#133](https://github.com/tricore-opentrix/opentrix/pull/133), SHA `84a7ca9e5b5f1012b95f676c86c2ec1d95dd3ea7`: JDBC replaced the JPA starter. Verify a fresh BOM excludes `hibernate-core`, `jakarta.persistence-api`, `antlr4-runtime` and `hibernate-commons-annotations`; `hibernate-validator` is not Hibernate ORM. The Hibernate 6.6.53.Final LGPL exception was removed; reintroducing ORM requires a new review.

- Policy consumes complete SPDX expressions, `AND`/`OR`/parentheses and reviewed `WITH` clauses; unknown/malformed declarations, unaccepted `WITH` clauses or versions outside a pinned exception must fail closed. Retain negative-canary evidence; do not relax the allow-list to bypass failures.

- The three BOMs, `build/r23/license-inventory.json`, regenerated notices, commands/exit codes and review verdict must identify the same exact HEAD. Compare tracked notices with `diff`; check `backend`, `portal-bff`, `frontend`, `r23-compliance` and `repo-hygiene` for that HEAD. Preserve run/artifact IDs and check download availability; `r23-sbom-and-notices` has 30-day retention.

**R23 implementation Done** requires merged #133 and [#131](https://github.com/tricore-opentrix/opentrix/pull/131), correctly scoped inventories, matching notices, exact-HEAD independent review/CI and an owner-accepted R24 handoff. It does not require publication of a future archive. Bảo owns automation and hands over BOMs/notices, the pending-obligations matrix, commands and CI artifact IDs; Yến coordinates compliance/distribution acceptance, with Ánh co-reviewing. `release_distribution_owner=R24 / Yến` does not transfer workflow coding ownership.

`license_policy_status=APPROVED` does not change `release_distribution_status=PENDING`. Generated notices are an inventory, not upstream LICENSE/NOTICE texts or rights certification. For **contents actually distributed**, R24 must review these obligations:

| Scope | Evidence/disposition to preserve |
| --- | --- |
| Logback classic/core (R23 baseline 1.5.34, selected EPL-2.0 option) | Selected terms, upstream texts, attribution/provenance and applicable source availability |
| Hibernate ORM LGPL-2.1, only if actually distributed again | Linking/packaging, license/source or offer and replacement/relink rights; do not carry old ORM obligations into a BOM verified to exclude ORM |
| MIT-0, BlueOak-1.0.0 in the runtime graph | Text/attribution or a valid license link under applicable terms; do not infer coverage from the old dev-only BOM |
| Other dependencies and frontend assets | License/NOTICE bytes, provenance, dual-license choice, source/source-offer when applicable; inspect actual bundles |
| Separately distributed service/base images, including Superset/Grafana if shipped | Separate inventories/SBOMs, license texts, attestations and OCI obligations beyond the three Gradle/npm BOMs |

#### 3.2 R24: mode-specific evidence and independent approval

After source freeze, merge the acceptance PR separately into `main`; any authorized release tag points to the **earlier frozen source SHA**, not the newer acceptance commit, avoiding circular self-reference. Inspect the acceptance PR/review and actual HTTPS evidence, not just JSON assertions.

| Mode | Evidence in addition to the common fields above |
| --- | --- |
| `source-only` | `source_provenance`, `source_license`, `sbom_source_boundary`, `archive_and_checksums`, `release_notes`; binary license groups do not clear this mode |
| `binary` — not authorized | Pinned `eclipse-temurin:21-jre@sha256:<digest>`; a `CLEARED` permissive group with evidence, individual `CLEARED` exceptions for licenses outside it; source/relink, upstream texts, assets, JRE/OCI and checksum/notes evidence |

The `scripts/r24-upstream.py` collector reads LICENSE/NOTICE from Gradle-cache JARs and LICENSE/COPYING/NOTICE from npm; reviewed supplements remain at `docs/06-deployment/r24-upstream/<project>/<name>-<version>/`. Bytes are preserved/hashed in `upstream-index.json`: found texts are `COLLECTED_UNREVIEWED`, absent texts remain `MISSING`; Maven `type=pom` is metadata-only, and `package.json` license identifiers do not replace actual texts. When preparing binary-validation inputs for review, use `python3 scripts/r24-upstream.py --root . --inventory build/r23/license-inventory.json --output build/r24/upstream`.

An independently accepted permissive group may cover only Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC and 0BSD; the archive still needs upstream bytes. EPL, GPL+Classpath, OFL, CC0 and other licenses outside the group require individual inventory-based dispositions/choices, including Logback/jakarta.annotation-api if shipped. Missing texts or unresolved source/NOTICE/asset/JRE/OCI obligations keep distribution **BLOCKED**.

Yến must verify the `r24-release` Environment has independent reviewers Yến/Ánh and a `v*` protection ruleset before any tag. **R24 implementation Done** means review, CI and merge; **source-only release Done** additionally requires #138 clearance, exact-source acceptance/review through a **new PR** (historical [#139](https://github.com/tricore-opentrix/opentrix/pull/139) is CLOSED), protection, authorized publication and independently checked downloaded asset hashes. Binary/JAR/GHCR obligations are not waived.

#### 3.3 #138: contribution-rights disposition and AI limitations (2026-11-16)

- **Decision scope:** [Q1–Q5 disposition record](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6899613976), [Bảo's own confirmation](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6907781691), and [Ánh's own confirmation](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6907788256); Yến posted the disposition. The three maintainers agree on evaluating **source-only `v0.2.0`** only to the extent they can license their own contributions under Apache-2.0. This internal decision does **not** clear upstream or third-party rights.
- **Disclosed limits:** complete per-prompt history is unavailable; AI output is not asserted fully independent of external sources; contributors report no intentional copying; no comprehensive file-by-file upstream comparison has occurred. Retain `UNKNOWN` / `NOT_RECALLED` / `RIGHTS_PENDING` where evidence is missing; do not claim repository-wide `CLEARED`.
- **Q3 documentation condition:** a separately reviewed PR must update bilingual `CONTRIBUTING.md` (AI disclosure and a 7-day response process for suspected source overlap), `docs/OPEN_SOURCE.md`, `docs/RELEASE.md`, and actual demo-image licenses for Keycloak/PostgreSQL/APISIX in `NOTICE`. Mark **MERGED** only on verifiable PR evidence.
- **Q4/Q6:** a new `v1.0.0` Issue will track file-level/upstream comparison; the approximately five-file risk spot-check in Q6 is **optional**, and no match found is not proof of independence.
- **Separate release gate:** #138 disposition ≠ R24 gate PASS. A separately reviewed acceptance PR must add `v0.2.0.json` after source freeze with all five evidence URLs and actual reviewers, followed by protected environment/tag authorization. Historical [PR #139](https://github.com/tricore-opentrix/opentrix/pull/139) is CLOSED, not current release approval. Do not close #138 until its recorded closure conditions are met.

### 4. Artifacts, checksums and nonpublishing verification

| Output | Contents / location |
| --- | --- |
| Candidate files | `dxos-open-core-<version>.tar.gz`, `SHA256SUMS` and `RELEASE-NOTES.md` from the packager |
| Inside archive | `MANIFEST.json` with `tag`, `source_sha`, `mode` and `files_sha256`; LICENSE, NOTICE, notes and mode-dependent SBOM/inventory |
| GitHub Actions candidates | `r24-candidate-<run_id>` and (PR/manual) `r24-source-only-candidate-<run_id>`; 30-day retention |
| Authorized publishing | Workflow attaches archive + `SHA256SUMS` to GitHub Release; binary mode also attaches `IMAGE-DIGESTS.txt`. SBOM/NOTICE are **inside** the archive rather than automatically attached as standalone assets |

**Acceptance gap to review:** [#190](https://github.com/tricore-opentrix/opentrix/issues/190) requires attached SBOM and NOTICE; the workflow currently uploads archive/checksums/(binary) digests as release assets. Review whether embedded files meet the requirement or separate attachments are needed in a **different reviewed PR**. Do not mark this criterion Done unilaterally.

To **verify an existing candidate artifact without publishing**, download the exact archive and checksum pair from its run and, in their containing directory, use:

```sh

sha256sum -c SHA256SUMS

python3 /path/to/repository/scripts/r24-release.py verify \
  --archive dxos-open-core-0.2.0.tar.gz --checksums SHA256SUMS

```

Use the actual version/file name; `0.2.0` is only an example, not a claim that such an artifact is available or release-cleared. On Windows use the Python verifier with actual paths. Inspect the archived `MANIFEST.json` for tag/full SHA/mode/file hashes and byte-compare `RELEASE-NOTES.md` to the archived member; never invent PASS output.

#### 4.1 Source-only candidate sequence and reproducibility

In a clean checkout of the **exact frozen source SHA**, generate the R23 inputs from §3.1 and run contract tests before packaging. This example uses a Linux/CI shell and version `v0.2.0` with matching CHANGELOG notes; for another version, change both the tag and archive name. It creates no tag and does not establish Windows parity. Stop on any failed step:

~~~sh

set -e

python3 -m unittest discover -s scripts -p 'test_r24_*.py'

SOURCE_SHA="$(git rev-parse HEAD)"

TAG=v0.2.0

python3 scripts/r24-release.py package --mode source-only \
  --tag "$TAG" --sha "$SOURCE_SHA" --output dist/r24-source-only

python3 scripts/r24-release.py verify \
  --archive dist/r24-source-only/dxos-open-core-0.2.0.tar.gz \
  --checksums dist/r24-source-only/SHA256SUMS

(cd dist/r24-source-only && sha256sum -c SHA256SUMS)

~~~

1. Source-only needs eligible tracked sources and R23 inputs, not the binary upstream collector. Inspect the `dxos-<tag>/` prefix, `MANIFEST.json`, three `compliance/*.cdx.json` files, inventory and notices; compare archive members/hashes and standalone notes. Do not edit checksums or normalize artifacts to make comparisons pass.

2. PR/manual binary-validation candidates use `dist/r24/`; source-only uses `dist/r24-source-only/`. Select the correct artifact/run/mode from the table above; never mix one candidate's archive with another's checksum.

3. After freeze, run **two workflow_dispatch candidates on the same source SHA** when authorized; download their source-only artifacts separately and compare archive digest, MANIFEST tag/full SHA/mode/member hashes, SHA256SUMS and notes. Preserve both run IDs/URLs and the reviewer verdict; two different source SHAs do not establish reproducibility.

4. The source-only packager collects tracked source with `git ls-files --cached`: editing/renaming docs also changes member bytes/paths and the archive hash. Never reuse old acceptance/checksums for new source. Preserve the frozen source and acceptance JSON.

**R24 history:** the 2026-11-06/07 targets in the [runbook](06-deployment/r24-release.md) were conditional, not verified publication dates. `v0.2.0-rc.1` is restricted to INTERNAL / NOT RELEASE-ACCEPTED verification, with no public tag/Release. If gates are incomplete, postpone and confirm the actual date before source freeze; do not backdate or treat the old R26/#141 schedule as new approval. A **validation-only reproducibility trial** at `ac36d01` was recorded on 2026-11-16 (§4.2); the **publishable acceptance sequence remains UNVERIFIED/BLOCKED**.

#### 4.2 Validation-only reproduction evidence at `ac36d01` — 2026-11-16

Per [Bảo's report in #225](https://github.com/tricore-opentrix/opentrix/issues/225#issuecomment-6907507813), two candidates from [CI run 43803840030](https://github.com/tricore-opentrix/opentrix/actions/runs/43803840030) and [43802505912](https://github.com/tricore-opentrix/opentrix/actions/runs/43802505912), plus an independent Ubuntu 24.04.5 Linux reproduction, used exact source `ac36d01091a42b7d4d82fbf2fb4f822014e98998`. **All 3 archives share SHA-256** `af9d5e71ced9b693d434a27e762cd4a1883a03444764954d2e1174ed397e8adc`; **421/421 members match byte-for-byte**. Bảo reports `verify`, `sha256sum -c`, and R23/R24 checks PASS within this validation scope.

**Mandatory limit:** all three builds used `--validation-only` and their MANIFEST has `validation_only=true`. The release gate **rejects** validation-only archives. This hash **must not** populate the publishable `v0.2.0.json` `archive_sha256` unless it is independently confirmed from the actual publishable archive. Bảo isolated `vcs.url` SBOM metadata differences caused by Git remote URL formatting; the normalization was confined to a temporary Linux clone, not tracked source changes. Any source/CHANGELOG/docs update requires a new freeze and new same-SHA evidence.

**Separate B3 demo evidence:** [#225](https://github.com/tricore-opentrix/opentrix/issues/225#issuecomment-6874592663) records integration-local 6/6 Golden Path at **`8903c2`**, not `ac36d01` and not R24 release acceptance. The B4 competition-laptop rehearsal and production LIVE status are not inferred from B3.

### 5. Release notes, operations and final verdict

- Packager derives release notes from the version section of [`CHANGELOG.md`](../CHANGELOG.md). Before freezing the source SHA, verify the date, delivered scope, MOCK/LIVE limits, #138 rights status, source-only boundary and attribution. Do not add unsupported claims.

- For `v0.2.0`, do not advertise JARs, frontend build, GHCR, Flowable, or an S3 provider as distributed without separate acceptance. APISIX and the Golden Path have **integration-local evidence at `8903c2`**, but this is not **production LIVE** or binary distribution under a source-only release.

- GHCR and GitHub Release publishing is not atomic in binary mode. On a partial failure record exact digests/states, stop for reconciliation, and **do not blindly retry**.

- Preserve: tag/full source SHA, run URLs, acceptance PR/reviewers, archive SHA-256, SHA256SUMS, MANIFEST, notes, mode, actual asset URLs, and `PASS / BLOCKED / UNVERIFIED` verdict.

**`RELEASE_ACCEPTED` requires** scope-bounded contributor-rights dispositions and transparent resolution of exceptions, **publishable-archive** repeatability, exact-SHA acceptance, independent review, authorized tag/release and verified downloaded assets. The competition release has **not** met that verdict at this inspected state; see [#190](https://github.com/tricore-opentrix/opentrix/issues/190).

#### 5.1 R26: cutover history, post-cutover checks and recovery

[R26 record](06-deployment/r26-repository-cutover.md), [#135](https://github.com/tricore-opentrix/opentrix/issues/135): **REPOSITORY RENAMED / POST-CUTOVER VERIFICATION INCOMPLETE**, snapshot **2026-11-06**. The existing repository was renamed from `tricore-opentrix/dxos-open-core` to `tricore-opentrix/opentrix`; no replacement repository was created. Bảo owns the work, with Yến/Ánh reviewing. The pre-rename freeze, availability checks and PR/R16 ordering are historical, not instructions to repeat a rename or merge.

| Preserved historical snapshot | Evidence limitation |
| --- | --- |
| Repository ID `1398198415`; old API aliases resolve to the same identity | PASS identity metadata; HTTP 301/302 and clean clone not verified |
| `main@5daa145d3b5f20f2f16fe0799c6d0808fd6c3e33`; CODEOWNERS/collaborator metadata present | Does not prove full protection/ruleset/review-policy equivalence |
| `gh-pages@a0e975dedb088d1aff5026636b6748ae731c9ad5`; metadata `protected:true` but enforcement `off` and no required checks | PENDING protection review; `https://tricore-opentrix.github.io/opentrix/` is only a candidate, live content unverified |
| `v0.1.0` tag object `98530b948c9200bcb43cec73759882a8750be5f4`; release ID `433767067`; archive 563495 bytes, SHA256SUMS 94 bytes | Preserve the pre-release and two assets; metadata does not prove downloaded-byte comparison |
| Pages/PR CI runs and exact-byte setup-script syntax/dry-run in the record | Historical evidence for those SHAs/fixtures only; not new-HEAD CI approval or deployed browser acceptance |

Remaining post-cutover checks must record SHA/date, URLs, actual results and reviewer:

1. Compare numeric ID, canonical name and HTTP redirects from old personal/Org URLs; check `git ls-remote` and a clean clone. API alias resolution does not replace HTTP/network verification.

2. Check README/NOTICE/CHANGELOG/docs/scripts and external links; preserve pinned-SHA links. Download the two exact `v0.1.0` assets, verify SHA256SUMS and compare the hash with original evidence; never change the tag or bytes to repair links.

3. Compare protections/rulesets, required checks, CODEOWNERS, all three collaborators' rights, workflows and integrations with the pre-cutover snapshot; never weaken review gates.

4. Verify the actual Pages URL, homepage/blog/API/release links and deployed-HEAD desktop/mobile behavior; Ánh confirms website/TikTok/external-channel updates, with Yến/Ánh reviewing. `has_pages=true` or historical deployment SUCCESS does not prove current content.

5. Mark R26 Done only after the full post-cutover checklist and independent sign-off; do not treat the R26 baseline as frozen R24 source, complete #139 or use the #141 schedule without a newly confirmed publication plan.

**Recovery:** preserve repository ID, main/Pages SHAs, settings/protection snapshots, PR/tag/release refs and external-integration/Pages/DNS configuration before related changes. On a failed post-check, stop and reconcile with the owner against the snapshot; renaming back alone does not prove recovery of Pages, webhooks, external links or DNS. Retain every NOT VERIFIED/PENDING status until new evidence exists.

**Retained documents:** R23 preserves policy/handoff history; R24 retains the technical runbook and upstream/acceptance paths; R26 preserves exact snapshots, script blob hashes, run URLs and historical checklists. `docs/06-deployment/r24-acceptances/<tag>.json` on `main` and `docs/06-deployment/r24-upstream/…` remain referenced dependencies. Do not change/remove legacy files, SQL evidence, upstream license bytes or checksums while consolidating this guidance.

### 6. Target — PROPOSED

[#190](https://github.com/tricore-opentrix/opentrix/issues/190) tracks the competition release, [#138](https://github.com/tricore-opentrix/opentrix/issues/138) tracks source rights, and [#119](https://github.com/tricore-opentrix/opentrix/issues/119) tracks the demo stack with integration-local evidence. These gates are **separate** from merging documentation under #194.
