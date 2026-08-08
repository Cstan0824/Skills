---
name: red-team
description: Adversarially assess artifacts and ideas using threat modeling, assumption testing, falsification, pre-mortem analysis, and failure-mode analysis. Use to challenge proposals, plans, designs, arguments, prompts, specifications, or code; expose evidence gaps, attack surfaces, edge cases, and fatal assumptions; and prioritize mitigations. Attack the work, not the author.
---

# Red Team

Perform an evidence-based adversarial assessment.

## Adversarial analysis methods

- Steelmanning and claim decomposition
- Assumption testing and falsification
- Threat modeling and abuse-case analysis
- Failure-mode and pre-mortem analysis
- Domain review: logical, evidentiary, technical, security, operational, incentive, market, regulatory, and communication
- Risk prioritization and mitigation analysis

Modes: `quick strike`, `kill test`, `pre-mortem`, `adversarial debate`, or `full assessment`.

## Report schema

- `verdict`: viability, decisive risk, confidence
- `strongest_case`: objective, value, load-bearing claims
- `findings[]`: defect, evidence or counterexample, failure scenario, impact, severity, confidence, mitigation or validation test
- `survivors[]`: claims that withstood review
- `unknowns[]`: decision-critical gaps and discriminating tests
- `salvage_plan`: prioritized mitigations

Order findings by severity and confidence. Use `critical` only for core invalidation or unacceptable harm. Label facts, observations, and inferences. Default to review-only. Exclude personal attacks, unsupported certainty, and harmful operational detail.
