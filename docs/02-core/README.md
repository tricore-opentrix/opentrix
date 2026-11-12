<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# 02-core — Thiết kế Core ban đầu / Early Core design

> **Trạng thái / Status:** Lịch sử — chỉ tham khảo / Historical — reference only · **Issue:** [#195](https://github.com/tricore-opentrix/opentrix/issues/195), [#194](https://github.com/tricore-opentrix/opentrix/issues/194)

Các file trong thư mục này là **bản ghi trước Giai đoạn 3**, giữ lại để tham khảo lý do thiết kế. Chúng **không** mô tả hiện trạng. Nguồn chuẩn là [bộ tài liệu chính](../README.md); kiến trúc hiện tại xem [ARCHITECTURE.md](../ARCHITECTURE.md).

Files in this folder are **pre-Phase 3 records**, kept for design rationale. They do **not** describe the current state. The canonical sources are the [main documentation set](../README.md); for the current architecture see [ARCHITECTURE.md](../ARCHITECTURE.md).

| File | Trạng thái / Status | Hiện trạng ở / Current source |
| --- | --- | --- |
| [identity/identity-architecture.md](identity/identity-architecture.md) | Lịch sử / Historical | [ARCHITECTURE.md](../ARCHITECTURE.md), [API.md](../API.md) |
| [gateway/gateway-architecture.md](gateway/gateway-architecture.md) | Lịch sử / Historical | [ARCHITECTURE.md](../ARCHITECTURE.md); APISIX `PROPOSED` (#116) |
| [workflow/workflow-architecture.md](workflow/workflow-architecture.md) | `PENDING #191` | Engine nội bộ hay Flowable chưa chốt / internal engine vs Flowable undecided |
| [data/data-architecture.md](data/data-architecture.md) | `PENDING #181` | MinIO hay S3-compatible chưa chốt / MinIO vs S3-compatible undecided |
| [data/storage-adapters.md](data/storage-adapters.md) | `PENDING #181` | Như trên / As above |

Không sửa, di chuyển hoặc xoá các file này trong Giai đoạn 3; phân loại theo [#195](https://github.com/tricore-opentrix/opentrix/issues/195). / Do not edit, move or delete these files in Phase 3; classification per #195.
