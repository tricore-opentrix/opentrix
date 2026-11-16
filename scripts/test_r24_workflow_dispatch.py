# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""Regression tests for guarded manual R24 candidate selection."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/release.yml"


def extract_run(name):
    content = WORKFLOW.read_text(encoding="utf-8")
    marker = f"      - name: {name}\n"
    assert content.count(marker) == 1, f"R24 step not unique: {name}"
    step = content.split(marker, 1)[1].split("\n      - ", 1)[0]
    assert step.count("        run: |\n") == 1, f"run script missing: {name}"
    script = step.split("        run: |\n", 1)[1]
    return "\n".join(line[10:] for line in script.splitlines() if line.startswith("          ")) + "\n"


def find_bash():
    if os.name == "nt":
        git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
        if git_bash.is_file():
            return str(git_bash)
    return shutil.which("bash")


class R24ManualDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.bash = find_bash()
        if not cls.bash:
            raise unittest.SkipTest("Bash is required for R24 workflow contract tests")
        cls.metadata_script = extract_run("Validate tag is on main and select candidate version")
        cls.package_script = extract_run("Package and independently verify candidate archive")

    def run_meta(self, *, event="workflow_dispatch", ref_name="main",
                 github_ref="refs/heads/main", requested="validation-only"):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "github-output.txt"
            env = dict(os.environ, EVENT=event, REF=ref_name,
                       GITHUB_REF=github_ref, REQUESTED_CANDIDATE_MODE=requested,
                       GITHUB_OUTPUT=output.as_posix())
            result = subprocess.run(
                [self.bash, "-e", "-o", "pipefail", "-c", self.metadata_script],
                cwd=ROOT, env=env, text=True, capture_output=True, check=False)
            if output.exists():
                result.stdout = output.read_text(encoding="utf-8") + result.stdout
            return result

    def assert_metadata(self, result, *, mode, validation_only):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        lines = dict(line.split("=", 1) for line in result.stdout.splitlines()
                     if line.startswith(("tag=", "mode=", "sha=", "validation_only=")))
        self.assertEqual(lines["tag"], "v0.2.0")
        self.assertEqual(lines["mode"], mode)
        self.assertEqual(lines["validation_only"], validation_only)
        self.assertEqual(len(lines["sha"]), 40)

    def test_manual_default_remains_validation_only(self):
        self.assert_metadata(self.run_meta(), mode="binary", validation_only="true")

    def test_manual_publishable_format_requires_main_and_omits_validation(self):
        self.assert_metadata(self.run_meta(requested="publishable-source-only"),
                             mode="source-only", validation_only="false")

    def test_pull_requests_remain_validation_only(self):
        self.assert_metadata(
            self.run_meta(event="pull_request", ref_name="feature",
                          github_ref="refs/pull/1/merge"),
            mode="binary", validation_only="true")

    def test_manual_publishable_format_rejects_non_main_ref(self):
        for ref_name, github_ref in (("feature", "refs/heads/feature"),
                                     ("main", "refs/heads/feature")):
            with self.subTest(ref_name=ref_name, github_ref=github_ref):
                result = self.run_meta(ref_name=ref_name, github_ref=github_ref,
                                       requested="publishable-source-only")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("main branch", result.stdout)

    def test_unknown_manual_mode_fails_closed(self):
        result = self.run_meta(requested="unexpected")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported R24 manual candidate mode", result.stdout)

    def test_dispatch_never_opens_publisher_and_artifacts_stay_separate(self):
        self.assertIn("if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')",
                      self.workflow)
        self.assertIn("VALIDATION_ONLY: ${{ steps.meta.outputs.validation_only }}",
                      self.workflow)
        self.assertIn('if [ "$VALIDATION_ONLY" = true ]; then',
                      self.package_script)
        self.assertIn("preview_args+=(--validation-only)", self.package_script)
        self.assertIn("name: r24-source-only-publishable-candidate-${{ github.run_id }}",
                      self.workflow)
        self.assertIn("if: steps.meta.outputs.validation_only == 'true'",
                      self.workflow)
        self.assertIn("default: validation-only", self.workflow)


if __name__ == "__main__":
    unittest.main()
