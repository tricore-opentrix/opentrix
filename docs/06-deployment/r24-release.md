<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R24 — reproducible release automation and independent clearance

Automation owner: Bảo (@lexuanbao258-collab). Compliance/release acceptance coordinator: Yến (@phanyen06ym-ien), with Ánh (@ngang02012007-crypto) as co-reviewer. R23 policy PASS is not permission to distribute.

## Candidate and naming

- Output: **dxos-open-core-<version>.tar.gz**, e.g. dxos-open-core-0.2.0.tar.gz, plus SHA256SUMS and RELEASE-NOTES.md.
- Accept vMAJOR.MINOR.PATCH and vMAJOR.MINOR.PATCH-rc.N (N >= 1) tags. A matching CHANGELOG [<version>] section with nonempty release notes is required.
- PR builds and default manual `validation-only` runs remain **nonpublishable**. Opt-in manual `publishable-source-only` runs prepare **release-format technical candidates only**, without distribution authorization. A tag-triggered release selects scope exclusively from the independently reviewed acceptance JSON on main; the tagged commit must be an ancestor of main. Neither candidate mode creates a tag or GitHub Release.
- Archive metadata are reproducible. SHA256SUMS and MANIFEST.json cover candidate bytes. The clearance gate additionally requires independently reviewed archive_sha256 in the acceptance JSON and verifies standalone release notes match the archive member. Publication extracts the verified archive notes.

## Binary scope

Binary packages contain backend and Portal BFF bootJars, frontend dist, three CycloneDX runtime SBOMs, R23 inventory, original LICENSE/NOTICE, CHANGELOG, notes, upstream-index.json, and actual extracted upstream texts. GHCR images may be published only after the binary scope is accepted.

The upstream collector reads matched Gradle-cache JAR META-INF LICENSE/NOTICE and npm package LICENSE/COPYING/NOTICE, with optional reviewed supplements under docs/06-deployment/r24-upstream/<project>/<name>-<version>/. File contents are preserved, hashed and listed in upstream-index.json. Found files are COLLECTED_UNREVIEWED, missing texts remain MISSING. Maven type=pom entries are metadata-only, not shipped JARs; package.json license identifiers are not substitutes for upstream text.

One independently accepted **permissive license group** may cover Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC and 0BSD. Actual bundled components still require upstream license bytes in the archive. Any non-group license (e.g. EPL, GPL+Classpath, OFL and CC0) needs individual evidence/choice in the exceptions list. The inventory determines those exceptions, including logback and jakarta.annotation-api where shipped; no blanket permission is inferred from the license name. The gate blocks missing/unchecked files and all unresolved source, NOTICE, asset, JRE and OCI obligations.

## Source-only `v0.2.0` (planned; fail-closed)

Mode source-only archives Git-tracked source, LICENSE, NOTICE, CHANGELOG, release notes, three runtime SBOMs and notices inventory. It **excludes JARs, frontend dist and GHCR images**. The SBOM records resolved build/runtime dependencies, not distributed binaries. An independent source provenance/licensing review is still required; source-only clearance does not satisfy later binary release obligations. The 2026-11-07 target is conditional: the first public `v0.2.0` release, if independently cleared, is SOURCE-ONLY. On 2026-11-06, `v0.2.0-rc.1` is for controlled internal TRICORE verification only (candidate artifact and checksums, explicitly INTERNAL / NOT RELEASE-ACCEPTED); do not create a public tag or GitHub Release for it. Do not publish `v0.2.0-rc.1` publicly. No JAR, built frontend dist or GHCR image is authorized. If #138/#139 or checksum evidence is incomplete, postpone the public tag/release and update CHANGELOG to the eventual actual date before source freeze.

## Manual candidate workflows (technical verification only)

The GitHub Actions workflow **R24 release candidate and publication** can be started via
**Actions → Run workflow → Branch: main → `candidate_mode`**. Manual workflow runs
**never** execute the tag-only `publish` job.

