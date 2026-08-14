# Tutorial Conversion Playbook

Version: 1.1-draft
Last Updated: 2026-08-14
Status: Working Draft

## 1. Purpose and Scope
This playbook defines the operational procedure for converting tutorial source content into final tutorial pages.

Objectives:
1. Achieve full conformance with [final-tutorial-template-spec.md](./final-tutorial-template-spec.md).
2. Keep edits minimal, traceable, and scoped.
3. Preserve instructional intent and content placement.

In scope:
1. Full tutorial conversions.
2. Incremental tutorial updates.
3. Pseudo-code, media, and nested-list normalization.
4. Verification and release gate reporting.

Out of scope:
1. Lecture slideshow conversion.
2. Broad style redesign not required for compliance.
3. Content rewrites not explicitly requested.

## 2. Normative References
1. [documentation-hub.md](./documentation-hub.md)
2. [final-tutorial-template-spec.md](./final-tutorial-template-spec.md)
3. [tutorial-layout-prompt.md](./tutorial-layout-prompt.md)
4. [tutorial-prompt-template.md](./tutorial-prompt-template.md)
5. [prompt-strategy-catalog.md](./prompt-strategy-catalog.md)
6. ../site/pages/tut-00-01-student-version.html
7. ../.github/copilot-instructions.md

## 3. Inputs, Outputs, and Preconditions
Inputs:
1. Target tutorial page path.
2. Source references and media assets.
3. Source DOCX when available for placement checks.
4. Conversion scope: full page or section subset.

Outputs:
1. Updated tutorial page conforming to mandatory checks.
2. PASS/FAIL report with exact failure locations.
3. Risk and assumption notes for unresolved issues.

Preconditions:
1. Target scope is explicitly confirmed.
2. Tutorial-only boundaries are confirmed.
3. Required source assets are available or documented as missing.
4. No unrelated-file edit policy is confirmed.

## 4. Conversion Modes
1. Full conversion: apply canonical structure and component patterns across the page.
2. Incremental update: change only impacted sections while preserving compliant areas.
3. Patch conversion: resolve identified compliance failures with minimal edits.

## 5. Stage 0: Pre-Flight and Scope Lock
Required actions:
1. Confirm target path and current file baseline.
2. Confirm conversion mode and scope boundaries.
3. Confirm source references for content and media placement.
4. Record assumptions before editing.

Exit criteria:
1. Scope and mode are unambiguous.
2. Required assets are present or exceptions documented.

## 6. Stage 1: Audit-Only Pass
Required actions:
1. Run full tutorial checklist with no edits.
2. Record PASS/FAIL line-by-line.
3. Identify exact locations for every FAIL.
4. Produce minimal ordered remediation plan.

Audit focus areas:
1. Canonical wrapper structure.
2. Task-section placement integrity.
3. Video embedding component pattern.
4. Pseudo-code presentation pattern.
5. Nested list semantics and marker sequence.
6. Link, iframe, and encoding integrity.

Exit criteria:
1. Full failure inventory and edit plan produced.

## 7. Stage 2: Minimal Edit Pass
Required actions:
1. Apply only edits necessary to convert FAIL to PASS.
2. Keep wording/casing unchanged unless rewrite is requested.
3. Preserve section ownership and content flow.

Operational rules:
1. Do not add wrappers not present in canonical template.
2. Convert inline video links to approved nested video component pattern.
3. Remove raw media-card placement outside approved wrappers.
4. Convert pseudo-code formatting to canonical line-by-line pattern.
4a. Unwrap any pseudo-code panel that is nested inside a collapsible details/summary accordion so it renders inline; if the removed summary named the section meaningfully, append that name to the "Pseudo Code:" trigger heading. See unwrap_pseudocode_panels.py (repo root).
5. Repair list nesting and marker hierarchy with minimal structural change.
6. Preserve source-aligned media placement when source DOCX is available.

Exit criteria:
1. All previously identified FAIL items are addressed or explicitly blocked.

## 8. Stage 3: Verification and Lock
Required actions:
1. Re-run full tutorial checklist.
2. Report PASS/FAIL for every mandatory item.
3. Continue minimal fixes until mandatory items PASS or blocker is approved.

Release gate policy:
1. Mandatory checklist items must PASS.
2. Any accepted exception must be documented with rationale.

