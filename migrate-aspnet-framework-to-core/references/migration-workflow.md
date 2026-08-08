# Migration workflow

Use the phases in order, but keep each phase small enough to compile and test. A migration may revisit a phase when a feature exposes a new dependency.

## Phase 0: Baseline and scope

- Record the source commit/tree, target tree, target framework constraint, deployment OS, database engine/version, and external services.
- Run the bundled audit against the source and target (if a target exists).
- Enumerate routes, areas, controllers, views, background jobs, scheduled work, imports, reports, authentication, authorization, session, static assets, and data boundaries.
- Mark each feature with a characterization test or a concrete manual/browser check.
- Preserve a risk register for Windows-only dependencies, native binaries, secrets, data migrations, and undocumented behavior.

Stop if the target framework, database compatibility, deployment topology, or critical feature behavior is unknown and the missing fact would change architecture.

## Phase 1: Project and dependency graph

- Convert or recreate projects as SDK-style only when the resulting project graph is understood.
- Establish one authoritative `<TargetFramework>` per project unless deliberate multi-targeting is required.
- Replace `packages.config` and assembly `Reference` entries with justified `PackageReference` entries.
- Remove packages that only supported System.Web, MVC 5, EF6, Crystal runtime, or Windows-only providers.
- Keep project boundaries that express domain/data/UI ownership; do not use conversion as a reason to merge unrelated layers.

Gate: restore and compile an empty/host skeleton before porting feature code. Record packages that have no supported Core equivalent.

## Phase 2: Host, configuration, and cross-cutting behavior

- Move `Global.asax` startup and `App_Start` registration into `Program.cs` and extension methods.
- Bind structured settings with options; validate required production settings early.
- Keep secrets out of source and publish artifacts.
- Order forwarded headers, exception handling, HTTPS/HSTS policy, static files, routing, CORS (if needed), authentication, authorization, session, rate limiting, and endpoint mapping intentionally.
- Add structured logging, health checks, and correlation/trace information where operations need them.

Gate: start the application with test configuration, resolve the service graph, and assert liveness/readiness behavior without requiring production credentials.

## Phase 3: MVC surface and assets

- Port controller inheritance and namespaces to ASP.NET Core MVC.
- Replace `RouteConfig`/area registration with endpoint routing and explicit route patterns.
- Replace `HttpPostedFileBase` with `IFormFile`; validate uploads and use private storage for sensitive files.
- Replace `Html.Action` child actions with view components, partials, or service calls. Preserve authorization and model state across the composition boundary.
- Replace `Scripts.Render`/`Styles.Render` with `wwwroot` assets and an explicit bundling/minification/build choice.
- Use strongly typed view models and Core tag helpers; avoid passing EF entities directly to views.

Gate: test an unauthenticated request, an authorized request, invalid model state, a valid form post, an upload, an area route, a static asset, and an error response.

## Phase 4: Identity and security

- Map legacy identity/session assumptions before selecting cookie auth, ASP.NET Core Identity, claims, or an external identity provider.
- Apply policies/roles at controller/action/endpoint boundaries and preserve least privilege.
- Configure cookie login/access-denied behavior deliberately; APIs typically need 401/403 rather than HTML redirects.
- Preserve antiforgery protection for cookie-authenticated form posts and uploads.
- Review data-protection key persistence when running multiple instances.

Gate: exercise login success/failure, timeout, authorization denial, antiforgery failure, session behavior, and API challenge semantics.

## Phase 5: Data and integrations

- Replace EF6/provider-specific code with EF Core or a deliberate SQL/data-access boundary.
- Keep `DbContext` scoped and queries/transactions in services.
- Rewrite `SELECT t1.*, t2.*` projections with explicit columns and aliases; verify nullability and MySQL zero-date behavior.
- Use parameterized SQL, retry/timeout policy, cancellation, and transaction boundaries appropriate to the provider.
- Replace OLE DB imports with a cross-platform reader and validate untrusted workbook content.
- Replace Windows/native report dependencies with an abstraction and a tested renderer.

Gate: run representative reads/writes/imports/reports against a disposable or approved test database and fixture files. Include failure/retry paths.

## Phase 6: Parity and operations

- Compare features by routes, permissions, outputs, side effects, and user-visible behavior—not file names.
- Run unit, integration, browser, report, and publish checks.
- Verify reverse-proxy headers, HTTPS/cookies, environment configuration, file permissions, private storage, health endpoints, and external service credentials.
- Record every intentional behavior change and every deferred check.

The migration is ready for a controlled cutover only when all must-pass features have evidence, no target blockers remain, and operational rollback/data plans are explicit.
