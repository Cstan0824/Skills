---
name: migrate-aspnet-framework-to-core
description: Plan, execute, review, and verify migrations from legacy ASP.NET MVC 5 or other ASP.NET Framework applications to ASP.NET Core on modern .NET. Use when a repository contains System.Web, Global.asax, web.config, classic .csproj files, packages.config, EF6, OLE DB, Crystal Reports, HttpPostedFileBase, HttpContext.Current, or similar Windows-bound dependencies that must move to SDK-style projects, Program.cs, DI, endpoint routing, Core MVC, cross-platform data/import/reporting libraries, and tested production behavior.
---

# Migrate ASP.NET Framework to Core

Use this skill to turn a legacy ASP.NET application into a buildable, testable, cross-platform ASP.NET Core application without confusing compilation with behavioral parity.

## Operating rules

- Inspect repository instructions and preserve unrelated user changes before editing.
- Inventory source and target trees before proposing replacements. Run `scripts/audit_aspnet_migration.py` and keep its output with the migration record.
- Treat the existing application as the behavioral specification: routes, permissions, validation, file formats, SQL results, reports, and browser flows matter more than filename or namespace equality.
- Keep the target framework pinned to the repository/user constraint. Prefer the latest stable .NET only for new work; do not silently retarget an existing migration.
- Migrate in buildable vertical slices. After each slice, compile, run focused tests, and record unresolved warnings or compatibility shims.
- Prefer constructor injection, options, explicit async boundaries, endpoint routing, strongly typed view models, and services that own business/data rules.
- Do not use static service locators, `HttpContext.Current`, committed secrets, or native Windows-only dependencies as the target architecture.
- Treat static compatibility wiring (for example a globally assigned `IHttpContextAccessor`) as migration debt and schedule its removal.
- Never claim feature parity from file counts or a successful build. Label each feature `pass`, `intentional change`, `deferred`, or `blocked` with evidence.
- Do not delete the legacy application, alter production traffic, or change a database schema without explicit authorization.

## Workflow

### 1. Establish the baseline

Identify the solution entry point, web project, project graph, target frameworks, package management, deployment topology, database provider, authentication/session model, uploads/imports, reports, and test projects. Search source/config/views—not generated `bin`, `obj`, `packages`, or output directories—for legacy indicators.

Read [migration-workflow.md](references/migration-workflow.md) for phase boundaries and stop conditions. Read [sicm-case-study.md](references/sicm-case-study.md) only when the repository resembles the SICM-to-G2G migration or uses its reporting/import/database patterns.

### 2. Choose the target shape

Keep MVC when controllers, areas, action filters, and server-rendered views are central. Establish an SDK-style web project, one authoritative target framework, `Program.cs`, `AddControllersWithViews()`, explicit area/default routes, `wwwroot`, and a test-visible `Program` type. Use [replacement-matrix.md](references/replacement-matrix.md) to choose a replacement deliberately; do not perform global search-and-replace.

### 3. Migrate host and configuration

Move `Global.asax`/`App_Start` responsibilities into service registration and ordered middleware. Move `web.config` settings into `appsettings*.json`, environment variables, options validation, and a secret store. Configure forwarded headers before redirects/auth when behind a proxy; keep exception handling, static files, routing, authentication, authorization, session, and endpoint mapping in a deliberate order.

### 4. Migrate one feature slice at a time

For each bounded feature (SEC, USER, INFO, PRODUCTION, or the target’s equivalent):

1. Map legacy routes/actions/views and write characterization tests.
2. Port models into Core-compatible view models and validation.
3. Port controllers to `Microsoft.AspNetCore.Mvc.Controller`, Core model binding, `IFormFile`, antiforgery, and explicit results.
4. Move business/data work behind injected services; keep controllers orchestration-only.
5. Replace child actions with view components, partials, or service-backed composition.
6. Move assets to `wwwroot` and replace MVC bundling with an explicit static-asset strategy.
7. Verify authentication, authorization, session, redirects, SQL projections, uploads, and error behavior before starting the next slice.

For EF6 or provider migrations, preserve transaction and query semantics, review joined projections for duplicate column names, and use provider-specific retry/timeouts intentionally. Prefer `MySqlConnector` plus an EF Core provider or a deliberate parameterized SQL boundary over carrying `MySql.Data` forward.

For Excel, replace OLE DB/LinqToExcel with `ExcelDataReader` for reading and `ClosedXML` (or another justified cross-platform library) for workbook output. Validate extension, size, content, encoding, and storage location; do not trust browser MIME types.

For Crystal Reports, abstract reporting behind an `IReportService`. When consistent cross-platform layout is required, render HTML/templates and print through headless Chromium (Playwright or an approved equivalent); verify browser installation and PDF bytes/layout in tests and deployment.

### 5. Verify progressively

Run the smallest relevant gate after every change, then the full matrix before handoff. Use [validation-gates.md](references/validation-gates.md) to distinguish static, build, unit, integration, browser, database, report, security, and deployment evidence. Report pre-existing failures separately from regressions.

At minimum, verify:

- `dotnet restore`, `dotnet build`, and `dotnet test` for the actual solution;
- `WebApplicationFactory<Program>`/HTTP tests for DI, routes, auth status/redirect behavior, antiforgery, uploads, and health endpoints;
- representative MySQL queries and migrations with explicit aliases and realistic null/zero-date data;
- browser flows for login, navigation, forms, area routes, assets, imports, and reports;
- publish/deployment behavior, proxy headers, secrets, private storage, and Chromium availability.

## Audit tool

Run from any shell:

```text
python scripts/audit_aspnet_migration.py --legacy <legacy-root> --target <target-root>
```

Use `--format json` for automation and `--fail-on none` when auditing only the legacy tree. The target audit fails on remaining `System.Web`, `HttpContext.Current`, `HttpPostedFileBase`, `ConfigurationManager.AppSettings`, OLE DB/Jet/ACE, CrystalDecisions, `MySql.Data`, classic project markers, or a web target without modern host evidence. Transitional patterns such as static `IHttpContextAccessor` storage and synchronous `.Result`/`.GetAwaiter().GetResult()` are warnings.

## References

- [migration-workflow.md](references/migration-workflow.md): phase sequencing, decisions, and stop conditions.
- [replacement-matrix.md](references/replacement-matrix.md): legacy-to-Core mappings and pitfalls.
- [sicm-case-study.md](references/sicm-case-study.md): source/production evidence from SICM-to-G2G.
- [validation-gates.md](references/validation-gates.md): evidence required before calling a migration ready.
