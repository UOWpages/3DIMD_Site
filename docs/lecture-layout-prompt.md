# Lecture Layout Prompt

Quick invocation template (copy/paste and replace TARGET_LECTURE):

```text
Apply docs/lecture-layout-prompt.md exactly to TARGET_LECTURE. No improvisation. Preserve wording/casing unless readability or correctness requires targeted fixes. If uncertain, stop and ask before editing.

Do not add tutorial wrappers or tutorial-only component patterns.
Do not rewrite lecture content intent.
Do not perform broad refactors.
Only make structural/tag/class changes required for PASS.

Before finishing, report PASS/FAIL for:
- Slide shell and frame structure consistency
- Required regions present on every scoped slide (title, content, controls/footer, keyboard hint)
- Slide type pattern fit (text/accordion/schedule/table/media/reference)
- Content overflow and scrolling behavior
- Typography/readability consistency
- Schedule card and deadline callout consistency (where applicable)
- Link and iframe safety requirements
- Navigation button state behavior
- Keyboard navigation behavior
- Counter behavior correctness
- Footer/logo/control arrangement consistency
- Tutorial-pattern contamination check
- Unscoped CSS/JS regression risk check

If any item is FAIL, continue editing and re-run checks until all mandatory items PASS.
```

Use [docs/final-lecture-template-spec.md](./final-lecture-template-spec.md) as the authoritative lecture output standard and [docs/lecture-conversion-playbook.md](./lecture-conversion-playbook.md) as the operational conversion procedure.

Locked execution contract for every use:

- Apply this prompt exactly with no improvisation.
- Preserve existing wording and casing unless the task explicitly asks for rewrite.
- If any instruction is ambiguous, stop and ask before editing.
- Make only the minimum structural/tag/class changes needed to achieve checklist PASS.
- Do not move lecture content across unrelated slides unless explicitly required by mapping/scope.
- Do not add tutorial-only wrappers, classes, or pseudo-code presentation patterns.
- Keep navigation, counter, and control behavior intact.

Follow these rules exactly:

1. Keep lecture slide shell structure consistent across scoped slides.
2. Keep required per-slide regions present: title, content, controls/footer, keyboard hint.
3. Keep slide content aligned to one primary slide type pattern:
3a. text,
3b. accordion,
3c. schedule,
3d. table,
3e. media-heavy,
3f. reference.
4. Keep content overflow inside intended content panes/scroll containers.
5. Keep schedule content chronological and represented by repeatable schedule-card pattern.
6. Keep deadlines represented by consistent deadline callout pattern.
7. Keep external links safe with `target="_blank"` and `rel="noopener noreferrer"` together where off-site.
8. Keep embedded iframes in approved containers and include `loading="lazy"` unless an explicit exception is required.
9. Keep navigation controls functionally consistent: previous/next disabled states at boundaries must remain correct.
10. Keep keyboard navigation behavior consistent with button navigation.
11. Keep counter behavior correct for current/total slide display.
12. Keep footer/logo/control arrangement consistent with lecture template behavior.
13. Keep CSS additions scoped to lecture components; avoid global leakage.
14. Keep JS behavior changes minimal and idempotent; do not break normalization expectations.
15. Keep accessibility baseline: keyboard operability, meaningful alt text, readable heading order.
16. Keep minimal-diff discipline: no unrelated cleanup/reflow.

Before finishing, run this mandatory PASS/FAIL checklist and report each line explicitly:

- Slide shell and frame structure is consistent: PASS/FAIL
- Required per-slide regions are present: PASS/FAIL
- Slide type pattern matches content intent: PASS/FAIL
- Overflow and scrolling behavior is compliant: PASS/FAIL
- Typography and spacing are readable and consistent: PASS/FAIL
- Schedule cards/deadline callouts are consistent where applicable: PASS/FAIL
- External links use required safety attributes: PASS/FAIL
- Embedded iframes follow loading/container rules: PASS/FAIL
- Navigation boundary states are correct: PASS/FAIL
- Keyboard navigation matches button navigation: PASS/FAIL
- Counter current/total behavior is correct: PASS/FAIL
- Footer/logo/control arrangement is consistent: PASS/FAIL
- No tutorial-only wrappers/patterns are present: PASS/FAIL
- No unscoped CSS/JS regressions introduced: PASS/FAIL
- Accessibility baseline checks pass: PASS/FAIL

Required integrity checks (in addition to visual review):

- Confirm first and last slide control states are correct.
- Confirm one active slide state at a time.
- Confirm counter updates after navigation.
- Confirm no tutorial-specific components were introduced.
- Confirm schedule chronology is preserved when schedule content exists.

Enforcement:

- If any checklist item is FAIL, do not stop.
- Continue minimal edits and re-run checklist until all mandatory items are PASS.
- Only finish after all mandatory checklist items are PASS, or after an explicit blocker is documented and approved.

If the source lecture already follows the final template, preserve structure and only change the scoped content, links, embeds, or styles required by the task.
