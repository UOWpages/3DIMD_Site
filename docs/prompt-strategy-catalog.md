# Prompt Strategy Catalog

Version: 1.0-draft
Last Updated: 2026-08-12
Status: Working Draft

## 1. Purpose and Scope
This catalog defines prompt strategies used to produce consistent, low-risk, checklist-driven work across tutorial and lecture pipelines.

Objectives:
1. Standardize prompt structure and output expectations.
2. Keep audit, edit, and verify behavior consistent.
3. Ensure prompts enforce system separation and minimal-diff policy.

In scope:
1. Prompt families for tutorial and lecture work.
2. Mode contracts and guardrails.
3. Required input and output schemas.
4. Stop-and-ask triggers.
5. Governance and versioning.

Out of scope:
1. Replacing template specs or conversion playbooks.
2. Tooling implementation details not relevant to prompt behavior.

## 2. Normative References
1. [documentation-hub.md](./documentation-hub.md)
2. [final-tutorial-template-spec.md](./final-tutorial-template-spec.md)
3. [final-lecture-template-spec.md](./final-lecture-template-spec.md)
4. [tutorial-conversion-playbook.md](./tutorial-conversion-playbook.md)
5. [lecture-conversion-playbook.md](./lecture-conversion-playbook.md)
6. [tutorial-prompt-template.md](./tutorial-prompt-template.md)
7. [lecture-prompt-template.md](./lecture-prompt-template.md)
8. [tutorial-layout-prompt.md](./tutorial-layout-prompt.md)
9. [lecture-layout-prompt.md](./lecture-layout-prompt.md)
10. ../.github/copilot-instructions.md

## 3. Prompt Families
1. Final Tutorial Authoring Prompt: use when refining already-converted tutorial pages to final standard.
2. Final Lecture Authoring Prompt: use when refining already-converted lecture slides to final standard.
3. Tutorial Conversion Prompt: use when converting source tutorial material into final tutorial pages.
4. Lecture/PPTX Conversion Prompt: use when converting lecture source or PPTX-derived assets into final lecture slides.
5. QA-Only Prompt: use for compliance checks with no edits.

## 4. Mode Contracts
All prompt families support these three modes.

### 4.1 Audit Mode
1. No file edits.
2. Produce PASS/FAIL checklist against governing spec.
3. Provide exact failure locations.
4. Provide minimal remediation sequence.

### 4.2 Edit Mode
1. Apply only minimal edits needed to convert FAIL to PASS.
2. Keep changes within explicit scope.
3. Preserve wording and structure unless changes are required for compliance or explicitly requested.

### 4.3 Verify Mode
1. Re-audit after edits.
2. Report PASS/FAIL for every mandatory item.
3. Continue minimal fixes until all mandatory checks PASS, or stop on approved blocker conditions.

## 5. Required Prompt Inputs
Every operational prompt should include:
1. Target path(s).
2. Scope boundaries: full file or specific sections/slides.
3. Source artifacts: source doc paths, extraction outputs, and media paths where applicable.
4. Mode: audit, edit, or verify.
5. Constraints: no unrelated edits, preserve system boundaries, and minimal-diff intent.

## 6. Global Guardrails
These lines must be enforced in all prompt families:
1. Follow governing specs and conversion playbooks exactly.
2. Do not cross tutorial and lecture systems.
3. Preserve wording and casing unless rewrite is explicitly requested.
4. Do not perform cleanup or refactor outside scoped compliance fixes.
5. If ambiguity affects correctness, stop and ask.

## 7. Required Prompt Output Schema
Every prompt run must output:
1. Scope summary: files or slides reviewed and edited.
2. Source summary: artifacts consulted and key assumptions.
3. Checklist summary: PASS/FAIL lines for all mandatory checks.
4. Findings summary: exact locations for each FAIL item.
5. Action summary: minimal edit plan or concise change summary.
6. Risk summary: residual risks, blockers, or assumptions.

## 8. Family-Specific Strategy Notes
### 8.1 Final Tutorial Authoring Prompt
1. Prioritize conformance to tutorial structural template.
2. Enforce pseudo-code and nested list integrity rules.
3. Avoid lecture component usage.

### 8.2 Final Lecture Authoring Prompt
1. Prioritize slide shell and region consistency.
2. Enforce readability, overflow, and control/counter behavior.
3. Avoid tutorial wrappers and conventions.

### 8.3 Tutorial Conversion Prompt
1. Require explicit audit-first pass.
2. Require minimal edit pass and verification pass.
3. Track any content that cannot be safely mapped without clarification.

### 8.4 Lecture/PPTX Conversion Prompt
1. Require source inventory and source-to-slide mapping before edits.
2. Require slide-type classification for scoped slides.
3. Require schedule and deadline normalization checks.
4. Require media sequence and placement checks.
5. Require navigation/counter behavior checks on verification.

### 8.5 QA-Only Prompt
1. No edits allowed.
2. Full PASS/FAIL evidence output.
3. Prioritized remediation list only.

## 9. Lecture/PPTX Strategy Mapping to Playbook Stages
For lecture conversion prompts, map outputs to playbook stages:
1. Stage 0 and 1: intake confirmation and source inventory.
2. Stage 2: slide mapping and type classification summary.
3. Stage 3 and 4: structural and content normalization edits.
4. Stage 5: media and embed conformance checks.
5. Stage 6: CSS and JS alignment checks.
6. Stage 7: full release checklist PASS/FAIL and gate status.

## 10. Stop-and-Ask Triggers
Stop and request clarification when:
1. Source instructions conflict with governing specs.
2. Required assets are missing and cannot be inferred safely.
3. Multiple plausible structural mappings exist with no clear best option.
4. Requested change requires broad non-minimal refactor.
5. Template requirements conflict with direct user intent and priority is unclear.

## 11. Prompt Quality Checklist
Before running a prompt, confirm:
1. Correct prompt family selected.
2. Correct mode selected.
3. Correct governing docs referenced.
4. Scope boundaries explicitly stated.
5. Output schema explicitly requested.

After running a prompt, confirm:
1. Mandatory checklist lines were reported.
2. Findings include exact failure locations.
3. Edit mode changes are minimal and scoped.
4. Verify mode ends with explicit gate status.

## 12. Governance and Versioning
1. Prompt templates must cite governing spec and playbook sections.
2. Update prompt language when specs/playbooks change.
3. Keep prompt wording stable across runs to improve consistency.
4. Record prompt strategy revisions in this document.

## 13. Change Log
- 1.0-draft: Expanded from skeleton to full strategy catalog aligned with tutorial and lecture specs/playbooks.
- 0.1-draft: Initial skeleton.
