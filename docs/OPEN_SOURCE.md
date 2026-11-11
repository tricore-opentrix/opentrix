<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# OpenTrix open source and compliance

[Documentation index](README.md) · [Architecture](ARCHITECTURE.md) · [Release](RELEASE.md)

> **Ngôn ngữ / Language:** [Tiếng Việt](#nguồn-mở-và-tuân-thủ--tiếng-việt) · [English](#open-source-and-compliance--english)

---

## Nguồn mở và tuân thủ — Tiếng Việt

[Mục lục tài liệu](README.md) · [Kiến trúc](ARCHITECTURE.md) · [Phát hành](RELEASE.md)

**Trạng thái xuất bản:** Repo đã có giấy phép, metadata SPDX/REUSE và cổng giấy phép phụ thuộc chạy trong CI. Bản công khai duy nhất là `v0.1.0` **pre-release**. Quyền nguồn gốc mã (#138) và bản dự thi (#190) **chưa hoàn tất**; các cổng dưới đây mô tả điều kiện phải đạt, không khẳng định đã đạt. Bằng chứng: B-018…B-021 trong [block-b-backend-infra.md](09-evidence/phase-2/block-b-backend-infra.md), POF-1…POF-6 trong [block-a-architecture.md](09-evidence/phase-2/block-a-architecture.md).

### 1. Ranh giới repo

- Mã nguồn OpenTrix — DX-OS Open-Core phát hành theo **Apache License 2.0** (SPDX: `Apache-2.0`).
- [`LICENSE`](../LICENSE) chứa toàn văn giấy phép; [`LICENSES/Apache-2.0.txt`](../LICENSES/Apache-2.0.txt) là bản sao theo REUSE, trùng điều khoản với `LICENSE`, chỉ khác cách xuống dòng.
- [`NOTICE`](../NOTICE) ghi công `Copyright 2026 TRICORE contributors` cho phần mã gốc. Thông báo của bên thứ ba nằm riêng trong [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md).
- Thư viện, container image và dịch vụ bên ngoài **giữ giấy phép riêng**; giấy phép Apache-2.0 của repo không thay đổi giấy phép của chúng.
- Đóng góp được nhận và phân phối theo điều 5 của Apache-2.0. Repo **không** yêu cầu CLA; [`CONTRIBUTING.md`](../CONTRIBUTING.md) hiện **không** yêu cầu DCO hay `Signed-off-by`.

### 2. Ranh giới self-hosting

- Thành phần trong repo: backend Spring Boot, Portal BFF, React Portal.
- Dịch vụ chạy tách biệt: **Keycloak** (danh tính) và **PostgreSQL** (dữ liệu). Chúng không được đóng gói vào mã nguồn và **nằm ngoài cổng R23**; image và giấy phép của chúng phải được rà soát thủ công.
- Chưa phân phối bản nhị phân (JAR, container image) cho tới khi #138 và #190 hoàn tất.

### 3. Vệ sinh giấy phép: header SPDX và REUSE

- Repo theo đặc tả **REUSE**: giấy phép nằm trong [`LICENSES/`](../LICENSES/); tệp không chèn được header được khai báo trong [`REUSE.toml`](../REUSE.toml).
- Mọi tệp nguồn mới do người đóng góp tự viết phải có header SPDX. Java/TypeScript dùng `//`, SQL dùng `--`, YAML/shell dùng `#`, Markdown dùng comment HTML ở dòng đầu (như đầu tệp này):

  ```text
  SPDX-FileCopyrightText: 2026 TRICORE contributors
  SPDX-License-Identifier: Apache-2.0
  ```

- CI chạy bước `REUSE licensing check` (`fsfe/reuse-action@v5`) trong job **`repo-hygiene`** của [`ci.yml`](../.github/workflows/ci.yml); lỗi REUSE làm job thất bại. Tại baseline `main@832c75f`: 338/338 tệp có metadata, 0 giấy phép bị thiếu (B-018).
- Kiểm tra trên máy: `reuse lint`, hoặc `docker run --rm -v "${PWD}:/data" fsfe/reuse lint`.
- **Không** gắn header TRICORE cho mã bên ngoài hoặc mã chưa xác minh quyền.

### 4. Chính sách phụ thuộc

- Phụ thuộc chỉ được khai báo qua trình quản lý chuẩn: Gradle ([`backend/build.gradle`](../backend/build.gradle), [`portal-bff/build.gradle`](../portal-bff/build.gradle)) và npm ([`frontend/package.json`](../frontend/package.json) cùng `package-lock.json`). Không commit thư mục `vendor/`, `third_party/` hay `lib/`.
- Giấy phép phụ thuộc phải nằm trong danh sách được phép ghi ở `CONTRIBUTING.md`.
- Job **`r23-compliance`** trong `ci.yml` thực thi chính sách này:
  1. Chạy canary test `scripts/test_r23_*.py`.
  2. Sinh SBOM CycloneDX: plugin `org.cyclonedx.bom` 3.5.1 cho backend và portal-bff; `@cyclonedx/cyclonedx-npm@6.0.1 --omit dev` cho frontend.
  3. Chạy [`scripts/r23-compliance.py`](../scripts/r23-compliance.py) để đối chiếu với danh sách được phép.
  4. So `THIRD-PARTY-NOTICES.md` với bản vừa sinh bằng `diff -u`.
- Artifact CI **`r23-sbom-and-notices`** (giữ 30 ngày) gồm ba SBOM (`backend`, `portal-bff`, `frontend-sbom.json`), `THIRD-PARTY-NOTICES.md` và `license-inventory.json`.
- `THIRD-PARTY-NOTICES.md` là bảng kiểm kê sinh tự động, **không phải** xác nhận pháp lý. Inventory gồm 131 thành phần thuộc ba phạm vi phụ thuộc, không phải 131 thư viện đóng gói vào bản phát hành (B-019).

### 5. Tệp nhị phân và tệp giữ nguyên byte

| Tệp | Nguồn gốc | Giấy phép / ghi công | Ghi chú |
| --- | --- | --- | --- |
| `backend/gradle/wrapper/gradle-wrapper.jar` | Gradle 8.14.3 wrapper chính thức | `SPDX-FileCopyrightText = "Gradle contributors"` (qua `REUSE.toml`) | Tệp nhị phân duy nhất được commit; kiểm tra bằng `gradle/actions/wrapper-validation@v6` trong `r23-compliance` và job `candidate` của `release.yml` (B-020) |
| Migration Flyway `V1`–`V4`, tệp SQL evidence | Mã của nhóm | Khai báo qua `REUSE.toml` | Phải giữ nguyên byte nên không chèn header |
| `package.json`, `package-lock.json`, `favicon.svg`, `.gitignore` và một số tệp khác | Mã/tài sản của nhóm | Khai báo qua `REUSE.toml` | Định dạng không cho phép comment hoặc phải giữ nguyên byte |

Portal BFF không có wrapper riêng; CI build bằng wrapper của backend (HYG-01). `repo-hygiene` kiểm tra `backend/gradlew` có quyền thực thi.

### 6. Cổng xuất bản

Bản dự thi được theo dõi tại [#190](https://github.com/tricore-opentrix/opentrix/issues/190). Chỉ công bố khi đạt đủ:

1. **Thông quyền nguồn gốc:** hoàn tất #138 — đối chiếu mã với upstream, xác nhận bản quyền và ghi công. Lint REUSE và R23 đạt **không** đồng nghĩa với `RIGHTS_CLEARED` hay `RELEASE_ACCEPTED` (B-020, B-021).
2. **Gắn tag đúng chuẩn:** tag SemVer mới, **không** đánh dấu pre-release.
3. **Đính kèm đủ tệp:** `.tar.gz`, `SHA256SUMS`, SBOM và `NOTICE`. Gói ứng viên `r24-candidate-<run_id>` của [`release.yml`](../.github/workflows/release.yml) đã chứa `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES.md` và `compliance/*.cdx.json`.
4. **Qua cổng R24:** job `publish` chỉ chạy với tag `v*` kèm manifest chấp thuận `docs/06-deployment/r24-acceptances/<tag>.json` trên `main`; thư mục này **chưa có** trên `origin/main`. Riêng `v0.2.0` bị ép chế độ `source-only` (không JAR, không đẩy image lên GHCR). Release notes phải ghi đúng trạng thái #138.

Người đóng góp chỉ đưa vào mã, dữ liệu và tài sản mình có quyền đóng góp; **không** sao chép code, template, icon hay asset từ dự án khác; **không** xóa hoặc sửa ghi công, bản quyền hay thông tin công bố về việc dùng AI để che giấu nguồn gốc (B-021).

Bản công khai hiện có là [`v0.1.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) — pre-release ngày 2026-11-04, asset `dxos-open-core-0.1.0.tar.gz` và `SHA256SUMS`, còn một bản Draft trùng tag (POF-3). Đây **không phải** bản dự thi.

| Hạng mục | Hiện trạng | Bằng chứng / Issue |
| --- | --- | --- |
| Toàn văn giấy phép | ✅ `LICENSE`, `LICENSES/Apache-2.0.txt` | B-019, POF-2 |
| Ghi công dự án | ✅ `NOTICE` | B-019 |
| SPDX/REUSE từng tệp | ✅ `repo-hygiene` đạt, 338/338 tệp | B-018, POF-2 |
| Cổng giấy phép phụ thuộc | ✅ `r23-compliance` đạt | B-019, POF-5 |
| SBOM + third-party notices | ✅ Artifact CI 30 ngày · ⏳ chưa đính vào release | POF-5, #190 |
| Xác thực Gradle wrapper | ✅ `wrapper-validation@v6` | B-020 |
| Đối chiếu mã với upstream | ⏳ Chưa thực hiện | B-020, #138 |
| Thông quyền nguồn gốc | ⏳ Chưa thông quyền | B-021, #138 |
| Bản dự thi (SemVer, không pre-release) | ⏳ Chưa phát hành | POF-3, #190 |

Tài liệu này không khẳng định đã qua rà soát pháp lý hay bảo mật.

---

## Open source and compliance — English

[Documentation index](README.md) · [Architecture](ARCHITECTURE.md) · [Release](RELEASE.md)

**Publication status:** The repository has its license, SPDX/REUSE metadata and a dependency-license gate running in CI. The only public release is the `v0.1.0` **pre-release**. Source-rights clearance (#138) and the competition release (#190) are **not complete**; the gates below state what must hold, not that it holds. Evidence: B-018…B-021 in [block-b-backend-infra.md](09-evidence/phase-2/block-b-backend-infra.md), POF-1…POF-6 in [block-a-architecture.md](09-evidence/phase-2/block-a-architecture.md).

### 1. Repository boundary

- OpenTrix — DX-OS Open-Core source is released under the **Apache License 2.0** (SPDX: `Apache-2.0`).
- [`LICENSE`](../LICENSE) holds the full license text; [`LICENSES/Apache-2.0.txt`](../LICENSES/Apache-2.0.txt) is the REUSE copy, with the same terms and different line wrapping.
- [`NOTICE`](../NOTICE) attributes original material to `Copyright 2026 TRICORE contributors`. Third-party notices are kept separately in [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md).
- Libraries, container images and external services **keep their own licenses**; the repository's Apache-2.0 license does not change them.
- Contributions are accepted and distributed under section 5 of Apache-2.0. **No** CLA is required; [`CONTRIBUTING.md`](../CONTRIBUTING.md) currently does **not** require DCO or `Signed-off-by`.

### 2. Self-hosting boundary

- In the repository: the Spring Boot backend, Portal BFF and React Portal.
- Running separately: **Keycloak** (identity) and **PostgreSQL** (data). They are not bundled with the source and are **outside the R23 gate**; their images and licenses must be reviewed manually.
- No binaries (JARs, container images) are distributed until #138 and #190 are complete.

### 3. Licensing hygiene: SPDX headers and REUSE

- The repository follows the **REUSE** specification: licenses live in [`LICENSES/`](../LICENSES/); files that cannot carry a header are declared in [`REUSE.toml`](../REUSE.toml).
- Every new source file a contributor writes must carry an SPDX header. Java/TypeScript use `//`, SQL uses `--`, YAML/shell use `#`, Markdown uses an HTML comment on the first line (as at the top of this file):

  ```text
  SPDX-FileCopyrightText: 2026 TRICORE contributors
  SPDX-License-Identifier: Apache-2.0
  ```

- CI runs the `REUSE licensing check` step (`fsfe/reuse-action@v5`) in the **`repo-hygiene`** job of [`ci.yml`](../.github/workflows/ci.yml); a REUSE error fails the job. At baseline `main@832c75f`: 338/338 files with metadata, 0 missing licenses (B-018).
- Local check: `reuse lint`, or `docker run --rm -v "${PWD}:/data" fsfe/reuse lint`.
- **Never** apply the TRICORE header to external code or code whose rights are unverified.

### 4. Dependency policy

- Dependencies are declared only through standard managers: Gradle ([`backend/build.gradle`](../backend/build.gradle), [`portal-bff/build.gradle`](../portal-bff/build.gradle)) and npm ([`frontend/package.json`](../frontend/package.json) with `package-lock.json`). No `vendor/`, `third_party/` or `lib/` directory is committed.
- Dependency licenses must be on the allow-list in `CONTRIBUTING.md`.
- The **`r23-compliance`** job in `ci.yml` enforces this policy:
  1. Runs the canary tests `scripts/test_r23_*.py`.
  2. Generates CycloneDX SBOMs: the `org.cyclonedx.bom` 3.5.1 plugin for backend and portal-bff; `@cyclonedx/cyclonedx-npm@6.0.1 --omit dev` for the frontend.
  3. Runs [`scripts/r23-compliance.py`](../scripts/r23-compliance.py) against the allow-list.
  4. Compares `THIRD-PARTY-NOTICES.md` with the freshly generated copy using `diff -u`.
- The CI artifact **`r23-sbom-and-notices`** (kept 30 days) holds three SBOMs (`backend`, `portal-bff`, `frontend-sbom.json`), `THIRD-PARTY-NOTICES.md` and `license-inventory.json`.
- `THIRD-PARTY-NOTICES.md` is a generated inventory, **not** a legal certification. The inventory covers 131 components across three dependency scopes, not 131 libraries shipped in a release (B-019).

### 5. Binary and byte-preserved files

| File | Origin | License / attribution | Note |
| --- | --- | --- | --- |
| `backend/gradle/wrapper/gradle-wrapper.jar` | Official Gradle 8.14.3 wrapper | `SPDX-FileCopyrightText = "Gradle contributors"` (via `REUSE.toml`) | The only committed binary; validated by `gradle/actions/wrapper-validation@v6` in `r23-compliance` and in the `candidate` job of `release.yml` (B-020) |
| Flyway migrations `V1`–`V4`, SQL evidence files | Team code | Declared in `REUSE.toml` | Must stay byte-identical, so no inline header |
| `package.json`, `package-lock.json`, `favicon.svg`, `.gitignore` and a few others | Team code/assets | Declared in `REUSE.toml` | Format does not allow comments or must stay byte-identical |

Portal BFF has no wrapper of its own; CI builds it with the backend wrapper (HYG-01). `repo-hygiene` checks that `backend/gradlew` is executable.

### 6. Publication gate

The competition release is tracked in [#190](https://github.com/tricore-opentrix/opentrix/issues/190). It is published only when all of these hold:

1. **Clear source rights:** complete #138 — compare the source with upstream, confirm copyright and attribution. Passing REUSE lint and R23 does **not** mean `RIGHTS_CLEARED` or `RELEASE_ACCEPTED` (B-020, B-021).
2. **Tag correctly:** a new SemVer tag, **not** marked pre-release.
3. **Attach every file:** `.tar.gz`, `SHA256SUMS`, SBOM and `NOTICE`. The `r24-candidate-<run_id>` package from [`release.yml`](../.github/workflows/release.yml) already contains `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES.md` and `compliance/*.cdx.json`.
4. **Pass the R24 gate:** the `publish` job runs only on a `v*` tag with an acceptance manifest at `docs/06-deployment/r24-acceptances/<tag>.json` on `main`; that directory **does not yet exist** on `origin/main`. `v0.2.0` is forced into `source-only` mode (no JARs, no GHCR images). Release notes must state the actual status of #138.

Contributors submit only code, data and assets they have the right to contribute; **never** copy code, templates, icons or assets from other projects; **never** remove or alter attribution, copyright or AI-use disclosures to conceal origin (B-021).

The current public release is [`v0.1.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) — a pre-release from 2026-11-04 with assets `dxos-open-core-0.1.0.tar.gz` and `SHA256SUMS`, plus a duplicate Draft for the same tag (POF-3). It is **not** the competition release.

| Item | Status | Evidence / Issue |
| --- | --- | --- |
| Full license text | ✅ `LICENSE`, `LICENSES/Apache-2.0.txt` | B-019, POF-2 |
| Project attribution | ✅ `NOTICE` | B-019 |
| Per-file SPDX/REUSE | ✅ `repo-hygiene` passes, 338/338 files | B-018, POF-2 |
| Dependency license gate | ✅ `r23-compliance` passes | B-019, POF-5 |
| SBOM + third-party notices | ✅ 30-day CI artifact · ⏳ not yet attached to a release | POF-5, #190 |
| Gradle wrapper validation | ✅ `wrapper-validation@v6` | B-020 |
| Source comparison with upstream | ⏳ Not done | B-020, #138 |
| Source-rights clearance | ⏳ Not cleared | B-021, #138 |
| Competition release (SemVer, not pre-release) | ⏳ Not released | POF-3, #190 |

This document does not assert that any legal or security review has passed.
