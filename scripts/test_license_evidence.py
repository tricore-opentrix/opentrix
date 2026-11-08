# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""Evidence-integrity regressions; fixtures make no human rights assertions."""
import csv
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import license_evidence as evidence

SCRIPTS = Path(__file__).resolve().parent
HEADER = "# SPDX-" + "FileCopyrightText: 2026 Fixture contributors\n# SPDX-" + "License-Identifier: Apache-2.0\n"


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.put("file.py", HEADER + "answer = 1\n")
        self.put("scripts/r23-compliance.py", (SCRIPTS / "r23-compliance.py").read_text(encoding="utf-8"))
        self.commit()

    def git(self, *args):
        p = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout

    def put(self, path, text):
        p = self.repo / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode("utf-8"))

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        self.sha = self.git("rev-parse", "HEAD").decode().strip()

    def meta(self):
        return evidence.common(self.sha, "living", "2026-11-09T00:00:00Z", "fixture")

    def test_committed_bytes_ignore_dirty_untracked_and_archive_attributes(self):
        self.put(".gitattributes", "file.py export-ignore\n")
        self.commit()
        original = self.git("show", self.sha + ":file.py")
        self.put("file.py", "dirty\n")
        self.put("untracked.py", "not committed\n")
        target = self.root / "tree"
        target.mkdir()
        entries = evidence.materialize(self.repo, self.sha, target)
        self.assertEqual((target / "file.py").read_bytes(), original)
        self.assertNotIn("untracked.py", {x[0] for x in entries})
        oid = next(x[1] for x in entries if x[0] == "file.py")
        self.assertEqual(oid, self.git("rev-parse", self.sha + ":file.py").decode().strip())

    def test_effective_external_metadata_and_sidecar_precedence(self):
        self.put("data.json", "{}\n")
        self.put("REUSE.toml", '# SPDX-' + 'FileCopyrightText: 2026 Fixture\n# SPDX-' + 'License-Identifier: Apache-2.0\nversion = 1\n[[annotations]]\npath = "data.json"\nprecedence = "closest"\nSPDX-' + 'FileCopyrightText = "2026 External fixture"\nSPDX-' + 'License-Identifier = "MIT"\n')
        self.commit()
        target = self.root / "tree"
        target.mkdir()
        entries = evidence.materialize(self.repo, self.sha, target)
        rows = {x["path"]:x for x in evidence.file_inventory(target, entries, self.meta())}
        self.assertEqual(json.loads(rows["data.json"]["effective_license_expressions_json"]), ["MIT"])
        self.assertEqual(json.loads(rows["data.json"]["metadata_sources_json"])[0]["path"], "REUSE.toml")
        self.put("data.json.license", "SPDX-" + "FileCopyrightText: 2026 Sidecar\nSPDX-" + "License-Identifier: Apache-2.0\n")
        self.commit()
        target2 = self.root / "tree2"
        target2.mkdir()
        entries = evidence.materialize(self.repo, self.sha, target2)
        rows = {x["path"]:x for x in evidence.file_inventory(target2, entries, self.meta())}
        self.assertEqual(json.loads(rows["data.json"]["effective_license_expressions_json"]), ["Apache-2.0"])
        self.assertIn("data.json.license", rows["data.json"]["metadata_sources_json"])

    def test_missing_and_invalid_metadata_are_not_guessed(self):
        self.put("missing.py", "no_metadata = True\n")
        self.put("invalid.py", HEADER.replace("Apache-2.0", "MIT OR") + "x=1\n")
        self.commit()
        target = self.root / "tree"
        target.mkdir()
        entries = evidence.materialize(self.repo, self.sha, target)
        rows = {x["path"]:x for x in evidence.file_inventory(target, entries, self.meta())}
        self.assertEqual(json.loads(rows["missing.py"]["effective_license_expressions_json"]), [])
        self.assertEqual(rows["missing.py"]["evidence_status"], "BLOCKED")
        self.assertIn("INVALID_LICENSE_EXPRESSION", rows["invalid.py"]["metadata_error"])

    def test_r23_notice_literals_do_not_corrupt_its_own_metadata(self):
        target = self.root / "tree"
        target.mkdir()
        entries = evidence.materialize(self.repo, self.sha, target)
        rows = {x["path"]:x for x in evidence.file_inventory(target, entries, self.meta())}
        row = rows["scripts/r23-compliance.py"]
        self.assertEqual(row["metadata_error"], "")
        self.assertEqual(json.loads(row["effective_license_expressions_json"]), ["Apache-2.0"])

    def dependency_fixture(self):
        spec = importlib.util.spec_from_file_location("fixture_r23", SCRIPTS / "r23-compliance.py")
        policy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(policy)
        inputs, records = {}, []
        for project in ("backend", "portal-bff", "frontend"):
            path = self.root / (project + ".json")
            component = {"type":"library", "name":"unknown-source", "version":"1.0",
                "purl":"", "licenses":[], "externalReferences":[]}
            path.write_text(json.dumps({"bomFormat":"CycloneDX", "specVersion":"1.6", "components":[component]}), encoding="utf-8")
            inputs[project] = path
            records += policy.read_bom(path, project)
        inv = self.root / "inventory.json"
        inv.write_text(json.dumps(records), encoding="utf-8")
        return inputs, inv

    def test_dependency_projection_retains_unknown_policy_and_pending_rights(self):
        inputs, inv = self.dependency_fixture()
        rows, missing = evidence.dependency_inventory(self.repo, inputs, inv, "1"*40, "", self.meta())
        self.assertEqual(missing, "")
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertEqual(row["release_distribution_status"], "PENDING")
            self.assertEqual(row["license_policy_status"], "REVIEW")
            self.assertEqual(row["upstream_sources_json"], "[]")
            self.assertEqual(row["license_choice"], "")
            self.assertIn("SBOM_SOURCE_SHA_DIFFERS", row["blockers"])
            self.assertIn("SBOM_RUN_ORIGIN_NOT_VERIFIED", row["blockers"])
        table = list(csv.DictReader(io.StringIO(evidence.csv_bytes(rows, evidence.DEP_FIELDS).decode())))
        self.assertEqual(table[0]["licenses_json"], rows[0]["licenses_json"])

    def test_mismatched_or_duplicate_inventory_fails_closed(self):
        inputs, inv = self.dependency_fixture()
        records = json.loads(inv.read_text())
        records[0]["release_distribution_status"] = "invented-clearance"
        inv.write_text(json.dumps(records), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differs"):
            evidence.dependency_inventory(self.repo, inputs, inv, self.sha, "https://example.invalid", self.meta())
        records.append(records[0])
        inv.write_text(json.dumps(records), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            evidence.dependency_inventory(self.repo, inputs, inv, self.sha, "", self.meta())

    def test_full_failed_lint_persisted_and_repeat_generation_is_deterministic(self):
        self.put("missing.py", "x=1\n")
        self.commit()
        outputs = [self.root / "out1", self.root / "out2"]
        for out in outputs:
            code = evidence.generate(self.repo, self.sha, out, "living", "2026-11-09T00:00:00Z")
            self.assertEqual(code, 1)
            report = (out / evidence.REPORTS[0]).read_text(encoding="utf-8")
            self.assertIn("missing.py", report)
            self.assertIn("exit_code: 1", report)
            self.assertIn("--- complete combined stdout/stderr ---", report)
        self.assertEqual({x.name:x.read_bytes() for x in outputs[0].iterdir()},
                         {x.name:x.read_bytes() for x in outputs[1].iterdir()})

    def test_snapshot_cannot_be_overwritten_and_requires_sha_directory(self):
        with self.assertRaisesRegex(ValueError, "Snapshot"):
            evidence.generate(self.repo, self.sha, self.root / "wrong", "snapshot")
        out = self.root / self.sha
        out.mkdir()
        with self.assertRaisesRegex(ValueError, "Snapshot"):
            evidence.generate(self.repo, self.sha, out, "snapshot")


if __name__ == "__main__":
    unittest.main()
