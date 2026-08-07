# Documentation Overview

## Purpose

This document summarizes how editing preferences, prompt templates, and project instruction documents are organized and used.

## Active Instruction Layers

1. Global repo behavior: [.github/copilot-instructions.md](../.github/copilot-instructions.md)
2. Tutorial-page execution contract: [docs/tutorial-layout-prompt.md](./tutorial-layout-prompt.md)
3. Reusable prompting workflow: [docs/prompt-template.md](./prompt-template.md)
4. General authoring standards: [docs/authoring-guide.md](./authoring-guide.md)
5. Migration/process reference: [docs/migration-plan.md](./migration-plan.md)

## Rule Precedence

For tutorial pages, use this precedence order:

1. Direct user request in the current task
2. [docs/tutorial-layout-prompt.md](./tutorial-layout-prompt.md) (authoritative tutorial spec)
3. [.github/copilot-instructions.md](../.github/copilot-instructions.md) (global minimal-diff behavior)
4. [docs/authoring-guide.md](./authoring-guide.md) (general guidance)
5. [docs/migration-plan.md](./migration-plan.md) (reference/history)

## Editing Preferences in Practice

Current expected behavior for page edits:

- Make the minimum change required for the task.
- Do not modify unrelated wording, structure, spacing, or formatting.
- Do not perform cleanup/refactors unless explicitly requested.
- Preserve wording/casing unless a rewrite is explicitly requested.
- If an instruction is ambiguous, ask before editing.

## Tutorial Layout Prompt Role

[docs/tutorial-layout-prompt.md](./tutorial-layout-prompt.md) is the strict tutorial-page rulebook. It defines:

- canonical structure reference page
- required pseudo-code presentation pattern
- ordered-list nesting and marker-style constraints
- mandatory PASS/FAIL checklist and integrity checks
- enforcement to continue until all checks pass

## Why Keep Multiple Docs

- [docs/tutorial-layout-prompt.md](./tutorial-layout-prompt.md): strict, task-execution rules for tutorial pages.
- [.github/copilot-instructions.md](../.github/copilot-instructions.md): global repo editing behavior.
- [docs/authoring-guide.md](./authoring-guide.md): broader authoring standards beyond tutorial-specific edge cases.
- [docs/migration-plan.md](./migration-plan.md): migration provenance and process record.
- [docs/prompt-template.md](./prompt-template.md): copy/paste prompt patterns for low-error workflows.

## Recommended Prompt Workflow

Use the 3-pass approach from [docs/prompt-template.md](./prompt-template.md):

1. Audit-only pass (no edits)
2. Minimal-edit pass to convert FAIL to PASS
3. Verification pass to confirm all PASS

For low ambiguity, always specify an exact target file path in your prompt.
