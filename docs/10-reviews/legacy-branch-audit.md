# OPENTRIX — Legacy Branch and Pull Request Audit

**Issue:** [#171](https://github.com/tricore-opentrix/opentrix/issues/171)  
**Snapshot:** 2026-11-10, before creating this audit branch  
**Comparison base:** `main` at `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`  
**Verdict:** **REVIEW REQUIRED — NO DELETION AUTHORIZED**

## Executive summary

This audit prepares OPENTRIX for a simpler open-source GitHub Flow while preserving release artifacts, contributor rights and security evidence, repository history, and ongoing stacked Pull Requests.

| Disjoint group | Number | Disposition |
|---|---:|---|
| Protected `main` and `gh-pages` | 2 | KEEP |
| Open PR head branches (seven also serve as stacked PR bases) | 47 | KEEP / REVIEW |
| Additional PR base-only branch: `feature/issue39-mvp-integration` | 1 | KEEP / INVESTIGATE |
| Unlinked branch HEADs already reachable from `main` | **16** | RETIREMENT REVIEW CANDIDATE |
| Unlinked branch HEADs with non-ancestor commits | **50** | INVESTIGATE / PRESERVE |
| **Total before this audit branch** | **116** | **Zero approved deletions** |

The inventory covers two paginated GitHub branch responses (100 + 16) and 47 open PRs. All 66 originally unlinked branches were compared to `main` with GitHub's compare-commits API. The audit itself creates one new temporary documentation branch, not included in the historical 116-branch snapshot.

**Meaning of comparison:** `ANCESTRY_REACHABLE` means `ahead_by=0`, so a branch's tip is reachable from `main`. `NON_ANCESTOR` means `ahead_by>0`, so Git ancestry identifies extra commits not on `main`. This does not establish whether patches were squash-merged or cherry-picked, nor whether a branch is safe to delete. No patch-equivalence or local-worktree check has been completed.

## High-risk dependencies

| Workstream | Stacked PR chain | Review requirement |
|---|---|---|
| R27B compliance | #164 → #169 | Preserve parent before child |
| R28 Core ACL | #160 → #165 → #168 → #170 | Do not delete stacked bases |
| License evidence | #161 → #162 | Retain contributor-rights evidence |
| Provenance | #149 → #152 | Retain review routing |
| Rights register | #143 → #151 | Retain archive metadata history |
| Portal BFF | #98 targets `feature/issue39-mvp-integration` | Resolve base-only branch |
| Website | #81, #92, #121, #137 target `gh-pages` | Confirm Pages deployment source |

`gh-pages` is GitHub-protected. Its actual publishing configuration has not been verified. Keep it until a replacement deployment has been demonstrated and reviewed.

## Frozen preservation boundaries

- **R24 source-only baseline:** `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`. Preserve MANIFEST, SHA256SUMS, workflow runs and source archive evidence.
- **R27 compliance:** [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138), rights register, contributor declarations, provenance evidence, NOTICE/license questions, and independent-review findings.
- Do not interpret green CI, a reachable commit, or an old PR as confirmation of contributor rights or release acceptance.
- Do not change Git tags, force-push `main`, or remove any branch as part of this report.

## Disposition rules

**KEEP:** protected branches, open-PR heads and required bases; evidence/deployment refs.  
**RETIREMENT REVIEW CANDIDATE:** ancestor-reachable branches after confirming no external dependencies, local work, or separate evidence retention requirement.  
**INVESTIGATE:** branches with unverified unique commits, patch equivalence, worktree dependencies, or owner attribution.  
**DELETE_CANDIDATE:** only after explicit, independent reviewer approval, current HEAD SHA verification, recovery plan and separate authorization. **None currently approved.**

## Reviewer routing

| Reviewer | Proposed ownership of the review | Required confirmation |
|---|---|---|
| Bảo | Backend, Helpdesk, Workflow, release | Unique commits, historic releases, worktrees and unpushed work |
| Ánh | Frontend, BFF, website | Portal dependencies, `gh-pages` deployment, worktrees |
| Yến | Identity, security, provenance | Compliance evidence and reviewer independence |

These are assignments for review, **not recorded approvals**. Contributors must not be counted as independent reviewers of their own surviving content.

## Acceptance checklist

- [ ] Verify all 16 ancestry-reachable tips have no active CI, deployment, worktree, PR, tag or evidence references.
- [ ] Trace the 50 non-ancestor branches to closed/merged PRs, squash/cherry-picked patch equivalence and contributor decisions.
- [ ] Verify stacked PR bases and website deployment.
- [ ] Confirm R24/R27 artifacts remain reachable, without asserting rights clearance.
- [ ] Document each branch's final owner, reviewer, evidence URL and disposition.
- [ ] Agree on a recovery plan; approve any destructive operations separately.
- [ ] Re-fetch current HEAD SHAs and PR statuses before any actual deletion.

## Appendix A — All 66 unlinked remote branches at snapshot

Every `NON_ANCESTOR` branch needs further comparison; **neither classification authorizes deletion**.

| # | Branch | Full HEAD SHA | Relationship to main | Current disposition |
|---:|---|---|---|---|
| 1 | `candidate/docs83-workflow-data-p2-20261031` | `c1576ac626b88dfd7aea79ccd98e820c7550e435` | NON_ANCESTOR | INVESTIGATE |
| 2 | `chore/issue26-hosted-verification-gate-20261017` | `ef8fe6f1a8ce933bb5e9c6fd3ae04b07a2b8b83e` | NON_ANCESTOR | INVESTIGATE |
| 3 | `chore/olp-folder-skeleton-20261028` | `845eea767a9e1d380d0ccc71c4c8926b2709d859` | NON_ANCESTOR | INVESTIGATE |
| 4 | `ci/verify-pr80-sql-fixtures-20261031` | `5b1290f140627e0ef6369e05136130a7de71c667` | NON_ANCESTOR | INVESTIGATE |
| 5 | `diagnostic/pr80-windows-acl-20261031` | `24503795c8b18b59ee7aaf198dded44518c9fd61` | NON_ANCESTOR | INVESTIGATE |
| 6 | `docs/adr010-core-helpdesk-service-boundary` | `3e049488dda57cf155ef1804f524b96c9e499e25` | ANCESTRY_REACHABLE | INVESTIGATE |
| 7 | `docs/capability-technology-baseline-20261031` | `49abc6f2699a68e3d10317a11c6447d09f45324b` | NON_ANCESTOR | INVESTIGATE |
| 8 | `docs/consolidate-navigation-20261031` | `6c256e9ce3ca60eedf9aa3c4598921b3ba81752d` | NON_ANCESTOR | INVESTIGATE |
| 9 | `docs/core-architecture-alignment` | `48cc6b3c09a492f5c7e23c0c63723be40595e62c` | NON_ANCESTOR | INVESTIGATE |
| 10 | `docs/helpdesk-swagger-openapi-20261030` | `3d5b5c3f4a413633fe1da1b874aa9743f2c6dc3c` | NON_ANCESTOR | INVESTIGATE |
| 11 | `docs/import-workspace` | `91bcbe63083558723b1e418ee8d0ef538ecfcdd3` | NON_ANCESTOR | INVESTIGATE |
| 12 | `docs/integrate-pr78-workspace` | `05c7e04f4e5d1e5693a6422fb301f0774155bf01` | NON_ANCESTOR | INVESTIGATE |
| 13 | `docs/issue-reorganization-review-20261031` | `2a94a46579c4d3d9999b0da831d9c3bb505cc3e2` | ANCESTRY_REACHABLE | INVESTIGATE |
| 14 | `docs/olp-project-documentation-20261025` | `16609ad6f4fdd0212d50515f3e199c7a4b546c8a` | NON_ANCESTOR | INVESTIGATE |
| 15 | `docs/r27-yen-git-blob-evidence-20261107` | `fde4159d324bfe483aa083074923b3ad1bf94ecd` | NON_ANCESTOR | INVESTIGATE |
| 16 | `docs/r28-q03-core-enforcement-closure-20261109` | `f26f0ed10e80c108015944e46d61bad481ca07fd` | NON_ANCESTOR | INVESTIGATE |
| 17 | `docs/repository-layout-governance-20261031` | `9a186ffe18b1fb5300cf331bfcae78cfc9373ba6` | NON_ANCESTOR | INVESTIGATE |
| 18 | `docs/restructure-documentation` | `2bda552126cbe5850dd17b88c733c6e42ad6a2dd` | ANCESTRY_REACHABLE | INVESTIGATE |
| 19 | `docs/stage6-security-review-549de8c-20261027` | `bdaf91a6bb5fcb7a6712836be7875dbafed3b3a9` | NON_ANCESTOR | INVESTIGATE |
| 20 | `docs/53-authz-evidence-mapping` | `00c42a987c35453eccc3666c4ab4fa2637757987` | ANCESTRY_REACHABLE | INVESTIGATE |
| 21 | `docs/53-history-visibility-review` | `7bde57373f85b110d456629552f964af8df7d9c4` | ANCESTRY_REACHABLE | INVESTIGATE |
| 22 | `feat/data-object-storage-contract` | `a66d6352c90c35afe6c34949d3bf7b452f2a4001` | ANCESTRY_REACHABLE | INVESTIGATE |
| 23 | `feature/data-core-contracts` | `ce56984973f3e7308f9e6a7e243163724b603e99` | ANCESTRY_REACHABLE | INVESTIGATE |
| 24 | `feature/data-postgres-adapter` | `899ef1132d9b1ff01d6db6f1efc2ea3a5c0d7aa0` | ANCESTRY_REACHABLE | INVESTIGATE |
| 25 | `feature/gateway-authorization` | `fd5469ef6a6607c6940c5c22e61d4c078fda13d9` | ANCESTRY_REACHABLE | INVESTIGATE |
| 26 | `feature/identity-oidc-runtime` | `d0d71dcc34b157c1cc60076f21fdcd40d790bf1e` | ANCESTRY_REACHABLE | INVESTIGATE |
| 27 | `feature/issue23-d2-admin-candidate` | `db6b1a8007d2cf4720e9dff6996572a1e819bc49` | NON_ANCESTOR | INVESTIGATE |
| 28 | `feature/issue23-identity-gateway-token-handoff-20261019` | `68c0fe018297a053d79f9036be11a817a0ff8ffc` | ANCESTRY_REACHABLE | INVESTIGATE |
| 29 | `feature/issue23-p1-02-integrity` | `549de8c63442d89dd03ff71a699848c10afc9b98` | NON_ANCESTOR | INVESTIGATE |
| 30 | `feature/issue23-secure-instance-id-foundation` | `ff824fc827cdef448fff82d907cef0d50113d81a` | NON_ANCESTOR | INVESTIGATE |
| 31 | `feature/issue23-stage3-authorized-workflow-service` | `4a2aa7e534ef9fd34a88eb78291abaa9771dc038` | NON_ANCESTOR | INVESTIGATE |
| 32 | `feature/issue23-stage4-exact-authority` | `b3bd87dd62c432df33163538ce382e14f3c1a19c` | NON_ANCESTOR | INVESTIGATE |
| 33 | `feature/issue23-stage5-tenant-resource-acl` | `32ca73fa8444ab51cf7cf30baa90fb39938b627b` | NON_ANCESTOR | INVESTIGATE |
| 34 | `feature/issue23-stage6-core-impl` | `11035ed204c76e3fcb4e9f565e17de366f60d089` | NON_ANCESTOR | INVESTIGATE |
| 35 | `feature/issue23-stage6-guarded-actions-candidate-20261021` | `663d7e51ce8ac21bb619b0e57609764df54bcfdd` | NON_ANCESTOR | INVESTIGATE |
| 36 | `feature/issue23-stage6-s61-postgres-contract` | `db0decfd19b408d000bf02144ec88dc878f332c4` | NON_ANCESTOR | INVESTIGATE |
| 37 | `feature/issue26-supabase-clean` | `5e5b48dce5d9b59c9ddee8bf3cd72c1d4006db26` | NON_ANCESTOR | INVESTIGATE |
| 38 | `feature/issue37-openapi-swagger-local` | `667f5e854a78ddfd7b5ab73eabc5057087f8d572` | NON_ANCESTOR | INVESTIGATE |
| 39 | `feature/issue39-portal-ui` | `076b9cba12af2841ec1b3dc2efd6530b8f15384b` | NON_ANCESTOR | INVESTIGATE |
| 40 | `feature/issue39-university-portal` | `ef521effa86b804e0ef7f036361ea60ba874fa33` | NON_ANCESTOR | INVESTIGATE |
| 41 | `feature/issue39-university-ui` | `00b10fa43d01cc3dcca725b2ed66a43bdaa92268` | NON_ANCESTOR | INVESTIGATE |
| 42 | `feature/issue53-helpdesk-backend` | `e12d105c89400a5fd69dd6cc1fca670ff1f04f51` | NON_ANCESTOR | INVESTIGATE |
| 43 | `feature/issue53-it-mvp-api-review-scaffold-20261025` | `4d9982d5bd35b831c6514569e32b4a54cba2bb19` | NON_ANCESTOR | INVESTIGATE |
| 44 | `feature/issue53-java-helpdesk-mvp-20261028` | `f943d33c7b7c003fc44d0234e4c912f24dcee847` | NON_ANCESTOR | INVESTIGATE |
| 45 | `feature/local-filesystem-storage-demo` | `01d14d35ac43a44e111051dc81e9480df69a7ad5` | NON_ANCESTOR | INVESTIGATE |
| 46 | `feature/portal-bff-session` | `d833b363d22c1ad30a1f5d7bdc7b3d7712fb7d27` | NON_ANCESTOR | INVESTIGATE |
| 47 | `feature/workflow-http-api` | `d85cf6858869347a1eb0f677ee63ea1e2f9f0619` | ANCESTRY_REACHABLE | INVESTIGATE |
| 48 | `feature/workflow-persistence-contracts` | `2efba4e8c79759f035f1e0cf6d2ec93716f6ffa9` | ANCESTRY_REACHABLE | INVESTIGATE |
| 49 | `feature/workflow-runtime` | `ad684d018a245d7debc816bcaf54d2a786f2a835` | ANCESTRY_REACHABLE | INVESTIGATE |
| 50 | `feature/09-audit-attachment` | `1e2aa20940d84e53ca86d0021def30ca83e36977` | NON_ANCESTOR | INVESTIGATE |
| 51 | `fix/data-input-stream-sanitization` | `fcc45fb65dc6c39ee5f75fd32f99f2a4de05241f` | ANCESTRY_REACHABLE | INVESTIGATE |
| 52 | `fix/issue23-gateway-error-bridge-mvp-20261021` | `089a779af5a19321306fcc58e6f1aff8cf7a7050` | NON_ANCESTOR | INVESTIGATE |
| 53 | `fix/issue26-hosted-worker-safety-20261017` | `1488bbbcfdd0a9b493a97049efffbc987b134d1d` | NON_ANCESTOR | INVESTIGATE |
| 54 | `fix/pr80-windows-acl-test-fixture-20261031` | `f06e0b05176702c7c5d49207f956f35357a17905` | NON_ANCESTOR | INVESTIGATE |
| 55 | `fix/pr93-windows-launchers-20261101` | `2b8b29070b9fc51230e008a0ae70f8acefe5994f` | NON_ANCESTOR | INVESTIGATE |
| 56 | `fix/r16-mobile-overflow` | `182397709f855ae8407d590f58e0a2451f7a5dc7` | NON_ANCESTOR | INVESTIGATE |
| 57 | `fix/request-jpa-public-schema` | `6400a486658bee717a871e58927ee9b66fdff7ef` | ANCESTRY_REACHABLE | INVESTIGATE |
| 58 | `fix/workflow-evidence-sql-regression` | `16d1f00493ec6b8eaeb5fac466a48c7f0469ed1e` | NON_ANCESTOR | INVESTIGATE |
| 59 | `integration/helpdesk-browser-e2e-20261029` | `b6e05d080ebb24b54cc4d61dc4e20e2907fd2eaa` | NON_ANCESTOR | INVESTIGATE |
| 60 | `mvp/fast-track-local-20261101` | `4ddedeaa88f99044785f3eba198946ad3ecf0c80` | NON_ANCESTOR | INVESTIGATE |
| 61 | `review/d2a-identity-evidence` | `2ce628ac79cd797c73df04160ec74d391c40e183` | NON_ANCESTOR | INVESTIGATE |
| 62 | `review/issue25-pg17-acceptance-20261101` | `045ef7672fbe5508063bb7b46035a738646d22a6` | NON_ANCESTOR | INVESTIGATE |
| 63 | `review/issue87-app-p0-01-proposal-20261101` | `22bc977b894f91d44a836cb4c39bf4f0da566247` | NON_ANCESTOR | INVESTIGATE |
| 64 | `review/issue87-integration-phase3-20261101` | `fe55347908eed6a351ca9724be899138f7683081` | NON_ANCESTOR | INVESTIGATE |
| 65 | `test/issue53-neg03-neg04` | `583feacfa79eb32ed36ee392628723b2738494d9` | NON_ANCESTOR | INVESTIGATE |
| 66 | `test/r22-missing-spdx-canary-20261105` | `a87204ca1ea17ac83cce983cb3235d2ecc6511e5` | NON_ANCESTOR | INVESTIGATE |

## Appendix B — All 47 open PRs at snapshot

| PR | Head | Base | State | Disposition |
|---|---|---|---|---|
| [#170](https://github.com/tricore-opentrix/opentrix/pull/170) | `review/r28-q03-m5-isolated-verification-20261109` | `docs/r28-r27a-p0-dependency-contract-20261109` | Draft | KEEP / REVIEW |
| [#169](https://github.com/tricore-opentrix/opentrix/pull/169) | `docs/r27b-step02-s02-01-matrix` | `docs/r27b-step01-canonical-inventory` | Draft | KEEP / REVIEW |
| [#168](https://github.com/tricore-opentrix/opentrix/pull/168) | `docs/r28-r27a-p0-dependency-contract-20261109` | `docs/r28-g0-design-readiness-review-chatgpt-20261109` | Draft | KEEP / REVIEW |
| [#167](https://github.com/tricore-opentrix/opentrix/pull/167) | `docs/r31-112-helpdesk-api-crosswalk` | `main` | Draft | KEEP / REVIEW |
| [#165](https://github.com/tricore-opentrix/opentrix/pull/165) | `docs/r28-g0-design-readiness-review-chatgpt-20261109` | `docs/r27-pr0b-adr015-g0-contract` | Draft | KEEP / REVIEW |
| [#164](https://github.com/tricore-opentrix/opentrix/pull/164) | `docs/r27b-step01-canonical-inventory` | `main` | Draft | KEEP / REVIEW |
| [#162](https://github.com/tricore-opentrix/opentrix/pull/162) | `docs/living-license-evidence` | `docs/license-evidence-consolidation` | Draft | KEEP / REVIEW |
| [#161](https://github.com/tricore-opentrix/opentrix/pull/161) | `docs/license-evidence-consolidation` | `main` | Draft | KEEP / REVIEW |
| [#160](https://github.com/tricore-opentrix/opentrix/pull/160) | `docs/r27-pr0b-adr015-g0-contract` | `main` | Draft | KEEP / REVIEW |
| [#159](https://github.com/tricore-opentrix/opentrix/pull/159) | `docs/r27-pr0a-adr010-boundary` | `main` | Open | KEEP / REVIEW |
| [#158](https://github.com/tricore-opentrix/opentrix/pull/158) | `docs/r37-readme-linux` | `main` | Open | KEEP / REVIEW |
| [#157](https://github.com/tricore-opentrix/opentrix/pull/157) | `lexuanbao258-collab-patch-1` | `main` | Draft | KEEP / REVIEW |
| [#156](https://github.com/tricore-opentrix/opentrix/pull/156) | `feature/r33-bff-transport-integration-20261107` | `main` | Draft | KEEP / REVIEW |
| [#155](https://github.com/tricore-opentrix/opentrix/pull/155) | `docs/r27-yen-group-c-content-reconciliation-20261107` | `main` | Draft | KEEP / REVIEW |
| [#154](https://github.com/tricore-opentrix/opentrix/pull/154) | `docs/r27-anh-git-blob-crosswalk-20261107` | `main` | Draft | KEEP / REVIEW |
| [#152](https://github.com/tricore-opentrix/opentrix/pull/152) | `docs/r27-s6-13-matrix-routing-20261107` | `docs/r27-step6-contributor-provenance-20261107` | Draft | KEEP / REVIEW |
| [#151](https://github.com/tricore-opentrix/opentrix/pull/151) | `docs/r27-s6-13-register-routing-20261107` | `docs/r27-rights-packages-20261107` | Draft | KEEP / REVIEW |
| [#150](https://github.com/tricore-opentrix/opentrix/pull/150) | `docs/r27-s6-01-02-identity-evidence-20261107` | `main` | Draft | KEEP / REVIEW |
| [#149](https://github.com/tricore-opentrix/opentrix/pull/149) | `docs/r27-step6-contributor-provenance-20261107` | `main` | Draft | KEEP / REVIEW |
| [#148](https://github.com/tricore-opentrix/opentrix/pull/148) | `docs/r27-step5-license-notice-handoff-20261107` | `main` | Draft | KEEP / REVIEW |
| [#147](https://github.com/tricore-opentrix/opentrix/pull/147) | `docs/r27-step4-status-id-vocabulary-20261107` | `main` | Draft | KEEP / REVIEW |
| [#146](https://github.com/tricore-opentrix/opentrix/pull/146) | `docs/r27-document-register-20261107` | `main` | Draft | KEEP / REVIEW |
| [#145](https://github.com/tricore-opentrix/opentrix/pull/145) | `feature/r29-typed-usecase-contract-20261107` | `main` | Draft | KEEP / REVIEW |
| [#144](https://github.com/tricore-opentrix/opentrix/pull/144) | `docs/r27-anh-rights-disposition-20261107` | `main` | Draft | KEEP / REVIEW |
| [#143](https://github.com/tricore-opentrix/opentrix/pull/143) | `docs/r27-rights-packages-20261107` | `main` | Draft | KEEP / REVIEW |
| [#142](https://github.com/tricore-opentrix/opentrix/pull/142) | `docs/r27-identity-provenance-evidence` | `main` | Draft | KEEP / REVIEW |
| [#139](https://github.com/tricore-opentrix/opentrix/pull/139) | `docs/infra-r24-rc1-source-acceptance` | `main` | Draft | KEEP / REVIEW |
| [#137](https://github.com/tricore-opentrix/opentrix/pull/137) | `docs/site-r26-opentrix-links-20261105` | `gh-pages` | Draft | KEEP / REVIEW |
| [#128](https://github.com/tricore-opentrix/opentrix/pull/128) | `feat/portal-opentrix-v621` | `main` | Open | KEEP / REVIEW |
| [#124](https://github.com/tricore-opentrix/opentrix/pull/124) | `feat/portal-v4-ui-preview` | `main` | Draft | KEEP / REVIEW |
| [#123](https://github.com/tricore-opentrix/opentrix/pull/123) | `docs/infra-r21-compose-plan` | `main` | Open | KEEP / REVIEW |
| [#122](https://github.com/tricore-opentrix/opentrix/pull/122) | `chore/r25-spdx-audit` | `main` | Open | KEEP / REVIEW |
| [#121](https://github.com/tricore-opentrix/opentrix/pull/121) | `docs/r16-mobile-reflow` | `gh-pages` | Open | KEEP / REVIEW |
| [#108](https://github.com/tricore-opentrix/opentrix/pull/108) | `validation/r10-pr103-pg17-20261103` | `main` | Draft | KEEP / REVIEW |
| [#100](https://github.com/tricore-opentrix/opentrix/pull/100) | `docs/issue89-security-evidence-matrix` | `main` | Draft | KEEP / REVIEW |
| [#99](https://github.com/tricore-opentrix/opentrix/pull/99) | `test/identity-d2a-evidence-main` | `main` | Draft | KEEP / REVIEW |
| [#98](https://github.com/tricore-opentrix/opentrix/pull/98) | `feature/a05-portal-bff-integration` | `feature/issue39-mvp-integration` | Draft | KEEP / REVIEW |
| [#92](https://github.com/tricore-opentrix/opentrix/pull/92) | `docs/olp-report-docs-readiness-20261031` | `gh-pages` | Draft | KEEP / REVIEW |
| [#81](https://github.com/tricore-opentrix/opentrix/pull/81) | `docs/portal-quality-gates-20261031` | `gh-pages` | Draft | KEEP / REVIEW |
| [#76](https://github.com/tricore-opentrix/opentrix/pull/76) | `docs/application-anh-docs` | `main` | Open | KEEP / REVIEW |
| [#75](https://github.com/tricore-opentrix/opentrix/pull/75) | `chore/remove-supabase-from-olp-mvp-20261028` | `main` | Draft | KEEP / REVIEW |
| [#69](https://github.com/tricore-opentrix/opentrix/pull/69) | `test/issue23-olp-pg17-e2e-preflight-20261027` | `main` | Draft | KEEP / REVIEW |
| [#68](https://github.com/tricore-opentrix/opentrix/pull/68) | `docs/issue53-isp-ba-originals` | `main` | Open | KEEP / REVIEW |
| [#61](https://github.com/tricore-opentrix/opentrix/pull/61) | `feature/issue37-openapi` | `main` | Draft | KEEP / REVIEW |
| [#60](https://github.com/tricore-opentrix/opentrix/pull/60) | `feature/issue53-mvp-contract` | `main` | Draft | KEEP / REVIEW |
| [#44](https://github.com/tricore-opentrix/opentrix/pull/44) | `feature/aws-staging-deployment` | `main` | Draft | KEEP / REVIEW |
| [#34](https://github.com/tricore-opentrix/opentrix/pull/34) | `feature/data-minio-adapter` | `main` | Draft | KEEP / REVIEW |

## Overall verdict

**INVENTORY COMPLETE; ANCESTRY TRIAGE COMPLETE; INDEPENDENT REVIEW PENDING; DELETION NOT AUTHORIZED.**

The goal is one durable `main` branch and short-lived issue-based PR branches. `gh-pages` remains a potential long-lived deployment exception until independently verified. No existing source files, PR states, releases or tags have been changed.


---

## Appendix C — Historical PR crosswalk and proposed branch decision matrix

**Added to Issue #171 review:** 2026-11-10. This compares **all 66 original unlinked remote branch heads** with GitHub's **79 closed Pull Requests** (head branch name match). The original branch count excludes the new audit branch itself; PR #172 is likewise excluded from the frozen 47-open-PR baseline. This is a **proposal**, not permission to delete. The historical PR lookup is by head *name*, not proof of exact commit identity or patch equivalence.

| Cohort | Closed/merged PR | Closed, unmerged PR | No closed PR found | Proposed outcome |
|---|---:|---:|---:|---|
| 16 ancestry-reachable branch tips | **13** | 0 | **3** | REVIEW_FOR_RETIREMENT, pending dependency checks |
| 50 non-ancestor branch tips | 0 | **41** | **9** | INVESTIGATE, preserve until resolved |
| **Total** | **13** | **41** | **12** | **0 deletion approvals** |

### C1. First cohort: 16 branches whose tips are ancestors of main

The absence of ahead commits is established by Git ancestry, not proof there is no automation, deployment, developer worktree, external reference or distinct historical-evidence need. **Recommendation: review these 16 first for retirement**, but do not delete without an explicit approved execution step.

| # | Branch | HEAD SHA (12) | Historical closed PR | Decision |
|---:|---|---|---|---|
| 1 | `docs/adr010-core-helpdesk-service-boundary` | `3e049488dda5` | None found | **REVIEW_FOR_RETIREMENT** |
| 2 | `docs/issue-reorganization-review-20261031` | `2a94a46579c4` | None found | **REVIEW_FOR_RETIREMENT** |
| 3 | `docs/restructure-documentation` | `2bda552126cb` | [#73](https://github.com/tricore-opentrix/opentrix/pull/73) (merged) | **REVIEW_FOR_RETIREMENT** |
| 4 | `docs/53-authz-evidence-mapping` | `00c42a987c35` | [#66](https://github.com/tricore-opentrix/opentrix/pull/66) (merged) | **REVIEW_FOR_RETIREMENT** |
| 5 | `docs/53-history-visibility-review` | `7bde57373f85` | [#62](https://github.com/tricore-opentrix/opentrix/pull/62) (merged) | **REVIEW_FOR_RETIREMENT** |
| 6 | `feat/data-object-storage-contract` | `a66d6352c90c` | [#18](https://github.com/tricore-opentrix/opentrix/pull/18) (merged) | **REVIEW_FOR_RETIREMENT** |
| 7 | `feature/data-core-contracts` | `ce56984973f3` | None found | **REVIEW_FOR_RETIREMENT** |
| 8 | `feature/data-postgres-adapter` | `899ef1132d9b` | [#31](https://github.com/tricore-opentrix/opentrix/pull/31) (merged) | **REVIEW_FOR_RETIREMENT** |
| 9 | `feature/gateway-authorization` | `fd5469ef6a66` | [#29](https://github.com/tricore-opentrix/opentrix/pull/29) (merged) | **REVIEW_FOR_RETIREMENT** |
| 10 | `feature/identity-oidc-runtime` | `d0d71dcc34b1` | [#33](https://github.com/tricore-opentrix/opentrix/pull/33) (merged) | **REVIEW_FOR_RETIREMENT** |
| 11 | `feature/issue23-identity-gateway-token-handoff-20261019` | `68c0fe018297` | [#46](https://github.com/tricore-opentrix/opentrix/pull/46) (merged) | **REVIEW_FOR_RETIREMENT** |
| 12 | `feature/workflow-http-api` | `d85cf6858869` | [#28](https://github.com/tricore-opentrix/opentrix/pull/28) (merged) | **REVIEW_FOR_RETIREMENT** |
| 13 | `feature/workflow-persistence-contracts` | `2efba4e8c797` | [#20](https://github.com/tricore-opentrix/opentrix/pull/20) (merged) | **REVIEW_FOR_RETIREMENT** |
| 14 | `feature/workflow-runtime` | `ad684d018a24` | [#21](https://github.com/tricore-opentrix/opentrix/pull/21) (merged) | **REVIEW_FOR_RETIREMENT** |
| 15 | `fix/data-input-stream-sanitization` | `fcc45fb65dc6` | [#30](https://github.com/tricore-opentrix/opentrix/pull/30) (merged) | **REVIEW_FOR_RETIREMENT** |
| 16 | `fix/request-jpa-public-schema` | `6400a486658b` | [#32](https://github.com/tricore-opentrix/opentrix/pull/32) (merged) | **REVIEW_FOR_RETIREMENT** |

**Priority checks for the 3 branches without a corresponding closed PR:** `docs/adr010-core-helpdesk-service-boundary`, `docs/issue-reorganization-review-20261031`, and `feature/data-core-contracts`. Their Git ancestry is preserved by `main`, but their naming/usage and evidence references still require confirmation.

### C2. Second cohort: 50 branches with non-ancestor commits

**None may be deleted on ancestry evidence alone.** Of these, **41** were the heads of closed-but-unmerged PRs, while **9** lack a matching closed PR. A closed-unmerged PR is **not** a recorded merge; its branch's changes could be superseded, cherry-picked, or still needed. Resolve the actual patch/value and owner before any retirement recommendation.

| # | Branch | HEAD SHA (12) | Historical closed PR | Decision |
|---:|---|---|---|---|
| 1 | `candidate/docs83-workflow-data-p2-20261031` | `c1576ac626b8` | [#84](https://github.com/tricore-opentrix/opentrix/pull/84) (closed-unmerged) | **INVESTIGATE** |
| 2 | `chore/issue26-hosted-verification-gate-20261017` | `ef8fe6f1a8ce` | [#42](https://github.com/tricore-opentrix/opentrix/pull/42) (closed-unmerged) | **INVESTIGATE** |
| 3 | `chore/olp-folder-skeleton-20261028` | `845eea767a9e` | [#77](https://github.com/tricore-opentrix/opentrix/pull/77) (closed-unmerged) | **INVESTIGATE** |
| 4 | `ci/verify-pr80-sql-fixtures-20261031` | `5b1290f14062` | None found | **INVESTIGATE** |
| 5 | `diagnostic/pr80-windows-acl-20261031` | `24503795c8b1` | None found | **INVESTIGATE** |
| 6 | `docs/capability-technology-baseline-20261031` | `49abc6f2699a` | [#91](https://github.com/tricore-opentrix/opentrix/pull/91) (closed-unmerged) | **INVESTIGATE** |
| 7 | `docs/consolidate-navigation-20261031` | `6c256e9ce3ca` | [#86](https://github.com/tricore-opentrix/opentrix/pull/86) (closed-unmerged) | **INVESTIGATE** |
| 8 | `docs/core-architecture-alignment` | `48cc6b3c09a4` | [#83](https://github.com/tricore-opentrix/opentrix/pull/83) (closed-unmerged) | **INVESTIGATE** |
| 9 | `docs/helpdesk-swagger-openapi-20261030` | `3d5b5c3f4a41` | [#79](https://github.com/tricore-opentrix/opentrix/pull/79) (closed-unmerged) | **INVESTIGATE** |
| 10 | `docs/import-workspace` | `91bcbe630835` | [#78](https://github.com/tricore-opentrix/opentrix/pull/78) (closed-unmerged) | **INVESTIGATE** |
| 11 | `docs/integrate-pr78-workspace` | `05c7e04f4e5d` | [#82](https://github.com/tricore-opentrix/opentrix/pull/82) (closed-unmerged) | **INVESTIGATE** |
| 12 | `docs/olp-project-documentation-20261025` | `16609ad6f4fd` | [#65](https://github.com/tricore-opentrix/opentrix/pull/65) (closed-unmerged) | **INVESTIGATE** |
| 13 | `docs/r27-yen-git-blob-evidence-20261107` | `fde4159d324b` | [#153](https://github.com/tricore-opentrix/opentrix/pull/153) (closed-unmerged) | **INVESTIGATE** |
| 14 | `docs/r28-q03-core-enforcement-closure-20261109` | `f26f0ed10e80` | None found | **INVESTIGATE** |
| 15 | `docs/repository-layout-governance-20261031` | `9a186ffe18b1` | [#85](https://github.com/tricore-opentrix/opentrix/pull/85) (closed-unmerged) | **INVESTIGATE** |
| 16 | `docs/stage6-security-review-549de8c-20261027` | `bdaf91a6bb5f` | [#72](https://github.com/tricore-opentrix/opentrix/pull/72) (closed-unmerged) | **INVESTIGATE** |
| 17 | `feature/issue23-d2-admin-candidate` | `db6b1a8007d2` | [#57](https://github.com/tricore-opentrix/opentrix/pull/57) (closed-unmerged) | **INVESTIGATE** |
| 18 | `feature/issue23-p1-02-integrity` | `549de8c63442` | [#58](https://github.com/tricore-opentrix/opentrix/pull/58) (closed-unmerged) | **INVESTIGATE** |
| 19 | `feature/issue23-secure-instance-id-foundation` | `ff824fc827cd` | [#36](https://github.com/tricore-opentrix/opentrix/pull/36) (closed-unmerged) | **INVESTIGATE** |
| 20 | `feature/issue23-stage3-authorized-workflow-service` | `4a2aa7e534ef` | [#47](https://github.com/tricore-opentrix/opentrix/pull/47) (closed-unmerged) | **INVESTIGATE** |
| 21 | `feature/issue23-stage4-exact-authority` | `b3bd87dd62c4` | [#48](https://github.com/tricore-opentrix/opentrix/pull/48) (closed-unmerged) | **INVESTIGATE** |
| 22 | `feature/issue23-stage5-tenant-resource-acl` | `32ca73fa8444` | [#49](https://github.com/tricore-opentrix/opentrix/pull/49) (closed-unmerged) | **INVESTIGATE** |
| 23 | `feature/issue23-stage6-core-impl` | `11035ed204c7` | None found | **INVESTIGATE** |
| 24 | `feature/issue23-stage6-guarded-actions-candidate-20261021` | `663d7e51ce8a` | [#55](https://github.com/tricore-opentrix/opentrix/pull/55) (closed-unmerged) | **INVESTIGATE** |
| 25 | `feature/issue23-stage6-s61-postgres-contract` | `db0decfd19b4` | [#50](https://github.com/tricore-opentrix/opentrix/pull/50) (closed-unmerged) | **INVESTIGATE** |
| 26 | `feature/issue26-supabase-clean` | `5e5b48dce5d9` | [#35](https://github.com/tricore-opentrix/opentrix/pull/35) (closed-unmerged) | **INVESTIGATE** |
| 27 | `feature/issue37-openapi-swagger-local` | `667f5e854a78` | [#45](https://github.com/tricore-opentrix/opentrix/pull/45) (closed-unmerged) | **INVESTIGATE** |
| 28 | `feature/issue39-portal-ui` | `076b9cba12af` | [#51](https://github.com/tricore-opentrix/opentrix/pull/51) (closed-unmerged) | **INVESTIGATE** |
| 29 | `feature/issue39-university-portal` | `ef521effa86b` | None found | **INVESTIGATE** |
| 30 | `feature/issue39-university-ui` | `00b10fa43d01` | [#52](https://github.com/tricore-opentrix/opentrix/pull/52) (closed-unmerged) | **INVESTIGATE** |
| 31 | `feature/issue53-helpdesk-backend` | `e12d105c8940` | [#63](https://github.com/tricore-opentrix/opentrix/pull/63) (closed-unmerged) | **INVESTIGATE** |
| 32 | `feature/issue53-it-mvp-api-review-scaffold-20261025` | `4d9982d5bd35` | [#64](https://github.com/tricore-opentrix/opentrix/pull/64) (closed-unmerged) | **INVESTIGATE** |
| 33 | `feature/issue53-java-helpdesk-mvp-20261028` | `f943d33c7b7c` | [#74](https://github.com/tricore-opentrix/opentrix/pull/74) (closed-unmerged) | **INVESTIGATE** |
| 34 | `feature/local-filesystem-storage-demo` | `01d14d35ac43` | [#43](https://github.com/tricore-opentrix/opentrix/pull/43) (closed-unmerged) | **INVESTIGATE** |
| 35 | `feature/portal-bff-session` | `d833b363d22c` | [#70](https://github.com/tricore-opentrix/opentrix/pull/70) (closed-unmerged) | **INVESTIGATE** |
| 36 | `feature/09-audit-attachment` | `1e2aa20940d8` | None found | **INVESTIGATE** |
| 37 | `fix/issue23-gateway-error-bridge-mvp-20261021` | `089a779af5a1` | [#54](https://github.com/tricore-opentrix/opentrix/pull/54) (closed-unmerged) | **INVESTIGATE** |
| 38 | `fix/issue26-hosted-worker-safety-20261017` | `1488bbbcfdd0` | [#41](https://github.com/tricore-opentrix/opentrix/pull/41) (closed-unmerged) | **INVESTIGATE** |
| 39 | `fix/pr80-windows-acl-test-fixture-20261031` | `f06e0b051767` | [#93](https://github.com/tricore-opentrix/opentrix/pull/93) (closed-unmerged) | **INVESTIGATE** |
| 40 | `fix/pr93-windows-launchers-20261101` | `2b8b29070b9f` | [#94](https://github.com/tricore-opentrix/opentrix/pull/94) (closed-unmerged) | **INVESTIGATE** |
| 41 | `fix/r16-mobile-overflow` | `182397709f85` | [#125](https://github.com/tricore-opentrix/opentrix/pull/125) (closed-unmerged) | **INVESTIGATE** |
| 42 | `fix/workflow-evidence-sql-regression` | `16d1f00493ec` | [#80](https://github.com/tricore-opentrix/opentrix/pull/80) (closed-unmerged) | **INVESTIGATE** |
| 43 | `integration/helpdesk-browser-e2e-20261029` | `b6e05d080ebb` | None found | **INVESTIGATE** |
| 44 | `mvp/fast-track-local-20261101` | `4ddedeaa88f9` | None found | **INVESTIGATE** |
| 45 | `review/d2a-identity-evidence` | `2ce628ac79cd` | [#56](https://github.com/tricore-opentrix/opentrix/pull/56) (closed-unmerged) | **INVESTIGATE** |
| 46 | `review/issue25-pg17-acceptance-20261101` | `045ef7672fbe` | None found | **INVESTIGATE** |
| 47 | `review/issue87-app-p0-01-proposal-20261101` | `22bc977b894f` | [#97](https://github.com/tricore-opentrix/opentrix/pull/97) (closed-unmerged) | **INVESTIGATE** |
| 48 | `review/issue87-integration-phase3-20261101` | `fe55347908ee` | [#95](https://github.com/tricore-opentrix/opentrix/pull/95) (closed-unmerged) | **INVESTIGATE** |
| 49 | `test/issue53-neg03-neg04` | `583feacfa79e` | [#67](https://github.com/tricore-opentrix/opentrix/pull/67) (closed-unmerged) | **INVESTIGATE** |
| 50 | `test/r22-missing-spdx-canary-20261105` | `a87204ca1ea1` | [#129](https://github.com/tricore-opentrix/opentrix/pull/129) (closed-unmerged) | **INVESTIGATE** |

**Priority preservation risks:** `docs/r27-yen-git-blob-evidence-20261107` has closed-unmerged PR #153 and is a provenance artifact; `docs/r28-q03-core-enforcement-closure-20261109` has no historical closed PR and appears related to current R28 architecture work; `test/r22-missing-spdx-canary-20261105` had closed-unmerged PR #129 and may supply negative licensing-test evidence. Do not assume any other closed PR branch is disposable merely because its PR was closed.

### C3. Practical cleanup verification sequence (repository maintenance scope)

1. **16 ancestry-reachable refs:** Search workflows/configuration/docs for literal branch references, check `gh-pages` and other release/deployment usages, ask owners only for ambiguous worktree/unpushed changes, refresh the exact HEAD SHAs. Then set `RETIREMENT_REVIEW_CANDIDATE` or `KEEP`; never immediately delete.
2. **41 closed-unmerged PR refs:** Read closure reason, parent/base chain, files/patch, and any replacement PR. If superseded and recoverable, record the corresponding merged or retained reference before proposing retirement.
3. **9 non-ancestor refs with no matching closed PR:** Treat as higher-risk, review last commit provenance and changed files; ask the owner where code or evidence still matters.
4. **Current open PRs and `main`/`gh-pages`:** Exclude from this retirement cycle. Audit branch `docs/issue171-legacy-branch-audit` is also excluded until Draft PR #172 is merged or otherwise resolved.
5. Review the resulting disposition table, preserve R24/R27 artifacts, and seek separate authorization for the exact branch names proposed for deletion.

### C4. Explicit remaining uncertainties

- No owner confirmation of local worktrees, unpushed commits, or references outside GitHub.
- No exhaustive workflow/deployment/reference search yet.
- No full patch-equivalence or closed-PR discussion review yet for the 50 non-ancestor branches.
- No license/rights clearance or independent reviewer sign-off.
- **Deletion approved: zero branches.**
