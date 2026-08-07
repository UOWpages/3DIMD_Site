# Copilot Instructions

## Scope
These instructions define repo-wide working behavior for edits in this workspace.

## Global Editing Rules
- Make the minimum change required for the user request.
- Do not modify unrelated content, structure, wording, spacing, or formatting.
- Do not perform cleanup, refactors, or style normalization unless explicitly requested.
- If a request is ambiguous, ask before editing.
- Preserve existing wording and casing unless a rewrite is explicitly requested.

## Tutorial Layout Layer
- For tutorial page structure and pseudo-code formatting rules, apply [docs/tutorial-layout-prompt.md](../docs/tutorial-layout-prompt.md) exactly when the user requests tutorial layout/template adherence.
- When applying that prompt, do not improvise beyond the documented rules.

## Conflict Handling
- If user request conflicts with this file, follow the direct user request for that task.
- If [docs/tutorial-layout-prompt.md](../docs/tutorial-layout-prompt.md) conflicts with a direct user request, follow the direct user request and keep all other changes minimal.
