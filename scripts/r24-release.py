# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""R24: reproducible release candidate archives and fail-closed distribution gate."""
import argparse
import gzip
import hashlib
import io
import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen, build_opener, HTTPRedirectHandler
from urllib.parse import urlsplit
import re
import sys
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path

TAG = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+(?:-rc\.[1-9][0-9]*)?$")
SHA = re.compile(r"[a-f0-9]{40}$")
REVIEWERS = {"phanyen06ym-ien", "ngang02012007-crypto"}
JAVA_BASE = re.compile(r"eclipse-temurin:21-jre@sha256:[a-f0-9]{64}$")
GATES = ("upstream_license_notices", "source_and_relink", "frontend_assets",
         "service_images", "base_images", "archive_and_checksums", "release_notes")
SOURCE_GATES = ("source_provenance", "source_license", "sbom_source_boundary",
                "archive_and_checksums", "release_notes")
PERMISSIVE = {"Apache-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD"}

def ident(row):
    return tuple(row[k] for k in ("project", "name", "version", "purl"))



def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def release_notes(changelog, tag, validation_only=False):
    version = re.escape(tag[1:])
    match = re.search(rf"(?ms)^## \[{version}\][^\n]*\n(.*?)(?=^## \[|\Z)", changelog)
    if match is None and validation_only:
        match = re.search(r"(?ms)^## \[Unreleased\][^\n]*\n(.*?)(?=^## \[|\Z)", changelog)
        require(match and match.group(1).strip(), "CHANGELOG is missing nonempty Unreleased notes")
        return (f"# DX-OS {tag} — validation only\n\n"
                "Unreleased preview; not approved for publication.\n\n"
                + match.group(1).strip() + "\n")
    require(match and match.group(1).strip(), "CHANGELOG is missing this version's release notes")
    return f"# DX-OS {tag}\n\n" + match.group(1).strip() + "\n"


