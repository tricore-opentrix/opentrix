# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""Derived, SHA-bound evidence views; never a rights or release decision engine."""
import argparse
import csv
import hashlib
import importlib.metadata
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

SCHEMA = "1"
COMMON = ["schema_version", "applicable_sha", "evidence_kind", "recorded_at_utc",
          "evidence_status", "evidence_source", "owner", "reviewer", "blockers",
          "update_conditions"]
FILE_FIELDS = COMMON + ["path", "git_blob_sha1", "file_sha256", "git_mode",
    "reuse_version", "reuse_selection", "effective_copyright_json",
    "effective_license_expressions_json", "metadata_sources_json", "metadata_error"]
DEP_FIELDS = COMMON + ["project", "package", "version", "purl", "licenses_json",
    "raw_bom_licenses_json", "license_choice", "approved", "license_policy_status",
    "release_distribution_status", "release_distribution_owner",
    "release_distribution_requirements_json", "license_reference_links_json",
    "upstream_sources_json", "sbom_source_sha", "sbom_sha256", "r23_inventory_sha256"]
UPDATE = "Regenerate after committed file/metadata/dependency changes; re-review before release freeze"
REPORTS = ("LIC-02-reuse-lint-report.txt", "LIC-03-file-spdx-inventory.csv",
           "LIC-04-third-party-inventory.csv")


