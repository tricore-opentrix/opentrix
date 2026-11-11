<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Hạ tầng / Infrastructure

> **Status / Trạng thái:** DRAFT, AS-IS inventory; runtime UNVERIFIED · [#194](https://github.com/tricore-opentrix/opentrix/issues/194) · [#197](https://github.com/tricore-opentrix/opentrix/issues/197)
>
> [Deployment guide](../docs/DEPLOYMENT.md) · [Development guide](../docs/DEVELOPMENT.md) · [Local Workflow](../backend/docs/local-workflow-runbook.md) · [R24 release](../docs/RELEASE.md)

## Tiếng Việt

### Các tệp hiện có

| Tệp | Phạm vi đã có (AS-IS) | Chưa chứng minh |
| --- | --- | --- |
| [`compose.workflow-postgres.yml`](compose.workflow-postgres.yml) | PostgreSQL `17.11-alpine`, DB/user `workflow_test`, port chỉ bind `127.0.0.1:55425:5432`, named volume và healthcheck `pg_isready` | **Không phải** Compose Backend/BFF/Portal/Keycloak/Caddy; chưa chạy lại tại SHA của tài liệu |
| [`release/`](release/) | Dockerfile backend/BFF phục vụ đóng gói R24; nguồn [workflow](../.github/workflows/release.yml) | Không tự chứng minh có deploy production, image đã phát hành hay full-stack |
| [`README.md`](README.md) | Chỉ mục vận hành hiện hành | Không thay thế bằng chứng triển khai |

### Biến, cổng và lệnh an toàn

`WORKFLOW_LOCAL_DB_PASSWORD` bắt buộc khi Compose xử lý cấu hình; phải cấp bằng kênh bí mật của process, **không** điền giá trị thật vào source, command history hay PR. Không có credential mặc định dùng cho triển khai. Từ **root repository**:

```powershell
docker compose -f infra/compose.workflow-postgres.yml config --quiet
docker compose -f infra/compose.workflow-postgres.yml ps
```

```sh
docker compose -f infra/compose.workflow-postgres.yml config --quiet
docker compose -f infra/compose.workflow-postgres.yml ps
```

Đây là kiểm tra không khởi động DB; cần secret process đã cấp. Các bước `up`, tạo role/schema, migration, `down -v`, reset/xóa volume có tác động dữ liệu và **không** nằm trong kiểm tra tài liệu. Trước khi làm phải có approval cho fixture disposable độc quyền. Volume tồn tại vẫn giữ mật khẩu gốc.

### Hiện trạng so với mục tiêu

`AS-IS` là có file/cấu hình được đọc, không phải triển khai thành công; `UNVERIFIED` là thiếu log same-SHA; `PROPOSED` theo [#119](https://github.com/tricore-opentrix/opentrix/issues/119) là full-stack Compose source-built đa hệ điều hành; [#118](https://github.com/tricore-opentrix/opentrix/issues/118) là browser E2E thật. APISIX [#116](https://github.com/tricore-opentrix/opentrix/issues/116) và object-storage provider [#192](https://github.com/tricore-opentrix/opentrix/issues/192) **chưa nghiệm thu**. R24 chỉ cung cấp candidate chưa phải quyền phát hành.

---

## English

### Existing files

| Path | Inspected AS-IS scope | Not established |
| --- | --- | --- |
| [`compose.workflow-postgres.yml`](compose.workflow-postgres.yml) | `postgres:17.11-alpine`, `workflow_test` DB/user, loopback-only `127.0.0.1:55425:5432`, named volume and `pg_isready` healthcheck | **Not** a Backend/BFF/Portal/Keycloak/Caddy Compose; no fresh same-SHA runtime test |
| [`release/`](release/) | Backend/BFF Dockerfile inputs to R24 [workflow](../.github/workflows/release.yml) | No proof of deployed production, published images or accepted full stack |
| [`README.md`](README.md) | Current operator navigation | Not deployment evidence |

### Variables, ports and safe commands

`WORKFLOW_LOCAL_DB_PASSWORD` is required to parse the Compose configuration; inject it securely into the process, **never** put actual credentials in source, command history, or PRs. There are no safe production default credentials. From the **repository root**:

```powershell
docker compose -f infra/compose.workflow-postgres.yml config --quiet
docker compose -f infra/compose.workflow-postgres.yml ps
```

```sh
docker compose -f infra/compose.workflow-postgres.yml config --quiet
docker compose -f infra/compose.workflow-postgres.yml ps
```

These checks do not start a DB and require pre-supplied process credentials. `up`, role/schema creation, migration, `down -v` and volume deletion/reset can change data and are **not** part of documentation verification; obtain approval for an exclusively owned disposable fixture. Existing volumes retain their original password.

### Current vs target

`AS-IS` indicates inspected configuration, **not** a successful deployment. `UNVERIFIED` means no same-SHA runtime record. The source-built cross-platform full-stack Compose is `PROPOSED` ([#119](https://github.com/tricore-opentrix/opentrix/issues/119)); real browser E2E is separate ([#118](https://github.com/tricore-opentrix/opentrix/issues/118)). Dedicated APISIX ([#116](https://github.com/tricore-opentrix/opentrix/issues/116)) and production object storage ([#192](https://github.com/tricore-opentrix/opentrix/issues/192)) are not accepted. R24 candidates do not grant distribution rights.