| `candidate_mode` | Guard and output | GitHub Actions artifacts | Release allowed? |
| --- | --- | --- | --- |
| `validation-only` (default) | Default PR/manual validation: binary candidate plus a source-only validation candidate | `r24-candidate-<run_id>` and `r24-source-only-candidate-<run_id>` | **No**; candidate flag `validation_only=true` |
| `publishable-source-only` (opt-in) | **Manual workflow_dispatch from `main` only**, `--mode source-only --tag v0.2.0` without `--validation-only` | `r24-source-only-publishable-candidate-<run_id>` | **No**; publishable-*format* is not independently accepted distribution |

The `publish` job has a **job-level** guard
`github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')`
and is the only job with `contents: write` and `packages: write`.
The workflow root / candidate job are read-only. The `publish` job also
requires the independently protected `r24-release` GitHub Environment.
A technical candidate is **not** permission to create a tag, GitHub Release,
GHCR image or a binary/JAR/frontend-dist distribution.

**R3 / hard prerequisite — BLOCKED until CHANGELOG is ready:** The exact
source SHA **must** contain a nonempty `## [0.2.0]` CHANGELOG section for
a publishable-format archive. When only `## [Unreleased]` is present,
`scripts/r24-release.py` intentionally rejects packaging without
`--validation-only`. Do not bypass the check, and do not substitute a
validation-only archive as publishable proof. The AI policy, NOTICE and
required source-rights documentation PRs must be merged and the final
`main` source SHA frozen before the final independently verified candidate run.

### Proposed single-candidate evidence procedure after source freeze (R4)

> **POLICY CHANGE PROPOSAL — NOT EFFECTIVE UNTIL INDEPENDENT REVIEW AND MERGE.**
> This section proposes replacing the historical two-candidate requirement with
> **one fully verified publishable-format technical candidate** plus an independent
> build from the actual extracted archive. No candidate is release authorization.
> **Yến's formal PR #250 decision: NO / CHANGES_REQUESTED.** The current
> **two independent publishable-format R4 candidates remain mandatory** under #190.
> A single candidate plus an extracted-source build is **not equivalent** to two
> independent archive packaging runs: it loses the cross-run archive SHA256,
> MANIFEST, SBOM and member-byte reproducibility comparison. Buildability tests
> do not prove independently reproduced archive bytes. Any future reduction needs
> a newly approved, explicit acceptance of that evidentiary risk by the team.
> **No such approval exists; do NOT change #190 or run only one final candidate.**

1. Finalize bounded source-rights disposition for the actual archived files under #138;
   agree the actual release date and update the dated `## [0.2.0]` CHANGELOG section.
   Record a **full frozen source SHA on main** only after all amendments pass CI and
   independent review.
2. Dispatch **one** `workflow_dispatch` from `main` with
   `candidate_mode=publishable-source-only`. It creates no tag/release:

   ```bash
   gh workflow run release.yml --repo tricore-opentrix/opentrix --ref main -f candidate_mode=publishable-source-only
   ```

3. Confirm run SUCCESS, `headSha` equals the **exact frozen SHA**,
   `tag=v0.2.0`, `mode=source-only`, and `validation_only=false`.
   Record run ID, action URL and workflow inputs; reject evidence from any
   different SHA or from validation-only runs.
4. Download the source-only publishable-format artifact:

   ```bash
   RUN=RUN_ID
   gh run download "$RUN" --repo tricore-opentrix/opentrix --name "r24-source-only-publishable-candidate-$RUN" --dir evidence/r24
   cd evidence/r24
   sha256sum -c SHA256SUMS
   python3 /path/to/repo/scripts/r24-release.py verify --archive dxos-open-core-0.2.0.tar.gz --checksums SHA256SUMS
   tar -xOf dxos-open-core-0.2.0.tar.gz dxos-v0.2.0/MANIFEST.json > MANIFEST.inspected.json
   tar -xOf dxos-open-core-0.2.0.tar.gz dxos-v0.2.0/RELEASE-NOTES.md > NOTES.inspected.md
   cmp RELEASE-NOTES.md NOTES.inspected.md
   ```

   Independently inspect `MANIFEST.json` tag/source_sha/mode/file hashes,
   archive SHA256, `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES.md`,
   the three CycloneDX SBOMs and recorded rights/disposition exceptions.
   The source archive excludes backend/BFF application JARs, frontend dist,
   Docker/GHCR images and the Gradle Wrapper JAR.
