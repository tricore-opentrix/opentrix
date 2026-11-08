<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# LIC-07 — NOTICE and license audit

Evidence group: LIC-G1; LIC-G2; LIC-G5.

Status: **PENDING**.

Evidence source: [NOTICE](../../../NOTICE), [LICENSE](../../../LICENSE), [generated notices](../../../THIRD-PARTY-NOTICES.md), [R24 upstream collector](../../../scripts/r24-upstream.py), [LIC-06](LIC-06-license-compatibility.md).

Applicable source SHA: `9aaff5854eb386d0602fb4575c4204d359881d73` (verified #161 integration base). These are living instructions; later generated reports name their own analyzed commit in `generation-manifest.json`. This document is not an assertion that future commits are covered.

Owner: Bảo supplies actual package/archive evidence; Yến coordinates obligations.

Reviewer: Noncontributing reviewer for affected notices and portions; proposed routing, no signature or approval recorded here.

Blockers: Collective-label authority, upstream notice completeness, font/icon/SVG and archive metadata obligations PENDING.

Update conditions: Third-party source/asset/dependency changes; NOTICE/license changes; distribution-mode or frozen archive changes.

## Audit scope

The generated THIRD-PARTY-NOTICES inventory is not a collection of every upstream license text. Compare actual delivered files with upstream LICENSE/COPYING/NOTICE and applicable attribution requirements. Preserve license choices and source URLs from canonical records. Retain required notices when adapting/vendoring material.

For a frozen archive, inspect the manifest and actual member bytes, including the ten archive-only metadata records. Compare SHA-256 values and source-only exclusions. Do not edit archived manifests, historical blobs or migration checksums to make an audit pass. The excluded wrapper JAR does not remove obligations for included Gradle scripts/properties.

New metadata coverage does not authorize the collective TRICORE label for unknown portions. Record real first-person/upstream authority and independent decisions through LIC-05 and the existing register. Missing texts or permissions remain blockers.

Use the existing R23 notice equality check and R24 collector/verification scripts. No new source-only archive or upstream clearance has been performed by writing this framework.
