<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Scripts — hướng dẫn / Scripts guide

> **Status / Trạng thái:** DRAFT, AS-IS inventory, no scripts executed for this edit · [#194](https://github.com/tricore-opentrix/opentrix/issues/194), [#197](https://github.com/tricore-opentrix/opentrix/issues/197)
>
> [Development](../docs/DEVELOPMENT.md) · [Testing](../docs/TESTING.md) · [Deployment](../docs/DEPLOYMENT.md) · [Release](../docs/RELEASE.md) · [Workflow archive](../backend/legacy-workflow-runbook.md)

## Tiếng Việt

### 1. Tìm đúng script, phân loại mức rủi ro

| Nhóm file hiện có | Chức năng / điều kiện | Mức rủi ro |
| --- | --- | --- |
| [`README-helpdesk-local.md`](README-helpdesk-local.md), [`helpdesk-local-setup.ps1`](helpdesk-local-setup.ps1) | Mô tả/preflight Helpdesk disposable; `-Execute -ConfirmDemoDatabase` tạo resource/ghi schema | **GHI DB** khi execute; xác nhận owner, tên/port/volume/labels |
| [`helpdesk-negative-local.ps1`](helpdesk-negative-local.ps1), [`helpdesk-b06-local.ps1`](helpdesk-b06-local.ps1) | Opt-in kiểm chứng HTTP/DB/identity | Có thể tạo tài nguyên hoặc ghi dữ liệu fixture; đọc chính xác script/runbook trước |
| [`workflow-verify-local.ps1`](workflow-verify-local.ps1) | Fixture PostgreSQL 17.11 dùng một lần với TLS/CA và JDK21; test/build | **TẠO/XÓA** fixture thuộc lượt chạy; cần Docker, JDK21, OpenSSL; không chạy cloud |
| [`workflow-read-only-preflight.ps1`](workflow-read-only-preflight.ps1), [`workflow-runtime-privilege-audit.ps1`](workflow-runtime-privilege-audit.ps1), [`workflow-security-definer-review.ps1`](workflow-security-definer-review.ps1) | Công cụ kiểm tra/catalog cho Workflow theo cấu hình có kiểm soát | Chỉ dùng endpoint được phép; kiểm tra script và quyền trước khi nối DB |
| [`workflow-schema-bootstrap.ps1`](workflow-schema-bootstrap.ps1), [`workflow-approved-migrations.ps1`](workflow-approved-migrations.ps1), [`workflow-approved-smoke.ps1`](workflow-approved-smoke.ps1) | **Lịch sử cloud #25**, các launcher ghi có gate phê duyệt | **KHÔNG CHẠY LẠI**: owner đã báo bootstrap/V3/V4/smoke hoàn tất; báo cáo cũ không phải acceptance mới |
| [`r23-compliance.py`](r23-compliance.py), [`r24-release.py`](r24-release.py), [`r24-upstream.py`](r24-upstream.py), `test_r23_*.py` / `test_r24_*.py` | Kiểm tra policy, tạo/verify candidate và độc lập release gate | `package` tạo file cục bộ; **không** tạo tag/Release/GHCR trong thao tác đọc tài liệu |
| [`git-cleanup-report.sh`](git-cleanup-report.sh), [`setup-github.sh`](setup-github.sh), [`poc/`](poc/) | Công cụ repo / thử nghiệm lịch sử | Không coi là setup bắt buộc; kiểm code trước khi thực thi |

### 2. Lệnh chỉ kiểm tra cấu trúc, không can thiệp DB

Từ **root repo**, kiểm tra mã Python R24 (không chạy release hoặc migration):

```powershell
python -m unittest discover -s scripts -p 'test_r24_*.py'
```

```sh
python3 -m unittest discover -s scripts -p 'test_r24_*.py'
```

Lệnh trên là lựa chọn kiểm tra **khi máy đã cài Python và dependency phù hợp**; không có kết quả thực thi mới. Kết quả test thực phải được lưu cùng SHA, OS, exit code, PASS/FAIL/SKIPPED. CI có [`ci.yml`](../.github/workflows/ci.yml) và [`release.yml`](../.github/workflows/release.yml); CI xanh không thay thế DB E2E, bản quyền [#138](https://github.com/tricore-opentrix/opentrix/issues/138) hay phát hành [#190](https://github.com/tricore-opentrix/opentrix/issues/190).

### 3. Điều kiện vận hành và bằng chứng lịch sử

- Các script `.ps1` hiện nhắm tới Windows PowerShell/Docker Desktop; **không có bản shell tương đương đã nghiệm thu** cho mọi fixture Linux/macOS. Build/test thuần trên Linux có trong [DEVELOPMENT](../docs/DEVELOPMENT.md).
- Runbook Helpdesk yêu cầu container/volume mới có nhãn sở hữu; không tái dùng fixture còn dữ liệu; secret chỉ qua process/prompt, không đưa vào tham số CLI, log/PR.
- Issue #25 có báo cáo **owner-reported** về cloud `COMMITTED_PASS` (bootstrap/migration/smoke). Đó là lịch sử tại ngày ghi, **không phải lệnh cần chạy hôm nay**. Xem [historical runbook](../backend/legacy-workflow-runbook.md) và [Issue #25](https://github.com/tricore-opentrix/opentrix/issues/25); không sửa/ghi đè chứng cứ gốc.
- R24 `source-only` candidate không cho phép publish; chỉ workflow `push tag` với acceptance và environment độc lập mới có đường publish. **Không tạo tag, Release, GHCR hoặc cleanup trong bước tài liệu**.

---

## English

### 1. Find scripts by purpose and risk

| Current path/group | Use / preconditions | Risk |
| --- | --- | --- |
| [`README-helpdesk-local.md`](README-helpdesk-local.md), [`helpdesk-local-setup.ps1`](helpdesk-local-setup.ps1) | Disposable Helpdesk preflight; `-Execute -ConfirmDemoDatabase` creates resources/schema | **DB WRITE** on execution; confirm owner, names, ports, volume and labels |
| [`helpdesk-negative-local.ps1`](helpdesk-negative-local.ps1), [`helpdesk-b06-local.ps1`](helpdesk-b06-local.ps1) | Opt-in HTTP/DB/identity checks | May create resources/write disposable fixtures; review exact script first |
| [`workflow-verify-local.ps1`](workflow-verify-local.ps1) | Owned PostgreSQL 17.11 TLS/CA/JDK21 test/build fixture | **CREATES/REMOVES** its fixture; Docker/JDK21/OpenSSL required; not a cloud command |
| [`workflow-read-only-preflight.ps1`](workflow-read-only-preflight.ps1), [`workflow-runtime-privilege-audit.ps1`](workflow-runtime-privilege-audit.ps1), [`workflow-security-definer-review.ps1`](workflow-security-definer-review.ps1) | Workflow catalog/audit utilities | Only connect to authorized endpoints; inspect code and access first |
| [`workflow-schema-bootstrap.ps1`](workflow-schema-bootstrap.ps1), [`workflow-approved-migrations.ps1`](workflow-approved-migrations.ps1), [`workflow-approved-smoke.ps1`](workflow-approved-smoke.ps1) | **Historical #25 cloud** write launchers with approval gates | **DO NOT REPLAY**: prior owner reports say bootstrap/V3/V4/smoke completed; not current acceptance |
| [`r23-compliance.py`](r23-compliance.py), [`r24-release.py`](r24-release.py), [`r24-upstream.py`](r24-upstream.py), `test_r23_*.py` / `test_r24_*.py` | Policy, candidate packaging/verification and independent release gate | Local `package` output is not a tag, Release or GHCR publication |
| [`git-cleanup-report.sh`](git-cleanup-report.sh), [`setup-github.sh`](setup-github.sh), [`poc/`](poc/) | Repo/legacy experimental utilities | Not mandatory setup; inspect source before execution |

### 2. Source checks without database operations

From the **repository root**, check R24 Python test sources without invoking release/migration:

```powershell
python -m unittest discover -s scripts -p 'test_r24_*.py'
```

```sh
python3 -m unittest discover -s scripts -p 'test_r24_*.py'
```

These are **source-defined commands**, not a new test result; Python and dependencies must already exist. Record SHA/OS/exit code/PASS/FAIL/SKIPPED for actual execution. CI [`ci.yml`](../.github/workflows/ci.yml) and [`release.yml`](../.github/workflows/release.yml) do not independently prove PostgreSQL E2E, rights under [#138](https://github.com/tricore-opentrix/opentrix/issues/138), or release acceptance under [#190](https://github.com/tricore-opentrix/opentrix/issues/190).

### 3. Operational prerequisites and historical evidence

- Current `.ps1` fixture launchers target Windows PowerShell/Docker Desktop; **no equivalently accepted Linux/macOS fixture scripts**. Ordinary Linux builds/tests are covered in [DEVELOPMENT](../docs/DEVELOPMENT.md).
- Helpdesk requires exclusively owned labelled disposable containers/volumes; do not reuse retained data. Keep secrets in secure process/prompt inputs, never CLI args, logs or PRs.
- For #25, prior **owner-reported** cloud `COMMITTED_PASS` for bootstrap/migrations/smoke is **historical**, not an invitation to rerun. See [archived workflow runbook](../backend/legacy-workflow-runbook.md) and [Issue #25](https://github.com/tricore-opentrix/opentrix/issues/25); preserve old evidence.
- R24 `source-only` candidates are nonpublishable. Only a separately accepted tag-triggered workflow with protected environment may publish. **No tag, GitHub Release, GHCR, or cleanup is authorized by docs changes.**
