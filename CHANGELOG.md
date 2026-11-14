<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Changelog

User-visible DX-OS Open Core changes are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Align architecture and documentation indexes with ADR-009/016/017/018: Helpdesk-first competition scope, S3-compatible storage direction, and separation of current behavior from target architecture (#221).
- Align GitHub setup label and milestone descriptions with accepted architecture decisions; editing the script does not update live GitHub metadata (#223).
- Add the shared-network-namespace demo spike for PostgreSQL, Keycloak and Backend (#226), and the versioned `tricore` demo realm (#227). These changes alone do not establish complete browser E2E acceptance.
- Add Contributor Covenant 2.1 with its own attribution/license and link the contribution conduct policy from README and CONTRIBUTING (#228).
- R24 tag-triggered release-candidate packaging (Java jars, frontend, SBOM/NOTICE inventory, SHA256SUMS), with independent distribution-acceptance gate before GitHub Release/GHCR publication.
- R24 reproducible release tooling, source-only packaging, archive checksums and versioned release-note generation; binary build candidates remain nonpublishable without separate clearance.
- A fail-closed independent release acceptance gate; candidate builds do not imply redistribution clearance.
- R26 canonical OpenTrix repository links and documentation alignment (PR #136).

### Changed

- Portal #233: use IT Helpdesk · OpenTrix branding and simpler request/version copy.
- Portal #233: add the integration-local login panel and CSRF-protected BFF logout; real OIDC role switching remains unverified.
- Portal #233 / #106: show Vietnamese workflow labels and distinct text badges, preserving canonical API values and unknown-state fallback.
- R26: Prepare OpenTrix canonical repository identity and update organization links, documentation and setup defaults after the existing repository rename; independent post-cutover acceptance remains pending.
- Clarify root license information and distinguish CI REUSE/SPDX checks from source-rights clearance (#228).

### Verification limits

- This is the planned source-only `v0.2.0` release scope, not confirmation that a public release occurred, nor proof of production integration or R12 browser acceptance.
- Publishing requires independently approved source-origin and Apache-2.0 rights review (#138), exact-source archive evidence and the independent source-only acceptance (#139). No JAR, built Frontend dist, container image or GHCR distribution is authorized.
- The v0.2.0 tag and release date are assigned only when release gates pass; do not backdate or treat this Unreleased section as a published release.

## [0.1.0] - 2026-11-04

### Added

- IT Helpdesk Backend HTTP API (nine application routes) with tenant/resource-scoped authorization, PostgreSQL 17 persistence and audited workflow transitions.
- Portal BFF with OIDC Authorization Code + PKCE, server-side browser session, and CSRF protection.
- React IT Helpdesk Portal: standalone MOCK demonstration and `integration-local` integration build mode; live browser/SSO acceptance remains a separate gate.
- Apache-2.0 root `LICENSE` and `NOTICE` files for original DX-OS work, subject to ongoing third-party/SPDX verification tracked by Issue #38.
- ArchUnit Core dependency rules and negative canary tests.
- Contribution guidelines, issue and PR templates, and CODEOWNERS.
- Shared CI for PRs to `main`: backend build and tests, applicable application
  builds, repository checks, and Identity–Gateway security regressions.

### Changed

- `backend/gradlew` is executable on Linux and macOS.
- The Helpdesk HTTP API uses a scoped HTTP 404 / `NOT_FOUND` response for
  hidden or missing resources; the Generic Workflow HTTP API retains its
  pre-existing distinct `DEFINITION_NOT_FOUND` / `INSTANCE_NOT_FOUND` public
  codes and messages. Generic contract evolution is tracked in Issue #105.

### Fixed

- Linux backend build and tests: restored three SQL evidence fixtures, pinned the
  manifest hash to Git LF bytes, and limited a PowerShell-specific test to Windows.
- Helpdesk CREATE rejects missing exact technical authorities before protected
  definition/binding lookups; uncertain Workflow commits return HTTP 503 with
  `COMMIT_OUTCOME_UNKNOWN` and must not be retried automatically.

### Removed

- R25: Remove the legacy `com.tricore.dxos.request` prototype (controllers, domain, DTOs, repositories, services and tests) and retire `/api/v1/requests/*` routes and their `CLOSED` lifecycle. Preserve historical Flyway V1/V2 migration bytes; Helpdesk remains available at `/api/v1/mvp/requests`.

- The separate Issue #23 workflow; its security gates run in shared CI.

[0.1.0]: https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0
