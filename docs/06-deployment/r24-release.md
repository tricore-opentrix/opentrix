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
`main` source SHA frozen before the two final candidate runs.

### Two-candidate evidence procedure after the final source freeze (R4)

1. Record the **full frozen source SHA** from `main`. Ensure the release
   CHANGELOG entry, required policy and NOTICE edits are reviewed and merged.
2. Use **main** and `candidate_mode=publishable-source-only` to dispatch
   the workflow **twice**, independently:

   ```bash
   gh workflow run release.yml --repo tricore-opentrix/opentrix --ref main -f candidate_mode=publishable-source-only
   gh workflow run release.yml --repo tricore-opentrix/opentrix --ref main -f candidate_mode=publishable-source-only
   ```

3. Record each Actions run ID and URL and check `headSha` of **both** runs
   against the frozen source SHA. If `main` moved, abort comparison and
   rerun both on the same newly approved SHA; never equate different source
   commits. Inspect status and SHA with
   `gh run view RUN_ID --repo tricore-opentrix/opentrix --json headSha,status,conclusion,url`.
4. Download the matching artifacts into different evidence folders
   (replace `RUN_ID_1` and `RUN_ID_2` with the real IDs):

   ```bash
   RUN1=RUN_ID_1
   RUN2=RUN_ID_2
   gh run download "$RUN1" --repo tricore-opentrix/opentrix      --name "r24-source-only-publishable-candidate-$RUN1" --dir evidence/run-1
   gh run download "$RUN2" --repo tricore-opentrix/opentrix      --name "r24-source-only-publishable-candidate-$RUN2" --dir evidence/run-2
   ```

5. Inspect **each** downloaded archive independently (example from repo root
   for run 1; repeat for run 2):

   ```bash
   cd evidence/run-1
   sha256sum dxos-open-core-0.2.0.tar.gz
   sha256sum -c SHA256SUMS
   python3 /path/to/repo/scripts/r24-release.py verify      --archive dxos-open-core-0.2.0.tar.gz --checksums SHA256SUMS
   tar -xOf dxos-open-core-0.2.0.tar.gz dxos-v0.2.0/MANIFEST.json > MANIFEST.inspected.json
   tar -xOf dxos-open-core-0.2.0.tar.gz dxos-v0.2.0/RELEASE-NOTES.md > NOTES.inspected.md
   cmp RELEASE-NOTES.md NOTES.inspected.md
   tar -tzf dxos-open-core-0.2.0.tar.gz | grep -E '(^|/)(backend|portal-bff|frontend)\.cdx\.json$'
   ```

   The three CycloneDX SBOMs must be in `compliance/`. Inspect the
   extracted `MANIFEST.inspected.json` for the exact full `source_sha`,
   `tag=v0.2.0`, `mode=source-only`, and `validation_only=false`.
   Confirm release notes match the archive, and `SHA256SUMS` matches
   the downloaded tarball.
6. Compare **archive SHA-256 byte-for-byte** between both runs; compare
   MANIFEST, archive member bytes, three SBOMs and release notes.
   Record the source SHA, both run URLs, both archive hashes, environment
   versions, mismatches and PASS/FAIL in Issue #190. Obtain independent
   review, then prepare the **separate** acceptance PR at
   `docs/06-deployment/r24-acceptances/v0.2.0.json`.

Validation-only candidate hashes from earlier SHAs do **not** replace this
evidence. Even if both publishable-format candidates match, a protected
tag/Release is **still blocked** until all independent rights, acceptance
and environment/tag gates pass.

## Independent acceptance and protected publishing

A versioned JSON must be merged to main in a **separate independently reviewed PR after source SHA is frozen**, under docs/06-deployment/r24-acceptances/<tag>.json. Point the tag at the earlier source SHA (not the newer acceptance commit), avoiding a circular self-reference. The publish workflow reads this file from main.

Both modes require tag, full source_sha, archive_sha256, explicit mode, independent reviewer assertion and supporting evidence. **SOURCE-ONLY hardening (separate technical PR, pending approval)** adds `acceptance_pr` (GitHub PR number known before final independent approval) and `candidate_run_ids` (**exactly two distinct numeric workflow run IDs**) without removing any existing SOURCE-ONLY evidence categories. Assertions in JSON are not review proof: verify the acceptance PR and underlying evidence.

- Binary mode: pinned eclipse-temurin:21-jre@sha256 digest, a CLEARED permissive group evidence URL, individual CLEARED exceptions for all other shipped licenses, source/relink, upstream texts, assets, OCI service/base images, checksums and notes evidence.
- Source-only mode: evidence for source_provenance, source_license, sbom_source_boundary, archive_and_checksums and release_notes; binary license groups do not authorize this mode.

### SOURCE-ONLY gate hardening: F01–F04 (technical proposal; not release acceptance)

**Existing two-candidate policy is unchanged.** The acceptance JSON must include
`candidate_run_ids: [RUN_ID_1, RUN_ID_2]` with **two different integers**, plus
`acceptance_pr` containing the acceptance PR number. The publisher discovers its actual final-HEAD APPROVED review via GitHub API.
All five original `evidence` fields are retained, not replaced or merged:
`source_provenance`, `source_license`, `sbom_source_boundary`,
`archive_and_checksums`, and `release_notes`.

