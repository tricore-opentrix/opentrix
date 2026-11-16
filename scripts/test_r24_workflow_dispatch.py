# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""Regression tests for guarded manual R24 candidate selection."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

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
        # BaseLoader preserves the YAML 'on' key (YAML 1.1 SafeLoader treats it as True).
        cls.workflow_yaml = yaml.load(cls.workflow, Loader=yaml.BaseLoader)
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

    def test_parsed_yaml_publisher_has_tag_only_job_guard(self):
        # R1: assert the real job-level guard, not text fragments elsewhere.
        wf = self.workflow_yaml
        self.assertEqual(wf["on"]["push"]["tags"], ["v*"])
        self.assertIn("workflow_dispatch", wf["on"])
        self.assertEqual(set(wf["jobs"]), {"candidate", "publish"})
        publisher = wf["jobs"]["publish"]
        self.assertEqual(publisher["needs"], "candidate")
        self.assertEqual(
            publisher["if"],
            "github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')",
        )
        self.assertEqual(publisher["environment"], "r24-release")
        # Manually dispatched events are not push events and cannot meet this guard.
        self.assertNotIn("workflow_dispatch", publisher["if"])

    def test_parsed_yaml_candidate_cannot_write_or_publish(self):
        # R1: root/candidate are read-only, only the tag-gated publisher may write.
        wf = self.workflow_yaml
        self.assertEqual(wf["permissions"], {"contents": "read"})
        candidate = wf["jobs"]["candidate"]
        effective_permissions = candidate.get("permissions", wf["permissions"])
        for scope in ("contents", "packages"):
            self.assertNotEqual(effective_permissions.get(scope), "write", scope)
        self.assertNotIn("environment", candidate)
        publisher_permissions = wf["jobs"]["publish"]["permissions"]
        self.assertEqual(publisher_permissions,
                         {"contents": "write", "packages": "write"})
        for job_id, job in wf["jobs"].items():
            permissions = job.get("permissions", wf["permissions"])
            if any(value == "write" for value in permissions.values()):
                self.assertEqual(job_id, "publish")

    def test_parsed_yaml_dispatch_modes_and_artifact_separation(self):
        wf = self.workflow_yaml
        mode = wf["on"]["workflow_dispatch"]["inputs"]["candidate_mode"]
        self.assertEqual(mode["default"], "validation-only")
        self.assertEqual(mode["required"], "true")
        self.assertEqual(mode["type"], "choice")
        self.assertEqual(mode["options"],
                         ["validation-only", "publishable-source-only"])
        steps = wf["jobs"]["candidate"]["steps"]
        publishable = [step for step in steps if
            (step.get("with") or {}).get("name", "").startswith(
                "r24-source-only-publishable-candidate-")]
        self.assertEqual(len(publishable), 1)
        self.assertEqual(publishable[0]["if"],
            "github.event_name == 'workflow_dispatch' && inputs.candidate_mode == 'publishable-source-only'")
        self.assertTrue(publishable[0]["uses"].startswith("actions/upload-artifact@"))
        preview = [step for step in steps if
            (step.get("with") or {}).get("name", "").startswith("r24-source-only-candidate-")]
        self.assertEqual(len(preview), 1)
        self.assertEqual(preview[0]["if"],
                         "steps.meta.outputs.validation_only == 'true'")

    def test_source_archive_is_built_from_extracted_tar_without_git(self):
        steps = self.workflow_yaml["jobs"]["candidate"]["steps"]
        extracted = [step for step in steps
                     if step.get("name") == "Build verified extracted SOURCE-ONLY archive (no Git worktree)"]
        self.assertEqual(len(extracted), 1)
        self.assertIn("steps.meta.outputs.mode == 'source-only'", extracted[0]["if"])
        self.assertIn('tar -xzf "$archive"', extracted[0]["run"])
        self.assertIn('test ! -e "$src/.git"', extracted[0]["run"])
        self.assertIn('gradle --no-daemon -p "$src/backend" bootJar', extracted[0]["run"])
        self.assertIn('gradle --no-daemon -p "$src/portal-bff" bootJar', extracted[0]["run"])
        self.assertIn("npm run build:integration-local", extracted[0]["run"])
        setup = [step for step in steps
                 if step.get("uses") == "gradle/actions/setup-gradle@v4"]
        self.assertEqual(len(setup), 1)
        self.assertEqual(setup[0]["with"]["gradle-version"], "8.14.3")

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
