# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""R23: license gate over three CycloneDX SBOMs; generate a notices inventory."""
import argparse
import json
import re
import sys
from pathlib import Path

ALLOWED = set("""0BSD Apache-2.0 BSD-2-Clause BSD-3-Clause CDDL-1.0 CDDL-1.1
CC0-1.0 EDL-1.0 EPL-1.0 EPL-2.0 ISC MIT MIT-0 BlueOak-1.0.0 MPL-2.0 OFL-1.1
Unicode-3.0 Unicode-DFS-2016 Unlicense Zlib""".split())
ALIASES = {
    "the apache software license, version 2.0": "Apache-2.0",
    "apache software license, version 2.0": "Apache-2.0",
    "apache license, version 2.0": "Apache-2.0",
    "apache license version 2.0": "Apache-2.0",
    "the mit license": "MIT",
    "mit license": "MIT",
    "eclipse public license 2.0": "EPL-2.0",
    "eclipse public license - v 2.0": "EPL-2.0",
    "isc license": "ISC",
}
EXCEPTIONS = {"GPL-2.0-only WITH Classpath-exception-2.0",
              "GPL-2.0-or-later WITH Classpath-exception-2.0",
              "GPL-2.0-with-classpath-exception"}

# Tokenize the entire expression; any unrecognized byte is a syntax error.
# This is a strict subset of SPDX license-expression grammar (AND, OR,
# parentheses and the specifically reviewed WITH exceptions).
SPDX_TOKEN = re.compile(r"\s*([()]|[A-Za-z0-9][A-Za-z0-9.+-]*)")

def license_status(value):
    if not isinstance(value, str) or not value.strip():
        return False, "UNDECLARED"
    val = ALIASES.get(value.lower().strip(), value.strip())
    # Legacy reviewed spelling is retained only for this exact identifier.
    if val == "GPL-2.0-with-classpath-exception":
        return True, val

    tokens = []
    position = 0
    while position < len(val):
        match = SPDX_TOKEN.match(val, position)
        if match is None:
            if val[position:].strip():
                return False, val
            break
        tokens.append(match.group(1))
        position = match.end()
        if len(tokens) > 128:
            return False, val

    index = 0

    def atom(depth=0):
        nonlocal index
        if index >= len(tokens) or depth > 32:
            raise ValueError("expected SPDX license")
        token = tokens[index]
        index += 1
        if token == "(":
            accepted = parse_or(depth + 1)
            if index >= len(tokens) or tokens[index] != ")":
                raise ValueError("unbalanced parentheses")
            index += 1
            return accepted
        if token in {"AND", "OR", "WITH", ")"}:
            raise ValueError("invalid SPDX operand")
        if index < len(tokens) and tokens[index] == "WITH":
            index += 1
            if index >= len(tokens) or tokens[index] in {"AND", "OR", "WITH", "(", ")"}:
                raise ValueError("missing SPDX exception")
            exception = tokens[index]
            index += 1
            # Unsupported WITH exceptions are invalid at the expression
            # level, including when another OR branch is acceptable.
            if token + " WITH " + exception not in EXCEPTIONS:
                raise ValueError("unsupported SPDX WITH exception")
            return True
        return token in ALLOWED

    def parse_and(depth=0):
        nonlocal index
        accepted = atom(depth)
        while index < len(tokens) and tokens[index] == "AND":
            index += 1
            rhs = atom(depth)
            accepted = accepted and rhs
        return accepted

    def parse_or(depth=0):
        nonlocal index
        accepted = parse_and(depth)
        while index < len(tokens) and tokens[index] == "OR":
            index += 1
            rhs = parse_and(depth)
            accepted = accepted and rhs
        return accepted

    try:
        accepted = parse_or()
        if index != len(tokens):
            return False, val
        return accepted, val
    except (ValueError, RecursionError):
        return False, val