**F01 — actual reproducibility:** At a future authorized tag-publish gate,
the script fetches both GitHub `workflow_dispatch` runs (main, exact frozen
source SHA, success), resolves each `r24-source-only-publishable-candidate-<run_id>`
artifact, downloads its actual ZIP bytes with a read-only Actions token, checks
artifact ZIP SHA-256, and unpacks the tarball/checksums/notes in a bounded
temporary directory. Each archive must have `validation_only=false`,
`mode=source-only`, exact tag/SHA, verified `SHA256SUMS`, and match the archive
SHA256 reviewed in acceptance. Both MANIFESTs, all archive members including
the three SBOMs, and release notes must equal the verified publisher archive.
Any missing run, duplicate ID, different source commit/hash/member, expired
artifact, API denial, oversized/unreadable ZIP or failed workflow is BLOCKED.
Rebuilding the extracted SOURCE-ONLY archive without `.git` remains an
**additional** buildability check, NOT a substitute for the second candidate.

**F02 — acceptance JSON byte integrity:** `verify_independent_review()`
uses the `acceptance_pr` number (available before approval), discovers the
latest independent APPROVED review at the final PR HEAD via GitHub API,
and compares the Git blob object ID of the exact JSON bytes read by publisher
to file blob IDs at reviewed PR HEAD, merged commit and current `main`.
A future review URL inside its own JSON would cause a circular dependency,
so it is NOT required. Stale, superseded, dismissed or unmerged reviews fail.

**F04 — human-auditable evidence:** Each existing evidence URL must be a
GitHub issue/PR comment permalink authored by an authorized independent
reviewer and contain one versioned `R24_SOURCE_EVIDENCE_V1` JSON block with
`kind`, `tag`, `mode=source-only`, `source_sha`, `archive_sha256`,
`reviewer`, `verdict=PASS`, `checks`, and actual supporting `references`.
The `source_provenance` and `source_license` comments additionally declare
`unresolved_distribution_blockers: []` **only after actual clearance**.
The `archive_and_checksums` comment includes the two exact `candidate_run_ids`
and both workflow-run URLs. Checklists, even when valid, are not independent
proof of rights; do not turn `UNKNOWN`/`NOT_RECALLED`/`RIGHTS_PENDING` into
`CLEARED` without #138 evidence. The required checklist keys are:

| Existing evidence key | Required PASS checks |
| --- | --- |
| `source_provenance` | `file_origin`, `contributor_authority`, `third_party_assets`, `independent_origin_review` |
| `source_license` | `osi_approved_license`, `apache_2_0`, `notice_and_attribution`, `exceptions_disposition`, `independent_license_review` |
| `sbom_source_boundary` | `backend_sbom`, `portal_bff_sbom`, `frontend_sbom`, `inventory`, `no_binary_or_ghcr_distribution` |
| `archive_and_checksums` | `two_independent_packaging_runs`, `sha256sums`, `manifest`, `sbom_member_bytes`, `notes_and_notice`, `extracted_source_build`, `independent_archive_review` |
| `release_notes` | `exact_version_notes`, `source_only_scope`, `rights_limitations`, `independent_notes_review` |

Example **format only**, not an actual rights attestation:

```text
<!-- R24_SOURCE_EVIDENCE_V1
{"kind":"source_provenance","tag":"v0.2.0","mode":"source-only",
 "source_sha":"<actual 40-character frozen SHA>",
 "archive_sha256":"<actual 64-character archive SHA256>",
 "reviewer":"phanyen06ym-ien","verdict":"PASS",
 "checks":{"file_origin":true,"contributor_authority":true,
 "third_party_assets":true,"independent_origin_review":true},
 "unresolved_distribution_blockers":[],
 "references":["https://github.com/tricore-opentrix/opentrix/issues/138"]}
-->
```

These are additional verification requirements to review in a **separate
technical PR**. Neither this draft nor successful PR CI authorizes final R4
dispatch, source freeze, tag, Release, Docker/JAR/GHCR distribution or
declaration that #138 rights blockers have been cleared.

**Yến must establish the protected r24-release GitHub Environment with required independent reviewers (Yến and Ánh) plus v* tag protection ruleset BEFORE any tag is created or pushed.** A workflow environment declaration alone does not guarantee protected configuration.

GHCR image tags and GitHub Releases are non-atomic: partial publishing requires manual digest reconciliation rather than blind retries. The implementation owner must record final package digests, artifact hashes and status.

## Reproduce

1. Run python3 -m unittest discover -s scripts -p 'test_r24_*.py'.
2. Produce the R23 SBOMs and inventory; run python3 scripts/r24-upstream.py --root . --inventory build/r23/license-inventory.json --output build/r24/upstream.
3. Run python3 scripts/r24-release.py package --mode source-only --tag v0.2.0 --sha <full-source-SHA> --output dist/r24.
4. Run python3 scripts/r24-release.py verify --archive dist/r24/dxos-open-core-0.2.0.tar.gz --checksums dist/r24/SHA256SUMS and, from dist/r24, sha256sum -c SHA256SUMS. After the final source SHA and the required CHANGELOG entry are frozen, run **two** `publishable-source-only` workflow_dispatch candidates per the procedure above; compare archive SHA-256, MANIFEST, SBOMs, SHA256SUMS and notes.
5. After merge, source SHA freeze, independent acceptance, Yến's environment/tag readiness and approved tag publication, verify real release assets, GHCR image digests (binary only), and the exact archive hash.

**R24 implementation Done** requires independent review, green CI and merge. **Full R24 source-only release Done** requires #138 rights clearance, exact-source #139 acceptance and review, protected `v0.2.0` tag publication, GitHub Release source-only assets and an independently verified downloaded SHA256SUMS. **Binary/JAR/GHCR distribution remains BLOCKED** until separately authorized; none of its obligations are waived.
