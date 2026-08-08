---
name: red-team
description: Adversarially assess artifacts and ideas using threat modeling, assumption testing, falsification, pre-mortem analysis, and failure-mode analysis. Use to challenge proposals, plans, designs, arguments, prompts, specifications, or code; expose evidence gaps, attack surfaces, edge cases, and fatal assumptions; and prioritize mitigations. Attack the work, not the author.
---

# Red Team

Make the work fail in analysis before it fails in practice. Be severe about defects and precise about evidence.

## Workflow

1. **Scope**: Identify the target, objective, audience, constraints, success criteria, and requested review lens. Inspect the complete artifact when available.
2. **Steelman**: State the strongest version of the work and extract its load-bearing claims. Mark each claim as supported, unverified, contradicted, or decision-critical unknown.
3. **Model threats**: Select realistic adversaries and failure conditions: skeptical user, buyer, operator, maintainer, competitor, reviewer, regulator, misuse, bad input, scale, or partial outage.
4. **Attack**: Search for invalid reasoning, evidence gaps, incentive failures, hidden dependencies, infeasibility, edge cases, abuse paths, recovery gaps, and misleading communication.
5. **Substantiate**: Tie every material finding to an exact passage, behavior, test result, counterexample, or missing control. Explain impact and affected stakeholders.
6. **Falsify**: State what evidence would disprove the strongest findings. Downgrade or withdraw findings that survive testing.
7. **Mitigate**: Recommend the smallest high-leverage repair or discriminating test.

Use a **quick strike** for the top three to five risks, a **kill test** for one fatal flaw, a **pre-mortem** for plausible failure chains, or an **adversarial debate** for balanced adjudication. Default to a full assessment.

## Finding format

For each finding, report:

- defect;
- evidence or counterexample;
- failure scenario and impact;
- severity: `critical`, `high`, `medium`, or `low`;
- confidence: `high`, `medium`, or `low`;
- mitigation or validation test.

Reserve `critical` for a defect that invalidates the core approach or creates unacceptable harm. Do not inflate severity.

## Output

Lead with:

1. **Verdict**: viability, decisive reason, and confidence.
2. **Strongest case**: the steelmanned objective and value.
3. **Findings**: ordered by severity and confidence.
4. **What survived**: important claims that held up.
5. **Unknowns**: decision-critical gaps and tests.
6. **Salvage plan**: prioritized mitigations.

Distinguish source-backed facts, direct observations, and inference. Default to review-only. Do not attack the creator, manufacture certainty, or provide harmful operational detail.
