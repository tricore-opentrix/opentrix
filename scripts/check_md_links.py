#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 TRICORE contributors
#
# SPDX-License-Identifier: Apache-2.0
"""Check relative links and #anchors in git-tracked Markdown files.

Usage: python3 scripts/check_md_links.py   (run from anywhere inside the repo)

Scope: every file matched by `git ls-files '*.md'`. Fenced code blocks and inline code
spans are ignored. Links with a URL scheme (https:, mailto:, ...) are NOT checked.
Anchors are derived from headings using GitHub-style slugs (approximation).
Exit status: 0 if no broken link, 1 otherwise.
"""
import os
import re
import subprocess
import sys


def repo_root():
    return subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()


def anchors(path):
    out = set()
    in_fence = False
    with open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = re.match(r"#{1,6}\s+(.*)", line)
            if m:
                slug = re.sub(r"[^\w\- ]", "", m.group(1).strip().lower())
                out.add(slug.replace(" ", "-"))
    return out


def main():
    os.chdir(repo_root())
    files = subprocess.check_output(
        ["git", "ls-files", "*.md"], text=True
    ).splitlines()
    bad = []
    for f in files:
        with open(f, encoding="utf-8-sig") as fh:
            text = re.sub(r"```.*?```", "", fh.read(), flags=re.S)
            text = re.sub(r"`[^`\n]*`", "", text)
        for m in re.finditer(r"\]\(([^)\s]+)\)", text):
            url = m.group(1)
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", url):
                continue
            path, _, frag = url.partition("#")
            target = os.path.normpath(os.path.join(os.path.dirname(f), path)) if path else f
            if not os.path.exists(target):
                bad.append((f, url, "missing target"))
            elif frag and target.endswith(".md") and frag.lower() not in anchors(target):
                bad.append((f, url, "missing anchor"))
    for item in bad:
        print(" | ".join(item))
    print(f"files {len(files)} broken {len(bad)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