def read_bom(path, project):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("bomFormat") != "CycloneDX" or not data.get("specVersion"):
        raise ValueError(project + ": invalid CycloneDX format")
    components = data.get("components")
    if not isinstance(components, list) or not components:
        raise ValueError(project + ": missing components")
    rows = []
    for c in components:
        if c.get("type") not in {"library", "framework", "application", "file"}:
            continue
        if not c.get("name") or not c.get("version"):
            raise ValueError(project + ": missing name/version")
        identifiers = []
        for record in c.get("licenses") or []:
            if not isinstance(record, dict):
                continue
            if "expression" in record:
                identifiers.append(record["expression"])
            value = record.get("license") or {}
            if isinstance(value, dict):
                identifiers.append(value.get("id") or value.get("name") or "")
        result = [license_status(x) for x in (identifiers or [""])]
        declared = sorted(set(y for _, y in result))
        approved = all(ok for ok, _ in result)
        choice = ""
        # Logback 1.5.34 is dual-licensed; choose its EPL-2.0 option.
        # https://logback.qos.ch/license.html
        if c["name"] in {"logback-classic", "logback-core"} and c["version"] == "1.5.34" \
                and set(declared) == {"EPL-2.0", "LGPL-2.1-only"}:
            approved, choice = True, "EPL-2.0"
        # CI policy approval and rights/redistribution acceptance are
        # independent gates. Do not turn a reviewed SPDX ID into a release PASS.
        obligations = ["CHECK_UPSTREAM_LICENSE_NOTICE_AND_ATTRIBUTION",
                       "R24_VERIFY_RELEASE_PACKAGING"]
        if c["name"] in {"logback-core", "logback-classic"} and c["version"] == "1.5.34":
            obligations.append("EPL_LICENSE_NOTICE_SOURCE_REVIEW")
        if "BlueOak-1.0.0" in declared:
            obligations.append("BLUEOAK_LICENSE_TEXT_OR_LINK")
        if "MIT-0" in declared:
            obligations.append("MIT_0_LICENSE_TEXT")
        license_links = {
            "BlueOak-1.0.0": "https://spdx.org/licenses/BlueOak-1.0.0.html",
            "MIT-0": "https://spdx.org/licenses/MIT-0.html",
            "EPL-2.0": "https://www.eclipse.org/legal/epl-2.0/",
            "LGPL-2.1-only": "https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html",
        }
        rows.append({"project": project, "name": c["name"],
                     "version": c["version"], "purl": c.get("purl") or "",
                     "licenses": declared, "license_choice": choice,
                     "approved": approved,
                     "license_policy_status": "APPROVED" if approved else "REVIEW",
                     "release_distribution_status": "PENDING",
                     "release_distribution_owner": "R24 / Yến",
                     "release_distribution_requirements": obligations,
                     "license_reference_links": {lic: license_links[lic] for lic in declared
                                                 if lic in license_links}})
    if not rows:
        raise ValueError(project + ": no eligible components")
    return rows

REPO = "https://github.com/tricore-opentrix/opentrix/blob/main/"
SPDX_IDS = ALLOWED | {"LGPL-2.1-only", "GPL-2.0-with-classpath-exception", "PostgreSQL"}
SECTIONS = [("backend", "Backend (Java)"), ("portal-bff", "Portal BFF (Java)"),
            ("frontend", "Frontend (npm)")]
# Upstream images used unmodified by the local deployment and its image builds.
# test_r23_compliance.py checks that each reference still exists in its source file.
IMAGES = [
    ("apache/apisix:3.13.0-debian", "https://hub.docker.com/r/apache/apisix", "Apache-2.0",
     "API gateway (optional) / Cổng API (tùy chọn)", "infra/compose.gateway.yml"),
    ("postgres:17.11-alpine", "https://hub.docker.com/_/postgres", "PostgreSQL",
     "Database / Cơ sở dữ liệu", "infra/compose.demo.yml"),
    ("quay.io/keycloak/keycloak:26.8.0", "https://quay.io/repository/keycloak/keycloak",
     "Apache-2.0", "Identity provider / Quản lý định danh", "infra/compose.demo.yml"),
    ("caddy:2.10.2-alpine", "https://hub.docker.com/_/caddy", "Apache-2.0",
     "HTTPS ingress serving the Portal / Ingress HTTPS phục vụ Portal",
     "infra/demo/ingress.Dockerfile"),
    ("eclipse-temurin:21-jre", "https://hub.docker.com/_/eclipse-temurin",
     "GPL-2.0-with-classpath-exception",
     "Java runtime of the locally built backend and Portal BFF images / "
     "Môi trường chạy Java của image backend và Portal BFF build cục bộ",
     "infra/demo/backend.Dockerfile"),
    ("gradle:8.14.3-jdk21", "https://hub.docker.com/_/gradle", "Apache-2.0",
     "Build stage only; not in the final image / Chỉ dùng khi build, không có trong image cuối",
     "infra/demo/backend.Dockerfile"),
    ("node:22.20.0-alpine", "https://hub.docker.com/_/node", "MIT",
     "Build stage only; not in the final image / Chỉ dùng khi build, không có trong image cuối",
     "infra/demo/ingress.Dockerfile"),
]

