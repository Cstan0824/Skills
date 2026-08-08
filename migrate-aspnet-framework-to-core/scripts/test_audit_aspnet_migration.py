#!/usr/bin/env python3
"""Unit tests for audit_aspnet_migration.py."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("audit_aspnet_migration.py")
SPEC = importlib.util.spec_from_file_location("audit_aspnet_migration", SCRIPT)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class AuditTests(unittest.TestCase):
    def make_legacy(self, root: Path) -> None:
        write(
            root,
            "SICM/SICM.csproj",
            '''<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup><TargetFrameworkVersion>v4.7.2</TargetFrameworkVersion><ProjectTypeGuids>legacy</ProjectTypeGuids></PropertyGroup>
</Project>''',
        )
        write(root, "SICM/packages.config", "<packages />")
        write(root, "SICM/Global.asax", "<%@ Application Language=\"C#\" %>")
        write(root, "SICM/Web.config", "<configuration><appSettings /></configuration>")
        write(
            root,
            "SICM/Controllers/HomeController.cs",
            "using System.Web;\nvar x = HttpContext.Current;\nHttpPostedFileBase file = null;\n",
        )
        write(
            root,
            "SICM/Reports/Report.cs",
            "using CrystalDecisions.CrystalReports.Engine;\nusing MySql.Data.MySqlClient;\n",
        )
        write(root, "SICM/Import.cs", "using System.Data.OleDb;\nvar value = ConfigurationManager.AppSettings[\"x\"];\n")

    def make_target(self, root: Path) -> None:
        write(
            root,
            "G2G/G2G.csproj",
            '<Project Sdk="Microsoft.NET.Sdk.Web"><PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>',
        )
        write(
            root,
            "G2G/Program.cs",
            "var builder = WebApplication.CreateBuilder(args);\nbuilder.Services.AddControllersWithViews();\nbuilder.Services.AddScoped<IThing, Thing>();\nvar app = builder.Build();\napp.MapControllerRoute(name: \"default\", pattern: \"{controller=Home}/{action=Index}\");\napp.Run();\n",
        )
        write(root, "G2G/Services/Import.cs", "using MySqlConnector;\nusing ExcelDataReader;\nusing ClosedXML.Excel;\nusing Microsoft.Playwright;\npublic sealed class Upload { public IFormFile File { get; set; } }\n")
        write(root, "G2G.Tests/G2G.Tests.csproj", '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup><ItemGroup><PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" /></ItemGroup></Project>')
        write(root, "G2G.Tests/SmokeTests.cs", "using Microsoft.AspNetCore.Mvc.Testing;\nWebApplicationFactory<Program> factory = null!;\n")

    def test_legacy_evidence_and_legacy_only_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_legacy(root)
            report = AUDIT.build_report(root)
            self.assertEqual(report["status"], "pass")
            self.assertGreater(report["legacy"]["legacy"]["system_web"]["count"], 0)
            self.assertGreater(report["legacy"]["legacy"]["classic_project"]["count"], 0)
            self.assertEqual(report["blockers"], [])

    def test_modern_target_has_no_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "legacy"
            target = root / "target"
            self.make_legacy(legacy)
            self.make_target(target)
            report = AUDIT.build_report(legacy, target)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["blockers"], [])
            self.assertGreater(report["target"]["modern"]["mysql_connector"]["count"], 0)
            self.assertGreater(report["target"]["modern"]["integration_tests"]["count"], 0)

    def test_each_target_blocker_is_reported(self) -> None:
        for filename, content, code in (
            ("SystemWeb.cs", "using System.Web;", "target-system_web"),
            ("Current.cs", "var x = HttpContext.Current;", "target-http_context_current"),
            ("Upload.cs", "HttpPostedFileBase file = null;", "target-http_posted_file"),
            ("Config.cs", "ConfigurationManager.AppSettings[\"x\"];", "target-configuration_manager"),
            ("Ole.cs", "using System.Data.OleDb;", "target-ole_db"),
            ("Report.cs", "CrystalDecisions.CrystalReports.Engine;", "target-crystal_reports"),
            ("Db.cs", "MySql.Data.MySqlClient;", "target-mysql_data"),
        ):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                legacy = root / "legacy"
                target = root / "target"
                self.make_legacy(legacy)
                self.make_target(target)
                write(target, f"G2G/{filename}", content)
                report = AUDIT.build_report(legacy, target)
                self.assertIn(code, {blocker["code"] for blocker in report["blockers"]})

    def test_ignored_directories_do_not_create_false_positives(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_legacy(root / "legacy")
            target = root / "target"
            self.make_target(target)
            write(target, "obj/Generated.cs", "using System.Web; HttpContext.Current;")
            write(target, "bin/Generated.cs", "CrystalDecisions.ReportSource;")
            report = AUDIT.build_report(root / "legacy", target)
            self.assertEqual(report["blockers"], [])

    def test_static_http_context_accessor_is_warning(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "legacy"
            target = root / "target"
            self.make_legacy(legacy)
            self.make_target(target)
            write(target, "G2G/Globalproperties.cs", "public static IHttpContextAccessor HttpContextAccessor;")
            report = AUDIT.build_report(legacy, target)
            self.assertEqual(report["blockers"], [])
            self.assertIn("static-http-context-accessor", {warning["code"] for warning in report["warnings"]})

    def test_missing_modern_host_is_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "legacy"
            target = root / "target"
            self.make_legacy(legacy)
            write(target, "G2G/G2G.csproj", '<Project Sdk="Microsoft.NET.Sdk.Web"><PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>')
            write(target, "G2G/Startup.cs", "public sealed class Startup { }")
            report = AUDIT.build_report(legacy, target)
            self.assertIn("target-missing-modern-host", {blocker["code"] for blocker in report["blockers"]})

    def test_json_is_serializable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_legacy(root / "legacy")
            self.make_target(root / "target")
            report = AUDIT.build_report(root / "legacy", root / "target")
            encoded = json.dumps(report, sort_keys=True)
            self.assertIn('"status": "pass"', encoded)


if __name__ == "__main__":
    unittest.main()