5. Verify the **extracted tarball** in a temporary directory *outside a Git
   checkout* (no `.git`): check executable shell modes `0755` from Git index
   and build Backend/BFF with JDK 21 and **external Gradle 8.14.3** (not
   `./gradlew`), then run frontend install/build with Node 22.
   The `release.yml` candidate job runs this extracted-archive build check;
   an independent reviewer must inspect its logs and, where required, repeat
   the test without privileged services or shared Docker volumes.
6. Record the single candidate's URL/hash, archive verification, independent
   extracted-build verdict, rights/source-license links, limitations and
   reviewer findings in Issue #190. Any failed check or SHA change resets the
   candidate evidence to **PENDING**, not PASS. Prepare the separate
   `docs/06-deployment/r24-acceptances/v0.2.0.json` PR only afterward.

**One candidate is a technical artifact, not release permission.** No tag,
GitHub Release, GHCR or binary distribution until #138 disposition,
independent acceptance PR review and Environment/tag safeguards all pass.

## Independent acceptance and protected publishing

A versioned JSON must be merged to main in a **separate independently reviewed PR after source SHA is frozen**, under docs/06-deployment/r24-acceptances/<tag>.json. Point the tag at the earlier source SHA (not the newer acceptance commit), avoiding a circular self-reference. The publish workflow reads this file from main.

Both modes require tag, full source_sha, archive_sha256, explicit mode, independent reviewer assertion and supporting HTTPS evidence. For source-only v0.2.0 the reduced acceptance JSON additionally requires a verifiable independent `review_url` plus `evidence.source_rights`, `evidence.archive_verification`, and `evidence.extracted_source_build`. The rights URL must cover provenance/Apache-2.0, third-party assets, NOTICE and recorded UNKNOWN/RIGHTS_PENDING limitations; the archive URL must cover checksums/MANIFEST/SBOM/notes. The Draft release gate checks the live merged acceptance PR, its final-HEAD independent APPROVED review and file path. **F02:** it additionally compares Git blob SHA-1 of the exact publisher-used JSON bytes with GitHub Contents blob IDs at the approved PR HEAD, merge commit and current main. **F03:** stale/dismissed/self review, unmerged PR, absent file or unavailable API fail closed. **F04:** the evidence comment must carry the structured tag/source SHA/archive SHA256/reviewer/checklists and successful workflow-run identity described below. A bare HTTPS URL is rejected. **These changes are a Draft proposal, not effective release policy.**

- Binary mode: pinned eclipse-temurin:21-jre@sha256 digest, a CLEARED permissive group evidence URL, individual CLEARED exceptions for all other shipped licenses, source/relink, upstream texts, assets, OCI service/base images, checksums and notes evidence.
- Source-only v0.2.0 mode (proposed reduced schema): `source_rights`, `archive_verification`, `extracted_source_build` plus `reviewed_by` and `review_url`; binary license groups do not authorize this mode.

### Proposed machine-verifiable evidence checklist (F02–F04) — NOT effective release policy

The Draft acceptance schema retains three HTTPS evidence comment permalinks:
`evidence.source_rights`, `evidence.archive_verification`, and
`evidence.extracted_source_build`. Each link must point to a GitHub comment in
`tricore-opentrix/opentrix` (issue or pull-request conversation) by an
independent Yến/Ánh reviewer listed in `reviewed_by` who is NOT the acceptance
PR author. The comment must contain exactly one versioned structured block:

```text
<!-- R24_SOURCE_EVIDENCE_V1
{"kind":"source_rights","tag":"v0.2.0","mode":"source-only",
 "source_sha":"<40-character frozen source SHA>",
 "archive_sha256":"<64-character verified archive SHA256>",
 "reviewer":"phanyen06ym-ien","verdict":"PASS",
 "checks":{"source_provenance":true,"apache_2_0_rights":true,
 "third_party_attribution":true,"notice":true,
 "exceptions_disposition":true,"independent_rights_review":true},
 "unresolved_distribution_blockers":[],
 "references":["https://github.com/tricore-opentrix/opentrix/issues/138"]}
-->
```

