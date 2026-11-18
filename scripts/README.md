<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Scripts

> **Language / Ngôn ngữ:** [English](#en) · [Tiếng Việt](#vi)

---

<a id="en"></a>

## Overview

Helper scripts for local verification, compliance checks, release packaging and repository maintenance. Builds and tests use the Gradle Wrapper in [`backend/`](https://github.com/tricore-opentrix/opentrix/tree/main/backend); none of these scripts is required to build the project.

Run every script from the repository root. Detailed prerequisites, expected output and the scripts' place in the test plan are documented in [docs/TESTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/TESTING.md) and [docs/DEVELOPMENT.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/DEVELOPMENT.md).

### Local verification

| Script                           | Purpose                                                                                                                                                                                                                                                                                                     | Requirements                                    |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `workflow-verify-local.ps1`      | Starts a disposable PostgreSQL 17 on loopback with generated TLS certificates and credentials, runs the full backend `test build`, then removes the fixture. Fails if any workflow integration suite fails or is skipped.                                                                                   | Docker, JDK 21, OpenSSL                         |
| `helpdesk-local-setup.ps1`       | Prepares a new local PostgreSQL container and volume for the IT Helpdesk. Read-only preflight by default; `-Execute -ConfirmDemoDatabase` creates resources and writes the schema. See [README-helpdesk-local.md](https://github.com/tricore-opentrix/opentrix/blob/main/scripts/README-helpdesk-local.md). | Docker Desktop, JDK 21                          |
| `helpdesk-local-actor-seed.ps1`  | Prints the SQL statements that register the Employee, Coordinator and Worker actors, from their Keycloak subjects, in a local Helpdesk schema. It does not connect to a database.                                                                                                                           | Keycloak issuer URL and the three user subjects |
| `helpdesk-negative-local.ps1`    | Runs the Helpdesk HTTP and PostgreSQL negative tests against a new disposable database. Keeps the container and volume for inspection.                                                                                                                                                                      | Docker Desktop, JDK 21                          |
| `helpdesk-b06-local.ps1`         | Opt-in run of the focused Helpdesk configuration and HTTP/PostgreSQL tests with real access tokens; removes its own container afterwards.                                                                                                                                                                   | Docker, JDK 21, access tokens                   |
| `gateway-smoke.ps1`              | Smoke test for the Apache APISIX gateway; correlates HTTP responses with gateway logs.                                                                                                                                                                                                                      | PowerShell 7.2+, Docker log access              |
| `poc/keycloak-auth-code-poc.ps1` | Proof of concept for the OIDC authorization code flow against the local Keycloak realm.                                                                                                                                                                                                                     | Local Keycloak                                  |

### Compliance and release

These scripts are run by CI ([`ci.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/.github/workflows/ci.yml), [`release.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/.github/workflows/release.yml)). The release process is described in [docs/RELEASE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/RELEASE.md).

| Script              | Purpose                                                                                                                                                                                         |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `r23-compliance.py` | Checks dependency licenses in the CycloneDX SBOMs against the allow-list and generates [THIRD-PARTY-NOTICES.md](https://github.com/tricore-opentrix/opentrix/blob/main/THIRD-PARTY-NOTICES.md). |
| `r24-upstream.py`   | Collects upstream LICENSE and NOTICE files for release review; never fills in missing texts.                                                                                                    |
| `r24-release.py`    | Builds reproducible release archives (`dxos-open-core-<version>.tar.gz`), verifies checksums and applies the release gate.                                                                      |

### Tests for the scripts

| Tests                | Command                                                                     |
| -------------------- | --------------------------------------------------------------------------- |
| Compliance           | `python3 -m unittest discover -s scripts -p 'test_r23_*.py'`                |
| Release              | `python3 -m unittest discover -s scripts -p 'test_r24_*.py'` (needs PyYAML) |
| Keycloak login theme | `python3 -m unittest discover -s scripts -p 'test_opentrix_*.py'`           |
| Gateway smoke        | `pwsh -File scripts/test-gateway-smoke.ps1`                                 |
| Helpdesk actor seed  | `pwsh -File scripts/test-helpdesk-local-actor-seed.ps1`                     |

CI runs the Python tests ([`ci.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/.github/workflows/ci.yml), [`release.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/.github/workflows/release.yml)).

### Repository maintenance

| Script                  | Purpose                                                                                                                                                                    | Requirements                    |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| `setup-github.sh`       | Configures repository metadata, topics, labels and milestones. Use `DRY_RUN=1` to preview. Branch protection is configured manually.                                       | Authenticated GitHub CLI (`gh`) |
| `git-cleanup-report.sh` | Reports cleanup candidates: merged or inactive branches, long-open draft pull requests and Issues without an assignee or milestone. Prints commands only; changes nothing. | git, authenticated GitHub CLI   |

### Remote database operations

The `workflow-*.ps1` scripts below operate on a remote PostgreSQL database over TLS (`verify-full`). They read connection settings from the `DB_*` and `PGSSLROOTCERT` environment variables and never accept passwords as parameters.

| Script                                 | Purpose                                                                    |
| -------------------------------------- | -------------------------------------------------------------------------- |
| `workflow-read-only-preflight.ps1`     | Read-only connection and TLS check.                                        |
| `workflow-live-guard.ps1`              | Read-only check of the reviewed database catalog.                          |
| `workflow-runtime-privilege-audit.ps1` | Read-only audit of runtime role privileges.                                |
| `workflow-security-definer-review.ps1` | Read-only review of `SECURITY DEFINER` functions.                          |
| `workflow-event-trigger-review.ps1`    | Read-only review of event triggers.                                        |
| `workflow-schema-bootstrap.ps1`        | Creates the empty workflow schema.                                         |
| `workflow-approved-migrations.ps1`     | Applies the approved Flyway migrations.                                    |
| `workflow-approved-smoke.ps1`          | Runs the approved write smoke test, or `-AuditOnly` for a read-only check. |

> **Warning:** `workflow-schema-bootstrap.ps1`, `workflow-approved-migrations.ps1` and `workflow-approved-smoke.ps1` were written for a single approved operation on one environment. That operation is complete. Do not run them again.

---

<a id="vi"></a>

## Tổng quan

Các script hỗ trợ kiểm tra cục bộ, kiểm tra tuân thủ, đóng gói phát hành và bảo trì kho mã. Build và test dùng Gradle Wrapper trong [`backend/`](https://github.com/tricore-opentrix/opentrix/tree/main/backend); không script nào là bắt buộc để build dự án.

Chạy mọi script từ thư mục gốc của kho mã. Điều kiện tiên quyết, kết quả mong đợi và vị trí của từng script trong kế hoạch kiểm thử được mô tả chi tiết trong [docs/TESTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/TESTING.md) và [docs/DEVELOPMENT.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/DEVELOPMENT.md).

### Kiểm tra cục bộ

| Script                           | Mục đích                                                                                                                                                                                                                                                                             | Yêu cầu                                              |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------- |
| `workflow-verify-local.ps1`      | Khởi tạo PostgreSQL 17 dùng một lần trên loopback, kèm chứng chỉ TLS và thông tin đăng nhập sinh ngẫu nhiên; chạy toàn bộ `test build` của backend rồi dọn fixture. Thất bại nếu bất kỳ bộ integration test nào của workflow lỗi hoặc bị bỏ qua.                                     | Docker, JDK 21, OpenSSL                              |
| `helpdesk-local-setup.ps1`       | Chuẩn bị container và volume PostgreSQL mới cho IT Helpdesk. Mặc định chỉ chạy preflight đọc; `-Execute -ConfirmDemoDatabase` tạo tài nguyên và ghi schema. Xem [README-helpdesk-local.md](https://github.com/tricore-opentrix/opentrix/blob/main/scripts/README-helpdesk-local.md). | Docker Desktop, JDK 21                               |
| `helpdesk-local-actor-seed.ps1`  | In ra các câu lệnh SQL để đăng ký actor Employee, Coordinator và Worker, theo subject của họ trong Keycloak, vào schema Helpdesk cục bộ. Script không kết nối tới database.                                                                                                          | URL issuer của Keycloak và subject của ba người dùng |
| `helpdesk-negative-local.ps1`    | Chạy các test âm tính HTTP và PostgreSQL của Helpdesk trên database dùng một lần mới. Giữ lại container và volume để kiểm tra.                                                                                                                                                       | Docker Desktop, JDK 21                               |
| `helpdesk-b06-local.ps1`         | Chạy tùy chọn các test cấu hình và HTTP/PostgreSQL của Helpdesk với access token thật; tự xóa container của mình sau khi chạy.                                                                                                                                                       | Docker, JDK 21, access token                         |
| `gateway-smoke.ps1`              | Smoke test cho gateway Apache APISIX; đối chiếu phản hồi HTTP với log của gateway.                                                                                                                                                                                                   | PowerShell 7.2+, quyền đọc log Docker                |
| `poc/keycloak-auth-code-poc.ps1` | Bản thử nghiệm luồng OIDC authorization code với realm Keycloak cục bộ.                                                                                                                                                                                                              | Keycloak cục bộ                                      |

### Tuân thủ và phát hành

Các script này được CI chạy ([`ci.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/.github/workflows/ci.yml), [`release.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/.github/workflows/release.yml)). Quy trình phát hành được mô tả trong [docs/RELEASE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/RELEASE.md).

| Script              | Mục đích                                                                                                                                                                                           |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `r23-compliance.py` | Kiểm tra giấy phép của các phụ thuộc trong SBOM CycloneDX theo danh sách cho phép và sinh [THIRD-PARTY-NOTICES.md](https://github.com/tricore-opentrix/opentrix/blob/main/THIRD-PARTY-NOTICES.md). |
| `r24-upstream.py`   | Thu thập tệp LICENSE và NOTICE gốc từ upstream để rà soát trước khi phát hành; không tự điền văn bản còn thiếu.                                                                                    |
| `r24-release.py`    | Đóng gói bản phát hành tái lập được (`dxos-open-core-<version>.tar.gz`), kiểm tra checksum và áp dụng điều kiện phát hành.                                                                         |

### Kiểm thử cho các script

| Nhóm test                    | Lệnh                                                                      |
| ---------------------------- | ------------------------------------------------------------------------- |
| Tuân thủ                     | `python3 -m unittest discover -s scripts -p 'test_r23_*.py'`              |
| Phát hành                    | `python3 -m unittest discover -s scripts -p 'test_r24_*.py'` (cần PyYAML) |
| Giao diện đăng nhập Keycloak | `python3 -m unittest discover -s scripts -p 'test_opentrix_*.py'`         |
| Gateway smoke                | `pwsh -File scripts/test-gateway-smoke.ps1`                               |
| Seed actor Helpdesk          | `pwsh -File scripts/test-helpdesk-local-actor-seed.ps1`                   |

CI chạy các test Python ([`ci.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/.github/workflows/ci.yml), [`release.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/.github/workflows/release.yml)).

### Bảo trì kho mã

| Script                  | Mục đích                                                                                                                                                                        | Yêu cầu                        |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| `setup-github.sh`       | Cấu hình metadata, topic, label và milestone của kho mã. Dùng `DRY_RUN=1` để xem trước. Branch protection được cấu hình thủ công.                                               | GitHub CLI (`gh`) đã đăng nhập |
| `git-cleanup-report.sh` | Liệt kê các mục cần dọn: nhánh đã merge hoặc không còn hoạt động, pull request nháp mở quá lâu và Issue chưa có người phụ trách hoặc milestone. Chỉ in lệnh, không thay đổi gì. | git, GitHub CLI đã đăng nhập   |

### Thao tác trên database từ xa

Các script `workflow-*.ps1` dưới đây làm việc với database PostgreSQL từ xa qua TLS (`verify-full`). Chúng đọc thông tin kết nối từ biến môi trường `DB_*` và `PGSSLROOTCERT`, không nhận mật khẩu qua tham số.

| Script                                 | Mục đích                                                                  |
| -------------------------------------- | ------------------------------------------------------------------------- |
| `workflow-read-only-preflight.ps1`     | Kiểm tra kết nối và TLS, chỉ đọc.                                         |
| `workflow-live-guard.ps1`              | Kiểm tra catalog database đã được rà soát, chỉ đọc.                       |
| `workflow-runtime-privilege-audit.ps1` | Rà soát quyền của role runtime, chỉ đọc.                                  |
| `workflow-security-definer-review.ps1` | Rà soát các hàm `SECURITY DEFINER`, chỉ đọc.                              |
| `workflow-event-trigger-review.ps1`    | Rà soát event trigger, chỉ đọc.                                           |
| `workflow-schema-bootstrap.ps1`        | Tạo schema workflow rỗng.                                                 |
| `workflow-approved-migrations.ps1`     | Áp dụng các migration Flyway đã được duyệt.                               |
| `workflow-approved-smoke.ps1`          | Chạy smoke test ghi đã được duyệt, hoặc `-AuditOnly` để kiểm tra chỉ đọc. |

> **Cảnh báo:** `workflow-schema-bootstrap.ps1`, `workflow-approved-migrations.ps1` và `workflow-approved-smoke.ps1` được viết cho một lần thao tác đã duyệt trên một môi trường cụ thể. Thao tác đó đã hoàn tất. Không chạy lại các script này.
