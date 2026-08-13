# Documentation Hub

Version: 1.1-draft
Last Updated: 2026-08-13
Status: Working Draft

## 1. Purpose
This hub defines how documentation is organized for tutorials and lectures, including PPTX-derived lecture content.

## 2. Scope
In scope:
1. Final tutorial template standards.
2. Final lecture template standards.
3. Tutorial conversion workflow.
4. Lecture conversion workflow.
5. Prompt strategy patterns.
6. Prompt execution templates for tutorials and lectures.
7. QA and governance.

Out of scope:
1. Rewriting teaching content itself.
2. Tool installation docs unrelated to conversion and templates.

## 3. Source-of-Truth Priority
1. Direct task request.
2. Repo-level instructions.
3. Final template specs.
4. Conversion playbooks.
5. Prompt strategy catalog.
6. General reference docs.

## 4. Separation Contract
Tutorial system:
1. Tutorial pages and tutorial conventions only.

Lecture system:
1. Lecture slideshow pages and slideshow conventions only.

Policy:
1. Do not mix tutorial wrappers into lecture slides.
2. Do not mix lecture slideshow mechanics into tutorial pages.

## 5. Document Map
1. [final-tutorial-template-spec.md](./final-tutorial-template-spec.md)
2. [final-lecture-template-spec.md](./final-lecture-template-spec.md)
3. [tutorial-conversion-playbook.md](./tutorial-conversion-playbook.md)
4. [lecture-conversion-playbook.md](./lecture-conversion-playbook.md)
5. [prompt-strategy-catalog.md](./prompt-strategy-catalog.md)
6. [tutorial-prompt-template.md](./tutorial-prompt-template.md)
7. [lecture-prompt-template.md](./lecture-prompt-template.md)
8. [tutorial-layout-prompt.md](./tutorial-layout-prompt.md)
9. [lecture-layout-prompt.md](./lecture-layout-prompt.md)
10. [emojibake-strategy.md](./emojibake-strategy.md)

## 6. Workflow Modes
1. Audit mode: no edits, PASS/FAIL only.
2. Edit mode: minimal changes to resolve FAIL items.
3. Verify mode: re-check until all mandatory items PASS.

## 7. Required Reporting Output
1. Scope summary.
2. Files reviewed and files changed.
3. Checklist PASS/FAIL lines.
4. Minimal-diff summary.
5. Residual risks and assumptions.

## 8. Cross-Document Section Name Alignment
Use these exact shared section names across spec and playbook docs where applicable:
1. Purpose and Scope.
2. Normative References.
3. Validation Checklist.
4. Compliance Reporting Format.
5. Stop-and-Ask Triggers.
6. Governance.
7. Change Log.

## 9. Governance
1. Version and date on all core docs.
2. Change log entries for each revision.
3. Named owner and review cadence per document.

## 10. Change Log
- 1.1-draft: Added emojibake strategy document to the documentation map.
- 1.0-draft: Promoted hub to working draft and added explicit doc links and section-name alignment guidance.
- 0.1-draft: Initial skeleton.
