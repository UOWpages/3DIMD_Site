# Prompt Template

Use this template to check and format/style tutorial pages with the highest chance of low-error, minimal-diff edits.

## Pass 1: Audit Only (No Edits)

Replace TARGET_PAGE with a specific page path.

```text
Audit TARGET_PAGE against docs/tutorial-layout-prompt.md exactly.
Do not edit yet.
Report only:
- PASS/FAIL for each required checklist item in the prompt doc
- Exact locations of each FAIL
- Minimal edit plan (smallest possible changes)
- DOCX image-placement check result (if source DOCX exists): image sequence and in-flow anchors compared with TARGET_PAGE
If anything is ambiguous, ask before editing.
```

When auditing, also include the following consistency checks in the PASS/FAIL report if they apply to the page:

- HTML indentation/readability remains consistent with the canonical tutorial pages
- Page text is UTF-8 clean with no mojibake or encoding corruption
- External links include `target="_blank"` and `rel="noopener noreferrer"` together
- Embedded iframes include `loading="lazy"` unless the canonical pattern requires otherwise
- Simple text-only list items use one-line `<li>content</li>` formatting
- Simple text-only `h3` headings use one-line `<h3>Heading</h3>` formatting
- Major numbered tasks are represented as top-level accordion sections where applicable
- Task-scoped content remains inside its matching major numbered section

## Pass 2: Apply Minimal Edits

```text
Apply the minimal edits needed to make every checklist item PASS for TARGET_PAGE, following docs/tutorial-layout-prompt.md exactly and .github/copilot-instructions.md.
Hard constraints:
- Change only what is required for PASS
- Do not alter unrelated wording, structure, spacing, or formatting
- No cleanup/refactor beyond requested fixes
- If source DOCX exists, keep embedded images at the same in-flow anchor positions as the original DOCX sequence
After editing, run the checklist again and report PASS/FAIL for every line.
```

## Pass 3: Verification Lock (Optional, Recommended)

```text
Re-open TARGET_PAGE and re-verify all checklist items from docs/tutorial-layout-prompt.md.
If any item is FAIL, fix only that item and re-run until all PASS.
Return a final summary with:
- Files changed
- Exactly what changed
- Anything intentionally left unchanged
```

## One-Shot Alternative

```text
Apply docs/tutorial-layout-prompt.md to TARGET_PAGE with strict adherence to .github/copilot-instructions.md.
Workflow required:
1. Audit first and list PASS/FAIL before edits.
2. Perform only minimal edits required to convert FAIL to PASS.
3. Re-audit and report full PASS/FAIL checklist.
4. If any FAIL remains, continue minimal edits until all PASS.
Do not change anything unrelated to checklist failures.
```

## Usage Tip

Always use one concrete page path (for example: site/pages/tut-04-students.html) rather than saying "these pages" to reduce ambiguity and accidental extra edits.
