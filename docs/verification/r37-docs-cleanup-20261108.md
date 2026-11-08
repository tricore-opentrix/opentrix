<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# R37 — Documentation cleanup: link check and removed paths (2026-11-08)

Docs-only checks for PR #158. They do not show that the software builds or runs; that evidence is in [r37-linux-build-20261108.md](r37-linux-build-20261108.md).

## Scope of this evidence

- Base: `main@187dbd2`. The link check below was run on the full tracked tree of the PR head at the time of writing; the exact PR head SHA and CI check-run links are posted in the PR conversation, because a file cannot contain the SHA of the commit that adds it.
- Changes against `main@187dbd2` outside Markdown: only the removal of nine empty `.gitkeep` files (listed below) and the new `scripts/check_md_links.py`. Nothing under `backend/src`, `portal-bff/` or `frontend/src` was changed.

## Link check

```text
$ python3 scripts/check_md_links.py
files 40 broken 0
$ echo $?
0
```

- Scope: all files returned by `git ls-files '*.md'` (40 files). Fenced code blocks and inline code spans are ignored.
- Checked: relative link targets and `#anchor` fragments (GitHub-style heading slugs, an approximation).
- Not checked: links with a URL scheme (`https:`, `mailto:`). The script has no network access by design.
- Negative test: a temporary tracked file containing `[x](nope.md) [y](README.md#no-such)` made the script print `missing target` and `missing anchor`, report `broken 2` and exit with status 1.
- Four references to Issue #39 material that exists only on the unmerged branch `feature/a05-portal-bff-integration` (in `frontend/README.md` and `frontend/DEMO_GUIDE.md`) now point to commit permalinks. Each target was confirmed to exist at that commit with `git cat-file -e <sha>:<path>`:

| Target | Commit |
| --- | --- |
| `docs/application/issue39-mvp-readiness-20261027.md` | `c73bbc306a698141169304e5da848ea0686700db` |
| `docs/evidence/issue39-portal/README.md` | `05c5d9967e88d24cfb4b41f4134dcc2522ac9253` |
| `docs/evidence/issue39-portal/auth/README.md` | `00b10fa43d01cc3dcca725b2ed66a43bdaa92268` |

These links stay valid only while those commits remain reachable in the repository. They should be replaced by relative links when the branch is merged.

## Removed paths against the R27 register

Register: `docs/verification/r27/r27-rights-remediation-register-187dbd2.csv` from PR #143 (head `6cb5a32`). Every removed path has a row in it, with `distribution_status = PACKAGED_AS_SOURCE`, and the register's `git_blob_sha1` equals the blob at `main@187dbd2` for all 11 paths.

| Removed path | Blob (`187dbd2`) | R27 `file_group` | What happened to the content |
| --- | --- | --- | --- |
| `frontend/DRAFT_PR.md` | `6161930e8f` | FRONTEND_PORTAL_ANH_ROUTE | Deleted. A pull-request draft, not product documentation. Remains in Git history. |
| `docs/00-project/glossary.md` | `1065ae9933` | PROJECT_DOCS_YEN_COORDINATION | Terms merged into the root `GLOSSARY.md` (sections 8 and 9); file deleted. |
| `docs/01-architecture/diagrams/.gitkeep` | `e69de29bb2` (empty) | PROJECT_DOCS_YEN_COORDINATION | Deleted; empty placeholder. |
| `docs/03-applications/facility/.gitkeep` | `e69de29bb2` (empty) | PROJECT_DOCS_YEN_COORDINATION | Deleted; empty placeholder. |
| `docs/03-applications/helpdesk/.gitkeep` | `e69de29bb2` (empty) | HELPDESK_DOCUMENTATION_ANH_ROUTE | Deleted; empty placeholder. |
| `docs/04-integration/.gitkeep` | `e69de29bb2` (empty) | PROJECT_DOCS_YEN_COORDINATION | Deleted; empty placeholder. |
| `docs/05-testing/.gitkeep` | `e69de29bb2` (empty) | PROJECT_DOCS_YEN_COORDINATION | Deleted; empty placeholder. |
| `docs/07-open-source/.gitkeep` | `e69de29bb2` (empty) | PROJECT_DOCS_YEN_COORDINATION | Deleted; empty placeholder. |
| `docs/09-evidence/.gitkeep` | `e69de29bb2` (empty) | PROJECT_DOCS_YEN_COORDINATION | Deleted; empty placeholder. |
| `docs/10-reviews/.gitkeep` | `e69de29bb2` (empty) | PROJECT_DOCS_YEN_COORDINATION | Deleted; empty placeholder. |
| `docs/11-poc/.gitkeep` | `e69de29bb2` (empty) | PROJECT_DOCS_YEN_COORDINATION | Deleted; empty placeholder. |

