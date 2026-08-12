# Lecture Prompt Template

Use this template to check and convert lecture slides with low-risk, minimal-diff edits.

## Pass 1: Audit Only (No Edits)

Replace TARGET_LECTURE with a specific lecture file path and scope.

```text
Audit TARGET_LECTURE against docs/lecture-layout-prompt.md exactly.
Do not edit yet.
Report only:
- PASS/FAIL for each mandatory lecture checklist item
- Exact slide-indexed locations of each FAIL
- Minimal edit plan in execution order
- Source-to-slide mapping summary for scoped slides
- Schedule/deadline normalization check (if schedule content exists)
- Media sequence and in-flow placement check (if source artifacts exist)
If anything is ambiguous, ask before editing.
```

## Pass 2: Apply Minimal Edits

```text
Apply the minimal edits needed to make every mandatory lecture checklist item PASS for TARGET_LECTURE, following docs/lecture-layout-prompt.md exactly and .github/copilot-instructions.md.
Hard constraints:
- Change only what is required for PASS
- Do not alter unrelated wording, structure, spacing, or formatting
- No cleanup/refactor beyond requested fixes
- Preserve lecture-only boundaries (do not introduce tutorial wrappers/patterns)
- Preserve slide shell behavior, navigation, counters, and footer consistency
After editing, run the checklist again and report PASS/FAIL for every line.
```

## Pass 3: Verification Lock (Recommended)

```text
Re-open TARGET_LECTURE and re-verify all mandatory lecture checklist items.
If any item is FAIL, fix only that item and re-run until all PASS.
Return a final summary with:
- Files changed
- Slide range covered
- Exactly what changed
- Anything intentionally left unchanged
- Remaining risks/assumptions
```

## One-Shot Alternative

```text
Apply docs/lecture-layout-prompt.md to TARGET_LECTURE with strict adherence to .github/copilot-instructions.md.
Workflow required:
1. Audit first and list PASS/FAIL before edits.
2. Perform only minimal edits required to convert FAIL to PASS.
3. Re-audit and report full PASS/FAIL checklist.
4. If any FAIL remains, continue minimal edits until all mandatory items PASS.
Do not change anything unrelated to checklist failures.
```

## Usage Tip

Always specify an exact target file path and slide scope (for example: site/lectures/lect-01a.html, slides 5-9) to avoid accidental broad edits.
