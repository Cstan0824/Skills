# Compatibility remediation guidelines

Use these as decision points, not mechanical substitutions.

| Legacy pattern | ASP.NET Core direction | Verify explicitly |
| --- | --- | --- |
| `Global.asax`, `Application_Start`, `App_Start` | `WebApplication.CreateBuilder`, service registration, middleware, endpoint mapping | middleware order, startup failures, route names |
| `web.config` app settings/connection strings | `appsettings*.json`, environment variables, options, secret store | environment overrides, missing/invalid values, secret leakage |
| Classic `.csproj`, `packages.config`, assembly references | SDK-style projects and `PackageReference` | target framework, transitive dependencies, publish output |
| `System.Web.Mvc.Controller` | `Microsoft.AspNetCore.Mvc.Controller` | action results, filters, model binding, validation |
| `RouteConfig`, `AreaRegistration` | `MapControllerRoute` and endpoint routing | route order, areas, generated links, constraints |
| `HttpContext.Current` | injected `IHttpContextAccessor`, or pass required request data explicitly | nullability, testability, background-thread misuse |
| `HttpPostedFileBase` / `Request.Files` | `IFormFile` / bound file collections | size, extension/content validation, antiforgery, private storage |
| `Html.Action` child actions | view components, partials, or service-backed composition | authorization, model state, async behavior, render performance |
| `Scripts.Render` / `Styles.Render` | `wwwroot`, tag helpers, explicit bundling/minification | asset paths, cache busting, CSP, missing area assets |
| `System.Web.Helpers` / MVC helpers | Core tag helpers, view helpers, view components, standard HTML | encoding, null behavior, generated markup |
| `FormsAuthentication` / session-only identity | cookie authentication, Identity, claims, policies, session only where needed | redirects vs 401/403, expiry, role/claim mapping, CSRF |
| EF6 `DbContext` / `ObjectContext` | EF Core scoped `DbContext` or an intentional SQL/repository boundary | provider support, tracking, transactions, query translation |
| `MySql.Data` | `MySqlConnector` and a compatible EF Core provider, or parameterized SQL | async APIs, zero dates, retries, command timeouts, pooling |
| `SELECT t1.*, t2.*` | explicit projection with aliases | duplicate names, nullability, materialization |
| OLE DB, Jet/ACE, LinqToExcel | `ExcelDataReader` for reading, `ClosedXML` for workbook manipulation | cross-platform deployment, type coercion, malformed files |
| Crystal Reports | `IReportService`; HTML/template rendering through headless Chromium when layout consistency matters | browser install, fonts/images, PDF bytes/layout, concurrency |
| synchronous blocking I/O | cancellable `async`/`await` service methods | cancellation, transaction lifetime, thread starvation |
| `System.Drawing` or native Windows APIs | cross-platform library or isolated OS-specific adapter | Linux/container behavior, licensing, native asset deployment |
| `web.config` custom errors | exception handler/problem details and safe user-facing error pages | no sensitive exception leakage, API vs HTML behavior |

## Compatibility risks

- A package that compiles on .NET Standard may still depend on a native or Windows-only runtime component.
- Cookie middleware can redirect API calls to a login page unless challenge events or endpoint conventions are configured.
- ASP.NET Core 8+ upload endpoints may require antiforgery configuration for form-bound files.
- Session is not a durable application data store and complicates multi-instance scaling.
- Forwarded headers must be processed before scheme-sensitive redirects, auth callbacks, or link generation.
- Replacing an MVC child action with a partial can silently remove the child action’s service call or authorization logic.
- A successful EF query migration can still change date, decimal, null, collation, or transaction semantics.
- Native report/PDF engines can produce different layout across operating systems; render and visually inspect representative reports.
