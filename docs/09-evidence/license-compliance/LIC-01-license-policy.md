<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# LIC-01 — License policy and evidence boundaries

Evidence group: LIC-G1; LIC-G2.

Status: **PENDING**.

Evidence source: [project LICENSE](../../../LICENSE), [REUSE.toml](../../../REUSE.toml), [R23 policy](../../../scripts/r23-compliance.py), [canonical vocabulary](../../verification/r27/r27-status-and-id-vocabulary.md).

Applicable source SHA: `9aaff5854eb386d0602fb4575c4204d359881d73` (verified #161 integration base). These are living instructions; later generated reports name their own analyzed commit in `generation-manifest.json`. This document is not an assertion that future commits are covered.

Owner: Yến coordinates policy; Bảo maintains executable R23 tooling.

Reviewer: Bảo/Ánh for documentation, excluding their own source portions; proposed routing, no signature or approval recorded here.

Blockers: Contributor authority, upstream obligations and 37 historical exceptions unresolved; the baseline REUSE literal-scanning defect is corrected by the narrowly scoped emitter change below, pending independent review.

Update conditions: License metadata, dependency policy, distribution scope or contributor authority changes.

## Policy

Project-origin material is declared Apache-2.0 by existing repository metadata. This declaration does not establish who can license each portion. Preserve third-party terms and original notices; do not relabel upstream material as TRICORE-owned.

The R23 script remains the sole executable dependency-license policy. This framework imports its decisions, not a new allowlist. Keep exact-version license choices and rejection canaries there. A policy-accepted declaration is not compatibility clearance or redistribution permission.

Use REUSE headers, sidecars or external annotations as appropriate. Preserve checksum-sensitive SQL bytes and existing REUSE external annotations. Never guess missing copyright, license, origin or permission. Retain UNKNOWN, NOT_RECALLED and pending rights evidence.

## Separate decisions

- LIC-02/03 establish named metadata facts at a SHA, not copyright title.
- LIC-04 projects existing R23 SBOM/inventory records; source version, digest and unresolved fields survive.
- LIC-05 requires direct portion-scoped contributor evidence and independent review.
- LIC-06/07 require actual upstream license/NOTICE and package-scope assessment.
- LIC-08 records actual scoped review; checkboxes do not create approval.
- LIC-09 requires separate R24 acceptance and explicit publication authorization.

Status meanings remain in the canonical R27 vocabulary. Existing register string RIGHTS_PENDING is not renamed. Framework IDs LIC-01..LIC-09 identify deliverables in this directory; they do not reassign the existing obligation IDs LIC-01..LIC-10 inside R27-LIC-001. Always qualify the document/path when referring to either namespace.

## Explicit baseline defect correction in Phase 2

At the verified #161 source, REUSE 6.3.0 reads embedded NOTICE-header string literals in `scripts/r23-compliance.py` as extra metadata and reports an invalid license expression. Phase 2 splits the marker string construction while emitting identical NOTICE header text. It does not add an ignore directive, change the dependency allowlist/parser/choices, edit frozen source, or relabel a failed run. The new metadata regression and existing R23 tests cover the change; the historical failed baseline report remains preserved separately. Re-run full lint on the new committed source, and compare generated notices against the existing R23 artifact.
