# Markdown2Share Plate Editor Handoff

## Purpose

This handoff documents what changed in the current session for future reference only. The requested implementation was a first vertical slice for a Plate-powered Markdown/rich text editor while keeping Markdown as the canonical persisted format.

## Current State

The implementation is present in the working tree of `$HOME/Documents/Programming/markdown2share`. It has not been committed in this session.

Reference the current repository diff for exact implementation details instead of duplicating code here.

## Main Changes To Reference

- Added Plate editor dependencies in `package.json` and `pnpm-lock.yaml`.
- Added authenticated document editor routes:
  - `app/(auth)/app/documents/new/page.tsx`
  - `app/(auth)/app/documents/[documentId]/edit/page.tsx`
- Added Markdown draft persistence action/service:
  - `features/markdown/actions/document-draft.action.ts`
  - `features/markdown/services/document-draft.service.ts`
- Added editor UI and Plate plugin setup:
  - `features/markdown/components/editor/plate-plugins.tsx`
  - `features/markdown/components/editor/markdown-rich-editor.tsx`
  - `features/markdown/components/editor/editor-toolbar.tsx`
  - `features/markdown/components/editor/editor-shell.tsx`
  - `features/markdown/components/editor/index.ts`
- Updated dashboard create UI in `app/(auth)/app/page.tsx` so “Create new file” opens `/app/documents/new`; upload remains disabled.

## Important Design Boundary

Markdown remains canonical.

- Draft saves write `documents.currentDraftMarkdown` only.
- No Plate/Slate JSON is persisted.
- The editor uses `@platejs/markdown` and `MarkdownPlugin` for conversion.
- GFM is configured with `remark-gfm` through `MarkdownPlugin.configure(...)`.

Reference files:

- `features/markdown/components/editor/plate-plugins.tsx`
- `features/markdown/components/editor/markdown-rich-editor.tsx`
- `features/markdown/services/document-draft.service.ts`

## Verification From This Session

- `pnpm build` passed.
- `pnpm lint` failed only on pre-existing unrelated lint issues in:
  - `components/blocks/form/field-controller.tsx`
  - `components/blocks/form/field-input.tsx`
  - `components/blocks/form/form-context.tsx`
  - `components/ui/dropzone.tsx`
- New editor lint issues found during implementation were fixed before final response.

## Known Limitations

- Manual browser/database verification was not performed.
- Upload Markdown remains intentionally disabled.
- New document creation uses an owner-scoped default collection policy instead of a collection picker.
- No publishing UX, revision history UI, comments, collaboration, AI, slash commands, or sharing controls were added.

## Suggested Skills

- `requirements-reviewer`: use if validating the implementation against the original prompt/acceptance criteria.
- `review-orchestrator`: use if a broader code review is requested for the working tree changes.
- `react-quality-review`: use for focused React/TypeScript quality review of the editor components.
- `impeccable`: use if continuing UI polish or browser-based UX/a11y review of the editor surface.
- `backend-dev-guidelines`: use if changing the draft action/service, authorization, or Drizzle persistence behavior.
- `workflow-orchestrator`: use if this work is later connected to Linear, ClickUp, Notion, or ticket publishing workflows.

## Notes For Fresh Agent

- Start by reading `AGENTS.md` in the repo and current `git status`/`git diff`.
- Treat the current working tree as intentional user-owned work.
- Do not add a custom Markdown serializer/deserializer.
- Do not add Tiptap.
- Do not change DB schema unless a future requirement explicitly blocks on it.
- Redacted: no secrets, tokens, passwords, or PII are included in this handoff.
