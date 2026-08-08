# Verification rules

- **Evidence provenance**: Record the procedure, environment, result, and origin of every finding.
- **Layered evidence**: Combine static, build, unit, integration, contract, system, security, data, and operational evidence as risk requires.
- **Contract focus**: Compare inputs, outputs, permissions, side effects, failures, and user-visible behavior.
- **Representative conditions**: Test critical behavior under production-relevant configuration, data, load, and dependencies.
- **Failure validation**: Exercise denial, timeout, partial failure, rollback, and recovery paths.
- **Regression separation**: Distinguish pre-existing defects from migration-introduced failures.
- **Explicit classification**: Label results `pass`, `intentional change`, `deferred`, `blocked`, or `unverified`.
- **Sufficient proof**: Do not infer parity or readiness from a successful build or static scan.
