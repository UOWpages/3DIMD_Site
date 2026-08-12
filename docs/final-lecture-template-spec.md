# Final Lecture Template Spec

Version: 1.0-draft
Last Updated: 2026-08-12
Status: Working Draft

## 1. Purpose and Scope
This document defines the end-state standard for lecture slideshow pages in this repository. It specifies required HTML structure, CSS usage boundaries, JS behavior expectations, and release-readiness checks for final lecture output.

In scope:
1. Lecture slideshow page structure.
2. Slide component patterns and allowed variants.
3. Shared slideshow CSS integration rules.
4. Slide navigation and normalization behavior.
5. Lecture release validation criteria.

Out of scope:
1. Tutorial page standards.
2. Source conversion workflow details (covered in [lecture-conversion-playbook.md](./lecture-conversion-playbook.md)).
3. Authoring-policy conflicts with repo-level instructions.

## 2. Normative References
Primary references:
1. [documentation-hub.md](./documentation-hub.md)
2. [lecture-conversion-playbook.md](./lecture-conversion-playbook.md)
3. ../site/lectures/lecture-template.html
4. ../site/lectures/lect-01a.html
5. ../site/assets/css/slideshow.css
6. ../site/assets/css/site.css
7. ../site/assets/js/site.js
8. ../.github/copilot-instructions.md

If conflicts occur, follow the priority model defined in [documentation-hub.md](./documentation-hub.md) and repo-level instructions.

## 3. Lecture Architecture Contract
Every lecture page must follow this base contract:
1. A slideshow container wraps all slides.
2. Each slide includes a title region, content region, controls/footer region, and keyboard hint region.
3. Slides are normalized into a shared frame pattern.
4. Only one slide is active at a time.

Required per-slide regions:
1. Title region: element uses slide title class and appears first in slide frame order.
2. Content region: main instructional content, variant by slide type.
3. Controls/footer region: previous and next controls, logo, and counter.
4. Keyboard hint region: present and consistent with navigation support policy.

Mandatory constraints:
1. Do not remove required regions on any slide.
2. Do not add tutorial-specific wrappers to lecture slides.
3. Do not create custom one-off slide shells that bypass normalization.

## 4. Slide Typology and Usage
Use one primary type per slide:
1. Text slide: linear instructional narrative and short lists.
2. Accordion summary slide: dense grouped information requiring progressive disclosure.
3. Schedule/timeline slide: chronological week-by-week teaching plans and deadlines.
4. Table/data slide: structured criteria, weighting, or matrix-style content.
5. Media-heavy slide: image-first or embed-first slides with supporting context.
6. Reference/resource slide: reading lists, links, and external resources.

Selection guidance:
1. Prefer text slide for concise content.
2. Prefer accordion for high-density grouped details.
3. Prefer schedule type when chronology and deadlines are central.
4. Prefer table type only when tabular relationships are essential.

## 5. HTML Rules
### 5.1 Structure and Semantics
1. Use semantic headings in descending order within each slide.
2. Keep sectioning consistent and predictable for scanability.
3. Use article wrappers for repeatable card-like schedule blocks.
4. Keep simple text items concise and avoid unnecessary wrapper nesting.

### 5.2 Links and Embeds
1. External links must include target and rel safety attributes together.
2. Embedded frames should include lazy loading unless an explicit exception is documented.
3. Embedded content must remain inside approved container components.

### 5.3 Accordion Rules
1. Use details and summary for collapsible lecture blocks.
2. Keep accordion body content structurally valid and readable.
3. Avoid deep nested accordions unless required by content density.

### 5.4 Schedule and Deadline Rules
1. Schedule slides use a dedicated schedule content container.
2. Each week or time unit should be represented as one schedule card.
3. Deadline statements must use a consistent deadline callout pattern.
4. Chronological order must be preserved.

### 5.5 Media Rules
1. All images must include useful alt text.
2. Media should appear in source-relevant in-flow positions.
3. Do not insert duplicate media blocks unless pedagogically justified.

## 6. CSS Rules
### 6.1 Shared Style Boundaries
1. Lecture visual behavior must be driven by shared slideshow styles.
2. Reuse existing component classes before introducing new classes.
3. New classes should be scoped to lecture slide content patterns.

### 6.2 Layout and Overflow
1. Slides must remain fixed within the lecture viewport shell.
2. Content overflow must occur inside content panes, not outside slide bounds.
3. Scroll behavior for dense content should be isolated to intended containers.

