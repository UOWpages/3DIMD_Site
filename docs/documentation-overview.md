# Documentation Overview

## Purpose

This document summarizes how all documentation in [docs/documentation-hub.md](./documentation-hub.md) is organized and how each file should be used.

## Active Instruction Layers

1. Global repo behavior: [.github/copilot-instructions.md](../.github/copilot-instructions.md)
2. Documentation system index: [docs/documentation-hub.md](./documentation-hub.md)
3. Final output standards:
4. [docs/final-tutorial-template-spec.md](./final-tutorial-template-spec.md)
5. [docs/final-lecture-template-spec.md](./final-lecture-template-spec.md)
6. Conversion procedures:
7. [docs/tutorial-conversion-playbook.md](./tutorial-conversion-playbook.md)
8. [docs/lecture-conversion-playbook.md](./lecture-conversion-playbook.md)
9. Prompt system:
10. [docs/prompt-strategy-catalog.md](./prompt-strategy-catalog.md)
11. [docs/tutorial-prompt-template.md](./tutorial-prompt-template.md)
12. [docs/lecture-prompt-template.md](./lecture-prompt-template.md)
13. Tutorial execution contract: [docs/tutorial-layout-prompt.md](./tutorial-layout-prompt.md)
14. Lecture execution contract: [docs/lecture-layout-prompt.md](./lecture-layout-prompt.md)
15. General authoring guidance: [docs/authoring-guide.md](./authoring-guide.md)
16. Migration reference/history: [docs/migration-reference.md](./migration-reference.md)

## Rule Precedence

Use this precedence order:

1. Direct user request in the current task.
2. [.github/copilot-instructions.md](../.github/copilot-instructions.md).
3. [docs/documentation-hub.md](./documentation-hub.md) and the relevant final template spec.
4. Relevant conversion playbook.
5. Prompt strategy and prompt templates.
6. [docs/authoring-guide.md](./authoring-guide.md).
7. [docs/migration-reference.md](./migration-reference.md) for historical reference.

For tutorial-page structure specifically, [docs/tutorial-layout-prompt.md](./tutorial-layout-prompt.md) remains the strict execution contract.

For lecture-slide structure and behavior checks, [docs/lecture-layout-prompt.md](./lecture-layout-prompt.md) is the strict execution contract.

## Current Roles by File

1. [docs/documentation-hub.md](./documentation-hub.md): canonical map for the documentation system.
2. [docs/final-tutorial-template-spec.md](./final-tutorial-template-spec.md): end-state tutorial standard.
3. [docs/final-lecture-template-spec.md](./final-lecture-template-spec.md): end-state lecture standard.
4. [docs/tutorial-conversion-playbook.md](./tutorial-conversion-playbook.md): tutorial conversion procedure.
5. [docs/lecture-conversion-playbook.md](./lecture-conversion-playbook.md): lecture and PPTX conversion procedure.
6. [docs/prompt-strategy-catalog.md](./prompt-strategy-catalog.md): prompt-family and mode contract rules.
7. [docs/tutorial-prompt-template.md](./tutorial-prompt-template.md): reusable pass-by-pass prompt text patterns.
8. [docs/lecture-prompt-template.md](./lecture-prompt-template.md): reusable pass-by-pass prompt text patterns for lecture workflows.
9. [docs/tutorial-layout-prompt.md](./tutorial-layout-prompt.md): strict tutorial execution checklist and enforcement.
10. [docs/lecture-layout-prompt.md](./lecture-layout-prompt.md): strict lecture execution checklist and enforcement.
11. [docs/authoring-guide.md](./authoring-guide.md): broad authoring conventions and component guidance.
12. [docs/migration-reference.md](./migration-reference.md): migration provenance, inventory, and metrics.

## Replaced, Complementary, or Conflicting

1. [docs/tutorial-layout-prompt.md](./tutorial-layout-prompt.md): not replaced; remains authoritative for tutorial structure rules.
2. [docs/tutorial-prompt-template.md](./tutorial-prompt-template.md): not replaced; still useful as tutorial execution wrapper template.
3. [docs/lecture-prompt-template.md](./lecture-prompt-template.md): new lecture execution wrapper template.
4. [docs/authoring-guide.md](./authoring-guide.md): not replaced; complementary general guidance.
5. [docs/migration-reference.md](./migration-reference.md): not replaced; reference/history rather than active rule source.
6. [docs/documentation-overview.md](./documentation-overview.md): current landscape summary and usage guide.

## Editing Preferences in Practice

Current expected behavior for page edits:

- Make the minimum change required for the task.
- Do not modify unrelated wording, structure, spacing, or formatting.
- Do not perform cleanup/refactors unless explicitly requested.
- Preserve wording/casing unless a rewrite is explicitly requested.
- If an instruction is ambiguous, ask before editing.

## Recommended Prompt Workflow

Use the 3-pass approach from:

1. [docs/tutorial-prompt-template.md](./tutorial-prompt-template.md) for tutorial pages.
2. [docs/lecture-prompt-template.md](./lecture-prompt-template.md) for lecture slides.

Both use:

1. Audit-only pass (no edits).
2. Minimal-edit pass to convert FAIL to PASS.
3. Verification pass to confirm all PASS.

For low ambiguity, always specify an exact target file path in your prompt.