def normalize_cyclonedx(raw):
    """Remove only volatile generator metadata from packaged CycloneDX JSON.

    CycloneDX runtime components, licenses and dependency edges remain intact.
    Raw generator SBOM files are still used by the R23 compliance policy gate.
    """
    sbom = json.loads(raw)
    require(isinstance(sbom, dict) and sbom.get("bomFormat") == "CycloneDX",
            "invalid CycloneDX SBOM for release")
    sbom.pop("serialNumber", None)  # generator UUID, changes on every build
    metadata = sbom.get("metadata")
    if isinstance(metadata, dict):
        metadata.pop("timestamp", None)  # generator wall-clock time
        component = metadata.get("component")
        if isinstance(component, dict) and isinstance(component.get("externalReferences"), list):
            refs = component["externalReferences"]
            refs = [ref for ref in refs if not (
                isinstance(ref, dict) and ref.get("type") == "build-system"
                and isinstance(ref.get("url"), str)
                and re.fullmatch(
                    r"https://github[.]com/[^/]+/[^/]+/actions/runs/[0-9]+",
                    ref["url"]
                )
            )]
            if refs:
                component["externalReferences"] = refs
            else:
                component.pop("externalReferences", None)
    return (json.dumps(sbom, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")) + "\n").encode("utf-8")


# Retain ALL five existing R24 SOURCE-ONLY evidence categories.
# Additional verification is fail-closed; it does not waive license/rights review.
EVIDENCE_CHECKS = {
    "source_provenance": ("file_origin", "contributor_authority",
                          "third_party_assets", "independent_origin_review"),
    "source_license": ("osi_approved_license", "apache_2_0",
                       "notice_and_attribution", "exceptions_disposition",
                       "independent_license_review"),
    "sbom_source_boundary": ("backend_sbom", "portal_bff_sbom", "frontend_sbom",
                             "inventory", "no_binary_or_ghcr_distribution"),
    "archive_and_checksums": ("two_independent_packaging_runs",
                              "sha256sums", "manifest", "sbom_member_bytes",
                              "notes_and_notice", "extracted_source_build",
                              "independent_archive_review"),
    "release_notes": ("exact_version_notes", "source_only_scope",
                       "rights_limitations", "independent_notes_review"),
}
MAX_ARTIFACT_ZIP_BYTES = 96 * 1024 * 1024

def _github_json(path):
    """Read live GitHub state; a missing/inaccessible API response blocks publication."""
    token = os.environ.get("GITHUB_TOKEN", "")
    require(token, "GITHUB_TOKEN is required to verify independent R24 review")
    url = "https://api.github.com/repos/tricore-opentrix/opentrix/" + path
    req = Request(url, headers={"Authorization": "Bearer " + token,
                                "Accept": "application/vnd.github+json",
                                "X-GitHub-Api-Version": "2022-11-28"})
    try:
        with urlopen(req, timeout=15) as response:
            return json.loads(response.read())
    except (URLError, ValueError, OSError) as exc:
        raise ValueError("cannot independently verify GitHub review/evidence: publication BLOCKED") from exc


def _blob_oid(contents):
    """Git blob object SHA-1 for exact bytes; not the SHA-256 release archive hash."""
    return hashlib.sha1(b"blob " + str(len(contents)).encode("ascii")
                        + b"\0" + contents).hexdigest()


def verify_independent_review(accepted, acceptance_file):
    """Verify actual reviewed bytes without a circular future review URL.

    The acceptance PR number is known before final review; the final APPROVED
    review is discovered from live GitHub API after it has been submitted.
    """
    pr_number = accepted.get("acceptance_pr")
    require(isinstance(pr_number, int) and not isinstance(pr_number, bool)
            and pr_number > 0,
            "invalid acceptance_pr: expected existing GitHub PR number")
    pr = _github_json(f"pulls/{pr_number}")
    reviews = _github_json(f"pulls/{pr_number}/reviews?per_page=100")
    require(isinstance(pr, dict) and isinstance(reviews, list)
            and len(reviews) < 100,
            "cannot exhaustively verify actual GitHub PR reviews")
    author = (pr.get("user") or {}).get("login")
    require(pr.get("merged_at") and (pr.get("base") or {}).get("ref") == "main",
            "independent acceptance PR must be merged to main")
    head_sha = (pr.get("head") or {}).get("sha")
    merge_sha = pr.get("merge_commit_sha")
    require(isinstance(head_sha, str) and SHA.fullmatch(head_sha)
            and isinstance(merge_sha, str) and SHA.fullmatch(merge_sha),
            "cannot identify reviewed acceptance PR HEAD and merged commit")
    # Most recent submitted review for each user supersedes earlier approvals.
    # REST review responses are chronological; dismissed/latest CHANGES_REQUESTED
    # cannot be silently overridden by a prior APPROVED review.
    latest = {}
    for review in reviews:
        require(isinstance(review, dict), "invalid GitHub review response")
        login = (review.get("user") or {}).get("login")
        if login:
            latest[login] = review
    eligible = [name for name, review in latest.items()
                if name in REVIEWERS
                and name != author
                and name in accepted.get("reviewed_by", [])
                and review.get("state") == "APPROVED"
                and review.get("commit_id") == head_sha]
    require(eligible, "independent review must APPROVE final PR HEAD (not dismissed)")
    acceptance_path = f"docs/06-deployment/r24-acceptances/{accepted['tag']}.json"
    files = _github_json(f"pulls/{pr_number}/files?per_page=100")
    require(isinstance(files, list) and len(files) < 100
            and any(isinstance(row, dict)
                    and row.get("filename") == acceptance_path for row in files),
            "independent review PR does not include exact R24 acceptance JSON")
    reviewed_oid = _blob_oid(Path(acceptance_file).read_bytes())
    for commit_ref in (head_sha, merge_sha, "main"):
        info = _github_json(f"contents/{acceptance_path}?ref={commit_ref}")
        require(isinstance(info, dict) and info.get("type") == "file"
                and info.get("sha") == reviewed_oid,
                "acceptance JSON bytes differ from approved PR HEAD/merged main")
    return eligible[0], author


def verify_source_evidence(accepted, pr_author):
    """Verify source-rights/manifest evidence without reducing legacy five gates.

    Reviewer statements are independently inspectable assertions, not proof
    that UNKNOWN/RIGHTS_PENDING code was cleared. A separate #138 disposition
    and the independent acceptance review remain indispensable.
    """
    run_ids = accepted.get("candidate_run_ids")
    require(isinstance(run_ids, list) and len(run_ids) == 2
            and all(isinstance(i, int) and not isinstance(i, bool) and i > 0
                    for i in run_ids), "exactly two final R4 candidate run IDs required")
    require(run_ids[0] != run_ids[1],
            "two final R4 candidate run IDs must be distinct")
    evidence = accepted.get("evidence")
    require(isinstance(evidence, dict), "source-only release evidence object is missing")
    for kind, checklist in EVIDENCE_CHECKS.items():
        url = evidence.get(kind, "")
        match = re.fullmatch(
            r"https://github[.]com/tricore-opentrix/opentrix/"
            r"(?:issues|pull)/[1-9][0-9]*#issuecomment-([1-9][0-9]*)",
            url) if isinstance(url, str) else None
        require(match, f"source-only release missing verified GitHub evidence: {kind}")
        comment = _github_json(f"issues/comments/{match.group(1)}")
        require(isinstance(comment, dict) and comment.get("html_url") == url,
                f"source-only evidence permalink mismatch: {kind}")
        reviewer = (comment.get("user") or {}).get("login")
        require(reviewer in REVIEWERS and reviewer != pr_author
                and reviewer in accepted.get("reviewed_by", []),
                f"source-only evidence reviewer is unauthorized or not independent: {kind}")
        body = comment.get("body") or ""
        blocks = re.findall(r"<!-- R24_SOURCE_EVIDENCE_V1\n(.*?)\n-->",
                            body, re.DOTALL) if isinstance(body, str) else []
        require(len(blocks) == 1, f"missing unique source-only checklist: {kind}")
        try:
            proof = json.loads(blocks[0])
        except (ValueError, TypeError) as exc:
            raise ValueError(f"invalid source-only evidence JSON: {kind}") from exc
        require(isinstance(proof, dict)
                and proof.get("kind") == kind
                and proof.get("tag") == accepted["tag"]
                and proof.get("mode") == "source-only"
                and proof.get("source_sha") == accepted["source_sha"]
                and proof.get("archive_sha256") == accepted["archive_sha256"]
                and proof.get("reviewer") == reviewer
                and proof.get("verdict") == "PASS",
                f"source-only evidence identity/verdict mismatch: {kind}")
        checks = proof.get("checks")
        require(isinstance(checks, dict)
                and all(checks.get(check) is True for check in checklist),
                f"source-only evidence mandatory checklist incomplete: {kind}")
        links = proof.get("references")
        require(isinstance(links, list) and links
                and all(isinstance(ref, str) and ref.startswith("https://")
                        for ref in links),
                f"source-only evidence lacks supporting references: {kind}")
        if kind in ("source_provenance", "source_license"):
            require(proof.get("unresolved_distribution_blockers") == [],
                    "source rights or license distribution blockers remain unresolved")
        if kind == "archive_and_checksums":
            require(proof.get("candidate_run_ids") == accepted.get("candidate_run_ids"),
                    "reviewer-attested candidate run IDs mismatch acceptance")
            for run_id in accepted["candidate_run_ids"]:
                require(f"https://github.com/tricore-opentrix/opentrix/actions/runs/{run_id}" in links,
                        "independent archive review lacks candidate run references")


class _DropArtifactAuthOnRedirect(HTTPRedirectHandler):
    """Follow only HTTPS signed artifact URLs; do not forward GitHub bearer token."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        require(urlsplit(newurl).scheme == "https",
                "insecure GitHub Actions artifact redirect rejected")
        moved = super().redirect_request(req, fp, code, msg, headers, newurl)
        if moved is not None and urlsplit(newurl).hostname != "api.github.com":
            moved.remove_header("Authorization")
        return moved


def _github_artifact_zip(artifact_id):
    """Download actual GitHub Actions artifact ZIP for independent byte comparison."""
    token = os.environ.get("GITHUB_TOKEN", "")
    require(token, "GITHUB_TOKEN required to download R24 reproducibility artifacts")
    req = Request(
        f"https://api.github.com/repos/tricore-opentrix/opentrix/actions/artifacts/{artifact_id}/zip",
        headers={"Authorization": "Bearer " + token,
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28"})
    try:
        with build_opener(_DropArtifactAuthOnRedirect()).open(req, timeout=60) as response:
            content = response.read(MAX_ARTIFACT_ZIP_BYTES + 1)
        require(len(content) <= MAX_ARTIFACT_ZIP_BYTES,
                "candidate artifact too large for bounded independent verification")
        return content
    except (URLError, ValueError, OSError) as exc:
        raise ValueError("unable to download actual candidate archive: publication BLOCKED") from exc


def verify_two_candidates(accepted, publisher_archive, expected_manifest, expected_members):
    """Download/verify TWO independently packaged real archives at frozen SHA.

    SHA-256 equality implies byte equality; MANIFEST and each extracted member
    are also compared explicitly so reviewers can inspect concrete boundaries.
    """
    run_ids = accepted.get("candidate_run_ids")
    require(isinstance(run_ids, list) and len(run_ids) == 2
            and all(isinstance(i, int) and not isinstance(i, bool) and i > 0
                    for i in run_ids),
            "exactly two final R4 candidate run IDs required")
    require(run_ids[0] != run_ids[1], "two final R4 candidate run IDs must be distinct")
    archive_name = Path(publisher_archive).name
    required_zip_files = {archive_name, "SHA256SUMS", "RELEASE-NOTES.md"}
    published_sha = digest(Path(publisher_archive).read_bytes())
    require(published_sha == accepted["archive_sha256"],
            "publisher archive SHA-256 does not match acceptance")
    for run_id in run_ids:
        run = _github_json(f"actions/runs/{run_id}")
        require(isinstance(run, dict)
                and run.get("id") == run_id
                and run.get("event") == "workflow_dispatch"
                and run.get("head_branch") == "main"
                and run.get("head_sha") == accepted["source_sha"]
                and run.get("path") == ".github/workflows/release.yml"
                and run.get("status") == "completed"
                and run.get("conclusion") == "success",
                f"R4 candidate {run_id}: wrong source SHA / event / workflow or failed run")
        listing = _github_json(f"actions/runs/{run_id}/artifacts?per_page=100")
        require(isinstance(listing, dict)
                and isinstance(listing.get("artifacts"), list)
                and len(listing["artifacts"]) < 100,
                f"R4 candidate {run_id}: cannot exhaustively verify artifacts")
        artifact_name = f"r24-source-only-publishable-candidate-{run_id}"
        matches = [a for a in listing["artifacts"] if isinstance(a, dict)
                   and a.get("name") == artifact_name]
        require(len(matches) == 1, f"R4 candidate {run_id}: publishable archive absent/ambiguous")
        item = matches[0]
        artifact_id = item.get("id")
        require(isinstance(artifact_id, int) and not isinstance(artifact_id, bool)
                and artifact_id > 0 and item.get("expired") is False
                and isinstance(item.get("size_in_bytes"), int)
                and item["size_in_bytes"] > 0
                and isinstance(item.get("digest"), str)
                and re.fullmatch(r"sha256:[a-f0-9]{64}", item["digest"]),
                f"R4 candidate {run_id}: invalid/expired artifact metadata")
        actual_zip = _github_artifact_zip(artifact_id)
        require(digest(actual_zip) == item["digest"].split(":", 1)[1],
                f"R4 candidate {run_id}: downloaded artifact ZIP digest mismatch")
        try:
            with zipfile.ZipFile(io.BytesIO(actual_zip)) as z:
                require(len(z.infolist()) == len(required_zip_files)
                        and set(z.namelist()) == required_zip_files,
                        f"R4 candidate {run_id}: unexpected artifact member list")
                for name in required_zip_files:
                    require(z.getinfo(name).file_size <= MAX_ARTIFACT_ZIP_BYTES,
                            "individual candidate artifact file exceeds size limit")
                archive_bytes = z.read(archive_name)
                checksums_bytes = z.read("SHA256SUMS")
                notes_bytes = z.read("RELEASE-NOTES.md")
        except (zipfile.BadZipFile, KeyError, OSError) as exc:
            raise ValueError(f"R4 candidate {run_id}: unreadable actual artifact ZIP") from exc
        require(digest(archive_bytes) == accepted["archive_sha256"],
                f"R4 candidate {run_id}: independently produced archive SHA256 mismatch")
        with tempfile.TemporaryDirectory(prefix="r24-candidate-") as d:
            archive_path = Path(d) / archive_name
            sums_path = Path(d) / "SHA256SUMS"
            archive_path.write_bytes(archive_bytes)
            sums_path.write_bytes(checksums_bytes)
            manifest, members, prefix = verify(archive_path, sums_path)
        require(manifest.get("mode") == "source-only"
                and manifest.get("validation_only", False) is False
                and manifest.get("tag") == accepted["tag"]
                and manifest.get("source_sha") == accepted["source_sha"],
                f"R4 candidate {run_id}: invalid publishable source-only MANIFEST identity")
        require(notes_bytes == members.get(prefix + "RELEASE-NOTES.md"),
                f"R4 candidate {run_id}: standalone release notes differ")
        require(manifest == expected_manifest,
                f"R4 candidate {run_id}: cross-run MANIFEST differs")
        require(members == expected_members,
                f"R4 candidate {run_id}: cross-run SBOM/member bytes differ")
        print(f"R24_R4_INDEPENDENT_CANDIDATE_PASS run={run_id} sha256={published_sha}")
    print("R24_R4_TWO_CANDIDATES_REPRODUCIBLE: SHA256/MANIFEST/SBOM/members match")
    return tuple(run_ids)


def package(repo, tag, sha, output, mode="binary", validation_only=False):
    require(mode in {"binary", "source-only"}, "unknown R24 release mode")
    require(TAG.fullmatch(tag), "release tag must be vMAJOR.MINOR.PATCH")
    require(SHA.fullmatch(sha), "source SHA must be a full lowercase commit hash")
    source = Path(repo)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    prefix = f"dxos-{tag}/"
    files = {}
    source_modes = {}  # Preserve Git index modes independently of the host filesystem.
    def add(target, path):
        path = source / path
        require(path.is_file() and not path.is_symlink(), f"missing/unsafe release input: {path}")
        contents = path.read_bytes()
        if target.endswith(".cdx.json"):
            contents = normalize_cyclonedx(contents)
        files[prefix + target] = contents

    if mode == "binary":
        for app in ("backend", "portal-bff"):
            jars = [p for p in (source / app / "build/libs").glob("*.jar")
                    if not p.name.endswith("-plain.jar")]
            require(len(jars) == 1, f"expected exactly one bootJar for {app}, got {len(jars)}")
            add(f"{app}/application.jar", jars[0].relative_to(source))
        frontend = source / "frontend/dist"
        require(frontend.is_dir(), "frontend/dist missing")
        assets = sorted(p for p in frontend.rglob("*") if p.is_file())
        require(assets and (frontend / "index.html").is_file(), "frontend build has no index.html")
        for path in assets:
            add("frontend/" + path.relative_to(frontend).as_posix(), path.relative_to(source))
    else:
        # The manifest's full source_sha must identify the *exact* commit archived.
        head = subprocess.run(["git", "rev-parse", "--verify", "HEAD^{commit}"],
                              cwd=source, capture_output=True, text=True)
        require(head.returncode == 0 and head.stdout.strip() == sha,
                "source SHA must match the checked-out HEAD commit")
        # Build outputs may be untracked/ignored, but any staged or unstaged
        # changes to tracked inputs could contaminate SBOMs and release notes.
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--"],
                               cwd=source, capture_output=True)
        require(clean.returncode == 0,
                "tracked working tree/index differs from source SHA: publication blocked")
        # Only Git-committed objects are archived; untracked files are ignored.
        proc = subprocess.run(["git", "ls-files", "--cached", "--stage", "-z"],
                              cwd=source, check=True, capture_output=True)
        index_modes, index_blobs = {}, {}
        for entry in (row for row in proc.stdout.split(b"\0") if row):
            metadata, path_bytes = entry.split(b"\t", 1)
            entry_mode, blob_sha, stage = metadata.split(b" ")
            require(entry_mode in {b"100644", b"100755"} and stage == b"0",
                    f"unsupported tracked file mode/stage: {path_bytes!r}")
            name = path_bytes.decode("utf-8")
            index_modes[name] = entry_mode
            index_blobs[name] = blob_sha.decode("ascii")
        tracked = sorted(index_modes)
        require(tracked, "source-only archive needs a checked-out git worktree")
        disallowed_binary = {".jar", ".war", ".class", ".zip", ".gz", ".tar",
                             ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico",
                             ".woff", ".woff2", ".ttf", ".otf", ".pdf", ".exe",
                             ".dll", ".mp4"}
        for name in tracked:
            require(not (name == ".env" or name.startswith(".env.") and name != ".env.example"),
                    "secret-like tracked .env file: source publication blocked")
            if Path(name).suffix.lower() in disallowed_binary:
                continue
            raw = subprocess.run(["git", "cat-file", "blob", index_blobs[name]],
                                 cwd=source, check=True, capture_output=True).stdout
            require(b"\0" not in raw, f"binary data in source-only archive: {name}")
            raw.decode("utf-8")
            files[prefix + "source/" + name] = raw
            source_modes[prefix + "source/" + name] = (
                0o755 if index_modes[name] == b"100755" else 0o644)

    # Candidate builds may be incomplete; reviewed upstream texts are added only
    # by the independently approved R24 distribution workstream.
    if mode == "binary":
        upstream = source / "build/r24/upstream"
        require((upstream / "upstream-index.json").is_file(),
                "R24 upstream evidence collector was not run")
        add("compliance/upstream-index.json",
            (upstream / "upstream-index.json").relative_to(source))
        for path in sorted(p for p in upstream.rglob("*") if p.is_file()
                           and p.name != "upstream-index.json"):
            add("compliance/upstream/" + path.relative_to(upstream).as_posix(),
                path.relative_to(source))
    for target, path in {
        "LICENSE": "LICENSE", "NOTICE": "NOTICE",
        "THIRD-PARTY-NOTICES.md": "THIRD-PARTY-NOTICES.md",
        "CHANGELOG.md": "CHANGELOG.md",
        "compliance/backend.cdx.json": "backend/build/reports/cyclonedx/bom.json",
        "compliance/portal-bff.cdx.json": "portal-bff/build/reports/cyclonedx/bom.json",
        "compliance/frontend.cdx.json": "frontend-sbom.json",
        "compliance/license-inventory.json": "build/r23/license-inventory.json",
    }.items():
        add(target, path)
    inventory = json.loads(files[prefix + "compliance/license-inventory.json"])
    require(isinstance(inventory, list) and inventory and
            all(row.get("license_policy_status") == "APPROVED" for row in inventory),
            "R23 dependency policy is not approved")
    notes = release_notes((source / "CHANGELOG.md").read_text(encoding="utf-8"), tag,
                          validation_only=validation_only)
    files[prefix + "RELEASE-NOTES.md"] = notes.encode()
    manifest = {"tag": tag, "source_sha": sha, "mode": mode,
                "files_sha256": {name[len(prefix):]: digest(data)
                                 for name, data in sorted(files.items())}}
    if validation_only:
        manifest["validation_only"] = True
    files[prefix + "MANIFEST.json"] = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    archive = output / f"dxos-open-core-{tag[1:]}.tar.gz"
    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tf:
                for name, contents in sorted(files.items()):
                    info = tarfile.TarInfo(name)
                    info.size, info.mode = len(contents), source_modes.get(name, 0o644)
                    info.uid = info.gid = info.mtime = 0
                    info.uname = info.gname = ""
                    tf.addfile(info, io.BytesIO(contents))
    (output / "SHA256SUMS").write_text(f"{digest(archive.read_bytes())}  {archive.name}\n")
    (output / "RELEASE-NOTES.md").write_text(notes, encoding="utf-8")
    verify(archive, output / "SHA256SUMS")
    print(f"R24_CANDIDATE_BUILT {archive.name}: {len(files)} files, {len(inventory)} distribution PENDING")


def verify(archive, checksums):
    archive, checksums = Path(archive), Path(checksums)
    line = checksums.read_text().strip()
    require(line == f"{digest(archive.read_bytes())}  {archive.name}", "checksum mismatch")
    with tarfile.open(archive, "r:gz") as tf:
        members = tf.getmembers()
        require(members and all(m.isfile() and not m.issym() and not m.islnk()
                                and not Path(m.name).is_absolute()
                                and ".." not in Path(m.name).parts for m in members),
                "unsafe archive member")
        data = {m.name: tf.extractfile(m).read() for m in members}
    require(len(data) == len(members), "duplicate archive entries")
    manifests = [name for name in data if name.endswith("/MANIFEST.json")]
    require(len(manifests) == 1, "missing/duplicate manifest")
    manifest = json.loads(data[manifests[0]])
    prefix = manifests[0][:-len("MANIFEST.json")]
    require(TAG.fullmatch(manifest.get("tag", "")) and SHA.fullmatch(manifest.get("source_sha", "")),
            "invalid release identity")
    require(prefix == f"dxos-{manifest['tag']}/", "invalid archive root")
    require(manifest.get("mode") in {"binary", "source-only"}, "release mode missing")
    require(isinstance(manifest.get("validation_only", False), bool),
            "invalid validation-only marker")
    expected = {prefix + name: d for name, d in manifest["files_sha256"].items()}
    require(set(expected) == set(data) - {manifests[0]}, "archive manifest coverage mismatch")
    require(all(digest(data[name]) == value for name, value in expected.items()),
            "archive file digest mismatch")
    print(f"R24_ARCHIVE_VERIFY_PASS {archive.name}")
    return manifest, data, prefix


def gate(archive, checksums, acceptance, tag, sha, notes_file=None):
    manifest, data, prefix = verify(archive, checksums)
    require(not manifest.get("validation_only", False),
            "validation-only archive cannot be published")
    if notes_file is not None:
        require(Path(notes_file).read_bytes() == data[prefix + "RELEASE-NOTES.md"],
                "standalone release notes mismatch verified archive")
    require(manifest["tag"] == tag and manifest["source_sha"] == sha,
            "release candidate identity differs from tag/commit")
    if tag == "v0.2.0":
        require(manifest["mode"] == "source-only",
                "v0.2.0 is SOURCE-ONLY; binary/JAR/GHCR publication BLOCKED")
    path = Path(acceptance)
    require(path.is_file(), "R24 distribution acceptance file is absent: publication BLOCKED")
    accepted = json.loads(path.read_text())
    require(accepted.get("tag") == tag and accepted.get("source_sha") == sha,
            "R24 acceptance is not for exact tag and source SHA")
    require(accepted.get("mode") == manifest["mode"],
            "R24 approval scope differs from published archive mode")
    require(accepted.get("archive_sha256") == digest(Path(archive).read_bytes()),
            "reviewed archive SHA-256 mismatch")
    require(set(accepted.get("reviewed_by", [])) & REVIEWERS,
            "R24 independent compliance reviewer is missing")
    if manifest["mode"] == "source-only":
        require(not any(name.startswith(prefix + "backend/") or
                        name.startswith(prefix + "portal-bff/") or
                        name.startswith(prefix + "frontend/") or
                        name.startswith(prefix + "compliance/upstream/") for name in data),
                "source-only package unexpectedly includes distributable binaries")
        require(any(name.startswith(prefix + "source/") for name in data),
                "source-only package has no tracked source")
        require(isinstance(accepted.get("evidence"), dict),
                "source-only release evidence object is missing")
        for key in SOURCE_GATES:
            ref = accepted["evidence"].get(key, "")
            require(isinstance(ref, str) and ref.startswith("https://"),
                    f"source-only release missing evidence: {key}")
        _, pr_author = verify_independent_review(accepted, path)
        verify_source_evidence(accepted, pr_author)
        verify_two_candidates(accepted, archive, manifest, data)
        print("R24_SOURCE_ONLY_GATE_PASS: no binary/GHCR authorization")
        return "source-only"
    require(JAVA_BASE.fullmatch(accepted.get("java_base_image", "")),
            "pinned, reviewed JRE base image digest is required")
    for key in GATES:
        ref = accepted.get("evidence", {}).get(key, "")
        require(isinstance(ref, str) and ref.startswith("https://"),
                f"missing independently reviewable evidence: {key}")
    inventory = json.loads(data[prefix + "compliance/license-inventory.json"])
    expected = {ident(row) for row in inventory}
    require(len(expected) == len(inventory), "duplicate dependency inventory identities")
    index = json.loads(data[prefix + "compliance/upstream-index.json"])
    require(isinstance(index, list), "upstream source manifest missing")
    records = {ident(row): row for row in index}
    require(len(records) == len(index) and set(records) == expected,
            "upstream source manifest does not cover resolved components")
    permissive = accepted.get("license_groups", {}).get("permissive", {})
    require(permissive.get("status") == "CLEARED" and
            isinstance(permissive.get("evidence"), str) and
            permissive["evidence"].startswith("https://"),
            "reviewed permissive-license group disposition is missing")
    exceptions = accepted.get("exceptions", [])
    require(isinstance(exceptions, list), "exception disposition list missing")
    exceptions_by_id = {ident(row): row for row in exceptions}
    require(len(exceptions_by_id) == len(exceptions), "duplicate license exception decisions")
    required_exceptions = set()
    for row in inventory:
        key = ident(row)
        record = records[key]
        # POM dependency management metadata is not bundled code.
        if record.get("status") == "METADATA_ONLY":
            require("type=pom" in row.get("purl", ""), "unproven metadata-only exclusion")
            continue
        require(record.get("status") == "COLLECTED_UNREVIEWED",
                f"unresolved upstream license text for {key}: cannot publish binaries")
        docs = record.get("docs", [])
        require(isinstance(docs, list) and docs, "upstream documents not collected")
        has_license = False
        for doc in docs:
            path = doc.get("path", "")
            require(path.startswith("compliance/upstream/") and
                    path in {name[len(prefix):] for name in data if name.startswith(prefix)},
                    "upstream license text absent from reviewed archive")
            require(doc.get("sha256") == digest(data[prefix + path]),
                    "upstream text checksum mismatch")
            has_license |= bool(doc.get("license_text")) and bool(data[prefix + path])
        require(has_license, f"actual upstream LICENSE/COPYING bytes missing: {key}")
        licenses = set(row.get("licenses", []))
        require(licenses, "empty license declaration cannot be grouped")
        if not licenses <= PERMISSIVE:
            required_exceptions.add(key)
            decision = exceptions_by_id.get(key, {})
            require(decision.get("status") == "CLEARED" and
                    isinstance(decision.get("evidence"), str) and
                    decision["evidence"].startswith("https://"),
                    f"special-license exception not accepted: {key}")
            require(decision.get("license_choice") in licenses or
                    (row.get("license_choice") and
                     decision.get("license_choice") == row.get("license_choice")),
                    f"special-license option not recorded: {key}")
    require(set(exceptions_by_id) == required_exceptions,
            "exception decisions are stale, missing or outside shipped scope")
    print(f"R24_BINARY_GATE_PASS {len(inventory)} resolved rows, "
          f"{len(required_exceptions)} individually reviewed exceptions")
    return "binary"


def main():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="command", required=True)
    a = sp.add_parser("package")
    a.add_argument("--repo", default=".")
    a.add_argument("--mode", choices=("binary", "source-only"), default="binary")
    a.add_argument("--tag", required=True)
    a.add_argument("--sha", required=True)
    a.add_argument("--output", default="dist/r24")
    a.add_argument("--validation-only", action="store_true",
                   help="Allow Unreleased preview notes; archive cannot pass publication gate")
    a = sp.add_parser("verify")
    a.add_argument("--archive", required=True)
    a.add_argument("--checksums", required=True)
    a = sp.add_parser("gate")
    a.add_argument("--archive", required=True)
    a.add_argument("--checksums", required=True)
    a.add_argument("--acceptance", required=True)
    a.add_argument("--tag", required=True)
    a.add_argument("--sha", required=True)
    a.add_argument("--release-notes", default=None)
    args = p.parse_args()
    try:
        if args.command == "package":
            package(args.repo, args.tag, args.sha, args.output, args.mode, args.validation_only)
        elif args.command == "verify":
            verify(args.archive, args.checksums)
        else:
            gate(args.archive, args.checksums, args.acceptance, args.tag, args.sha, args.release_notes)
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError,
            tarfile.TarError, subprocess.CalledProcessError) as exc:
        print("R24_BLOCKED:", exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
