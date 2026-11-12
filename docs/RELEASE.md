<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Phát hành / Release

**Điều hướng / Navigation:** [Tài liệu](README.md) · [Development](DEVELOPMENT.md) · [Deployment](DEPLOYMENT.md) · [Release](RELEASE.md) · **Ngôn ngữ / Language:** [Tiếng Việt](#vi) | [English](#en)

> **Trạng thái / Status:** Đã review — merge ở #203 / Reviewed — merged in #203 · **Owner:** @lexuanbao258-collab · **Refs:** [#194](https://github.com/tricore-opentrix/opentrix/issues/194), [#197](https://github.com/tricore-opentrix/opentrix/issues/197), [#190](https://github.com/tricore-opentrix/opentrix/issues/190)
>
> **Source SHA:** `main@e31497f364cc7e9d3cee03ee59b9e48db524ea77` (R24 scripts/workflow và CHANGELOG được đối chiếu / inspected). **GitHub Releases kiểm tra ngày 2026-11-12:** v0.1.0 có public pre-release, v0.2.0 chưa có public release; trạng thái có thể thay đổi. Đây không phải phê duyệt tạo tag, Release hay GHCR. / GitHub Releases inspected 2026-11-12: v0.1.0 public pre-release, no public v0.2.0 release; this is not publication approval.

[Docs index](README.md) · [Open source and compliance](OPEN_SOURCE.md) · [Development](DEVELOPMENT.md) · [R24 canonical technical runbook](06-deployment/r24-release.md) · [R24 workflow](../.github/workflows/release.yml)

<a id="vi"></a>

## Tiếng Việt

### 1. Trạng thái bản phát hành (AS-IS / UNVERIFIED)

#### Bảng trạng thái tính năng / Feature status matrix (AS-IS / UNVERIFIED / PROPOSED)

| Thành phần | Nguồn có sẵn | Xác minh / giới hạn |
| --- | --- | --- |
| Identity / Keycloak | Backend [OIDC](../backend/src/main/resources/application.yml), BFF [OAuth client](../portal-bff/src/main/resources/application.yml) | **SOURCE IMPLEMENTED**; browser login ba người dùng **LIVE E2E UNVERIFIED** ([#118](https://github.com/tricore-opentrix/opentrix/issues/118)) |
| Workflow Core | `WorkflowRuntime`, `WorkflowPersistencePort`, PostgreSQL adapter và test source ([Backend](../backend/README.md)) | **SOURCE IMPLEMENTED / TEST-LEVEL**; không chứng minh Flowable/E2E |
| Helpdesk | `/api/v1/mvp/requests` khi bật `dxos.helpdesk.enabled`, authorization/version test | **SOURCE IMPLEMENTED / TEST-LEVEL**; Golden Path thật **UNVERIFIED** |
| Portal Frontend | [Frontend](../frontend/package.json): MOCK và build `integration-local` | MOCK dùng dữ liệu giả; build bundle chưa chứng minh kết nối runtime |
| Portal BFF | [BFF](../portal-bff/README.md): OAuth/PKCE, session, CSRF, fixture test | **TEST-LEVEL**; Keycloak/Browser/DB **LIVE E2E UNVERIFIED** |
| PostgreSQL / Flyway | [Compose](../infra/compose.workflow-postgres.yml), migration Workflow V1–V4/Helpdesk SQL | **SOURCE IMPLEMENTED**; schema/ACL/restart cùng SHA cần kiểm chứng |
| Docker Compose | `infra/compose.workflow-postgres.yml`: chỉ PostgreSQL | Full-stack Compose **PROPOSED** [#119](https://github.com/tricore-opentrix/opentrix/issues/119) |
| APISIX / Flowable | Chưa có runtime tích hợp được nghiệm thu; Workflow dùng engine nội bộ | **PROPOSED** [APISIX #116](https://github.com/tricore-opentrix/opentrix/issues/116) / [Flowable #191](https://github.com/tricore-opentrix/opentrix/issues/191) |

SOURCE IMPLEMENTED = có mã; TEST-LEVEL = chỉ các ca được ghi; UNVERIFIED ≠ FAIL. Nguồn: [Block B](09-evidence/phase-2/block-b-backend-infra.md) / [Block C](09-evidence/phase-2/block-c-application.md).




**Bảng phiên bản / Version status** (GitHub Releases kiểm tra ngày 12/11/2026):

| Version | Trạng thái | Phạm vi và bằng chứng |
| --- | --- | --- |
| [`v0.1.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) | **Released — pre-release**, không phải bản ổn định | GitHub Release công khai ngày **04/11/2026**, 2 assets khi kiểm tra; MVP theo [README gốc](../README.md), không suy ra LIVE E2E |
| `v0.2.0` | **In development / Not released** | SOURCE-ONLY chỉ là phạm vi candidate **dự kiến, có điều kiện** theo [R24](06-deployment/r24-release.md); quyền phân phối còn chặn bởi [#138](https://github.com/tricore-opentrix/opentrix/issues/138)/[#190](https://github.com/tricore-opentrix/opentrix/issues/190) |
| `v0.3.0+` | **Planned / PROPOSED** | Không có tag/phạm vi/cam kết phát hành đã nghiệm thu; tính năng tương lai chưa được ship |


| Đối tượng | Trạng thái có thể công bố | Không được suy diễn |
| --- | --- | --- |
| [`v0.1.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) | Bản công khai **pre-release lịch sử**, không phải bản dự thi ổn định ([#190](https://github.com/tricore-opentrix/opentrix/issues/190)) | Không phải `RELEASE_ACCEPTED` của giai đoạn hiện tại |
| R23, SPDX/REUSE | Có kiểm tra license-policy/SBOM/notices và metadata trong [`ci.yml`](../.github/workflows/ci.yml); bằng chứng kiểm kê ở [Block B](09-evidence/phase-2/block-b-backend-infra.md) | CI xanh không chứng minh sở hữu bản quyền hoặc quyền phân phối |
| R24 candidate | [`release.yml`](../.github/workflows/release.yml) và [`r24-release.py`](../scripts/r24-release.py) có lệnh tạo/kiểm archive và fail-closed gate | Candidate PASS không tự cho phép publish |
| `v0.2.0` | **Mục tiêu SOURCE-ONLY, chưa được xác nhận phát hành**; [#190](https://github.com/tricore-opentrix/opentrix/issues/190) và [#138](https://github.com/tricore-opentrix/opentrix/issues/138) vẫn mở tại thời điểm kiểm tra | Không được nói đã phát hành, đã thông quyền, hoặc cho phép JAR/`frontend/dist`/GHCR |

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
2. **Quyền nguồn gốc:** [#138](https://github.com/tricore-opentrix/opentrix/issues/138) phải có register/attribution/permission được review; `reuse lint` và policy allowlist chỉ kiểm tra metadata/phụ thuộc, **không chứng minh quyền**.
3. **Đóng băng source SHA:** xác định exact Git commit và package hash; kiểm hai ứng viên độc lập trên **cùng source SHA** nếu đang làm xác nhận tính tái lập. Không dùng checksum của SHA khác.
4. **Acceptance riêng trên `main`:** sau khi đóng băng source, PR khác có reviewer độc lập phải đưa `docs/06-deployment/r24-acceptances/<tag>.json` lên `main`. JSON cần `tag`, `source_sha`, `mode`, `archive_sha256`, `reviewed_by` và HTTPS evidence đúng mode; file JSON tự nó không chứng minh review đã xảy ra.
5. **Bảo vệ phát hành:** xác minh GitHub Environment `r24-release` cùng reviewer bắt buộc và quy tắc bảo vệ tag trước khi tạo tag. **Khai báo `environment: r24-release` trong YAML không tự chứng minh thiết lập bảo vệ đã có**.
6. **Đối chiếu trước công bố:** hash archive, MANIFEST file checksums, SHA256SUMS, release notes trong archive với file ngoài, source SHA/tag/mode, bằng chứng #138 và quyết định của reviewer. Nếu thiếu/bất đồng, **BLOCKED**.

Không tự tạo tag, release, phát hành GHCR hay chạy migration chỉ vì tài liệu hoặc CI đã được cập nhật.

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

### 5. Release notes, vận hành và quyết định cuối

- Release notes được packager sinh từ phần version tương ứng trong [`CHANGELOG.md`](../CHANGELOG.md). Trước khi chốt source SHA, review ngày phát hành, tính năng thực tế, giới hạn MOCK/LIVE, trạng thái #138, scope source-only và license notices; không tự chèn tuyên bố thành công.
- Với `v0.2.0`, không quảng cáo JAR, frontend build, image GHCR, Flowable, APISIX, provider S3 hoặc E2E như đã phát hành nếu chưa có chấp thuận/bằng chứng riêng.
- Nếu binary publish từng phần, GHCR tags và GitHub Release không phải thao tác atomic; ghi digest/trạng thái và dừng để đối soát, **không retry mù**.
- Lưu chứng cứ: source/tag/full SHA, run URLs, commit acceptance PR, reviewer, exact archive SHA-256, SHA256SUMS, MANIFEST, notes, mode, asset URLs và verdict `PASS / BLOCKED / UNVERIFIED`.

**Điều kiện được ghi `RELEASE_ACCEPTED`:** toàn bộ quyền nguồn gốc, reproducibility, manifest exact-SHA, review độc lập, tag/release được duyệt và xác minh lại tài sản tải về đã đạt. Trạng thái hiện tại của bản dự thi: **chưa đạt/UNVERIFIED**, theo [#190](https://github.com/tricore-opentrix/opentrix/issues/190).

### 6. Mục tiêu — PROPOSED

[#190](https://github.com/tricore-opentrix/opentrix/issues/190) theo dõi release dự thi; [#138](https://github.com/tricore-opentrix/opentrix/issues/138) theo dõi quyền nguồn gốc; [#119](https://github.com/tricore-opentrix/opentrix/issues/119) theo dõi demo stack; các cổng này **độc lập** với việc merge tài liệu #194.

---

<a id="en"></a>

## English

### 1. Release status (AS-IS / UNVERIFIED)

#### Feature status matrix / Bảng trạng thái tính năng (AS-IS / UNVERIFIED / PROPOSED)

| Component | Existing source | Verification / limits |
| --- | --- | --- |
| Identity / Keycloak | Backend [OIDC](../backend/src/main/resources/application.yml), BFF [OAuth client](../portal-bff/src/main/resources/application.yml) | **SOURCE IMPLEMENTED**; real three-principal browser login **LIVE E2E UNVERIFIED** ([#118](https://github.com/tricore-opentrix/opentrix/issues/118)) |
| Workflow Core | `WorkflowRuntime`, `WorkflowPersistencePort`, PostgreSQL adapter and test sources ([Backend](../backend/README.md)) | **SOURCE IMPLEMENTED / TEST-LEVEL**; does not prove Flowable/E2E |
| Helpdesk | `/api/v1/mvp/requests` when `dxos.helpdesk.enabled` is enabled, authorization/version tests | **SOURCE IMPLEMENTED / TEST-LEVEL**; real Golden Path **UNVERIFIED** |
| Portal Frontend | [Frontend](../frontend/package.json): MOCK and `integration-local` build | MOCK uses synthetic data; bundle build is not proof of runtime integration |
| Portal BFF | [BFF](../portal-bff/README.md): OAuth/PKCE, session, CSRF, fixture test | **TEST-LEVEL**; Keycloak/browser/DB **LIVE E2E UNVERIFIED** |
| PostgreSQL / Flyway | [Compose](../infra/compose.workflow-postgres.yml), migration Workflow V1–V4/Helpdesk SQL | **SOURCE IMPLEMENTED**; same-SHA schema/ACL/restart evidence pending |
| Docker Compose | `infra/compose.workflow-postgres.yml`: Workflow PostgreSQL only | Full-stack Compose **PROPOSED** [#119](https://github.com/tricore-opentrix/opentrix/issues/119) |
| APISIX / Flowable | No accepted integrated runtime; Workflow uses an in-house engine | **PROPOSED** [APISIX #116](https://github.com/tricore-opentrix/opentrix/issues/116) / [Flowable #191](https://github.com/tricore-opentrix/opentrix/issues/191) |

SOURCE IMPLEMENTED = source exists; TEST-LEVEL = recorded test scope only; UNVERIFIED ≠ FAIL. Sources: [Block B](09-evidence/phase-2/block-b-backend-infra.md) / [Block C](09-evidence/phase-2/block-c-application.md).




**Version status / Bảng phiên bản** (GitHub Releases checked 2026-11-12):

| Version | Status | Scope and evidence |
| --- | --- | --- |
| [`v0.1.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) | **Released — pre-release**, not stable | Public GitHub Release **2026-11-04**, 2 assets at check; MVP scope in [root README](../README.md), not LIVE E2E acceptance |
| `v0.2.0` | **In development / Not released** | SOURCE-ONLY is a **conditional planned candidate scope** under [R24](06-deployment/r24-release.md); distribution blocked pending [#138](https://github.com/tricore-opentrix/opentrix/issues/138)/[#190](https://github.com/tricore-opentrix/opentrix/issues/190) |
| `v0.3.0+` | **Planned / PROPOSED** | No accepted tag/scope/publication commitment; future features are not shipped |


| Item | Supportable status | Not implied |
| --- | --- | --- |
| [`v0.1.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) | Historical public **pre-release**, not the stable competition submission ([#190](https://github.com/tricore-opentrix/opentrix/issues/190)) | Not current `RELEASE_ACCEPTED` |
| R23, SPDX/REUSE | License-policy/SBOM/notices and metadata checks in [`ci.yml`](../.github/workflows/ci.yml); [Phase 2 Block B](09-evidence/phase-2/block-b-backend-infra.md) | Green CI does not establish source ownership or distribution permission |
| R24 candidate | [`release.yml`](../.github/workflows/release.yml) and [`r24-release.py`](../scripts/r24-release.py) create/verify archives with fail-closed gate | Candidate PASS does not authorize publishing |
| `v0.2.0` | **SOURCE-ONLY target, not verified as published**; [#190](https://github.com/tricore-opentrix/opentrix/issues/190) and [#138](https://github.com/tricore-opentrix/opentrix/issues/138) remain open at inspection | No claim of release, rights clearance, JAR/`frontend/dist`/GHCR permission |

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
2. **Provenance:** [#138](https://github.com/tricore-opentrix/opentrix/issues/138) needs independently reviewed source/rightsholder/attribution evidence. `reuse lint` and an allowed dependency list are **not legal clearance**.
3. **Freeze source SHA:** bind the candidate digest to a full commit; two independently generated candidates must use the **same source SHA** before claiming reproducibility.
4. **Separate acceptance on `main`:** after source freeze, a separately reviewed PR must add `docs/06-deployment/r24-acceptances/<tag>.json` to `main`. Required fields include `tag`, `source_sha`, `mode`, `archive_sha256`, `reviewed_by`, and HTTPS evidence for that mode. Assertions in JSON alone are not proof of approval.
5. **Protected publishing:** verify configured `r24-release` Environment, required reviewers and tag protection **before** creating a tag. Declaring an environment in YAML does **not** prove its protection settings exist.
6. **Verify before publication:** exact archive/hash/MANIFEST member checksums/notes, tag/SHA/mode, #138 provenance and independent review. Missing or mismatching evidence means **BLOCKED**.

Updating documentation or passing CI does not authorize tag creation, GitHub Release, GHCR publishing or database migration.

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

### 5. Release notes, operations and final verdict

- Packager derives release notes from the version section of [`CHANGELOG.md`](../CHANGELOG.md). Before freezing the source SHA, verify the date, delivered scope, MOCK/LIVE limits, #138 rights status, source-only boundary and attribution. Do not add unsupported claims.
- For `v0.2.0`, do not advertise JARs, frontend build, GHCR, Flowable, APISIX, an S3 provider or E2E as shipped without separate acceptance.
- GHCR and GitHub Release publishing is not atomic in binary mode. On a partial failure record exact digests/states, stop for reconciliation, and **do not blindly retry**.
- Preserve: tag/full source SHA, run URLs, acceptance PR/reviewers, archive SHA-256, SHA256SUMS, MANIFEST, notes, mode, actual asset URLs, and `PASS / BLOCKED / UNVERIFIED` verdict.

**`RELEASE_ACCEPTED` requires** cleared provenance, repeatability, exact-SHA acceptance, independent review, authorized tag/release and verified downloaded assets. The competition release has **not** met that verdict at this inspected state; see [#190](https://github.com/tricore-opentrix/opentrix/issues/190).

### 6. Target — PROPOSED

[#190](https://github.com/tricore-opentrix/opentrix/issues/190) tracks the competition release, [#138](https://github.com/tricore-opentrix/opentrix/issues/138) tracks source rights, and [#119](https://github.com/tricore-opentrix/opentrix/issues/119) tracks the full demo stack. These gates are **separate** from merging documentation under #194.
