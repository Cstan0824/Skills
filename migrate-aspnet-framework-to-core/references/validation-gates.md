# Verification guidelines

Use a layered evidence table. For every gate, record command, date, environment, result, and whether a failure is pre-existing, introduced, or unverified.

| Gate | Evidence | Typical failure meaning |
| --- | --- | --- |
| Static inventory | bundled audit, project/package scan, banned-API report | unsupported residue, missing host, hidden native dependency |
| Restore/build | `dotnet restore`, `dotnet build`, publish compile | project graph/package/API errors; warnings still need classification |
| Unit | pure services, validators, import parsers, policies, formatters, state machines | behavior changed in isolated logic |
| Integration | `WebApplicationFactory<Program>` + `HttpClient` | DI, middleware, routes, auth, antiforgery, DB/test-host wiring |
| Database | representative queries/writes/import transactions and failure paths | provider translation, aliases, null/date/decimal/transaction mismatch |
| Browser | login, navigation, area pages, forms, uploads, assets, imports, reports | rendered UI, JavaScript, cookies, redirects, view-composition regressions |
| Reporting | valid PDF signature plus visual/layout inspection | missing browser/fonts/assets, concurrency or template regression |
| Security | authn/authz matrix, 401/403 vs redirects, CSRF, secret scan, HTTPS/proxy behavior | privilege escalation, leakage, broken callbacks, spoofed proxy data |
| Operations | publish, startup, health endpoints, logs, private storage, browser install, rollback plan | deployment-only failure or no safe recovery |
| Parity | feature matrix with evidence and explicit intentional changes | false confidence from file counts/compilation |

## Integration-test guidance

- Build a test host with `WebApplicationFactory<Program>` and replace external services/test database deliberately.
- Assert unauthenticated HTML requests redirect only where intended and API requests receive 401/403.
- Assert route/area resolution and representative model validation.
- Exercise antiforgery-protected form/file posts.
- Assert liveness does not require the database and readiness does.
- Verify exception handling returns safe HTML/problem details without stack traces or connection strings.

## System-test guidance

Use Playwright or the project’s approved browser harness for the highest-risk flows. Check console/network errors, asset status, navigation, form validation, role-dependent visibility, upload feedback, and report downloads. For PDFs, assert the `%PDF-` signature and inspect at least one representative page for clipping, fonts, images, pagination, and locale/number formatting.

## Evidence classification

- `pass`: command or test evidence exists and the behavior is correct.
- `intentional change`: behavior differs by design and is documented/approved.
- `deferred`: known work remains but does not block the stated scope.
- `blocked`: evidence cannot be obtained or a required behavior is broken.

Never turn `deferred` or `unverified` into `pass` merely because the project compiles.
