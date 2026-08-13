# Emojibake Strategy

Version: 1.0-draft
Last Updated: 2026-08-13
Status: Working Draft

## 1. Purpose and Scope
This document defines a practical strategy for detecting, preventing, and fixing mojibake and related encoding corruption in tutorial and lecture HTML content.

In scope:
1. Detection of mojibake patterns in repository text files.
2. Safe remediation patterns for HTML lecture and tutorial pages.
3. Verification and regression checks after fixes.
4. Integration guidance for conversion workflows.

Out of scope:
1. Re-authoring curriculum content.
2. Binary file repair for media assets.

## 2. Common Symptoms
Typical mojibake markers include:
1. Replacement-glyph-like sequences such as Ã¢â€ and Â artifacts.
2. Arrow/icon corruption in controls and hints.
3. Corrupted punctuation where en dash or em dash should appear.
4. Unexpected mixed encodings in one file.

High-risk areas:
1. Navigation labels and keyboard hints.
2. Imported PPTX-derived text blocks.
3. Files edited by multiple tools with different default encodings.

## 3. Root Cause Patterns
1. UTF-8 text interpreted as Windows-1252 or ISO-8859-1.
2. Windows-1252 text re-saved as UTF-8 without conversion intent.
3. Partial copy/paste from rich text sources.
4. Bulk replacement tools that do not preserve encoding.

## 4. Prevention Rules
1. Standardize on UTF-8 for HTML, CSS, JS, and Markdown.
2. Preserve existing file encoding when editing legacy content unless an intentional conversion is planned.
3. Prefer entity-safe arrows in controls and hints where presentation allows:
3a. &larr;
3b. &rarr;
4. Avoid mixed encoding edits in the same change set.
5. Keep fixes minimal and local to affected text.

## 5. Detection Workflow
Run a lightweight scan before and after conversion edits.

Recommended checks:
1. Search for common mojibake sequences.
2. Spot-check control labels and keyboard hints.
3. Compare rendered output in the index iframe flow.

Example scan targets:
1. Ã¢â€
2. Â
3. â†
4. ï¿½

## 6. Remediation Workflow
1. Identify the exact corrupted tokens and where they appear.
2. Replace only corrupted text, preserving structure and semantics.
3. Normalize recurring UI symbols using entities where appropriate.
4. Re-run scans and verify in rendered context.

Lecture and tutorial safe-fix guidance:
1. Keep slide/page structure unchanged while fixing text.
2. Do not combine encoding cleanup with unrelated refactors.
3. Re-verify navigation labels, counters, and hints after replacements.

## 7. Legacy Windows-1252 Handling
For legacy Windows-1252 tutorial files:
1. Prefer byte-safe insertion around stable ASCII anchors when possible.
2. Avoid broad text-mode rewrites that can recode unchanged characters.
3. Validate output in rendered page context, not only file text.

## 8. Validation Checklist
Report PASS/FAIL for each run:
1. No targeted mojibake markers remain in scoped files.
2. Control labels and keyboard hints render correctly.
3. External links and entities remain valid.
4. No structural regressions introduced during cleanup.
5. Index iframe rendering remains correct for scoped pages.

## 9. Integration with Conversion Docs
Use this strategy alongside:
1. tutorial-conversion-playbook.md
2. lecture-conversion-playbook.md
3. final-tutorial-template-spec.md
4. final-lecture-template-spec.md

## 10. Change Log
- 1.0-draft: Initial strategy for mojibake detection, remediation, and validation across lecture/tutorial conversion workflows.
