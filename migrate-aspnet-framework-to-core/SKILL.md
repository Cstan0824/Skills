---
name: migrate-aspnet-framework-to-core
description: Assess and modernize ASP.NET Framework MVC 5/System.Web applications to ASP.NET Core. Use for migration assessment, strategy selection, compatibility analysis, SDK-style conversion, vertical-slice migration, and behavioral-parity verification.
---

# Migrate ASP.NET Framework to Core

Apply official migration patterns. Treat legacy behavior as the verification baseline.

## Principles

- **Behavior over structure**: Preserve observable contracts, not legacy file or namespace layouts.
- **Evidence over assertion**: Require reproducible evidence for compatibility, parity, and readiness claims.
- **Risk-proportional strategy**: Select incremental or in-place migration from availability, complexity, and cutover risk.
- **Vertical coherence**: Keep each migrated feature independently testable, deployable, and reversible.
- **Explicit migration debt**: Assign ownership and removal criteria to every compatibility layer.
- **Operational continuity**: Preserve security, data integrity, observability, rollback, and recovery behavior.

## Guardrails

- Preserve repository instructions and unrelated changes.
- Keep the requested target framework and migration scope.
- Establish system boundaries, dependencies, constraints, risks, and baseline behavior before making architectural claims.
- Replace, isolate, or retire incompatibilities against explicit acceptance criteria.
- Classify every behavioral difference as intentional, defective, deferred, blocked, or unverified.
- Do not delete the legacy system, change production routing, or alter schemas without explicit authorization.
- Do not claim parity or readiness from compilation, file counts, or static analysis alone.

## Review rules

- Evaluate application behavior, architecture, compatibility, security, data, integrations, deployment, and recovery.
- Separate baseline defects from migration regressions.
- Prefer supported platform capabilities; keep unavoidable platform coupling behind explicit boundaries.
- Require rollback and recovery evidence for changes with operational or data impact.
- Report decisions, evidence, risks, migration debt, and unresolved blockers.

Read [migration-principles.md](references/migration-principles.md), [compatibility-rules.md](references/compatibility-rules.md), or [verification-rules.md](references/verification-rules.md) only when that concern requires more detail.

## Audit rule

When source or target trees are available, run:

```text
python scripts/audit_aspnet_migration.py --legacy <legacy-root> --target <target-root>
```

Use `--format json` for automation and `--fail-on none` for source-only analysis. Treat audit results as static evidence, not behavioral proof.