## 9. Common Failure Patterns and Fix Guidance
1. Incorrect video embedding structure: replace with canonical nested video accordion component in-place.
2. Invalid nested list semantics: reattach nested ordered lists under correct parent list item.
3. Pseudo-code rendered in forbidden tags: replace with canonical line-by-line pseudo layout.
3a. Pseudo-code wrapped in a collapsible details/summary accordion: unwrap it so the panel renders inline, appending the wrapper's section name to the trigger heading if meaningful.
4. Duplicate wrappers or content blocks: remove redundant wrapper and preserve one authoritative content path.
5. Encoding corruption: restore UTF-8 clean text and verify symbols/special characters.

## 10. Stop-and-Ask Triggers
Stop and request clarification when:
1. Source structure intent is ambiguous.
2. Source media placement reference is missing for critical sections.
3. Required change conflicts with canonical tutorial structure rules.
4. Requested changes imply a broad refactor outside minimal-diff scope.
5. Direct task instructions conflict with existing constraints and priority is unclear.

## 11. Minimal-Diff Enforcement
1. Edit only scoped tutorial file(s) and required shared assets.
2. Preserve unrelated wording, spacing, and structure.
3. Avoid repo-wide formatting passes.
4. Do not refactor compliant sections.

## 12. Mandatory Verification Checklist
Report PASS/FAIL for each:
1. Content wrapper contract compliance.
2. Major numbered task sections at top-level accordions where applicable.
3. No separate video resources block when videos are in-place.
4. No raw unembedded video links where embedding is required.
5. No raw media cards outside nested video wrappers.
6. No pre/code or markdown-fence pseudo-code blocks.
7. Pseudo-code style matches canonical line-by-line format.
7a. Pseudo-code panels are not wrapped in a collapsible details/summary accordion.
8. No duplicate media links blocks.
9. No unnecessary wrapper sections.
10. Nested ordered-list structure validity.
11. Ordered-list marker sequence correctness.
12. Embedded image placement in source-aligned positions where available.
13. HTML indentation and readability consistency.
14. UTF-8 text integrity and no mojibake.
15. External link safety attributes compliance.
16. Iframe lazy loading compliance where applicable.
17. Simple one-line formatting for text-only list items where practical.
18. Simple one-line formatting for text-only headings where practical.
19. Task-scoped content remains in correct parent section.

## 13. Compliance Reporting Format
Every conversion run outputs:
1. Scope summary and conversion mode.
2. Files changed.
3. PASS/FAIL checklist lines.
4. Exact failure locations.
5. Minimal ordered remediation summary.
6. Risks, assumptions, exceptions, and blockers.

## 14. Pairing Matrix to Final Tutorial Template Spec
1. [Canonical Structure Contract](./final-tutorial-template-spec.md) maps to Stage 1 and Stage 2 structure checks.
2. [HTML Rules](./final-tutorial-template-spec.md) map to Stage 2 content normalization.
3. [CSS Rules](./final-tutorial-template-spec.md) and [JS Rules](./final-tutorial-template-spec.md) map to Stage 2 alignment and Stage 3 verification.
4. [Validation Checklist](./final-tutorial-template-spec.md) maps directly to Stage 3 release gate.
5. [Anti-Patterns](./final-tutorial-template-spec.md) map to Stage 2 prohibited actions and Stage 11 minimal-diff policy.

## 15. Governance
1. Keep this playbook synchronized with [final-tutorial-template-spec.md](./final-tutorial-template-spec.md) and [tutorial-layout-prompt.md](./tutorial-layout-prompt.md).
2. Update [prompt-strategy-catalog.md](./prompt-strategy-catalog.md) when tutorial process rules change.
3. Version and date each revision.
4. Record material process updates in the change log.

## 16. Change Log
- 1.1-draft: Canonized inline pseudo-code rendering: pseudo-code panels must not be wrapped in a collapsible details/summary accordion, and a removed/absent wrapper's meaningful section name is appended to the "Pseudo Code:" trigger heading. Applied via unwrap_pseudocode_panels.py (repo root).
- 1.0-draft: Expanded from skeleton to full operational tutorial conversion playbook aligned to tutorial template spec.
- 0.1-draft: Initial skeleton.
