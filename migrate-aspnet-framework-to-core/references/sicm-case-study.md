# SICM-to-G2G case study

This is evidence for the workflow, not a template that requires a future application to copy names or structure.

## Source inventory

The source tree `sicm-web-portal-master` contains a classic solution and ten project files. The web project targets `.NET Framework 4.7.2` and uses classic project XML, `packages.config`, `Global.asax`, `web.config`, MVC 5/System.Web references, EF6, legacy MySQL provider references, Crystal Reports generated classes, and Windows-oriented Excel/reporting dependencies. Source scans find `System.Web`, `HttpContext.Current`/legacy MVC helpers, `HttpPostedFileBase`-style upload boundaries, OLE DB/provider strings, `CrystalDecisions`, and `MySql.Data`.

The source application is organized into security (`SEC`), user management (`USER`), imports (`INFO`), production/reporting (`PRODUCTION`), shared helpers, data, processing, repository, and encryption projects. Preserve those feature boundaries while changing framework boundaries.

## Production evidence

The production tree is renamed `SICM_Production` at the repository level and `G2G` in the application namespaces/projects. It currently contains SDK-style projects targeting `net8.0`, a `Microsoft.NET.Sdk.Web` MVC web project, `Program.cs`, `appsettings.json`/example configuration, DI registration, cookie authentication, authorization policy, session, forwarded headers, health checks, structured logging, and explicit area/default routes.

The data/import/reporting replacements include:

- EF Core with Pomelo and `MySqlConnector`;
- `ExcelDataReader` for spreadsheet parsing;
- `ClosedXML` for workbook output/manipulation;
- `Microsoft.Playwright` for Chromium rendering;
- xUnit, Moq, `Microsoft.AspNetCore.Mvc.Testing`, and `WebApplicationFactory<Program>`-style tests.

The target scan is expected to have no source residue for `System.Web`, `HttpContext.Current`, `HttpPostedFileBase`, `ConfigurationManager.AppSettings`, OLE DB/Jet/ACE, CrystalDecisions, or `MySql.Data.MySqlClient` after generated/build/vendor folders are excluded.

## Proven migration decisions

### Host and MVC

`Program.cs` registers MVC, antiforgery, health checks, HTTP context access, session, authentication/authorization, the database, feature services, background workers, and endpoint routes. The application keeps MVC/areas because server-rendered controllers and views remain the primary UI model.

Legacy child-action composition was replaced with Core view components/partials where the feature needed a service-backed render boundary. Legacy bundle references were replaced with explicit static URL/asset partials under `wwwroot`.

### Data and imports

The target uses a MySQL connection string builder, provider retry/timeout settings, and an EF Core scoped context. Joined SQL projections are written explicitly with aliases to avoid duplicate column materialization. Spreadsheet imports validate files and parse them with ExcelDataReader instead of OLE DB.

### Reporting

The production `IReportService` renders HTML templates/data and invokes headless Chromium through Playwright to produce PDFs. Native report-engine PDF output is intentionally not the default for this case study because layout consistency across supported environments was the failure mode being addressed. Test the renderer with installed browser binaries, representative fonts/images, and realistic data.

### Transitional debt

The target still initializes a static `Globalproperties.HttpContextAccessor` for legacy callers. This is a compatibility bridge, not a recommended Core pattern. Track it as a warning and migrate consumers to constructor injection or explicit request-context parameters.

## Parity cautions

- SICM was renamed to G2G; compare routes, areas, permissions, behavior, and outputs rather than namespaces/file names.
- Existing project documentation may describe an earlier snapshot or a different target framework. Verify claims against current source/project files.
- A clean build does not prove database connectivity, browser rendering, auth/session behavior, or UI parity.
- The production tree may contain user changes. Preserve them and report build/test failures with their provenance.