The example is **not** a rights statement. Replace placeholders only after
checking real source/rights documents. The archive/build comments use the same
identity fields, their appropriate `kind`, `run_id` (integer) and the actual
GitHub Actions run URL in `references`.

| Kind | Mandatory checks (every listed key is exactly `true`) |
| --- | --- |
| `source_rights` | `source_provenance`, `apache_2_0_rights`, `third_party_attribution`, `notice`, `exceptions_disposition`, `independent_rights_review`; `unresolved_distribution_blockers` must be `[]` |
| `archive_verification` | `sha256sums`, `manifest`, `three_cyclonedx_sboms`, `license`, `notice`, `release_notes`, `frozen_sha`, `independent_archive_review` |
| `extracted_source_build` | `no_git_checkout`, `external_gradle_8_14_3_jdk21`, `backend_build`, `portal_bff_build`, `frontend_node22_build`, `independent_build_review` |

For archive/build links, the gate reads the live GitHub Actions run:
`workflow_dispatch`, `head_branch=main`, `head_sha=source_sha`,
`status=completed`, `conclusion=success`, and
`path=.github/workflows/release.yml` and **the actual unexpired artifact**
`r24-source-only-publishable-candidate-<run_id>` with a verified GitHub artifact
digest. GitHub REST run JSON does **not** expose workflow_dispatch inputs;
this artifact is emitted only by the workflow's publishable-source-only branch.
Both evidence records must
refer to the same run, and any missing metadata causes BLOCKED.
These are auditable technical checks, **not independent legal proof**.
Yến/Ánh must inspect actual R27 rights dispositions, GitHub logs, archive
hashes, MANIFEST, SBOM, LICENSE/NOTICE and source assets; no checklist can
turn `UNKNOWN`, `NOT_RECALLED` or `RIGHTS_PENDING` into `CLEARED`.

**F01 still blocks policy change:** The current TWO independently packaged
final candidates (with hash/byte comparison) remain mandatory in #190.
A proposed ONE-candidate evidence comment cannot replace that gate.

**Yến must establish the protected r24-release GitHub Environment with required independent reviewers (Yến and Ánh) plus v* tag protection ruleset BEFORE any tag is created or pushed.** A workflow environment declaration alone does not guarantee protected configuration.

GHCR image tags and GitHub Releases are non-atomic: partial publishing requires manual digest reconciliation rather than blind retries. The implementation owner must record final package digests, artifact hashes and status.

## Reproduce

1. Run python3 -m unittest discover -s scripts -p 'test_r24_*.py'.
2. Produce the R23 SBOMs and inventory; run python3 scripts/r24-upstream.py --root . --inventory build/r23/license-inventory.json --output build/r24/upstream.
3. Run python3 scripts/r24-release.py package --mode source-only --tag v0.2.0 --sha <full-source-SHA> --output dist/r24.
4. Run python3 scripts/r24-release.py verify --archive dist/r24/dxos-open-core-0.2.0.tar.gz --checksums dist/r24/SHA256SUMS and, from dist/r24, sha256sum -c SHA256SUMS. After the final source SHA and the required CHANGELOG entry are frozen, run **two independent** `publishable-source-only` workflow_dispatch candidates on the same frozen source SHA under the currently binding #190 rule. Verify both archives and compare SHA256/MANIFEST/member bytes, SBOM/NOTICE/notes; independently build the extracted source outside Git. One-candidate reduction remains UNAPPROVED (F01).
5. After merge, source SHA freeze, independent acceptance, Yến's environment/tag readiness and approved tag publication, verify real release assets, GHCR image digests (binary only), and the exact archive hash.

**R24 implementation Done** requires independent review, green CI and merge. **Full R24 source-only release Done** requires #138 rights clearance, exact-source #139 acceptance and review, protected `v0.2.0` tag publication, GitHub Release source-only assets and an independently verified downloaded SHA256SUMS. **Binary/JAR/GHCR distribution remains BLOCKED** until separately authorized; none of its obligations are waived.
