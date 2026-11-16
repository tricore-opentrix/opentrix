<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# OpenTrix — Open source and compliance

[Documentation index](README.md) · [Architecture](ARCHITECTURE.md) · [Release](RELEASE.md) · [Contributing](../CONTRIBUTING.md)

> **Ngôn ngữ / Language:** [Tiếng Việt](#vi) · [English](#en)
>
> **Phụ trách / Owner:** @phanyen06ym-ien · **Theo dõi / Tracking:** [#138](https://github.com/tricore-opentrix/opentrix/issues/138), [#190](https://github.com/tricore-opentrix/opentrix/issues/190), [#194](https://github.com/tricore-opentrix/opentrix/issues/194), [#195](https://github.com/tricore-opentrix/opentrix/issues/195)
>
> **Nguồn tài liệu / Document baseline:** [PR #201](https://github.com/tricore-opentrix/opentrix/pull/201). **Bản cập nhật này / This revision:** đề xuất để review theo [biên bản #138 ngày 16/11/2026](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6899613976); chưa phải chứng nhận pháp lý hoặc chấp thuận phát hành / proposed for review; neither legal certification nor release approval.

---

<a id="vi"></a>

## Nguồn mở và tuân thủ — Tiếng Việt

### 1. Trạng thái xuất bản và phạm vi kết luận

OpenTrix — DX-OS Open-Core có giấy phép Apache-2.0, metadata SPDX/REUSE và kiểm tra giấy phép phụ thuộc trong CI. Theo trạng thái được ghi nhận ở [Issue #190](https://github.com/tricore-opentrix/opentrix/issues/190), bản phát hành công khai lịch sử `v0.1.0` là **pre-release**, không phải bản ổn định dự thi. Không suy đoán trạng thái phát hành hiện tại từ một báo cáo lịch sử: phải kiểm tra [GitHub Releases](https://github.com/tricore-opentrix/opentrix/releases), tag và asset thực tế trước khi đưa ra tuyên bố mới.

Ngày **16/11/2026**, ba maintainer đã ghi nhận đồng thuận Q1–Q5 về **phạm vi xem xét phát hành source-only `v0.2.0`**, dựa trên các cam kết cá nhân có giới hạn quyền. Đây là **quyết định nội bộ có công khai hạn chế**, không phải bằng chứng chứng minh toàn bộ source độc lập với bên thứ ba, không phải xác nhận tất cả file đã được kiểm toán và **không tự động cho phép công bố**:

- [Biên bản Q1–Q5](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6899613976)
- [Xác nhận riêng của Bảo](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6907781691)
- [Xác nhận riêng của Ánh](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6907788256)
- [Cam kết gốc của Yến](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841), [Bảo](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707960117), [Ánh](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708767215)

Kết luận của #138 chỉ có hiệu lực trong phạm vi và điều kiện đã nêu. Việc hoàn thành PR tài liệu Q3, ghi acceptance R24, review độc lập và bảo vệ phát hành vẫn là các bước riêng. Không dùng trạng thái đóng Issue làm bằng chứng thay thế cho bất kỳ bước nào.

### 2. Ranh giới repository, giấy phép và quyền đóng góp

- Source do TRICORE có quyền cấp phép được cung cấp theo **Apache License 2.0** (`Apache-2.0`); xem [`LICENSE`](../LICENSE) và bản lưu dùng cho REUSE tại [`LICENSES/Apache-2.0.txt`](../LICENSES/Apache-2.0.txt).
- [`NOTICE`](../NOTICE) ghi nhận attribution của dự án; [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md) kiểm kê thông báo dependency theo quy trình R23. Không suy ra quyền sở hữu từ các dòng SPDX hay Git author/committer.
- Mỗi contributor chỉ có thể cấp phép **phần đóng góp thuộc quyền của chính mình**. Quyền và giấy phép của mã ngoài, asset, model, dataset, công cụ và container image vẫn thuộc bên tương ứng. Apache-2.0 không mặc nhiên cấp quyền dùng tên/logo OpenTrix như nhãn hiệu.
- Đóng góp tuân theo Mục 5 của Apache-2.0 và [`CONTRIBUTING.md`](../CONTRIBUTING.md). Repo không yêu cầu CLA riêng; chính sách hiện hành không quy định DCO/`Signed-off-by` bắt buộc.
- Không sao chép mã, icon, template, fixture, ảnh hoặc tài sản không có quyền sử dụng. Nếu phát hiện khả năng trùng nguồn/giấy phép, xử lý theo chính sách báo cáo và xác minh **trong 7 ngày** tại [`CONTRIBUTING.md`](../CONTRIBUTING.md), sau đó ghi nhận quyết định phù hợp trong [`CHANGELOG.md`](../CHANGELOG.md).

### 3. Nguồn gốc mã và phát triển có hỗ trợ AI

Nhóm khai báo đã sử dụng các công cụ như **ChatGPT, Codex, Claude và Claude Code** hỗ trợ thiết kế, sinh/sửa code, kiểm tra và tài liệu, với mức tham gia khác nhau theo người và phạm vi. Các xác nhận này không chứng minh mức đóng góp hoặc quyền sở hữu của từng dòng/hunk.

Các giới hạn được công khai trong quyết định Q2 của #138:

1. **Không có hồ sơ đầy đủ từng prompt AI lịch sử.** Không tự dựng lại prompt để làm bằng chứng nguồn gốc.
2. **Không khẳng định AI output hoàn toàn độc lập với nguồn bên ngoài.** Nhóm khai báo không **cố ý** sao chép mã bên ngoài hoặc đưa mã bên ngoài cho AI để sao chép; tuyên bố này giới hạn ở hành vi của người khai báo, không kiểm chứng nội dung được sinh ra.
3. **Chưa đối chiếu chi tiết từng file với source bên ngoài.** Việc kiểm tra sâu hơn, kể cả bằng GitHub Code Search, SCANOSS hoặc ScanCode nếu phù hợp, được chuyển sang issue thuộc milestone `v1.0.0` theo Q4; đây không phải sự miễn trừ các nghĩa vụ còn tồn tại.

Dùng `UNKNOWN` khi chưa xác định nguồn, `NOT_RECALLED` khi người đóng góp không nhớ, `RIGHTS_PENDING` khi quyền cấp phép/phân phối chưa được xác minh. **Không tự chuyển sang `CLEARED`** chỉ vì REUSE, SBOM hay CI PASS. Với bất kỳ phát hiện rủi ro nào, cần xử lý riêng hoặc tiếp tục chặn phạm vi phân phối bị ảnh hưởng. Chính sách khai báo AI cho PR mới được quy định trong [`CONTRIBUTING.md`](../CONTRIBUTING.md); lịch sử được theo dõi tại [#138](https://github.com/tricore-opentrix/opentrix/issues/138).

### 4. Ranh giới self-hosting và dịch vụ bên ngoài

| Thành phần          | Trách nhiệm                          | Phạm vi quyền/triển khai                                               |
| ------------------- | ------------------------------------ | ---------------------------------------------------------------------- |
| Spring Boot backend | Identity, Workflow, Data và Helpdesk | Source thuộc phạm vi repo; quyền đóng góp phải được xác minh theo phần |
| Portal BFF          | OIDC/session, CSRF, chuyển tiếp API  | Source thuộc phạm vi repo                                              |
| React Portal        | Giao diện Helpdesk                   | Source thuộc phạm vi repo                                              |
| Keycloak            | Identity provider                    | Thành phần/image bên ngoài, có giấy phép và nghĩa vụ riêng             |
| Apache APISIX       | API Gateway                          | Thành phần/image bên ngoài, có giấy phép và nghĩa vụ riêng             |
| PostgreSQL          | Cơ sở dữ liệu                        | Thành phần/image bên ngoài, có giấy phép và nghĩa vụ riêng             |
| Caddy               | HTTPS ingress và routing demo        | Thành phần/image bên ngoài, có giấy phép và nghĩa vụ riêng             |

Docker Compose và cấu hình demo có thể tham chiếu hoặc kéo các image này; việc tự host **không** làm chúng trở thành mã nguồn do TRICORE sáng tạo. R23 kiểm tra dependency của backend/BFF/frontend, **không thay thế** rà soát giấy phép container image và các dịch vụ chạy riêng. `NOTICE` phải liệt kê attribution và các giấy phép image demo đã được kiểm chứng, theo Q3 của [biên bản #138](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6899613976). Xem [hướng dẫn demo](../infra/demo/README.md) và [tài liệu triển khai/phát hành](RELEASE.md).

### 5. Vệ sinh giấy phép: SPDX và REUSE

- Repo sử dụng [`LICENSES/`](../LICENSES/) và [`REUSE.toml`](../REUSE.toml) cho những tệp không thể hoặc không nên chèn header (do định dạng hay yêu cầu giữ nguyên byte).
- Tệp nguồn mới do contributor có quyền cấp phép phải mang SPDX phù hợp. Java/TypeScript dùng `//`, SQL dùng `--`, YAML/shell dùng `#`, Markdown dùng comment HTML, trừ ngoại lệ được khai báo qua REUSE.

  ```text
  SPDX-FileCopyrightText: 2026 TRICORE contributors
  SPDX-License-Identifier: Apache-2.0
  ```

- Chạy `reuse lint`; CI chạy `fsfe/reuse-action` trong job `repo-hygiene`. **Không** gắn header TRICORE lên mã ngoài hoặc nội dung chưa xác minh quyền.
- Bằng chứng **lịch sử**, không phải chỉ số HEAD hiện tại: Phase 2 tại `main@832c75f` báo cáo **338/338** tệp có metadata và không thiếu license (B-018). Khi công bố tỷ lệ hiện tại phải chạy lại trên SHA tương ứng.

### 6. Dependency, SBOM và notices

- Dependency được khai báo qua Gradle ([`backend/build.gradle`](../backend/build.gradle), [`portal-bff/build.gradle`](../portal-bff/build.gradle)) và npm ([`frontend/package.json`](../frontend/package.json) / lockfile). Không đưa mã vendored/third-party vào repo nếu chưa qua quy trình nguồn và giấy phép.
- CI `r23-compliance` tạo ba SBOM CycloneDX (backend, Portal BFF, frontend production), kiểm chính sách license qua [`scripts/r23-compliance.py`](../scripts/r23-compliance.py), kiểm thử canary và so [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md) với bản được sinh lại.
- Artifact `r23-sbom-and-notices` có retention được cấu hình ở CI; không coi việc artifact từng có mặt là bằng chứng nó còn tải được. SBOM **liệt kê phụ thuộc được resolve**, không đồng nghĩa mọi mã nhị phân có trong archive source-only.
- Inventory **131 thành phần** ghi trong báo cáo Phase 2 B-019 là **số liệu của baseline lịch sử**, không khẳng định đó là inventory hiện tại hoặc 131 thư viện được đóng gói/phân phối. `THIRD-PARTY-NOTICES.md` không tự nó là chứng nhận pháp lý.
- License allow-list và điều kiện dependency được mô tả trong [`CONTRIBUTING.md`](../CONTRIBUTING.md). Image/dịch vụ chạy riêng yêu cầu rà soát và attribution độc lập.

### 7. File nhị phân và nội dung phải giữ nguyên byte

| File/nhóm                                                                        | Nguồn hoặc xử lý                                                                 | Giới hạn                                                                                      |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `backend/gradle/wrapper/gradle-wrapper.jar`                                      | Gradle Wrapper upstream, metadata qua `REUSE.toml`; kiểm bằng wrapper validation | Không nhận là mã TRICORE tự sáng tạo; source-only archive đã kiểm tra có quy tắc loại JAR này |
| Flyway V1–V4 và SQL evidence được giữ nguyên                                     | Metadata REUSE ngoài file khi cần bảo toàn checksum                              | Không thay bytes để thêm header                                                               |
| `package.json`, `package-lock.json`, `favicon.svg`, `.gitignore` và file đặc thù | Header hoặc `REUSE.toml` tùy định dạng                                           | Metadata không chứng minh quyền tác giả hay asset clearance                                   |

Không coi bản kiểm tra wrapper thành xác nhận quyền phân phối của toàn bộ mã nguồn. Theo baseline trước đây, Portal BFF dùng Gradle wrapper của backend trong CI (HYG-01); kiểm tra lại nếu cấu trúc build thay đổi.

### 8. Cổng phát hành source-only `v0.2.0`

Phân biệt rõ **kết luận có giới hạn tại #138**, **nghiệm thu phát hành R24** và **việc kiểm toán chi tiết chuyển tiếp sang v1.0.0**.

1. **Phạm vi:** `v0.2.0` chỉ được xét phát hành **source-only**. Không được từ đó suy ra quyền phát hành bootJAR, `frontend/dist`, GHCR image hoặc binary khác. Source-only package phải có mã nguồn theo dõi bởi Git trong phạm vi được chấp thuận, LICENSE/NOTICE, CHANGELOG, release notes, SBOM/inventory và MANIFEST theo [R24 runbook](06-deployment/r24-release.md).
2. **Quyền và attribution:** dựa trên lời khai riêng, biên bản Q1–Q5 và quyết định về các ngoại lệ thực tế. Giới hạn nguồn gốc AI phải được công khai. Các trường hợp chưa được quyết định trong phạm vi phát hành không được âm thầm coi là `CLEARED`.
3. **Đóng băng source SHA và tái lập:** dùng exact full commit SHA; đối chiếu các lần build độc lập, archive hash, `MANIFEST.json`, `SHA256SUMS` và release notes. **Không sử dụng checksum từ commit khác hoặc từ archive có `validation_only=true`** để thông qua publication gate.
4. **PR chấp thuận riêng:** sau khi freeze SHA, đưa `docs/06-deployment/r24-acceptances/v0.2.0.json` lên `main` bằng PR có review độc lập. Trường bắt buộc gồm `tag`, `source_sha`, `mode`, `archive_sha256`, `reviewed_by` và năm HTTPS evidence: `source_provenance`, `source_license`, `sbom_source_boundary`, `archive_and_checksums`, `release_notes`. URL và JSON không tự chứng minh tính đúng của bằng chứng.
5. **Bảo vệ tag và publication:** kiểm tra cấu hình thực tế của environment `r24-release`, required reviewers và quy tắc bảo vệ tag `v*` trước khi tạo tag. Tag phát hành trỏ về **source SHA đã đóng băng trước commit acceptance**. Chỉ xác nhận release khi asset xuất bản thật được tải và hash được kiểm lại.
6. **Yêu cầu bản dự thi #190:** đối chiếu yêu cầu SemVer không phải pre-release, SBOM/NOTICE được đính kèm theo hình thức được chấp thuận, `CHANGELOG.md` và release notes đúng tình trạng pháp lý/kỹ thuật; nếu workflow chưa đáp ứng yêu cầu asset riêng thì xử lý bằng PR riêng.

Các kết quả CI, REUSE, R23, kiểm tra source hoặc đồng thuận contributor **không thay thế** chấp thuận phát hành. Mốc thời gian cũ là kế hoạch lịch sử, không phải căn cứ để backdate CHANGELOG hoặc tag. [Issue #190](https://github.com/tricore-opentrix/opentrix/issues/190) theo dõi bản dự thi; [#138](https://github.com/tricore-opentrix/opentrix/issues/138) theo dõi quyết định quyền nguồn có giới hạn; [`RELEASE.md`](RELEASE.md) là hướng dẫn vận hành release.

### 9. Bằng chứng và giới hạn

| Hạng mục                  | Đã ghi nhận / Hiện trạng có giới hạn                                          | Nguồn kiểm tra                                                                                                                     |
| ------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Apache-2.0 và attribution | LICENSE, LICENSES, NOTICE có trong repo; không chứng minh mọi nội dung gốc    | Files gốc và [#138](https://github.com/tricore-opentrix/opentrix/issues/138)                                                       |
| SPDX/REUSE                | CI có kiểm tra; 338/338 là số liệu **lịch sử**                                | Phase 2 B-018, `main@832c75f`                                                                                                      |
| Dependency policy         | CI R23 và SBOM; 131 là inventory **lịch sử**                                  | Phase 2 B-019                                                                                                                      |
| Đồng thuận Q1–Q5          | Ba maintainer đã đăng biên bản/xác nhận; giới hạn công khai                   | [Biên bản](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6899613976) và hai xác nhận riêng                  |
| Kiểm toán nguồn từng file | Chưa hoàn tất; có nội dung được chuyển tiếp sang v1.0.0                       | #138 Q4 / issue theo dõi v1.0.0 khi được tạo                                                                                       |
| Release `v0.2.0`          | **Không kết luận đã publish** khi chưa kiểm tra tag, acceptance và asset cuối | [Releases](https://github.com/tricore-opentrix/opentrix/releases), [#190](https://github.com/tricore-opentrix/opentrix/issues/190) |

Báo cáo Phase 2 liên quan: [Block B — Backend/Infrastructure](09-evidence/phase-2/block-b-backend-infra.md) (B-018…B-021) và [Block A — Architecture](09-evidence/phase-2/block-a-architecture.md) (POF-1…POF-6). Không diễn giải kết luận của báo cáo ở baseline cũ thành kết quả tại source SHA mới.

**Tuyên bố giới hạn:** Tài liệu này mô tả chính sách, phạm vi và bằng chứng đã ghi nhận. Đây không phải ý kiến pháp lý, chứng nhận quyền sở hữu toàn repository, chứng nhận vận hành production hoặc chấp thuận phát hành riêng biệt.

---

<a id="en"></a>

## Open source and compliance — English

### 1. Publication status and decision scope

OpenTrix — DX-OS Open-Core has an Apache-2.0 license, SPDX/REUSE metadata and automated dependency-license checks in CI. [Issue #190](https://github.com/tricore-opentrix/opentrix/issues/190) records the historical public `v0.1.0` release as a **pre-release**, not a stable competition release. Do not extrapolate today's publication status from a historical report: verify actual [GitHub Releases](https://github.com/tricore-opentrix/opentrix/releases), tags and assets before making a current claim.

On **16 November 2026**, all three maintainers recorded agreement on Q1–Q5 for the prospective **source-only `v0.2.0`** scope, based on individual declarations limited to each contributor's rights. This is a **bounded internal disposition with explicit limitations**, not proof that all source is independently originated, not a repository-wide file-level audit, and **not automatic publication authorization**:

- [Q1–Q5 disposition record](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6899613976)
- [Bảo's individual confirmation](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6907781691)
- [Ánh's individual confirmation](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6907788256)
- [Original declarations from Yến](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841), [Bảo](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707960117), and [Ánh](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708767215)

The #138 disposition is effective only within the recorded scope and conditions. Merging the Q3 documentation PR, R24 acceptance, independent review and publication protection are separate steps. A closed Issue is not a substitute for any of these gates.

### 2. Repository boundary, licensing and contribution rights

- Source that TRICORE has the authority to license is provided under the **Apache License 2.0** (`Apache-2.0`); see [`LICENSE`](../LICENSE) and the REUSE copy [`LICENSES/Apache-2.0.txt`](../LICENSES/Apache-2.0.txt).
- [`NOTICE`](../NOTICE) records project attribution; [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md) inventories dependency notices under R23. SPDX and Git author/committer data do not establish ownership.
- Each contributor can license only **contributions within their own rights**. Third-party code, assets, models, datasets, tooling and container images retain their respective licenses. Apache-2.0 does not generally grant rights to use the OpenTrix name or logo as a trademark.
- Contributions follow Section 5 of Apache-2.0 and [`CONTRIBUTING.md`](../CONTRIBUTING.md). No separate CLA is required; current policy does not mandate DCO/`Signed-off-by`.
- Do not copy code, icons, templates, fixtures, images or assets without permission. Potential source/license overlap must be reported and investigated **within seven days** under [`CONTRIBUTING.md`](../CONTRIBUTING.md), with appropriate resolution recorded in [`CHANGELOG.md`](../CHANGELOG.md).

### 3. Source provenance and AI-assisted development

The team has disclosed the use of tools including **ChatGPT, Codex, Claude and Claude Code** for design, code generation/modification, checks and documentation, with different contributor-specific scopes. These declarations do not resolve authorship or rights for individual lines or hunks.

The limitations disclosed under Q2 of #138 are:

1. **Complete per-prompt historical records are unavailable.** Do not reconstruct prompts and present them as provenance evidence.
2. **AI-generated output is not asserted to be independent of external sources.** Contributors report that they did not **intentionally** copy external source code or provide external code for AI to copy; this describes their actions, not a verification of generated content.
3. **Detailed file-by-file comparison with external source has not been completed.** Further review, potentially including GitHub Code Search, SCANOSS or ScanCode where appropriate, is deferred to an issue under milestone `v1.0.0` per Q4; deferral does not waive remaining obligations.

Use `UNKNOWN` for unidentified origins, `NOT_RECALLED` for contributor recollection gaps and `RIGHTS_PENDING` where licensing/distribution rights remain unverified. **Do not silently upgrade entries to `CLEARED`** because REUSE, SBOM or CI passes. Any material risks require a separate disposition or continued blocking of affected distribution scope. New-PR AI disclosure is governed by [`CONTRIBUTING.md`](../CONTRIBUTING.md); historical work is tracked in [#138](https://github.com/tricore-opentrix/opentrix/issues/138).

### 4. Self-hosting boundary and external services

| Component           | Responsibility                            | Rights/deployment boundary                              |
| ------------------- | ----------------------------------------- | ------------------------------------------------------- |
| Spring Boot backend | Identity, Workflow, Data and Helpdesk     | In-repository source; contribution rights remain scoped |
| Portal BFF          | OIDC/session, CSRF and backend forwarding | In-repository source                                    |
| React Portal        | Helpdesk user interface                   | In-repository source                                    |
| Keycloak            | Identity provider                         | External software/image with its own terms              |
| Apache APISIX       | API Gateway                               | External software/image with its own terms              |
| PostgreSQL          | Database                                  | External software/image with its own terms              |
| Caddy               | HTTPS ingress and demo routing            | External software/image with its own terms              |

Docker Compose and demo configuration may reference or pull these images; self-hosting does **not** make them TRICORE-authored source. R23 checks application dependency scopes and **does not replace** licensing review for separate service/container images. `NOTICE` must record verified attribution and demo image licenses as required by Q3 of the [#138 disposition](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6899613976). See the [demo guide](../infra/demo/README.md) and [release documentation](RELEASE.md).

### 5. Licensing hygiene: SPDX and REUSE

- The repository uses [`LICENSES/`](../LICENSES/) and [`REUSE.toml`](../REUSE.toml) for files that cannot or should not include inline headers due to format or byte-preservation constraints.
- New original source that a contributor has the rights to license requires appropriate SPDX metadata. Java/TypeScript use `//`, SQL uses `--`, YAML/shell use `#` and Markdown uses an HTML comment, except for properly declared REUSE exceptions.

  ```text
  SPDX-FileCopyrightText: 2026 TRICORE contributors
  SPDX-License-Identifier: Apache-2.0
  ```

- Run `reuse lint`; CI uses `fsfe/reuse-action` in the `repo-hygiene` job. **Never** apply the TRICORE header to external or rights-unverified material.
- **Historical evidence**, not a current HEAD metric: Phase 2 at `main@832c75f` reported **338/338** files with metadata and no missing licenses (B-018). Rerun against the exact relevant SHA before publishing a current figure.

### 6. Dependencies, SBOMs and notices

- Dependencies are declared through Gradle ([`backend/build.gradle`](../backend/build.gradle), [`portal-bff/build.gradle`](../portal-bff/build.gradle)) and npm ([`frontend/package.json`](../frontend/package.json) / lockfile). Do not introduce vendored/third-party material without origin and license review.
- `r23-compliance` CI produces three CycloneDX SBOMs (backend, Portal BFF, production frontend), checks licensing with [`scripts/r23-compliance.py`](../scripts/r23-compliance.py), runs canary tests and compares [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md) to generated output.
- `r23-sbom-and-notices` CI artifact availability depends on configured retention. An older artifact's existence does not prove it is still downloadable. An SBOM **inventories resolved dependencies**, not binaries necessarily included in a source-only archive.
- The **131 components** in the Phase 2 B-019 report are a **historical baseline**, not a current inventory or a count of shipped packages. `THIRD-PARTY-NOTICES.md` is not a legal certification.
- License allow-list and conditional dependency rules are in [`CONTRIBUTING.md`](../CONTRIBUTING.md). Separate images/services require independent license and attribution review.

### 7. Binary and byte-preserved files

| File/group                                                                         | Origin or handling                                          | Limitation                                                                     |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `backend/gradle/wrapper/gradle-wrapper.jar`                                        | Upstream Gradle Wrapper, REUSE metadata; wrapper validation | Not claimed as TRICORE-created; tested source-only packaging excludes this JAR |
| Flyway V1–V4 and byte-preserved SQL evidence                                       | External REUSE metadata where checksums must remain fixed   | Do not edit bytes to add inline headers                                        |
| `package.json`, `package-lock.json`, `favicon.svg`, `.gitignore` and special files | Inline metadata or `REUSE.toml` as applicable               | Metadata does not establish authorship or asset clearance                      |

Wrapper checks are not repository-wide redistribution authorization. Under the earlier baseline, Portal BFF used the backend Gradle wrapper in CI (HYG-01); recheck if the build layout changes.

### 8. `v0.2.0` source-only publication gate

Keep separate the **bounded #138 contributor disposition**, **R24 release acceptance**, and **deferred file-level v1.0.0 review**.

1. **Scope:** `v0.2.0` is eligible only for a **source-only** release. This does not authorize bootJARs, `frontend/dist`, GHCR images or other binary distribution. The package must include accepted Git-tracked source plus LICENSE/NOTICE, CHANGELOG, release notes, SBOM/inventory and MANIFEST as specified in the [R24 runbook](06-deployment/r24-release.md).
2. **Rights and attribution:** use the individual declarations, Q1–Q5 record and actual exception dispositions. Disclose AI-origin limitations. Never silently treat unresolved in-scope findings as `CLEARED`.
3. **Source freeze and reproducibility:** use the exact full source SHA; compare independent candidate builds, archive digests, `MANIFEST.json`, `SHA256SUMS` and release notes. **Do not reuse hashes from a different SHA or from `validation_only=true` archives** to pass the publication gate.
4. **Separate acceptance PR:** after source freeze, merge `docs/06-deployment/r24-acceptances/v0.2.0.json` to `main` via independent review. Required fields: `tag`, `source_sha`, `mode`, `archive_sha256`, `reviewed_by` and five HTTPS evidence keys: `source_provenance`, `source_license`, `sbom_source_boundary`, `archive_and_checksums`, `release_notes`. JSON URLs alone do not establish evidentiary sufficiency.
5. **Tag protection and publication:** verify the actual `r24-release` environment, required reviewers and `v*` tag protection before creating a tag. The published tag targets the **frozen source SHA predating the acceptance commit**. Claim publication only after downloading and hashing the actual release assets.
6. **Competition requirements #190:** confirm non-prerelease SemVer, approved attachment treatment of SBOM/NOTICE, and CHANGELOG/release notes accurately reflecting technical and rights status. If the workflow cannot provide required separate attachments, resolve that in a separately reviewed PR.

CI, REUSE, R23, source scanning and contributor agreement are **not substitutes** for release acceptance. Historical target dates must not be used to backdate a CHANGELOG entry or tag. [#190](https://github.com/tricore-opentrix/opentrix/issues/190) tracks the competition release; [#138](https://github.com/tricore-opentrix/opentrix/issues/138) the bounded contributor decision; [`RELEASE.md`](RELEASE.md) is the operational release guide.

### 9. Evidence and limitations

| Item                           | Recorded / limited status                                                               | Reference                                                                                                                          |
| ------------------------------ | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Apache-2.0 and attribution     | LICENSE, LICENSES and NOTICE exist; not proof of origin for all content                 | Root files and [#138](https://github.com/tricore-opentrix/opentrix/issues/138)                                                     |
| SPDX/REUSE                     | CI enforces checks; 338/338 is **historical**                                           | Phase 2 B-018, `main@832c75f`                                                                                                      |
| Dependency policy              | R23 CI and SBOM; 131 is a **historical** inventory                                      | Phase 2 B-019                                                                                                                      |
| Q1–Q5 agreement                | Three maintainers recorded a bounded disposition with limitations                       | [Decision](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6899613976) and individual sign-offs               |
| File-level upstream comparison | Not completed; work deferred in part to v1.0.0                                          | #138 Q4 / follow-up issue when created                                                                                             |
| `v0.2.0` release               | **Not asserted published** without current tag, acceptance and final asset verification | [Releases](https://github.com/tricore-opentrix/opentrix/releases), [#190](https://github.com/tricore-opentrix/opentrix/issues/190) |

Related Phase 2 reports: [Block B — Backend/Infrastructure](09-evidence/phase-2/block-b-backend-infra.md) (B-018…B-021) and [Block A — Architecture](09-evidence/phase-2/block-a-architecture.md) (POF-1…POF-6). Do not treat historical report conclusions as evidence for a newer source SHA.

**Limitations:** This document describes policy, scope and recorded evidence. It is not legal advice, repository-wide ownership certification, production certification or an independent release approval.
