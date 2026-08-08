# Migration principles

| Principle | Rule |
| --- | --- |
| Behavioral preservation | Treat externally observable behavior as the migration contract unless a change is explicitly approved. |
| Risk proportionality | Match migration strategy and control depth to availability, complexity, reversibility, and business impact. |
| Reversible change | Keep changes bounded, independently verifiable, and recoverable. |
| Vertical coherence | Migrate complete feature behavior rather than disconnected technical layers. |
| Dependency awareness | Evaluate direct, transitive, platform, operational, and organizational dependencies. |
| Explicit debt | Record transitional architecture with owner, risk, scope, and removal criterion. |
| Operational continuity | Preserve security, data integrity, observability, deployment, rollback, and recovery capabilities. |
| Scope discipline | Avoid unrelated redesign unless required to remove a migration blocker. |

Stop work when missing information could materially change architecture, security, data integrity, or cutover risk.
