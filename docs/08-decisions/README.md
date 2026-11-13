<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Quyết định kiến trúc (ADR) / Architecture Decision Records

> **Trạng thái / Status:** Đã review / Reviewed · **Issue:** [#216](https://github.com/tricore-opentrix/opentrix/issues/216)

Mỗi ADR ghi một quyết định kiến trúc, lý do và đánh đổi. ADR chỉ `ACCEPTED` khi PR được merge với approve của hai maintainer không phải tác giả ([GOVERNANCE.md](../../GOVERNANCE.md)). Khi đổi quyết định, viết ADR mới và đánh dấu ADR cũ `SUPERSEDED`; không sửa nội dung ADR cũ.

Each ADR records one architecture decision, its rationale and trade-offs. An ADR is `ACCEPTED` only when its PR is merged with approvals from both non-author maintainers ([GOVERNANCE.md](../../GOVERNANCE.md)). A changed decision gets a new ADR and the old one is marked `SUPERSEDED`; old ADR content is not rewritten.

| ADR | Quyết định / Decision | Trạng thái / Status | Issue / PR |
| --- | --- | --- | --- |
| [ADR-007](ADR-007-data-storage.md) | MVP object storage provider (MinIO) | SUPERSEDED by ADR-016 | #181 |
| [ADR-008](ADR-008-dashboard-tool.md) | MVP analytics dashboard provider (Apache Superset) | ACCEPTED; triển khai sau cuộc thi / implementation after the competition (ADR-017) | R21, R54 |
| [ADR-009](ADR-009-modular-monolith-flowable.md) | Modular Monolith with embedded Flowable | ACCEPTED | #191, #218 |
| [ADR-016](ADR-016-s3-compatible-storage.md) | S3-compatible object storage and module data ownership | ACCEPTED | #181, #217 |
| [ADR-017](ADR-017-helpdesk-first-scope.md) | Helpdesk-first competition scope | ACCEPTED | #216, #219 |
| [ADR-018](ADR-018-apisix-api-gateway.md) | Apache APISIX as the API gateway | ACCEPTED | #116, #220 |

Số ADR-010 đến ADR-015 không dùng: chúng gắn với các đề xuất cũ đã đóng (ví dụ #159, #160). / Numbers ADR-010 to ADR-015 are unused; they belong to closed historical proposals (for example #159, #160).
