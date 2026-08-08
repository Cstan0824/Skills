#!/usr/bin/env python3
"""Audit legacy ASP.NET Framework and ASP.NET Core migration trees.

The tool intentionally uses only the Python standard library. It reports
legacy evidence for a source tree and actionable blockers/warnings for a
target tree; it does not attempt to prove runtime parity.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable


IGNORED_DIRS = {
    ".git",
    ".vs",
    ".venv",
    "bin",
    "obj",
    "packages",
    "node_modules",
    "artifacts",
    "output",
    "outputs",
    "dist",
}

SCANNED_SUFFIXES = {
    ".asax",
    ".config",
    ".cs",
    ".cshtml",
    ".csproj",
    ".json",
    ".props",
    ".targets",
    ".vb",
    ".xaml",
}

MAX_SAMPLES_PER_SIGNAL = 40

LEGACY_PATTERNS = {
    "system_web": re.compile(r"System\.Web", re.IGNORECASE),
    "http_context_current": re.compile(r"HttpContext\s*\.\s*Current", re.IGNORECASE),
    "http_posted_file": re.compile(r"HttpPostedFileBase", re.IGNORECASE),
    "configuration_manager": re.compile(
        r"ConfigurationManager\s*\.\s*(?:AppSettings|ConnectionStrings)", re.IGNORECASE
    ),
    "ole_db": re.compile(r"System\.Data\.OleDb|Microsoft\.(?:Jet|ACE)\.OLEDB", re.IGNORECASE),
    "crystal_reports": re.compile(r"CrystalDecisions", re.IGNORECASE),
    "mysql_data": re.compile(r"MySql\.Data(?:\.MySqlClient)?", re.IGNORECASE),
    "classic_project": re.compile(
        r"<TargetFrameworkVersion\b|<ProjectTypeGuids\b|packages\.config", re.IGNORECASE
    ),
    "html_action": re.compile(r"Html\s*\.\s*Action\s*\(", re.IGNORECASE),
    "bundle_helpers": re.compile(r"(?:Scripts|Styles)\s*\.\s*Render\s*\(", re.IGNORECASE),
}

MODERN_PATTERNS = {
    "sdk_style": re.compile(r"<Project\b[^>]*\bSdk\s*=", re.IGNORECASE),
    "web_sdk": re.compile(r"<Project\b[^>]*Microsoft\.NET\.Sdk\.Web", re.IGNORECASE),
    "modern_target_framework": re.compile(r"<TargetFramework(?:s)?\s*>\s*net\d", re.IGNORECASE),
    "program_host": re.compile(
        r"WebApplication\s*\.\s*CreateBuilder|WebApplicationBuilder", re.IGNORECASE
    ),
    "mvc_registration": re.compile(r"AddControllersWithViews\s*\(", re.IGNORECASE),
    "route_mapping": re.compile(r"MapControllerRoute\s*\(", re.IGNORECASE),
    "di_registration": re.compile(r"Add(?:Singleton|Scoped|Transient)\s*<", re.IGNORECASE),
    "http_context_accessor": re.compile(r"IHttpContextAccessor", re.IGNORECASE),
    "iform_file": re.compile(r"\bIFormFile\b", re.IGNORECASE),
    "mysql_connector": re.compile(r"MySqlConnector", re.IGNORECASE),
    "ef_core": re.compile(r"Microsoft\.EntityFrameworkCore|UseMySql\s*\(", re.IGNORECASE),
    "excel_reader": re.compile(r"ExcelDataReader", re.IGNORECASE),
    "closed_xml": re.compile(r"ClosedXML", re.IGNORECASE),
    "playwright": re.compile(r"Microsoft\.Playwright|\bPlaywright\b", re.IGNORECASE),
    "health_checks": re.compile(r"AddHealthChecks\s*\(|MapHealthChecks\s*\(", re.IGNORECASE),
    "integration_tests": re.compile(
        r"WebApplicationFactory|Microsoft\.AspNetCore\.Mvc\.Testing", re.IGNORECASE
    ),
}

TARGET_BLOCKING_SIGNALS = {
    "system_web",
    "http_context_current",
    "http_posted_file",
    "configuration_manager",
    "ole_db",
    "crystal_reports",
    "mysql_data",
    "classic_project",
}


def _empty_signal_map(patterns: dict[str, re.Pattern[str]]) -> dict[str, dict[str, Any]]:
    return {name: {"count": 0, "samples": []} for name in patterns}


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_files(root: Path) -> Iterable[Path]:
    """Yield relevant files while excluding generated/vendor directories."""

    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SCANNED_SUFFIXES:
            continue
        if any(part.lower() in IGNORED_DIRS for part in path.relative_to(root).parts[:-1]):
            continue
        yield path


def _record(signal_map: dict[str, dict[str, Any]], name: str, path: str, line: int, text: str) -> None:
    entry = signal_map[name]
    entry["count"] += 1
    if len(entry["samples"]) < MAX_SAMPLES_PER_SIGNAL:
        entry["samples"].append({"path": path, "line": line, "text": text.strip()[:240]})


def _parse_project(path: Path, root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": _relative(path, root),
        "sdk": None,
        "sdk_style": False,
        "web_sdk": False,
        "classic": False,
        "target_frameworks": [],
        "package_references": [],
    }
    try:
        document = ET.parse(path)
    except (ET.ParseError, OSError):
        result["parse_error"] = True
        return result

    project = document.getroot()
    sdk = project.attrib.get("Sdk")
    result["sdk"] = sdk
    result["sdk_style"] = bool(sdk)
    result["web_sdk"] = bool(sdk and sdk.lower() == "microsoft.net.sdk.web")

    for element in project.iter():
        name = element.tag.rsplit("}", 1)[-1]
        if name in {"TargetFramework", "TargetFrameworks", "TargetFrameworkVersion"}:
            value = (element.text or "").strip()
            if value:
                result["target_frameworks"].extend(
                    part.strip() for part in value.split(";") if part.strip()
                )
            if name == "TargetFrameworkVersion":
                result["classic"] = True
        elif name == "ProjectTypeGuids":
            result["classic"] = True
        elif name == "PackageReference":
            include = element.attrib.get("Include")
            version = element.attrib.get("Version")
            if include:
                result["package_references"].append(
                    {"include": include, "version": version}
                )

    if (path.parent / "packages.config").is_file():
        result["classic"] = True
    return result


def audit_tree(root: str | Path) -> dict[str, Any]:
    """Return a JSON-serializable inventory for one repository tree."""

    root_path = Path(root).resolve()
    legacy = _empty_signal_map(LEGACY_PATTERNS)
    modern = _empty_signal_map(MODERN_PATTERNS)
    files = list(iter_files(root_path))
    projects: list[dict[str, Any]] = []

    for path in files:
        relative = _relative(path, root_path)
        lower_name = path.name.lower()
        if lower_name == "global.asax" or lower_name.startswith("global.asax."):
            _record(legacy, "classic_project", relative, 1, path.name)
        if lower_name == "web.config" or lower_name.startswith("web.config."):
            _record(legacy, "classic_project", relative, 1, path.name)

        if path.suffix.lower() == ".csproj":
            projects.append(_parse_project(path, root_path))

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line_number, line in enumerate(content.splitlines(), start=1):
            for name, pattern in LEGACY_PATTERNS.items():
                if pattern.search(line):
                    _record(legacy, name, relative, line_number, line)
            for name, pattern in MODERN_PATTERNS.items():
                if pattern.search(line):
                    _record(modern, name, relative, line_number, line)

    # Project parsing is more reliable than a text scan for SDK/framework shape.
    for project in projects:
        if project["sdk_style"]:
            _record(modern, "sdk_style", project["path"], 1, f"SDK: {project['sdk']}")
        if project["web_sdk"]:
            _record(modern, "web_sdk", project["path"], 1, f"SDK: {project['sdk']}")
        if any(framework.lower().startswith("net") and not framework.lower().startswith("net4")
               for framework in project["target_frameworks"]):
            _record(
                modern,
                "modern_target_framework",
                project["path"],
                1,
                ";".join(project["target_frameworks"]),
            )
        if project["classic"]:
            _record(legacy, "classic_project", project["path"], 1, "classic project metadata")

    return {
        "root": str(root_path),
        "files_scanned": len(files),
        "projects": projects,
        "legacy": legacy,
        "modern": modern,
    }


def _samples(inventory: dict[str, Any], category: str, limit: int = 4) -> list[dict[str, Any]]:
    return inventory["legacy"].get(category, {}).get("samples", [])[:limit]


def build_report(legacy_root: str | Path, target_root: str | Path | None = None) -> dict[str, Any]:
    legacy = audit_tree(legacy_root)
    target = audit_tree(target_root) if target_root else None
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if target:
        for signal in sorted(TARGET_BLOCKING_SIGNALS):
            count = target["legacy"][signal]["count"]
            if count:
                blockers.append(
                    {
                        "code": f"target-{signal}",
                        "message": f"Target contains {count} {signal.replace('_', ' ')} indicator(s).",
                        "samples": _samples(target, signal),
                    }
                )

        web_target = any(project["web_sdk"] for project in target["projects"])
        if web_target and target["modern"]["program_host"]["count"] == 0:
            blockers.append(
                {
                    "code": "target-missing-modern-host",
                    "message": "Target has an SDK-style web project but no WebApplication.CreateBuilder/WebApplicationBuilder evidence.",
                    "samples": [],
                }
            )

        static_accessor_samples: list[dict[str, Any]] = []
        for path in iter_files(Path(target_root)):
            relative = _relative(path, Path(target_root).resolve())
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for line_number, line in enumerate(content.splitlines(), start=1):
                if "IHttpContextAccessor" in line and re.search(r"\bstatic\b", line):
                    static_accessor_samples.append(
                        {"path": relative, "line": line_number, "text": line.strip()[:240]}
                    )
        if static_accessor_samples:
            warnings.append(
                {
                    "code": "static-http-context-accessor",
                    "message": "Target stores IHttpContextAccessor statically; migrate consumers to constructor injection or explicit request data.",
                    "samples": static_accessor_samples[:4],
                }
            )

        blocking_calls: list[dict[str, Any]] = []
        for path in iter_files(Path(target_root)):
            if path.suffix.lower() != ".cs":
                continue
            relative = _relative(path, Path(target_root).resolve())
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for line_number, line in enumerate(content.splitlines(), start=1):
                if re.search(r"\.GetAwaiter\(\)\.GetResult\(\)|\.Wait\(\)", line):
                    blocking_calls.append({"path": relative, "line": line_number, "text": line.strip()[:240]})
        if blocking_calls:
            warnings.append(
                {
                    "code": "synchronous-blocking-call",
                    "message": "Target contains synchronous task blocking; review request and browser/data hot paths.",
                    "samples": blocking_calls[:4],
                    "count": len(blocking_calls),
                }
            )

        if web_target and target["modern"]["integration_tests"]["count"] == 0:
            warnings.append(
                {
                    "code": "missing-integration-test-evidence",
                    "message": "Target web project has no WebApplicationFactory/Mvc.Testing evidence; add request-pipeline tests.",
                    "samples": [],
                }
            )

    return {
        "legacy": legacy,
        "target": target,
        "blockers": blockers,
        "warnings": warnings,
        "status": "blocked" if blockers else "pass",
    }


def _format_signal_section(title: str, signal_map: dict[str, dict[str, Any]]) -> list[str]:
    lines = [title]
    nonzero = [(name, data["count"]) for name, data in signal_map.items() if data["count"]]
    if not nonzero:
        return lines + ["  none"]
    for name, count in sorted(nonzero):
        lines.append(f"  {name}: {count}")
    return lines


def format_text(report: dict[str, Any]) -> str:
    legacy = report["legacy"]
    lines = [
        f"ASP.NET migration audit: {legacy['root']}",
        f"Files scanned: {legacy['files_scanned']}",
        f"Projects: {len(legacy['projects'])}",
        "",
    ]
    lines.extend(_format_signal_section("Legacy indicators", legacy["legacy"]))
    lines.append("")
    lines.extend(_format_signal_section("Modern indicators", legacy["modern"]))
    if report["target"]:
        target = report["target"]
        lines.extend(["", f"Target: {target['root']}", f"Target files scanned: {target['files_scanned']}"])
        lines.extend(_format_signal_section("Target legacy residue", target["legacy"]))
        lines.extend(_format_signal_section("Target modern indicators", target["modern"]))
    lines.extend(["", f"Status: {report['status'].upper()}"])
    if report["blockers"]:
        lines.append("Blockers:")
        for blocker in report["blockers"]:
            lines.append(f"  [{blocker['code']}] {blocker['message']}")
            for sample in blocker.get("samples", [])[:2]:
                lines.append(f"    {sample['path']}:{sample['line']}: {sample['text']}")
    if report["warnings"]:
        lines.append("Warnings:")
        for warning in report["warnings"]:
            lines.append(f"  [{warning['code']}] {warning['message']}")
            for sample in warning.get("samples", [])[:2]:
                lines.append(f"    {sample['path']}:{sample['line']}: {sample['text']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy", required=True, help="legacy/source repository root")
    parser.add_argument("--target", help="migrated/target repository root")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--fail-on",
        choices=("target-blockers", "none"),
        default="target-blockers",
        help="return nonzero on target blockers (default) or always return zero",
    )
    args = parser.parse_args(argv)
    try:
        report = build_report(args.legacy, args.target)
    except (OSError, ValueError) as error:
        parser.error(str(error))
        return 2

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_text(report))
    return 1 if args.fail_on == "target-blockers" and report["blockers"] else 0


if __name__ == "__main__":
    sys.exit(main())
