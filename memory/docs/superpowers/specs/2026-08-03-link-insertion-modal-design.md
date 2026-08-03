# Design: Link Insertion Modal for Editor Toolbar (PROJ-158)

Date: 2026-08-03
Status: Approved (design), pending user review of this spec
Provider: Notion Coding Projects Tracker — PROJ-158 "Add link insertion modal to editor toolbar" (Not Started, Feature)

## Objective

Replace the native `window.prompt("Link URL")` dialog used by the editor's Link toolbar button with an in-app modal. Link insertion uses the app's own UI and accessibility patterns (existing `@/components/ui/dialog` + `@/components/ui/input` primitives, no new dependencies).

## Scope

- New component `nextjs/features/markdown/components/editor/link-dialog.tsx` that owns dialog open state, URL and link-text fields, URL validation, and link insertion.
- `editor-toolbar.tsx` renders the dialog (with the Link toolbar button as its trigger) instead of calling `window.prompt`.
- The modal includes a URL input **and** a link-text field (user decision: Option B).
  - When text is selected in the editor, the link-text field is pre-filled with the selection and editable.
  - When nothing is selected, the user can type a label; the editor inserts text + link together.
- Keep existing behavior: `editor.tf.focus()` before `upsertLink`, `target: "_blank"`, cancel or empty URL is a no-op, cancel closes the modal without modifying the document.

## Non-Goals

- Editing or removing existing links (only the insert dialog is replaced).
- Link tooltip (`link-tooltip.tsx`) behavior is untouched.
- No changes to `@platejs/link` plugin configuration.

## Architecture

### LinkDialog component (`features/markdown/components/editor/link-dialog.tsx`)

- `"use client"`.
- Props: `{ editor: PlateEditor }`.
- Internal state: `open`, `url`, `text`.
- Renders `Dialog` from `@/components/ui/dialog` with `DialogTrigger` wrapping the toolbar Link button (moved from `editor-toolbar.tsx`), so the toolbar keeps its visual grouping by rendering `<LinkDialog editor={editor} />` in place of the current Link button.
- On open: clear `url`; pre-fill `text` from the current editor selection (editable).
- Fields: URL input + link-text input using existing `Field`/`Input` primitives.
- Confirm behavior:
  - Validate URL starts with `http://` or `https://`; show inline field error otherwise.
  - On valid input, call `editor.tf.focus()` then `upsertLink(editor, { target: "_blank", url })` (selection path) or insert a link node with the typed label (no-selection path), then close.
  - If `text` is empty and nothing is selected, Insert is disabled.
- Cancel / Escape / empty URL closes without document changes.

### Validation

- Light validation: URL must start with `http://` or `https://`. Inline error message: "Enter a valid URL starting with http:// or https://".
- No auto-prepending of schemes (avoids surprising localhost/mailto cases).

## Data Flow

```
Toolbar Link button (DialogTrigger) -> LinkDialog open
  -> user fills URL (and link text if no selection)
  -> confirm -> validate -> editor.tf.focus() -> upsertLink / insert link node -> close
  -> cancel / empty URL -> close, no document change
```

No tRPC, persistence, or server involvement. `features/markdown` remains isolated (dialog is in `components/ui`, allowed).

## Testing

- `pnpm lint`, `pnpm typecheck`.
- Markdown feature unit tests if a test file exists for the editor components.
- Manual verification paths:
  - Select text, click Link, verify modal opens (no browser prompt), insert with `_blank` target.
  - No selection, type label + URL, verify text + link inserted together.
  - Cancel path: modal closes, document unchanged.
  - Empty URL: no-op, modal closes.
  - Invalid URL: inline error shown, nothing inserted.

## Files Touched

- `nextjs/features/markdown/components/editor/link-dialog.tsx` (new).
- `nextjs/features/markdown/components/editor/editor-toolbar.tsx` (replace `window.prompt` link insertion with dialog).
