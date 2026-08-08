# Compatibility rules

| Concern | Rule |
| --- | --- |
| Build and dependencies | Confirm target support, transitive risk, and deployment compatibility. |
| Application semantics | Preserve request, execution, failure, and externally observable behavior. |
| Hosting | Reconstruct startup, pipeline ordering, environment, and failure handling deliberately. |
| State and context | Make lifetime and ownership explicit; verify concurrency and background execution. |
| Identity and security | Preserve trust boundaries, policy semantics, protection controls, and denial behavior. |
| Data | Preserve query, transaction, concurrency, persistence, and recovery semantics. |
| Integrations | Verify protocol, file, report, native, and external-service contracts. |
| Presentation | Preserve routing, rendering, input, asset, and accessibility contracts. |
| Asynchrony | Preserve cancellation, resource lifetime, transaction, and error semantics. |

Prefer supported platform capabilities over compatibility shims. Treat compilation as compatibility evidence, not proof.
