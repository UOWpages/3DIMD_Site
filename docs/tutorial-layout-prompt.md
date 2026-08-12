# Tutorial Layout Prompt

Quick invocation template (copy/paste and replace TARGET_PAGE):

```text
Apply docs/tutorial-layout-prompt.md exactly to TARGET_PAGE. No improvisation. Preserve wording/casing. Pseudo-code must match Tut 00 01 visual style exactly. If uncertain, stop and ask before editing.

Do not add wrappers not in template.
Do not use pre/code or markdown code blocks.
Do not move content across sections.
Do not rewrite script text.
Only make structural/tag/class changes needed to match template.
Keep ordered-list nesting valid: nested `ol` must be inside parent `li`, with no orphan `li` items and no duplicate closing tags.
For ordered-list marker styles, enforce this exact nesting sequence: top level decimal (`1.`), second level lower-alpha (`a.`), third level lower-roman (`i.`).

Before finishing, report PASS/FAIL for:
- Content wrapper
- Separate Video Resources accordion
- Raw video links left unembedded
- Raw article.embed-card outside nested video accordions
- Pseudo-code rendered as pre/code or markdown fences
- Pseudo-code styling matches Tut 00 01 line-by-line h3/p
- Duplicate media links blocks
- Unnecessary extra wrapper sections
- Nested list structure is valid (no orphan `li`, no `</li></li>`, parent/child `ol` nesting intact)
- Nested ordered-list marker styles follow `1.` -> `a.` -> `i.`

If any item is FAIL, continue editing and re-run checks until all PASS.
```

Use [site/pages/tut-00-01-student-version.html](../site/pages/tut-00-01-student-version.html) as the canonical structural template for tutorial pages.

This file is the authoritative tutorial-page specification. Where tutorial-page instructions differ, this file takes precedence over [docs/authoring-guide.md](./authoring-guide.md). [docs/migration-reference.md](./migration-reference.md) is process/reference only.

Locked execution contract for every use:

- Apply this prompt exactly with no improvisation.
- Preserve existing wording and casing unless the task explicitly asks to rewrite content.
- If any instruction is ambiguous, stop and ask before editing.
- Make only the minimum structural/tag/class changes needed to match Tut 00 01.
- Do not move content across sections unless the task explicitly requires it.
- Do not add wrappers or sections that are not in the canonical pattern.
- Do not rewrite script text inside pseudo-code blocks.

Follow these rules exactly:

