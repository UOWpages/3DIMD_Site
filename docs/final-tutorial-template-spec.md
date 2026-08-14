# Final Tutorial Template Spec

Version: 1.1-draft
Last Updated: 2026-08-14
Status: Working Draft

## 1. Purpose and Scope
This document defines the end-state standard for final tutorial pages in this repository.

Objectives:
1. Standardize tutorial structure and component usage.
2. Preserve tutorial content intent while ensuring consistent rendering.
3. Provide explicit validation criteria for release-ready tutorial pages.

In scope:
1. HTML structure and semantic rules for tutorial pages.
2. Required component patterns for videos, pseudo-code, and media.
3. CSS and JS constraints relevant to tutorial behavior.
4. Mandatory tutorial release checklist.

Out of scope:
1. Lecture slideshow standards.
2. Conversion process steps (covered in [tutorial-conversion-playbook.md](./tutorial-conversion-playbook.md)).
3. Content rewrites not requested by task scope.

## 2. Normative References
1. [documentation-hub.md](./documentation-hub.md)
2. [tutorial-conversion-playbook.md](./tutorial-conversion-playbook.md)
3. [tutorial-layout-prompt.md](./tutorial-layout-prompt.md)
4. [tutorial-prompt-template.md](./tutorial-prompt-template.md)
5. ../site/pages/tut-00-01-student-version.html
6. ../.github/copilot-instructions.md

## 3. Canonical Structure Contract
Tutorial pages must mirror the canonical top-level hierarchy from the tutorial reference pattern.

Required structural contract:
1. Use canonical top-level wrapper order from the tutorial reference page.
2. Keep the tutorial's real headings and sections as primary page content.
3. Use top-level accordion sections for major numbered task groups where applicable.
4. Keep task-scoped content inside the matching parent task section.

Forbidden structure patterns:
1. Adding a synthetic content wrapper not in canonical layout.
2. Adding nested content sections that duplicate existing hierarchy.
3. Moving content between major task sections without explicit task request.

## 4. HTML Rules
### 4.1 Heading and Section Semantics
1. Use logical heading order within each section.
2. Keep simple text-only headings concise and one-line where possible.
3. Preserve original wording and casing unless explicitly requested.

### 4.2 Ordered and Unordered Lists
1. Keep nested lists structurally valid at all levels.
2. Nested ordered-list levels must render as decimal, lower-alpha, and lower-roman in sequence.
3. Keep simple text-only list items one-line where possible.

### 4.3 Pseudo-Code Presentation Contract
1. Pseudo-code must use the tutorial visual pattern, not code fences.
2. Do not use pre/code blocks for pseudo-code.
3. Keep brace lines as standalone lines in the visual pseudo-code pattern.
4. Keep pseudo-code content placement aligned to its matching tutorial section.
5. Pseudo-code panels render inline and must not be wrapped in a collapsible
   `<details>`/`<summary>` accordion — the panel itself must always be visible
   without requiring an extra click.
6. When removing an existing collapsible wrapper around a pseudo-code block,
   or authoring a new one, if the wrapper's `<summary>` (or equivalent
   heading) named the section (for example a filename or task name) and that
   name is not merely a duplicate of the generic "Pseudo Code:" trigger text,
   append that name to the trigger heading (for example `Pseudo Code:
   logoScreen.cs (attached to logo screen plane, which is child of camera)`).

### 4.4 Video and Embed Contract
1. Video links in content must be converted using the canonical nested video accordion component.
2. Raw media cards must not appear outside the approved nested video wrapper.
3. Avoid duplicate video or media blocks.

### 4.5 Links, Iframes, and Media
1. External links include target and rel safety attributes together.
2. Embedded iframes include lazy loading unless exception is required by canonical pattern.
3. Embedded images should remain at source-relevant in-flow positions.
4. Keep text encoding clean and free of mojibake.

## 5. CSS Rules
### 5.1 Shared Style Usage
1. Reuse existing tutorial component classes before adding new classes.
2. Keep new styles scoped and minimal when required.