### 6.3 Typography and Readability
1. Title, heading, and body scales should remain consistent across slides.
2. Dense content must keep line-height and spacing readable.
3. Avoid ad-hoc font-size overrides that break deck consistency.

### 6.4 Component Contracts
Accordion contract:
1. Summary has clear contrast and clickable affordance.
2. Body uses consistent spacing and text size.

Table contract:
1. Header and body cells remain visually distinct.
2. Horizontal overflow is handled safely for narrower screens.

Schedule contract:
1. Schedule cards use repeatable card styling.
2. Subtitle and timeline flow are visually scannable.

Deadline callout contract:
1. Deadline callouts are visually distinct from normal paragraphs.
2. Color and border treatment is consistent across the deck.

## 7. JS Rules
### 7.1 Navigation Behavior
1. Previous and next controls move through slide index deterministically.
2. First slide disables previous control.
3. Last slide disables next control.

### 7.2 Counter Behavior
1. Counter reflects current active slide and total slides.
2. Counter updates on every navigation event.

### 7.3 Keyboard Behavior
1. Right arrow advances slides.
2. Left arrow reverses slides.
3. Keyboard behavior mirrors button behavior exactly.

### 7.4 Normalization Behavior
1. Structural normalization must be idempotent.
2. Already-normalized slides must not be rewrapped.
3. Normalization should not reorder instructional content unexpectedly.

### 7.5 Linkification Behavior
1. URL text may be transformed into anchors for usability.
2. Linkification must not corrupt existing markup structure.

## 8. Accessibility Requirements
1. All interactive controls must be keyboard reachable.
2. Focus indicators must remain visible for controls.
3. Images require meaningful alternative text.
4. Heading hierarchy should support assistive navigation.
5. Contrast and font readability should meet instructional usage expectations.
6. Dense sections should remain navigable with scrolling and headings.

## 9. Validation Checklist
Run and report these items explicitly as PASS/FAIL:
1. Slide shell and frame structure is consistent.
2. Every slide has title, content, controls/footer, and keyboard hint regions.
3. Slide type assignment matches content intent.
4. Content overflow behavior remains inside intended scroll containers.
5. Typography and spacing are consistent and readable.
6. Accordion slides follow details and summary component pattern.
7. Schedule slides follow schedule card and deadline callout pattern.
8. Table slides follow shared table contract.
9. External links use required safety attributes.
10. Embedded iframes follow loading and containment rules.
11. Navigation control states are correct at first and last slide.
12. Keyboard navigation works and matches button behavior.
13. Counter displays current and total slide values correctly.
14. Footer logo and control arrangement remains consistent.
15. No tutorial-only wrappers or patterns are present.
16. No unscoped style changes introduce regressions outside lecture components.
17. Normalization behavior remains idempotent.
18. Accessibility baseline requirements are met.

## 10. Anti-Patterns
1. Importing tutorial wrapper patterns into lecture slides.
2. Adding broad global CSS overrides to solve one slide issue.
3. Creating alternate slide structures that bypass shared frame normalization.
4. Using inline styles for persistent component behavior.
5. Overloading one slide with unstructured schedule content.
6. Breaking chronological order in schedule and deadline content.
7. Duplicating media or resource blocks without instructional purpose.

## 11. Compliance Reporting Format
Every lecture compliance report should include:
1. Scope statement: target lecture file and slide range reviewed.
2. Files changed: include only directly touched lecture files and shared assets.
3. Checklist section: PASS/FAIL for each required checklist line.
4. Findings section: exact slide-indexed locations for FAIL items.
5. Remediation section: minimal ordered fix plan.
6. Risk section: remaining assumptions, unresolved ambiguities, or accepted exceptions.

## 12. Mapping to Lecture Conversion Playbook
This spec pairs directly with [lecture-conversion-playbook.md](./lecture-conversion-playbook.md):
1. Architecture contract maps to playbook stages for mapping and structural conversion.
2. HTML rules map to content normalization stage.
3. CSS and JS rules map to alignment and regression checks stage.
4. Accessibility and validation checklist map to verification and release gate stage.

## 13. Governance
1. Update this spec when repeat lecture patterns change.
2. Record version/date changes in the change log.
3. Keep examples and checklist lines synchronized with real lecture implementation patterns.
4. Do not relax structural requirements without updating conversion and prompt docs.

## 14. Change Log
- 1.0-draft: Expanded from skeleton to full draft, aligned to current lecture slideshow structure and schedule/accordion patterns.
- 0.1-draft: Initial skeleton.
