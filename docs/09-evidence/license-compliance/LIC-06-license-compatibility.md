<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# LIC-06 — License compatibility review

Evidence group: LIC-G2.

Status: **PENDING**.

Evidence source: [R23 executable policy](../../../scripts/r23-compliance.py), [LIC-04 projection](LIC-04-third-party-inventory.csv), [R27-LIC-001](https://github.com/tricore-opentrix/opentrix/blob/25faa214835093d591eb381be910e1efc1b8c085/docs/verification/r27/r27-third-party-license-notice-assessment.md).

Applicable source SHA: `9aaff5854eb386d0602fb4575c4204d359881d73` (verified #161 integration base). These are living instructions; later generated reports name their own analyzed commit in `generation-manifest.json`. This document is not an assertion that future commits are covered.

Owner: Yến coordinates; Bảo supplies dependency/build scope.

Reviewer: Eligible independent reviewer with upstream license/package evidence; proposed routing, no signature or approval recorded here.

Blockers: Upstream texts, source-only versus future binary/image obligations and actual contributor authority remain unresolved.

Update conditions: Dependency version/license expression/packaging changes; source reuse or release scope changes.

## Assessment method

Start from R23 SBOMs and license-inventory.json. LIC-04 retains their decisions, source SHA/digests and unresolved fields; it does not make a new compatibility verdict. Review actual package version, upstream LICENSE/COPYING/NOTICE, chosen dual-license option and distribution mode. Record real URLs and affected portions in the canonical obligation workstream.

The existing Logback 1.5.34 EPL-2.0 choice is version-specific. The obsolete Hibernate ORM LGPL waiver was removed; do not extend any historical exception to another version. Unknown/malformed expressions and unsupported WITH exceptions must remain rejected by R23 policy. A missing upstream source URL remains missing, not guessed from a package name.

Check fonts, icons, SVGs, copied examples/fixtures and service images separately when actually shipped. These can be outside the three runtime dependency SBOMs. Source-only evidence does not clear future JARs, frontend bundles or containers.

## Required manual record

For each unresolved obligation, link the existing canonical case/obligation, exact package/source SHA and version, actual upstream text/notice, proposed license choice, applicable distribution duty, independent reviewer and remaining blocker. This is a review method, not a parallel decisions CSV. No compatibility or rights PASS is recorded by this draft.