def license_link(value):
    if value in SPDX_IDS:
        return f"[{value}](https://spdx.org/licenses/{value}.html)"
    return value or "UNDECLARED"

def package_link(row):
    purl = row["purl"]
    match = re.match(r"pkg:maven/([^/]+)/([^@]+)@([^?]+)", purl)
    if match:
        group, artifact, version = match.groups()
        return f"[{group}:{artifact}](https://central.sonatype.com/artifact/{group}/{artifact}/{version})"
    match = re.match(r"pkg:npm/(.+)@([^?]+)", purl)
    if match:
        name = match.group(1).replace("%40", "@")
        return f"[{name}](https://www.npmjs.com/package/{name}/v/{match.group(2)})"
    return row["name"]

def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")

def license_summary(rows, headers):
    counts = {}
    for r in rows:
        if r["project"] == "gateway":
            continue
        for lic in r["licenses"]:
            counts[lic] = counts.get(lic, 0) + 1
    lines = ["| " + " | ".join(headers) + " |", "| --- | --- |"]
    for lic in sorted(counts, key=lambda x: (-counts[x], x)):
        lines.append(f"| {license_link(lic)} | {counts[lic]} |")
    return lines

def render_notices(rows):
    total = len([r for r in rows if r["project"] != "gateway"])
    # REUSE-IgnoreStart
    out = ["<!--", "SPDX-FileCopyrightText: 2026 TRICORE contributors",
           "SPDX-License-Identifier: Apache-2.0", "-->", "",
           # REUSE-IgnoreEnd
           "# Third-Party Notices", "",
           "> **Language / Ngôn ngữ:** [English](#en) · [Tiếng Việt](#vi)", "",
           f"Generated by [`scripts/r23-compliance.py`]({REPO}scripts/r23-compliance.py) from the "
           "CycloneDX SBOMs of the backend, Portal BFF and frontend. Do not edit by hand.", "",
           "---", "", '<a id="en"></a>', "", "## Overview", "",
           f"OpenTrix is licensed under the Apache License 2.0 ([LICENSE]({REPO}LICENSE), "
           f"[NOTICE]({REPO}NOTICE)). This file lists the {total} third-party packages that "
           "OpenTrix uses at runtime and the upstream container images used by the local "
           "deployment, with their declared licenses.", "",
           "- Java packages are the runtime dependencies of the backend and the Portal BFF.",
           "- npm packages are the runtime dependencies of the frontend; development-only "
           "packages are not included.",
           "- Container images are used as published upstream and are not modified.", "",
           "This file is an inventory. It is not a legal certification and does not replace "
           "the license and NOTICE texts published by each upstream project.", "",
           "Where a package is offered under more than one license, the Elected column "
           "shows the license under which OpenTrix uses it.", "",
           "## License summary", "",
           "A package that declares more than one license is counted under each license.", ""]
    out += license_summary(rows, ["License", "Packages"])
    out += ["", "## Scope and limitations", "",
            "- Operating-system packages and other contents of container images are not "
            "listed and require a separate review before distribution.",
            "- Before each release, upstream notice texts, bundled services, copyright "
            f"provenance and release packaging are reviewed as described in [docs/RELEASE.md]({REPO}docs/RELEASE.md).",
            "", "---", "", '<a id="vi"></a>', "", "## Tổng quan", "",
            f"OpenTrix được cấp phép theo Apache License 2.0 ([LICENSE]({REPO}LICENSE), "
            f"[NOTICE]({REPO}NOTICE)). Tệp này liệt kê {total} gói bên thứ ba mà OpenTrix "
            "sử dụng khi chạy và các image container gốc dùng cho triển khai cục bộ, kèm "
            "giấy phép được khai báo.", "",
            "- Gói Java là phụ thuộc lúc chạy của backend và Portal BFF.",
            "- Gói npm là phụ thuộc lúc chạy của frontend; không gồm các gói chỉ dùng khi phát triển.",
            "- Image container được dùng nguyên bản như upstream phát hành, không chỉnh sửa.", "",
            "Tệp này là bản kiểm kê, không phải xác nhận pháp lý và không thay thế văn bản "
            "giấy phép, NOTICE do từng dự án upstream công bố.", "",
            "Khi một gói được cung cấp theo nhiều giấy phép, cột Giấy phép áp dụng ghi giấy "
            "phép mà OpenTrix sử dụng.", "",
            "## Tóm tắt giấy phép", "",
            "Gói khai báo nhiều giấy phép được tính ở từng giấy phép.", ""]
    out += license_summary(rows, ["Giấy phép", "Số gói"])
    out += ["", "## Phạm vi và giới hạn", "",
            "- Gói hệ điều hành và các nội dung khác bên trong image container không được "
            "liệt kê và cần rà soát riêng trước khi phân phối.",
            "- Trước mỗi bản phát hành, văn bản notice của upstream, dịch vụ đi kèm, nguồn gốc "
            f"bản quyền và gói phát hành được rà soát theo [docs/RELEASE.md]({REPO}docs/RELEASE.md).",
            "", "---", "", "## Component inventory / Danh mục thành phần", "",
            "Each package links to its page on Maven Central or npm; each license links to "
            "its SPDX page. / Mỗi gói liên kết tới trang trên Maven Central hoặc npm; mỗi "
            "giấy phép liên kết tới trang SPDX.", ""]
    known = {key for key, _ in SECTIONS} | {"gateway"}
    sections = SECTIONS + [(p, p) for p in sorted({r["project"] for r in rows} - known)]
    for key, title in sections:
        items = [r for r in rows if r["project"] == key]
        if not items:
            continue
        out += [f"### {title}", "",
                "| Package / Gói | Version / Phiên bản | Declared licenses / Giấy phép khai báo "
                "| Elected / Giấy phép áp dụng |", "| --- | --- | --- | --- |"]
        for r in items:
            declared = ", ".join(license_link(x) for x in r["licenses"])
            elected = license_link(r["license_choice"]) if r["license_choice"] else "—"
            out.append(f"| {cell(package_link(r))} | {cell(r['version'])} | {declared} | {elected} |")
        out.append("")
    gateway = {r["version"] for r in rows if r["project"] == "gateway"}
    out += ["### Container images / Image container", "",
            "| Image | License / Giấy phép | Use / Mục đích |", "| --- | --- | --- |"]
    for image, url, lic, use, _source in IMAGES:
        if image.startswith("apache/apisix:") and image.split(":", 1)[1] not in gateway:
            continue
        out.append(f"| [`{image}`]({url}) | {license_link(lic)} | {use} |")
    out.append("")
    return "\n".join(out)

def audit(paths, destination):
    rows = read_bom(Path(__file__).resolve().parent.parent / "infra/apisix/bom.json", "gateway")
    for project, path in paths:
        rows += read_bom(path, project)
    rows.sort(key=lambda r: (r["project"], r["name"].lower(), r["version"], r["purl"]))
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "license-inventory.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (destination / "THIRD-PARTY-NOTICES.md").write_text(
        render_notices(rows), encoding="utf-8")
    bad = [r for r in rows if not r["approved"]]
    print(f"R23: {len(rows)} components, {len(bad)} unapproved or unknown license declarations")
    print(f"R23 release distribution: {sum(r['release_distribution_status'] == 'PENDING' for r in rows)} PENDING; independent R24 sign-off required")
    for r in bad:
        print("R23 REVIEW:", r["project"], r["name"], r["version"], r["licenses"], file=sys.stderr)
    return not bad

def main():
    p = argparse.ArgumentParser()
    for name in ("backend", "portal-bff", "frontend"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    try:
        ok = audit([("backend", a.backend), ("portal-bff", a.portal_bff),
                    ("frontend", a.frontend)], a.output)
        return 0 if ok else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("R23 failed:", exc, file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