Conclusions and open points:

- The nine `.gitkeep` files are empty (`e69de29`, the empty-blob hash), so no authored content is lost.
- The register is pinned to `187dbd2`; deleting files later does not alter that snapshot or Git history. If the R27 owners want the register to describe the post-merge tree, they must regenerate it.
- Not resolved by this PR: the terms moved from `docs/00-project/glossary.md` into `GLOSSARY.md` keep the provenance status the register assigned to the source file (`RIGHTS_PENDING`, owner `@phanyen06ym-ien`). The same applies to the registered files that this PR edits (`README.md`, `GLOSSARY.md`, `docs/README.md`, `frontend/README.md`, `scripts/README.md`): their blobs no longer equal the register's. Both are for the R27 owners to decide.

## Object-storage wording (MinIO dropped)

The team's technology checklist records MinIO as dropped on 2026-11-05 (upstream stopped publishing community images and binaries in October 2025 and archived the repository in 2026) and SeaweedFS with its S3 API as the planned replacement (container v0.2.0 / R32b in Docker Compose; `ObjectStoragePort` adapter, integration tests and application use v0.3.0 / R43). These are planned milestones, not implemented or accepted. Docs that still presented MinIO as the selected target were reworded to a provider-neutral "S3-compatible object store (SeaweedFS planned)", with a note that the SeaweedFS ADR is pending and no adapter exists:

`GLOSSARY.md`, `docs/00-project/project-overview.md`, `docs/00-project/scope-and-mvp.md`, `docs/01-architecture/{core-application-boundary,dependency-rules,deployment-topology,repository-layout-and-ownership,system-architecture}.md`, `docs/02-core/data/{data-architecture,storage-adapters}.md`, `docs/06-deployment/prerequisites.md`.

Left unchanged on purpose:

- `docs/08-decisions/ADR-007-data-storage.md`: owned by the ADR work; it is to be marked Superseded by the SeaweedFS ADR (pending).
- `docs/verification/issue53-*.md` and `issue90-*.md`: historical evidence that must not be rewritten.
- References to PR #34 (a MinIO candidate that was never merged): historical facts, kept and labelled as such.
- `scripts/setup-github.sh`: label and milestone descriptions that mention MinIO; changing them would not change labels already created on GitHub.

SeaweedFS is described only as planned. Nothing here claims it is selected by an accepted ADR or implemented.

## SPDX coverage and REUSE status

Measured with `reuse lint` 6.3.0 on the branch head before this wording change (`1f57dba`, 337 files):

| Measure | Result |
| --- | --- |
| Files with copyright information | 337 / 337 |
| Files with license information | 337 / 337 |
| Missing or unused licences | 0 |
| Invalid SPDX License Expressions | 1 (`scripts/r23-compliance.py`, a pre-existing file) |

SPDX header coverage is 100%, but REUSE compliance is **not** a full PASS: `reuse lint` exits non-zero because of the invalid expression above. It is not fixed here (out of scope for R37); the repo-hygiene CI job passes with it. On `main@187dbd2` the same check reports 336 / 336 files with the same single invalid expression.

## Reconciliation with code (second batch)

- `backend/README.md`: added a Linux/macOS build section and a `curl` health check; listed the Keycloak realm and the three `OIDC_*` variables as run-time requirements (all four have no default in `application.yml`; checked by reading the file, not by running it); the intro no longer presents the removed Request prototype as current. The Windows-only content and the Issue #25 history sections are unchanged.
- `docs/01-architecture/repository-layout-and-ownership.md`: section 2 now matches `git ls-files` on the branch head (`frontend/` and `portal-bff/` tracked, `request/` removed, `application/helpdesk/` and `gateway/helpdesk/` present, `application/facility/` is only a `.gitkeep`). Section 3 (the target tree) is otherwise unchanged and may still describe `helpdesk` as a target.
- Not checked: the other claims in these two files that I did not touch, for example the CI job count and every Issue #25 cloud statement.