def stable(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def command(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True)


def git(repo, *args):
    result = command(["git", "-C", str(repo), *args], repo)
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace"))
    return result.stdout


def full_sha(repo, ref):
    sha = git(repo, "rev-parse", "--verify", ref + "^{commit}").decode().strip()
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("Expected a full SHA-1 commit identity")
    return sha


def materialize(repo, sha, destination):
    """Read a committed Git tree, not a dirty/untracked working directory."""
    # Reject gitlinks: absence of submodule bytes must not imply complete coverage.
    listing = git(repo, "ls-tree", "-r", "-z", sha)
    entries = []
    for entry in listing.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        path = raw_path.decode("utf-8")
        if kind != "blob" or mode == "120000":
            raise ValueError("Submodules/symlinks require explicit evidence support: " + path)
        entries.append((path, oid, mode))
    # Read objects directly: git archive can apply export-ignore/export-subst,
    # which would omit or transform the very bytes this inventory describes.
    process = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"],
        input="".join(oid + "\n" for _, oid, _ in entries).encode(), capture_output=True)
    if process.returncode:
        raise ValueError(process.stderr.decode("utf-8", errors="replace"))
    stream = io.BytesIO(process.stdout)
    for name, oid, _ in entries:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
            raise ValueError("Unsafe Git path: " + name)
        actual, kind, size = stream.readline().decode().split()
        if actual != oid or kind != "blob":
            raise ValueError("Git object identity mismatch")
        data = stream.read(int(size))
        if len(data) != int(size) or stream.read(1) != b"\n":
            raise ValueError("Truncated Git object stream")
        target = destination.joinpath(*path.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return sorted(entries)


def common(sha, kind, timestamp, source, status="NOT_VERIFIED", blockers="Independent review pending"):
    return dict(zip(COMMON, [SCHEMA, sha, kind, timestamp, status, source,
        "Yen (evidence coordination; not presumed rightsholder)",
        "Bao/Anh proposed; actual noncontributor review required", blockers, UPDATE]))


def file_inventory(root, entries, meta):
    from reuse.project import Project
    project = Project.from_directory(root)
    selected = {p.relative_to(root).as_posix() for p in project.all_files()}
    version = importlib.metadata.version("reuse")
    rows = []
    for path, oid, mode in entries:
        expressions, notices, sources, errors = set(), set(), [], []
        try:
            information = project.reuse_info_of(root / path)
            for info in information:
                expressions.update(str(x) for x in info.spdx_expressions)
                notices.update(str(x) for x in info.copyright_notices)
                sources.append({"path": str(info.source_path), "type": info.source_type.value})
                if any(not x.is_valid for x in info.spdx_expressions):
                    errors.append("INVALID_LICENSE_EXPRESSION")
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(type(exc).__name__ + ": " + str(exc))
        if path in selected and (not notices or not expressions):
            errors.append("MISSING_EFFECTIVE_METADATA")
        row = dict(meta)
        # PASS is only the narrow presence/syntax check; license texts and rights
        # are assessed by the full lint/manual workflows separately.
        row["evidence_status"] = "BLOCKED" if errors else ("PASS" if path in selected else "NOT_VERIFIED")
        row["blockers"] = "; ".join(errors) if errors else "Rights/NOTICE review pending; row PASS covers metadata presence/syntax only"
        row.update(path=path, git_blob_sha1=oid, file_sha256=digest((root / path).read_bytes()),
            git_mode=mode, reuse_version=version,
            reuse_selection="SELECTED" if path in selected else "TOOL_EXCLUDED_NOT_RIGHTS_EXCLUDED",
            effective_copyright_json=stable(sorted(notices)),
            effective_license_expressions_json=stable(sorted(expressions)),
            metadata_sources_json=stable(sorted(sources, key=stable)), metadata_error="; ".join(errors))
        rows.append(row)
    return rows


def identity(row):
    return (row["project"], row["name"], row["version"], row.get("purl", ""))


def dependency_inventory(root, inputs, inventory_path, sbom_sha, source_url, meta):
    """Project existing canonical R23 decisions, validating them against SBOMs."""
    if not inputs and inventory_path is None:
        return [], "R23_INPUTS_NOT_SUPPLIED"
    if set(inputs) != {"backend", "portal-bff", "frontend"} or inventory_path is None or not sbom_sha:
        raise ValueError("All three existing R23 SBOMs, R23 inventory and its source SHA are required")
    if len(sbom_sha) != 40 or any(c not in "0123456789abcdef" for c in sbom_sha):
        raise ValueError("SBOM source SHA must be 40 lowercase hexadecimal characters")
    spec = importlib.util.spec_from_file_location("canonical_r23", root / "scripts/r23-compliance.py")
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    raw_inventory = inventory_path.read_bytes()
    inventory = json.loads(raw_inventory)
    if not isinstance(inventory, list) or not inventory:
        raise ValueError("Empty/invalid R23 inventory")
    indexed = {}
    for row in inventory:
        key = identity(row)
        if key in indexed:
            raise ValueError("Duplicate canonical inventory identity: " + repr(key))
        indexed[key] = row
    computed, details = {}, {}
    for project, path in sorted(inputs.items()):
        raw = path.read_bytes()
        bom = json.loads(raw)
        # The digest and policy evaluation must refer to the same input bytes,
        # even if a producer updates the supplied file during generation.
        with tempfile.TemporaryDirectory(prefix="opentrix-r23-input-") as tmp:
            frozen_bom = Path(tmp) / "bom.json"
            frozen_bom.write_bytes(raw)
            evaluated = policy.read_bom(frozen_bom, project)
        for row in evaluated:
            key = identity(row)
            if key in computed:
                raise ValueError("Duplicate eligible SBOM identity: " + repr(key))
            computed[key] = row
        for item in bom["components"]:
            if item.get("type") not in {"library", "framework", "application", "file"}:
                continue
            key = (project, item.get("name"), item.get("version"), item.get("purl", ""))
            if key in computed:
                details[key] = (item, digest(raw))
    if computed != indexed:
        raise ValueError("Supplied R23 inventory differs from canonical policy over supplied SBOMs")
    result = []
    for key in sorted(indexed):
        row, original = dict(meta), indexed[key]
        item, sbom_digest = details[key]
        row["evidence_status"] = "NOT_VERIFIED"
        blockers = ["Independent upstream/license/NOTICE review pending"]
        if sbom_sha != meta["applicable_sha"]:
            blockers.append("SBOM_SOURCE_SHA_DIFFERS_FROM_ANALYZED_SOURCE")
        if not source_url.startswith("https://"):
            blockers.append("SBOM_RUN_ORIGIN_NOT_VERIFIED")
        row["blockers"] = "; ".join(blockers)
        row["evidence_source"] = source_url or "UNKNOWN"
        row.update(project=original["project"], package=original["name"], version=original["version"],
            purl=original.get("purl", ""), licenses_json=stable(original.get("licenses", [])),
            raw_bom_licenses_json=stable(item.get("licenses", [])),
            license_choice=original.get("license_choice", ""), approved=stable(original.get("approved")),
            license_policy_status=original.get("license_policy_status", ""),
            release_distribution_status=original.get("release_distribution_status", ""),
            release_distribution_owner=original.get("release_distribution_owner", ""),
            release_distribution_requirements_json=stable(original.get("release_distribution_requirements", [])),
            license_reference_links_json=stable(original.get("license_reference_links", {})),
            upstream_sources_json=stable(sorted(item.get("externalReferences", []), key=stable)),
            sbom_source_sha=sbom_sha, sbom_sha256=sbom_digest, r23_inventory_sha256=digest(raw_inventory))
        result.append(row)
    return result, ""


def csv_bytes(rows, fields):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def sidecar(meta):
    # Split marker literals so REUSE does not parse embedded fixtures as headers.
    lines = ["SPDX-" + "FileCopyrightText: 2026 TRICORE contributors",
             "SPDX-" + "License-Identifier: Apache-2.0", ""]
    lines += ["# " + k + ": " + str(v) for k, v in meta.items()]
    return ("\n".join(lines) + "\n").encode("utf-8")


def generate(repo, ref, output, kind, timestamp=None, inputs=None, inventory=None,
             sbom_sha="", source_url=""):
    repo, output = Path(repo).resolve(), Path(output).resolve()
    version = importlib.metadata.version("reuse")
    if version != "6.3.0":
        raise ValueError("Use pinned REUSE 6.3.0; found " + version)
    sha = full_sha(repo, ref)
    timestamp = timestamp or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError("Timestamp must include UTC timezone")
    if kind == "snapshot" and (output.name != sha or output.exists()):
        raise ValueError("Snapshot output must be a new directory named by the full source SHA")
    with tempfile.TemporaryDirectory(prefix="opentrix-license-") as tmp:
        root = Path(tmp)
        entries = materialize(repo, sha, root)
        meta = common(sha, kind, timestamp, "git:" + sha + "; REUSE " + version)
        files = file_inventory(root, entries, meta)
        deps, missing = dependency_inventory(root, inputs or {}, inventory, sbom_sha, source_url, meta)
        # Merge streams so the complete tool output keeps ordering and survives failure.
        lint = subprocess.run([sys.executable, "-m", "reuse", "--no-multiprocessing", "--root", str(root), "lint"],
            cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lint_meta = dict(meta, evidence_status="PASS" if lint.returncode == 0 else "BLOCKED",
            blockers="Rights review pending" if lint.returncode == 0 else "Full REUSE lint returned nonzero")
        report = ["OpenTrix LIC-02 — generated full REUSE lint evidence",
            *[k + ": " + str(v) for k, v in lint_meta.items()],
            "command: python -m reuse --no-multiprocessing --root <isolated-committed-tree> lint",
            "tool_version: " + version, "python_version: " + sys.version.split()[0],
            "timestamp_note: recorded_at_utc is an explicit reproducibility input when supplied",
            "output_normalization: random isolation-root prefix and CRLF line endings only",
            "exit_code: " + str(lint.returncode), "--- complete combined stdout/stderr ---", ""]
        # Normalize only the random isolation path, never tool findings/exit status.
        body = lint.stdout.decode("utf-8", errors="replace").replace(str(root), "<SOURCE_ROOT>").replace("\r\n", "\n")
        # Keep every tool line, including its blank lines, inside explicit bounds.
        content = {REPORTS[0]: ("\n".join(report) + body + "\n--- end complete stdout/stderr ---\n").encode("utf-8"),
                   REPORTS[1]: csv_bytes(files, FILE_FIELDS), REPORTS[2]: csv_bytes(deps, DEP_FIELDS)}
        for name in REPORTS:
            status_meta = lint_meta if name == REPORTS[0] else dict(meta)
            if name == REPORTS[2] and missing:
                status_meta["blockers"] = missing
            content[name + ".license"] = sidecar(status_meta)
        manifest = dict(meta, reuse_version=version, reuse_exit_code=lint.returncode,
            generator_sha256=digest(Path(__file__).read_bytes()), python_version=sys.version.split()[0],
            platform=sys.platform, canonical_r23_policy_sha256=digest((root / "scripts/r23-compliance.py").read_bytes()),
            tracked_file_count=len(entries), dependency_count=len(deps), dependency_input_status=missing or "SUPPLIED_R23_PROJECTION",
            sbom_source_sha=sbom_sha, sbom_source_url=source_url, generated_files={name:digest(data) for name,data in sorted(content.items())})
        content["generation-manifest.json"] = (json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        content["generation-manifest.json.license"] = sidecar(meta)
        output.mkdir(parents=True, exist_ok=True)
        for name, data in content.items():
            (output / name).write_bytes(data)
        blocked_files = any(r["evidence_status"] == "BLOCKED" for r in files)
        blocked_deps = any(row["license_policy_status"] != "APPROVED" for row in deps)
        stale_inputs = bool(deps) and (sbom_sha != sha or not source_url.startswith("https://"))
        code = 1 if lint.returncode or blocked_files or missing or blocked_deps or stale_inputs else 0
        print(stable({"source_sha":sha,"kind":kind,"output":str(output),"reuse_exit_code":lint.returncode,
            "tracked_files":len(files),"dependency_rows":len(deps),"missing_inputs":missing,"exit_code":code}))
        return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--ref", required=True, help="Committed source ref; dirty/untracked edits are not analyzed")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--kind", choices=("living", "snapshot"), required=True)
    parser.add_argument("--timestamp", help="Explicit UTC timestamp for byte-reproducible regeneration")
    for project in ("backend", "portal-bff", "frontend"):
        parser.add_argument("--" + project, type=Path)
    parser.add_argument("--r23-inventory", type=Path)
    parser.add_argument("--sbom-source-sha", default="")
    parser.add_argument("--sbom-source-url", default="")
    args = parser.parse_args()
    try:
        return generate(args.repo, args.ref, args.output, args.kind, args.timestamp,
            {name:getattr(args,name.replace("-","_")) for name in ("backend","portal-bff","frontend") if getattr(args,name.replace("-","_"))},
            args.r23_inventory, args.sbom_source_sha, args.sbom_source_url)
    except (ValueError, OSError, ImportError, KeyError, TypeError, UnicodeError) as exc:
        print("LICENSE_EVIDENCE_BLOCKED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