1. Mirror the top-level wrapper hierarchy from Tut 00 01.
2. Keep the actual tutorial headings and sections as the top-level content.
2a. When a tutorial uses major numbered tasks (for example `7.1`, `7.2`, `7.3`), each major numbered task must be its own top-level `details.accordion` section.
2b. When a page includes Core Principles content, place that content in its own top-level `details.accordion` section.
3. Do not add a `Content` wrapper, a nested `Content` section, or any extra `section-card` wrapper around the page body.
4. Keep nested headings and ordered lists structured so numbering renders naturally.
5. When a video link appears in the content, replace it at that exact content location with the exact Tut 00 01 video component pattern: a nested `details.accordion.accordion--nested.video-accordion`, with the embed inside its `accordion-body`.
6. Apply that same exact nested video component pattern to both Panopto links and YouTube links.
7. Do not place a raw `article.embed-card` directly in the page flow; it must sit inside the nested video accordion component.
8. Do not create a separate Video Resources block if the videos already appear in their content locations.
9. Keep only page-specific content and links; remove duplicate media listings or redundant wrappers.
10. For pseudo-code content, match Tut 00 01 style exactly: line-by-line `h3`/`p` pseudo-code formatting, not Markdown code fences and not `pre`/`code` blocks.
11. Keep pseudo-code brace lines as their own lines (for example `h3` lines for `{` and `}`), and preserve the existing pseudo-code wording/casing unless a task explicitly asks to rewrite it.
12. If pseudo-code is split into multiple sections, place each pseudo-code block at the end of its matching tutorial section while keeping the same Tut 00 01 visual style.
13. Do not use `pre`/`code` blocks or Markdown code fences for pseudo-code under any circumstances.
14. Keep pseudo-code in the same visual pattern as Tut 00 01, including line-by-line `h3`/`p` presentation and standalone brace lines.
14a. CSS requirement: Pseudo-panel lines must have `white-space: normal;` to collapse formatting whitespace and maintain tight line spacing. Never use `white-space: pre;` on `.pseudo-panel__line` elements.
14b. Image interaction requirement: for Gyazo and other embedded figure images, clicking the image must expand it in-page, and clicking the expanded image/overlay must close it. Use caption wording `Gyazo preview (click image to expand).`
14c. HTML indentation/readability requirement: keep tutorial-page markup consistently indented and nested for human readability, matching the style of the canonical tutorial pages. Do not flatten or reflow markup unless required to fix structure.
14d. Encoding integrity requirement: keep page text UTF-8 clean and reject mojibake or other corrupted character output.
14e. External-link safety requirement: external links should include `target="_blank"` and `rel="noopener noreferrer"` together.
14f. Iframe loading requirement: embedded iframes should include `loading="lazy"` unless a specific exception is required by the canonical pattern.
14g. Simple `li` formatting requirement: when a list item has only inline text (no nested block content), prefer one-line markup as `<li>content</li>`.
14h. Simple `h3` formatting requirement: when a heading has only inline text (no nested tags/content), prefer one-line markup as `<h3>Heading</h3>`.
15. Maintain valid ordered-list semantics exactly: each nested `ol` must be inside its parent `li`, close tags in order, and never leave `li` items outside an `ol`.
16. Enforce ordered-list marker styles exactly as Tut 00 01: level 1 decimal (`1.`), level 2 lower-alpha (`a.`), level 3 lower-roman (`i.`).
17. Source placement requirement: when a source DOCX exists, embedded images (including Gyazo previews) must be placed at the same in-flow content locations as the original DOCX sequence, not moved into a separate media/reference section unless the source already does so.
18. Major numbered task sectioning requirement: content belonging to a major numbered task must remain inside that task's top-level accordion section, and extras/subtasks (for example `7.1a`, `7.1b`) must remain inside the matching parent task section unless the source clearly separates them.

Before finishing, run this mandatory PASS/FAIL checklist and report each line explicitly:

- Content wrapper: PASS/FAIL
- Major numbered task sections are present as top-level accordions where applicable: PASS/FAIL
- Separate Video Resources accordion: PASS/FAIL
- Raw video links left unembedded: PASS/FAIL
- Raw `article.embed-card` outside nested video accordions: PASS/FAIL
- Pseudo-code rendered as `pre`/`code` or Markdown fences: PASS/FAIL
- Pseudo-code styling matches Tut 00 01 line-by-line `h3`/`p`: PASS/FAIL
- Duplicate media links blocks: PASS/FAIL
- Unnecessary extra wrapper sections: PASS/FAIL
- Nested ordered-list structure valid (no orphan `li`, no `</li></li>`, correct parent/child nesting): PASS/FAIL
- Nested ordered-list marker styles are `1.` -> `a.` -> `i.`: PASS/FAIL
- Embedded images match original DOCX in-flow placement sequence: PASS/FAIL
- HTML indentation remains consistent with canonical tutorial-page readability style: PASS/FAIL
- Page text is UTF-8 clean with no mojibake: PASS/FAIL
- External links include `target="_blank"` and `rel="noopener noreferrer"` together: PASS/FAIL
- Embedded iframes include `loading="lazy"` unless the canonical pattern requires otherwise: PASS/FAIL
- Simple text-only list items use one-line `<li>content</li>` formatting: PASS/FAIL
- Simple text-only `h3` headings use one-line `<h3>Heading</h3>` formatting: PASS/FAIL
- Task-scoped content remains inside its matching major numbered section: PASS/FAIL

Required integrity checks (in addition to visual review):

- Confirm no `</li></li>` pattern exists.
- Confirm no `li` line appears directly after a closed `ol` where a parent `li`/`ol` wrapper is expected.
- Confirm nested ordered-list marker styles render as decimal at level 1, lower-alpha at level 2, and lower-roman at level 3.
- Confirm embedded image positions are checked against the original DOCX when available.

Enforcement:

- If any checklist item is FAIL, do not stop.
- Continue editing and re-run the checklist until all items are PASS.
- Only finish after all checklist items are PASS.

If the source page already follows Tut 00 01, preserve that structure and only change the page-specific text, links, and embeds.