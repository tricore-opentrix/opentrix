# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""R24 contract tests: candidate integrity, authorization boundaries, and release modes."""
import importlib.util
import io
import zipfile
import json
import os
import tarfile
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("r24_release", Path(__file__).with_name("r24-release.py"))
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)
SHA = "a" * 40
TAG = "v0.2.0-rc.1"
ROW = {"project": "backend", "name": "example", "version": "1.0",
       "purl": "pkg:maven/test/example@1.0?type=jar",
       "licenses": ["Apache-2.0"], "license_policy_status": "APPROVED",
       "release_distribution_status": "PENDING"}



class R24ReleaseTests(unittest.TestCase):
    def fake_github_zip(self, artifact_id):
        self.assertIn(artifact_id, (111110, 222220))
        memory = io.BytesIO()
        with zipfile.ZipFile(memory, "w", compression=zipfile.ZIP_STORED) as z:
            z.writestr(self.archive.name, self.archive.read_bytes())
            z.writestr("SHA256SUMS", self.sums.read_bytes())
            z.writestr("RELEASE-NOTES.md",
                       (self.output / "RELEASE-NOTES.md").read_bytes())
        return memory.getvalue()

    def fake_github_review(self, path):
        head, merged = "b" * 40, "c" * 40
        if path == "pulls/123":
            return {"merged_at": "2026-11-17T00:00:00Z",
                    "merge_commit_sha": merged, "base": {"ref": "main"},
                    "user": {"login": "r24-acceptance-author"},
                    "head": {"sha": head}}
        if path == "pulls/123/reviews/456":
            return {"id": 456, "state": "APPROVED",
                    "user": {"login": "phanyen06ym-ien"}, "commit_id": head}
        if path == "pulls/123/files?per_page=100":
            return [{"filename": "docs/06-deployment/r24-acceptances/v0.2.0.json"},
                    {"filename": "docs/06-deployment/r24-acceptances/v0.2.0-rc.1.json"}]
        if path.startswith("contents/docs/06-deployment/r24-acceptances/"):
            return {"type": "file", "sha": release._blob_oid(self.acceptance.read_bytes())}
        for run_id, artifact_id in ((11111, 111110), (22222, 222220)):
            if path == f"actions/runs/{run_id}":
                return {"id": run_id, "event": "workflow_dispatch",
                        "head_branch": "main", "head_sha": self.source_sha,
                        "status": "completed", "conclusion": "success",
                        "path": ".github/workflows/release.yml"}
            if path == f"actions/runs/{run_id}/artifacts?per_page=100":
                zipped = self.fake_github_zip(artifact_id)
                return {"artifacts": [{
                    "id": artifact_id,
                    "name": f"r24-source-only-publishable-candidate-{run_id}",
                    "expired": False, "digest": "sha256:" + release.digest(zipped),
                    "size_in_bytes": len(zipped)}]}
        for offset, kind in enumerate(release.EVIDENCE_CHECKS, start=701):
            if path == f"issues/comments/{offset}":
                doc = json.loads(self.acceptance.read_text())
                proof = {"kind": kind, "tag": doc["tag"], "mode": "source-only",
                         "source_sha": doc["source_sha"],
                         "archive_sha256": doc["archive_sha256"],
                         "reviewer": "phanyen06ym-ien", "verdict": "PASS",
                         "checks": {c: True for c in release.EVIDENCE_CHECKS[kind]},
                         "references": [
                            "https://github.com/tricore-opentrix/opentrix/issues/138"]}
                if kind in ("source_provenance", "source_license"):
                    proof["unresolved_distribution_blockers"] = []
                if kind == "archive_and_checksums":
                    proof["candidate_run_ids"] = doc["candidate_run_ids"]
                    proof["references"] += [
                        f"https://github.com/tricore-opentrix/opentrix/actions/runs/{i}"
                        for i in doc["candidate_run_ids"]]
                return {
                    "html_url": f"https://github.com/tricore-opentrix/opentrix/issues/190#issuecomment-{offset}",
                    "user": {"login": "phanyen06ym-ien"},
                    "body": "<!-- R24_SOURCE_EVIDENCE_V1\n" + json.dumps(proof) + "\n-->"
                }
        raise AssertionError("unexpected GitHub review API path: " + path)


    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        def put(name, value):
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value if isinstance(value, bytes) else value.encode())
        self.put = put
        put("backend/build/libs/dxos-backend-0.1.0.jar", b"backend-jar")
        put("backend/build/libs/dxos-backend-0.1.0-plain.jar", b"plain-ignored")
        put("portal-bff/build/libs/dxos-portal-bff-0.1.0.jar", b"bff-jar")
        put("frontend/dist/index.html", "<html>demo</html>")
        for name in ("LICENSE", "NOTICE", "THIRD-PARTY-NOTICES.md"):
            put(name, "example")
        put("README.md", "source")
        put("CHANGELOG.md", "## [Unreleased]\n\n## [0.2.0-rc.1] - 2026-11-05\n\n### Added\n- test release\n")
        for name in ("backend/build/reports/cyclonedx/bom.json",
                     "portal-bff/build/reports/cyclonedx/bom.json", "frontend-sbom.json"):
            put(name, '{"bomFormat":"CycloneDX"}')
        put("build/r23/license-inventory.json", json.dumps([ROW]))
        self.upstream_path = "build/r24/upstream/backend/example-1.0/00-LICENSE.txt"
        put(self.upstream_path, "actual upstream license bytes")
        self.index_row = {
            "project": ROW["project"], "name": ROW["name"], "version": ROW["version"],
            "purl": ROW["purl"], "status": "COLLECTED_UNREVIEWED",
            "docs": [{"path": "compliance/upstream/backend/example-1.0/00-LICENSE.txt",
                      "sha256": release.digest(b"actual upstream license bytes"),
                      "origin": "META-INF/LICENSE.txt", "license_text": True}],
            "source": "gradle-cache-jar:example-1.0.jar"}
        put("build/r24/upstream/upstream-index.json", json.dumps([self.index_row]))
        self._review_stub = mock.patch.object(release, "_github_json",
                                              side_effect=self.fake_github_review)
        self._review_stub.start()
        self.addCleanup(self._review_stub.stop)
        self._zip_stub = mock.patch.object(release, "_github_artifact_zip",
                                            side_effect=self.fake_github_zip)
        self._zip_stub.start()
        self.addCleanup(self._zip_stub.stop)
        self.source_sha = SHA  # Binary fixture uses the synthetic historical SHA.
        self.output = self.repo / "output"
        self.make()
        self.acceptance = self.repo / "acceptance.json"

    def commit_sources(self):
        subprocess.run(["git", "-c", "user.name=R24 Contract Tests",
                        "-c", "user.email=r24@example.invalid", "commit", "-q",
                        "-m", "tracked source fixture"], cwd=self.repo, check=True)
        self.source_sha = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                                  cwd=self.repo, text=True).strip()

    def make(self, mode="binary", tag=TAG):
        release.package(self.repo, tag, self.source_sha if mode == "source-only" else SHA,
                        self.output, mode)
        self.archive = self.output / f"dxos-open-core-{tag[1:]}.tar.gz"
        self.sums = self.output / "SHA256SUMS"

    def accept(self, mode="binary"):
        doc = {"tag": TAG, "source_sha": self.source_sha if mode == "source-only" else SHA,
               "mode": mode,
               "archive_sha256": release.digest(self.archive.read_bytes()),
               "reviewed_by": ["phanyen06ym-ien"],
               "evidence": {key: "https://example.test/verified" for key in
                            (release.GATES if mode == "binary" else release.SOURCE_GATES)}}
        if mode == "source-only":
            doc["candidate_run_ids"] = [11111, 22222]
            doc["evidence"] = {kind: (
                f"https://github.com/tricore-opentrix/opentrix/issues/190#issuecomment-{701 + i}")
                for i, kind in enumerate(release.SOURCE_GATES)}
            doc["review_url"] = ("https://github.com/tricore-opentrix/opentrix/"
                                 "pull/123#pullrequestreview-456")
        if mode == "binary":
            doc.update({"java_base_image": "eclipse-temurin:21-jre@sha256:" + "b" * 64,
                        "license_groups": {"permissive": {"status": "CLEARED",
                                                           "evidence": "https://example.test/group"}},
                        "exceptions": []})
        self.acceptance.write_text(json.dumps(doc))
        return doc

    def gate(self):
        return release.gate(self.archive, self.sums, self.acceptance, TAG, self.source_sha,
                            self.output / "RELEASE-NOTES.md")

    def test_archive_reproducible_and_verified(self):
        first = release.digest(self.archive.read_bytes())
        self.make()
        self.assertEqual(first, release.digest(self.archive.read_bytes()))
        release.verify(self.archive, self.sums)

    def test_unreleased_notes_require_explicit_validation_mode(self):
        changelog = "## [Unreleased]\n\n### Added\n- preview change\n\n## [0.1.0]\n- old release\n"
        with self.assertRaisesRegex(ValueError, "this version's release notes"):
            release.release_notes(changelog, TAG)
        notes = release.release_notes(changelog, TAG, validation_only=True)
        self.assertIn("validation only", notes)
        self.assertIn("preview change", notes)
        self.assertNotIn("old release", notes)

    def test_validation_mode_still_rejects_missing_or_empty_notes(self):
        for changelog in ("## [0.1.0]\n- old release\n",
                          "## [Unreleased]\n\n## [0.1.0]\n- old release\n",
                          f"## [{TAG[1:]}]\n\n## [Unreleased]\n- preview\n"):
            with self.subTest(changelog=changelog), self.assertRaises(ValueError):
                release.release_notes(changelog, TAG, validation_only=True)

    def test_exact_version_notes_take_precedence_over_unreleased(self):
        changelog = f"## [Unreleased]\n- future\n\n## [{TAG[1:]}]\n- approved version\n"
        notes = release.release_notes(changelog, TAG, validation_only=True)
        self.assertIn("approved version", notes)
        self.assertNotIn("future", notes)

    def test_unreleased_archives_verify_but_cannot_pass_publication_gate(self):
        self.put("CHANGELOG.md", "## [Unreleased]\n\n- preview change\n")
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "README.md", "LICENSE", "NOTICE", "CHANGELOG.md"],
                       cwd=self.repo, check=True)
        self.commit_sources()
        for mode in ("binary", "source-only"):
            with self.subTest(mode=mode):
                release.package(self.repo, TAG, self.source_sha if mode == "source-only" else SHA,
                                self.output, mode, validation_only=True)
                manifest, data, prefix = release.verify(self.archive, self.sums)
                self.assertIs(manifest["validation_only"], True)
                self.assertIn(b"preview change", data[prefix + "RELEASE-NOTES.md"])
                first = release.digest(self.archive.read_bytes())
                release.package(self.repo, TAG, self.source_sha if mode == "source-only" else SHA,
                                self.output, mode, validation_only=True)
                self.assertEqual(first, release.digest(self.archive.read_bytes()))
                self.accept(mode)
                with self.assertRaisesRegex(ValueError, "validation-only archive cannot be published"):
                    self.gate()

    def test_validation_marker_blocks_publication_even_with_versioned_notes(self):
        release.package(self.repo, TAG, SHA, self.output, validation_only=True)
        self.accept()
        with self.assertRaisesRegex(ValueError, "validation-only archive cannot be published"):
            self.gate()

    def test_generated_sbom_timestamp_uuid_and_run_link_do_not_change_archive(self):
        def populate(uuid, timestamp, run):
            generated = {
                "bomFormat": "CycloneDX", "specVersion": "1.6",
                "serialNumber": "urn:uuid:" + uuid,
                "metadata": {
                    "timestamp": timestamp,
                    "component": {
                        "type": "application", "name": "dxos",
                        "externalReferences": [
                            {"type": "build-system",
                             "url": "https://github.com/tricore-opentrix/dxos-open-core/actions/runs/" + run},
                            {"type": "vcs",
                             "url": "https://github.com/tricore-opentrix/dxos-open-core"}]
                    }},
                "components": [{"type": "library", "name": "example", "version": "1.0",
                                "licenses": [{"license": {"id": "Apache-2.0"}}]}]
            }
            for name in ("backend/build/reports/cyclonedx/bom.json",
                         "portal-bff/build/reports/cyclonedx/bom.json", "frontend-sbom.json"):
                self.put(name, json.dumps(generated))

        populate("aaa", "2026-11-05T01:02:03Z", "12345")
        self.make()
        first = release.digest(self.archive.read_bytes())
        populate("bbb", "2026-11-06T04:05:06Z", "99999")
        self.make()
        self.assertEqual(first, release.digest(self.archive.read_bytes()))
        _, data, prefix = release.verify(self.archive, self.sums)
        bom = json.loads(data[prefix + "compliance/backend.cdx.json"])
        self.assertNotIn("serialNumber", bom)
        self.assertNotIn("timestamp", bom["metadata"])
        self.assertEqual(len(bom["components"]), 1)
        self.assertEqual(bom["metadata"]["component"]["externalReferences"],
                         [{"type": "vcs", "url": "https://github.com/tricore-opentrix/dxos-open-core"}])

    def test_repository_rename_keeps_binary_and_source_only_archive_digests(self):
        # Both repo name and run number change; unrelated refs must remain intact.
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "README.md", "LICENSE", "NOTICE", "CHANGELOG.md"],
                       cwd=self.repo, check=True)
        self.commit_sources()

        retained = [
            {"type": "vcs", "url": "https://github.com/tricore-opentrix/dxos-open-core"},
            {"type": "build-system", "url": "https://ci.example.test/build/unchanged"}]
        def generate(repo_name, run_number, timestamp, serial):
            bom = {
                "bomFormat": "CycloneDX", "specVersion": "1.6",
                "serialNumber": "urn:uuid:" + serial,
                "metadata": {
                    "timestamp": timestamp,
                    "component": {
                        "name": "dxos", "type": "application",
                        "externalReferences": [
                            {"type": "build-system",
                             "url": f"https://github.com/tricore-opentrix/{repo_name}/actions/runs/{run_number}"},
                            *retained]
                    }},
                "components": [{"type": "library", "name": "preserved", "version": "1.0",
                                "licenses": [{"license": {"id": "Apache-2.0"}}]}],
                "dependencies": [{"ref": "pkg:maven/example@1.0", "dependsOn": []}]
            }
            for name in ("backend/build/reports/cyclonedx/bom.json",
                         "portal-bff/build/reports/cyclonedx/bom.json",
                         "frontend-sbom.json"):
                self.put(name, json.dumps(bom))

        generate("dxos-open-core", "11111", "2026-11-05T00:00:00Z", "one")
        first = {}
        for mode in ("binary", "source-only"):
            self.make(mode)
            first[mode] = release.digest(self.archive.read_bytes())

        generate("opentrix", "22222", "2026-11-06T00:00:00Z", "two")
        for mode in ("binary", "source-only"):
            self.make(mode)
            self.assertEqual(first[mode], release.digest(self.archive.read_bytes()),
                             f"{mode} archive changed after repository rename")
            _, data, prefix = release.verify(self.archive, self.sums)
            packaged = json.loads(data[prefix + "compliance/backend.cdx.json"])
            self.assertEqual(packaged["metadata"]["component"]["externalReferences"], retained)
            self.assertEqual(len(packaged["components"]), 1)
            self.assertEqual(len(packaged["dependencies"]), 1)

    def test_source_only_candidate_stable_across_generated_sbom_runs(self):
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "README.md", "LICENSE", "NOTICE", "CHANGELOG.md"],
                       cwd=self.repo, check=True)
        self.commit_sources()
        self.put("frontend-sbom.json",
                 json.dumps({"bomFormat": "CycloneDX", "serialNumber": "urn:uuid:old",
                             "metadata": {"timestamp": "2026-11-05T12:00:00Z"}}))
        self.make("source-only")
        first = release.digest(self.archive.read_bytes())
        self.put("frontend-sbom.json",
                 json.dumps({"bomFormat": "CycloneDX", "serialNumber": "urn:uuid:new",
                             "metadata": {"timestamp": "2026-11-06T12:00:00Z"}}))
        self.make("source-only")
        self.assertEqual(first, release.digest(self.archive.read_bytes()))
        release.verify(self.archive, self.sums)

    def test_stable_v020_source_only_has_exact_tag_and_separate_acceptance(self):
        stable = "v0.2.0"
        self.put("CHANGELOG.md",
                 "## [Unreleased]\n\n## [0.2.0] - 2026-11-07\n\n### Added\n- source-only release\n")
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "README.md", "LICENSE", "NOTICE", "CHANGELOG.md"],
                       cwd=self.repo, check=True)
        self.commit_sources()
        self.make("source-only", tag=stable)
        doc = self.accept(mode="source-only")
        doc["tag"] = stable
        self.acceptance.write_text(json.dumps(doc))
        self.assertEqual(
            release.gate(self.archive, self.sums, self.acceptance, stable, self.source_sha,
                         self.output / "RELEASE-NOTES.md"),
            "source-only")
        doc["tag"] = "v0.2.0-rc.1"
        self.acceptance.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError, "exact tag"):
            release.gate(self.archive, self.sums, self.acceptance, stable, self.source_sha,
                         self.output / "RELEASE-NOTES.md")

    def test_source_only_requires_all_rights_build_and_actual_independent_review(self):
        stable = "v0.2.0"
        self.put("CHANGELOG.md", "## [Unreleased]\n\n## [0.2.0]\n\n### Added\n- sources\n")
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "README.md", "LICENSE", "NOTICE", "CHANGELOG.md"],
                       cwd=self.repo, check=True)
        self.commit_sources()
        self.make("source-only", tag=stable)
        base = self.accept(mode="source-only")
        base["tag"] = stable
        self.acceptance.write_text(json.dumps(base))
        self.assertEqual(release.gate(self.archive, self.sums, self.acceptance,
                                      stable, self.source_sha), "source-only")
        for missing in release.SOURCE_GATES:
            doc = json.loads(json.dumps(base))
            del doc["evidence"][missing]
            self.acceptance.write_text(json.dumps(doc))
            with self.subTest(missing=missing), self.assertRaisesRegex(ValueError,
                    "source-only release missing evidence"):
                release.gate(self.archive, self.sums, self.acceptance, stable, self.source_sha)
        bad = json.loads(json.dumps(base))
        bad.pop("review_url")
        self.acceptance.write_text(json.dumps(bad))
        with self.assertRaisesRegex(ValueError, "invalid independent review_url"):
            release.gate(self.archive, self.sums, self.acceptance, stable, self.source_sha)
        bad = json.loads(json.dumps(base))
        bad["reviewed_by"] = ["unrelated-contributor"]
        self.acceptance.write_text(json.dumps(bad))
        with self.assertRaisesRegex(ValueError, "independent compliance reviewer"):
            release.gate(self.archive, self.sums, self.acceptance, stable, self.source_sha)
        self.acceptance.write_text(json.dumps(base))
        with mock.patch.object(release, "_github_json",
                side_effect=lambda path: dict(self.fake_github_review(path),
                    state="COMMENTED") if path == "pulls/123/reviews/456"
                    else self.fake_github_review(path)):
            with self.assertRaisesRegex(ValueError, "APPROVE the final PR HEAD"):
                release.gate(self.archive, self.sums, self.acceptance, stable, self.source_sha)
        self.assertEqual(release.verify_independent_review(base, self.acceptance)[0],
                         "phanyen06ym-ien")

    def make_accepted_source_case(self):
        stable = "v0.2.0"
        self.put("CHANGELOG.md", "## [Unreleased]\n\n## [0.2.0]\n\n### Added\n- sources\n")
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "README.md", "LICENSE", "NOTICE", "CHANGELOG.md"],
                       cwd=self.repo, check=True)
        self.commit_sources()
        self.make("source-only", tag=stable)
        doc = self.accept("source-only")
        doc["tag"] = stable
        self.acceptance.write_text(json.dumps(doc))
        return doc, stable

    def assert_source_gate_rejected(self, stable, error):
        with self.assertRaisesRegex(ValueError, error):
            release.gate(self.archive, self.sums, self.acceptance,
                         stable, self.source_sha)

    def test_f02_acceptance_bytes_bound_to_pr_head_squash_merge_and_main(self):
        doc, stable = self.make_accepted_source_case()
        self.assertEqual(release.gate(self.archive, self.sums, self.acceptance,
                                      stable, self.source_sha), "source-only")
        for ref in ("b" * 40, "c" * 40, "main"):
            path_ref = f"?ref={ref}"
            def spoof(path):
                if path.startswith("contents/") and path.endswith(path_ref):
                    return {"type": "file", "sha": "d" * 40}
                return self.fake_github_review(path)
            with self.subTest(ref=ref), mock.patch.object(release, "_github_json",
                                                           side_effect=spoof):
                self.assert_source_gate_rejected(
                    stable, "acceptance JSON bytes differ from approved PR HEAD/merged main")

    def test_f03_invalid_independent_review_cases_fail_closed(self):
        _, stable = self.make_accepted_source_case()
        mutations = (
            ("outdated_head", "pulls/123/reviews/456", {"commit_id": "e" * 40},
             "APPROVE the final PR HEAD"),
            ("dismissed", "pulls/123/reviews/456", {"state": "DISMISSED"},
             "APPROVE the final PR HEAD"),
            ("self_review", "pulls/123", {"user": {"login": "phanyen06ym-ien"}},
             "unauthorized, or the PR author"),
            ("unmerged", "pulls/123", {"merged_at": None},
             "must be merged to main"),
            ("missing_file", "pulls/123/files?per_page=100",
             [{"filename": "unrelated.json"}], "does not include exact"),
            ("missing_merge_commit", "pulls/123", {"merge_commit_sha": None},
             "cannot identify reviewed PR HEAD"),
        )
        for name, at, mutated, expected in mutations:
            def spoof(path):
                original = self.fake_github_review(path)
                if path == at:
                    if isinstance(mutated, list):
                        return mutated
                    return dict(original, **mutated)
                return original
            with self.subTest(name=name), mock.patch.object(
                    release, "_github_json", side_effect=spoof):
                self.assert_source_gate_rejected(stable, expected)
        with mock.patch.object(release, "_github_json",
                               side_effect=ValueError("API unreachable")):
            self.assert_source_gate_rejected(stable, "API unreachable")

    def test_f04_original_five_evidence_categories_and_identity(self):
        _, stable = self.make_accepted_source_case()
        self.assertEqual(release.gate(self.archive, self.sums, self.acceptance,
                                      stable, self.source_sha), "source-only")
        failures = (
            ("wrong_source", "issues/comments/701", {"source_sha": "d" * 40},
             "evidence identity/verdict mismatch"),
            ("wrong_archive", "issues/comments/702", {"archive_sha256": "d" * 64},
             "evidence identity/verdict mismatch"),
            ("wrong_reviewer", "issues/comments/703", {"reviewer": "other"},
             "evidence identity/verdict mismatch"),
            ("wrong_mode", "issues/comments/701", {"mode": "binary"},
             "evidence identity/verdict mismatch"),
            ("pending_rights", "issues/comments/701",
             {"unresolved_distribution_blockers": ["RIGHTS_PENDING"]},
             "distribution blockers remain unresolved"),
            ("pending_license", "issues/comments/702",
             {"unresolved_distribution_blockers": ["UNKNOWN"]},
             "distribution blockers remain unresolved"),
            ("missing_checks", "issues/comments/703", {"checks": {}},
             "mandatory checklist incomplete"),
            ("run_ids_mismatch", "issues/comments/704",
             {"candidate_run_ids": [11111, 33333]},
             "candidate run IDs mismatch acceptance"),
        )
        for name, path_id, modifications, expected in failures:
            def modified(path):
                result = self.fake_github_review(path)
                if path == path_id:
                    value = dict(result)
                    marker = "R24_SOURCE_EVIDENCE_V1\n"
                    proof = json.loads(value["body"].split(marker)[1].split("\n-->")[0])
                    proof.update(modifications)
                    value["body"] = "<!-- " + marker + json.dumps(proof) + "\n-->"
                    return value
                return result
            with self.subTest(name=name), mock.patch.object(
                    release, "_github_json", side_effect=modified):
                self.assert_source_gate_rejected(stable, expected)

    def test_f01_require_distinct_two_candidates_and_same_frozen_source_sha(self):
        doc, stable = self.make_accepted_source_case()
        self.assertEqual(release.gate(self.archive, self.sums, self.acceptance,
                                      stable, self.source_sha), "source-only")
        for ids, reason in ((None, "exactly two"), ([11111], "exactly two"),
                            ([11111, 11111], "must be distinct"),
                            ([11111, "22222"], "exactly two")):
            variant = dict(doc)
            if ids is None:
                variant.pop("candidate_run_ids")
            else:
                variant["candidate_run_ids"] = ids
            self.acceptance.write_text(json.dumps(variant))
            with self.subTest(ids=ids):
                self.assert_source_gate_rejected(stable, reason)
        self.acceptance.write_text(json.dumps(doc))
        cases = (
            ("wrong_sha", "actions/runs/22222", {"head_sha": "d" * 40},
             "wrong source SHA"),
            ("wrong_event", "actions/runs/22222", {"event": "pull_request"},
             "wrong source SHA"),
            ("failed_run", "actions/runs/11111", {"conclusion": "failure"},
             "wrong source SHA"),
            ("wrong_workflow", "actions/runs/22222",
             {"path": "other.yml"}, "wrong source SHA"),
            ("missing_artifact", "actions/runs/22222/artifacts?per_page=100",
             {"artifacts": []}, "publishable archive absent"),
            ("expired_artifact", "actions/runs/22222/artifacts?per_page=100",
             {"artifacts": [{"id": 222220,
                 "name": "r24-source-only-publishable-candidate-22222",
                 "expired": True, "digest": "sha256:" + "a" * 64,
                 "size_in_bytes": 1024}]}, "invalid/expired artifact metadata"),
        )
        for name, path_id, modifications, expected in cases:
            def modified(path):
                result = self.fake_github_review(path)
                return dict(result, **modifications) if path == path_id else result
            with self.subTest(name=name), mock.patch.object(
                    release, "_github_json", side_effect=modified):
                self.assert_source_gate_rejected(stable, expected)

    def test_f01_different_archive_hash_manifest_sbom_member_bytes_fail_closed(self):
        _, stable = self.make_accepted_source_case()
        good = self.fake_github_zip(222220)
        def corrupted_zip(artifact_id):
            if artifact_id != 222220:
                return self.fake_github_zip(artifact_id)
            with zipfile.ZipFile(io.BytesIO(good)) as z:
                members = {name: z.read(name) for name in z.namelist()}
            # Any change to MANIFEST/SBOM/member bytes changes the source tarball
            # hash; a candidate mismatch cannot pass the SHA256 precondition.
            members[self.archive.name] += b"independent packaging drift"
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as z:
                for name, data in members.items():
                    z.writestr(name, data)
            return buf.getvalue()
        with mock.patch.object(release, "_github_artifact_zip",
                               side_effect=corrupted_zip):
            self.assert_source_gate_rejected(stable, "artifact ZIP digest mismatch")

        def altered_metadata(path):
            result = self.fake_github_review(path)
            if path == "actions/runs/22222/artifacts?per_page=100":
                result["artifacts"][0]["digest"] = (
                    "sha256:" + release.digest(corrupted_zip(222220)))
            return result
        with mock.patch.object(release, "_github_artifact_zip",
                               side_effect=corrupted_zip), mock.patch.object(
                release, "_github_json", side_effect=altered_metadata):
            self.assert_source_gate_rejected(stable, "archive SHA256 mismatch")

    def test_f01_unavailable_actual_archive_download_blocks(self):
        _, stable = self.make_accepted_source_case()
        with mock.patch.object(release, "_github_artifact_zip",
                               side_effect=ValueError("GitHub artifact download failed")):
            self.assert_source_gate_rejected(stable, "download failed")


    def test_stable_v020_binary_publication_is_blocked_even_if_reviewed(self):
        stable = "v0.2.0"
        self.put("CHANGELOG.md",
                 "## [Unreleased]\n\n## [0.2.0] - 2026-11-07\n\n### Added\n- stable release\n")
        self.make("binary", tag=stable)
        doc = self.accept(mode="binary")
        doc["tag"] = stable
        self.acceptance.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError, "SOURCE-ONLY"):
            release.gate(self.archive, self.sums, self.acceptance, stable, self.source_sha,
                         self.output / "RELEASE-NOTES.md")

    def test_invalid_tag_and_checksum_rejected(self):
        with self.assertRaises(ValueError):
            release.package(self.repo, "../../bad", SHA, self.output)
        self.sums.write_text("bad  dxos-open-core-0.2.0-rc.1.tar.gz\n")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            release.verify(self.archive, self.sums)

    def test_missing_clearance_blocks(self):
        with self.assertRaisesRegex(ValueError, "publication BLOCKED"):
            self.gate()

    def test_binary_grouped_clearance_can_pass_with_upstream_bytes(self):
        self.accept()
        self.assertEqual(self.gate(), "binary")

    def test_reviewed_digest_rejects_repackaged_archive_same_tag_sha(self):
        self.accept()
        self.put("NOTICE", "tampered but internally consistent")
        self.make()
        release.verify(self.archive, self.sums)
        with self.assertRaisesRegex(ValueError, "reviewed archive SHA-256 mismatch"):
            self.gate()

    def test_mismatched_standalone_notes_rejected(self):
        self.accept()
        (self.output / "RELEASE-NOTES.md").write_text("wrong notes")
        with self.assertRaisesRegex(ValueError, "release notes mismatch"):
            self.gate()

    def test_stale_sha_or_uncleared_group_rejected(self):
        doc = self.accept()
        doc["source_sha"] = "b" * 40
        self.acceptance.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError, "exact tag"):
            self.gate()
        doc["source_sha"] = SHA
        doc["license_groups"]["permissive"]["status"] = "PENDING"
        self.acceptance.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError, "permissive-license group"):
            self.gate()

    def test_missing_upstream_license_blocks_binary(self):
        self.accept()
        (self.repo / self.upstream_path).unlink()
        self.make()
        doc = json.loads(self.acceptance.read_text())
        doc["archive_sha256"] = release.digest(self.archive.read_bytes())
        self.acceptance.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError, "absent from reviewed archive"):
            self.gate()

    def test_epl_requires_individual_exception(self):
        row = dict(ROW, licenses=["EPL-2.0"])
        self.put("build/r23/license-inventory.json", json.dumps([row]))
        self.make()
        doc = self.accept()
        with self.assertRaisesRegex(ValueError, "special-license exception"):
            self.gate()
        doc["exceptions"] = [{"project": row["project"], "name": row["name"],
                              "version": row["version"], "purl": row["purl"],
                              "status": "CLEARED", "license_choice": "EPL-2.0",
                              "evidence": "https://example.test/epl"}]
        self.acceptance.write_text(json.dumps(doc))
        self.assertEqual(self.gate(), "binary")

    def test_rc_source_only_does_not_ship_compiled_assets_or_require_131_clearances(self):
        self.put("frontend/src/example.ts", "export const example = 1;")
        self.put("backend/gradle/wrapper/gradle-wrapper.jar", b"example binary jar")
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "README.md", "LICENSE", "NOTICE", "CHANGELOG.md",
                        "frontend/src/example.ts",
                        "backend/gradle/wrapper/gradle-wrapper.jar"], cwd=self.repo, check=True)
        self.commit_sources()
        self.make("source-only")
        doc = self.accept(mode="source-only")
        self.assertEqual(self.gate(), "source-only")
        _, data, prefix = release.verify(self.archive, self.sums)
        self.assertIn(prefix + "source/frontend/src/example.ts", data)
        self.assertNotIn(prefix + "backend/application.jar", data)
        self.assertNotIn(prefix + "frontend/index.html", data)
        self.assertNotIn(prefix + "source/backend/gradle/wrapper/gradle-wrapper.jar", data)
        doc["mode"] = "binary"
        self.acceptance.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError, "scope differs"):
            self.gate()

    def test_source_only_archive_keeps_git_index_modes_after_extraction(self):
        self.put("infra/demo/demo-up.sh", "#!/usr/bin/env bash\necho demo\n")
        self.put("backend/gradlew", "#!/bin/sh\necho gradle\n")
        self.put("backend/gradle/wrapper/gradle-wrapper.jar", b"wrapper-binary")
        for name in ("infra/demo/demo-up.sh", "backend/gradlew"):
            os.chmod(self.repo / name, 0o755)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "README.md", "LICENSE", "NOTICE",
                        "CHANGELOG.md", "infra/demo/demo-up.sh", "backend/gradlew",
                        "backend/gradle/wrapper/gradle-wrapper.jar"], cwd=self.repo,
                       check=True)
        self.commit_sources()
        self.make("source-only")
        root = "dxos-" + TAG + "/"
        with tarfile.open(self.archive, "r:gz") as tf:
            self.assertEqual(tf.getmember(root + "source/backend/gradlew").mode, 0o755)
            self.assertEqual(tf.getmember(root + "source/infra/demo/demo-up.sh").mode, 0o755)
            self.assertEqual(tf.getmember(root + "source/README.md").mode, 0o644)
            self.assertNotIn(root + "source/backend/gradle/wrapper/gradle-wrapper.jar",
                             tf.getnames())
            target = self.repo / "extracted"
            target.mkdir()
            tf.extractall(target)
        self.assertFalse((target / root / "source/.git").exists())
        self.assertTrue(os.access(target / root / "source/backend/gradlew", os.X_OK))
        self.assertTrue(os.access(target / root / "source/infra/demo/demo-up.sh", os.X_OK))
        self.assertEqual(release.verify(self.archive, self.sums)[0]["mode"], "source-only")

    def test_source_integrity_rejects_wrong_sha_dirty_and_staged_inputs(self):
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "README.md", "LICENSE", "NOTICE", "CHANGELOG.md"],
                       cwd=self.repo, check=True)
        self.commit_sources()
        with self.assertRaisesRegex(ValueError, "source SHA must match"):
            release.package(self.repo, TAG, SHA, self.output, mode="source-only")
        self.put("README.md", "tampered working tree")
        with self.assertRaisesRegex(ValueError, "tracked working tree/index differs"):
            self.make("source-only")
        self.put("README.md", "source")
        self.put("unknown-untracked.md", "must not be included")
        self.make("source-only")
        manifest, data, prefix = release.verify(self.archive, self.sums)
        self.assertEqual(manifest["source_sha"], self.source_sha)
        self.assertNotIn(prefix + "source/unknown-untracked.md", data)
        subprocess.run(["git", "add", "unknown-untracked.md"], cwd=self.repo, check=True)
        with self.assertRaisesRegex(ValueError, "tracked working tree/index differs"):
            self.make("source-only")

    def test_rc_tag_validation(self):
        self.assertTrue(release.TAG.fullmatch(TAG))
        self.assertFalse(release.TAG.fullmatch("v0.2.0-rc.0"))
        self.assertFalse(release.TAG.fullmatch("v0.2.0-rc.1/evil"))


if __name__ == "__main__":
    unittest.main()
