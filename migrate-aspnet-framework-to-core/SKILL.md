---
name: migrate-aspnet-framework-to-core
description: Assess and modernize ASP.NET Framework MVC 5/System.Web applications to ASP.NET Core. Use for migration assessment, strategy selection, compatibility analysis, SDK-style conversion, vertical-slice migration, and behavioral-parity verification.
---

# Migrate ASP.NET Framework to Core

Apply official ASP.NET Core migration patterns. Treat legacy behavior as the verification baseline.

## Guardrails

- Inspect repository instructions and preserve unrelated changes.
- Preserve the system-under-test (SUT) contract: routes, authorization, validation, data, reports, and user flows.
- Keep the requested target framework; do not silently retarget.
- Use compatibility layers only as transitional architecture.
- Do not retain service locators, `HttpContext.Current`, committed secrets, or unisolated Windows-only dependencies.
- Do not delete the legacy application, change production traffic, or modify database schemas without explicit authorization.

## Workflow

### 1. Conduct migration assessment

Inventory the project graph, dependencies, platform constraints, application surface, integrations, and test coverage. Run:

```text
python scripts/audit_aspnet_migration.py --legacy <legacy-root> --target <target-root>
```

Use `--format json` for automation and `--fail-on none` for source-only analysis. Apply [migration-workflow.md](references/migration-workflow.md).

### 2. Select migration strategy

- **Incremental migration**: Apply the Strangler Fig pattern and side-by-side routing for large, high-risk, or continuously available systems.
- **In-place migration**: Apply to bounded systems with acceptable cutover risk.
- **System.Web adapters**: Apply only as an incremental compatibility layer.

### 3. Define target architecture

Define SDK-style projects, target frameworks, `WebApplication`, dependency injection, middleware, endpoint routing, configuration, observability, and test hosting.

### 4. Perform compatibility remediation

Apply [replacement-matrix.md](references/replacement-matrix.md). Replace unsupported APIs, packages, hosting constructs, data providers, and platform-specific dependencies.

### 5. Execute vertical-slice migration

For each feature, conduct contract mapping, characterization testing, implementation, integration testing, and regression testing before the next slice.

### 6. Verify behavioral parity

Apply [validation-gates.md](references/validation-gates.md). Classify each feature as `pass`, `intentional change`, `deferred`, or `blocked`. Separate baseline failures from regressions.

### 7. Conduct operational-readiness review

Validate publish output, deployment configuration, reverse-proxy behavior, security controls, observability, data integrity, rollback, and recovery. Never infer readiness from compilation alone.

## References

- [migration-workflow.md](references/migration-workflow.md): migration phases and quality gates.
- [replacement-matrix.md](references/replacement-matrix.md): compatibility-remediation guidance.
- [validation-gates.md](references/validation-gates.md): parity and readiness evidence.