### 5.2 Pseudo-Panel Rendering
1. Pseudo-panel line rendering must collapse formatting whitespace for tight tutorial readability.
2. Do not use preformatted whitespace rules that break pseudo-code visual style.

### 5.3 Readability and Spacing
1. Maintain consistent indentation and nested readability in markup.
2. Keep spacing conventions aligned with canonical tutorial pages.

## 6. JS Rules
1. Tutorial JS interactions must remain minimal and purposeful.
2. Image-expand behavior for relevant embedded figures must follow approved open/close interaction rules.
3. Do not add broad script behavior unrelated to tutorial interaction requirements.

## 7. Accessibility Requirements
1. Interactive components must be keyboard operable.
2. Structural semantics should support assistive reading order.
3. Images require meaningful alternative text or captions as appropriate.
4. Link text should remain understandable in isolation.

## 8. Validation Checklist
Report every line as PASS/FAIL:
1. Content wrapper contract compliance.
2. Major numbered task sections are top-level accordions where applicable.
3. No separate video resources block when videos are in context.
4. No raw unembedded video links where embedding is required.
5. No raw media cards outside nested video accordion wrappers.
6. Pseudo-code is not rendered as pre/code or markdown fences.
7. Pseudo-code visual style matches canonical line-by-line pattern.
7a. Pseudo-code panels are not wrapped in a collapsible details/summary accordion.
7b. A removed/absent wrapper's section name (filename or task name), when meaningful, is appended to the pseudo-code trigger heading.
8. No duplicate media links blocks.
9. No unnecessary extra wrapper sections.
10. Nested ordered-list structure is valid.
11. Ordered-list marker style sequence is correct.
12. Embedded image placement aligns with source flow where available.
13. HTML indentation/readability remains consistent with canonical style.
14. UTF-8 text integrity is preserved with no mojibake.
15. External link safety attributes are present together.
16. Iframe lazy loading requirement is satisfied where applicable.
17. Simple text-only list items use concise one-line formatting where practical.
18. Simple text-only headings use concise one-line formatting where practical.
19. Task-scoped content remains in the correct parent section.

## 9. Anti-Patterns
1. Adding wrappers not present in canonical tutorial structure.
2. Using pre/code or markdown fences for pseudo-code sections.
3. Placing raw media cards directly in page flow outside approved wrappers.
4. Breaking nested list semantics or marker sequence.
5. Wrapping a pseudo-code panel in a collapsible details/summary accordion instead of rendering it inline.
5. Moving source content to unrelated sections for convenience.
6. Introducing encoding corruption during edits.

## 10. Compliance Reporting Format
Every tutorial compliance report should include:
1. Scope statement with target page and section boundaries.
2. Files changed.
3. PASS/FAIL lines for all mandatory checklist items.
4. Exact location of each failure.
5. Minimal remediation plan in ordered steps.
6. Residual risks, assumptions, or blockers.

## 11. Mapping to Tutorial Conversion Playbook
This spec pairs directly with [tutorial-conversion-playbook.md](./tutorial-conversion-playbook.md):
1. Canonical structure contract maps to conversion structural stages.
2. HTML rules map to tutorial content normalization stage.
3. CSS and JS constraints map to alignment and behavior checks.
4. Validation checklist maps to conversion verification and release gate.

## 12. Governance
1. Keep this spec synchronized with [tutorial-layout-prompt.md](./tutorial-layout-prompt.md).
2. Update conversion and prompt docs when this spec changes materially.
3. Record version/date changes in the change log.

## 13. Change Log
- 1.1-draft: Established as canon that pseudo-code panels render inline and must not be wrapped in a collapsible details/summary accordion; when a wrapper's summary named the section, that name is appended to the pseudo-code trigger heading. Applied via unwrap_pseudocode_panels.py (repo root) to tut-00-01-student-version.html, tut-02-03-lecturer.html, tut-02-03-students.html, and tut-04-students.html.
- 1.0-draft: Expanded from skeleton to full tutorial standard aligned with canonical tutorial layout rules.
- 0.1-draft: Initial skeleton.
