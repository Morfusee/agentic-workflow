# Link Insertion Modal Implementation Plan (PROJ-158)

> **For agentic workers:** REQUIRED SUB-SKILL: Use $subagent-driven-development (recommended) or $executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the `window.prompt("Link URL")` link insertion in the editor toolbar with an in-app modal containing URL and link-text fields.

**Architecture:** New `LinkDialog` component (feature-local, under `features/markdown/components/editor/`) owns open state, fields, URL validation, and link insertion. The toolbar's Link button becomes the dialog trigger. Uses existing `@/components/ui/dialog` and `@/components/ui/field` primitives — no new dependencies. Reuses `@platejs/link`'s `upsertLink` (selection path) and `insertLink` (no-selection path, inserts label + link).

**Tech Stack:** React 19, Plate 53 (`platejs`), `@platejs/link`, Base UI Dialog, Vitest + Testing Library.

---

## File Structure

- **Create:** `nextjs/features/markdown/components/editor/link-dialog.tsx` — the dialog: props `{ editor: PlateEditor }`, internal `open`/`url`/`text` state, validation, insertion logic. Renders the Link `ToolbarButton` as its trigger so the toolbar keeps its visual group.
- **Modify:** `nextjs/features/markdown/components/editor/editor-toolbar.tsx` — remove the `insertLink` helper and its `window.prompt`; render `<LinkDialog editor={editor} />` in place of the Link button; drop now-unused `upsertLink` import.
- **Create:** `nextjs/__tests__/unit/features/markdown/components/link-dialog.test.tsx` — component tests for open/insert/cancel/validation/no-selection paths.
- **Create:** `nextjs/__tests__/unit/features/markdown/components/link-dialog.insert.test.ts` — pure insertion-logic tests (selection vs no-selection), no DOM needed.

Design doc: `memory/docs/superpowers/specs/2026-08-03-link-insertion-modal-design.md` (committed).

---

### Task 1: Extract pure link-insertion logic

**Files:**
- Create: `nextjs/features/markdown/components/editor/link-dialog-insert.ts`
- Test: `nextjs/__tests__/unit/features/markdown/components/link-dialog.insert.test.ts`

- [ ] **Step 1: Write the failing tests**

```ts
import { describe, expect, it, vi } from "vitest";

import { insertLinkFromDialog } from "@/features/markdown/components/editor/link-dialog-insert";

const editor = {
  api: { string: vi.fn(() => "") },
  tf: { focus: vi.fn(), insertNodes: vi.fn() },
};

vi.mock("@platejs/link", () => ({
  upsertLink: vi.fn(),
  insertLink: vi.fn(),
}));

import { insertLink as insertLinkMock, upsertLink as upsertLinkMock } from "@platejs/link";

describe("insertLinkFromDialog", () => {
  it("wraps the selection with upsertLink when text is selected", () => {
    vi.mocked(editor.api.string).mockReturnValue("selected words");
    const result = insertLinkFromDialog(editor as never, "https://example.com", "selected words");

    expect(result).toBe(true);
    expect(editor.tf.focus).toHaveBeenCalledTimes(1);
    expect(upsertLinkMock).toHaveBeenCalledWith(editor, {
      target: "_blank",
      url: "https://example.com",
    });
  });

  it("inserts label + link when nothing is selected", () => {
    const result = insertLinkFromDialog(editor as never, "https://example.com", "My link");

    expect(result).toBe(true);
    expect(editor.tf.focus).toHaveBeenCalledTimes(1);
    expect(insertLinkMock).toHaveBeenCalledWith(editor, {
      target: "_blank",
      url: "https://example.com",
      text: "My link",
    });
  });

  it("returns false and does not touch the editor when url is empty", () => {
    const result = insertLinkFromDialog(editor as never, "", "My link");

    expect(result).toBe(false);
    expect(editor.tf.focus).not.toHaveBeenCalled();
  });

  it("returns false and does not touch the editor when url is invalid", () => {
    const result = insertLinkFromDialog(editor as never, "example.com", "My link");

    expect(result).toBe(false);
    expect(editor.tf.focus).not.toHaveBeenCalled();
  });

  it("returns false and does not touch the editor when text is empty and nothing is selected", () => {
    const result = insertLinkFromDialog(editor as never, "https://example.com", "");

    expect(result).toBe(false);
    expect(editor.tf.focus).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run (workdir `nextjs`): `pnpm vitest run __tests__/unit/features/markdown/components/link-dialog.insert.test.ts`

Expected: FAIL — module `link-dialog-insert` not found.

- [ ] **Step 3: Write the implementation**

Create `nextjs/features/markdown/components/editor/link-dialog-insert.ts`:

```ts
import { insertLink, upsertLink } from "@platejs/link";
import type { PlateEditor } from "platejs/react";

export function isValidLinkUrl(url: string): boolean {
  return url.startsWith("http://") || url.startsWith("https://");
}

export function insertLinkFromDialog(
  editor: PlateEditor,
  url: string,
  text: string,
): boolean {
  const trimmedUrl = url.trim();
  if (!isValidLinkUrl(trimmedUrl)) return false;
  if (!text.trim()) return false;

  editor.tf.focus();

  const hasSelection = editor.api.string() !== "";
  if (hasSelection) {
    upsertLink(editor, { target: "_blank", url: trimmedUrl });
  } else {
    insertLink(editor, { target: "_blank", url: trimmedUrl, text: text.trim() });
  }

  return true;
}
```

Note: `editor.api.string()` returns the selected text; empty string means collapsed/no selection.

- [ ] **Step 4: Run tests to verify they pass**

Run (workdir `nextjs`): `pnpm vitest run __tests__/unit/features/markdown/components/link-dialog.insert.test.ts`

Expected: 5 passing.

- [ ] **Step 5: Commit**

```bash
git add nextjs/features/markdown/components/editor/link-dialog-insert.ts nextjs/__tests__/unit/features/markdown/components/link-dialog.insert.test.ts
git commit -m "feat(editor): add pure link insertion logic for link dialog"
```

---

### Task 2: Build the LinkDialog component

**Files:**
- Create: `nextjs/features/markdown/components/editor/link-dialog.tsx`
- Test: `nextjs/__tests__/unit/features/markdown/components/link-dialog.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";

vi.mock("@/features/markdown/components/editor/link-dialog-insert", () => ({
  insertLinkFromDialog: vi.fn(() => true),
}));

vi.mock("@platejs/link", () => ({
  insertLink: vi.fn(),
  upsertLink: vi.fn(),
}));

import { insertLinkFromDialog } from "@/features/markdown/components/editor/link-dialog-insert";
import { LinkDialog } from "@/features/markdown/components/editor/link-dialog";

const editorMock = {
  api: { string: vi.fn(() => "") },
  tf: { focus: vi.fn() },
};

function renderDialog() {
  return render(<LinkDialog editor={editorMock as never} />);
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("LinkDialog", () => {
  it("opens from the toolbar Link button without using window.prompt", () => {
    const promptSpy = vi.spyOn(window, "prompt").mockImplementation(() => "");
    renderDialog();

    fireEvent.click(screen.getByLabelText("Link"));

    expect(screen.getByLabelText("URL")).toBeInTheDocument();
    expect(promptSpy).not.toHaveBeenCalled();
    promptSpy.mockRestore();
  });

  it("pre-fills the link text field from the editor selection", () => {
    vi.mocked(editorMock.api.string).mockReturnValue("selected words");
    renderDialog();

    fireEvent.click(screen.getByLabelText("Link"));

    expect((screen.getByLabelText("Link text") as HTMLInputElement).value).toBe(
      "selected words",
    );
  });

  it("inserts the link on confirm and closes", () => {
    renderDialog();
    fireEvent.click(screen.getByLabelText("Link"));

    fireEvent.change(screen.getByLabelText("URL"), {
      target: { value: "https://example.com" },
    });
    fireEvent.change(screen.getByLabelText("Link text"), {
      target: { value: "My link" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Insert link" }));

    expect(insertLinkFromDialog).toHaveBeenCalledWith(
      editorMock,
      "https://example.com",
      "My link",
    );
    await waitFor(() =>
      expect(screen.queryByLabelText("URL")).not.toBeInTheDocument(),
    );
  });

  it("closes without inserting on cancel", () => {
    renderDialog();
    fireEvent.click(screen.getByLabelText("Link"));
    fireEvent.change(screen.getByLabelText("URL"), {
      target: { value: "https://example.com" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(insertLinkFromDialog).not.toHaveBeenCalled();
    expect(screen.queryByLabelText("URL")).not.toBeInTheDocument();
  });

  it("closes without inserting when URL is empty", () => {
    renderDialog();
    fireEvent.click(screen.getByLabelText("Link"));

    fireEvent.click(screen.getByRole("button", { name: "Insert link" }));

    expect(insertLinkFromDialog).not.toHaveBeenCalled();
    expect(screen.queryByLabelText("URL")).not.toBeInTheDocument();
  });

  it("shows an inline error when insertion is rejected and keeps the dialog open", () => {
    vi.mocked(insertLinkFromDialog).mockReturnValue(false);
    renderDialog();
    fireEvent.click(screen.getByLabelText("Link"));

    fireEvent.change(screen.getByLabelText("URL"), {
      target: { value: "example.com" },
    });
    fireEvent.change(screen.getByLabelText("Link text"), {
      target: { value: "My link" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Insert link" }));

    expect(
      screen.getByText(
        "Enter a valid URL starting with http:// or https://.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("URL")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run (workdir `nextjs`): `pnpm vitest run __tests__/unit/features/markdown/components/link-dialog.test.tsx`

Expected: FAIL — module `link-dialog` not found.

- [ ] **Step 3: Write the implementation**

Create `nextjs/features/markdown/components/editor/link-dialog.tsx`:

```tsx
"use client";

import { useState } from "react";
import { LinkIcon } from "lucide-react";
import type { PlateEditor } from "platejs/react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

import { EditorToolbarButton as ToolbarButton } from "./editor-toolbar-button";
import { insertLinkFromDialog } from "./link-dialog-insert";

type LinkDialogProps = {
  editor: PlateEditor;
};

export function LinkDialog({ editor }: LinkDialogProps) {
  const [open, setOpen] = useState(false);
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleOpenChange = (nextOpen: boolean) => {
    setOpen(nextOpen);
    if (nextOpen) {
      setUrl("");
      setText(editor.api.string());
      setError(null);
    }
  };

  const handleInsert = () => {
    if (!url.trim()) {
      setOpen(false);
      return;
    }

    const inserted = insertLinkFromDialog(editor, url, text);
    if (!inserted) {
      setError("Enter a valid URL starting with http:// or https://.");
      return;
    }

    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger
        render={
          <ToolbarButton label="Link">
            <LinkIcon aria-hidden className="size-4" />
          </ToolbarButton>
        }
      />
      <DialogContent showCloseButton={false}>
        <DialogHeader>
          <DialogTitle>Add link</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4">
          <Field>
            <FieldLabel htmlFor="link-url">URL</FieldLabel>
            <Input
              id="link-url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              autoFocus
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="link-text">Link text</FieldLabel>
            <Input
              id="link-text"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </Field>
          <p
            role="alert"
            className={cn(
              "min-h-5 text-sm font-medium",
              error ? "text-destructive" : "text-muted-foreground",
            )}
            aria-live="polite"
          >
            {error ?? "Leave link text empty to use your selected text."}
          </p>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleInsert}>Insert link</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

Note: the `FieldError`-style inline error uses an `aria-live` paragraph; if `FieldError` from `@/components/ui/field` fits better with your copy, it is an accepted drop-in (the test only asserts the message text). If `render` prop on `DialogTrigger` is unsupported by the installed Base UI version, fall back to wrapping the button as a child — verify against `dialog.tsx` exports at implementation time.

- [ ] **Step 4: Run tests to verify they pass**

Run (workdir `nextjs`): `pnpm vitest run __tests__/unit/features/markdown/components/link-dialog.test.tsx`

Expected: 6 passing. If the `render` prop on `DialogTrigger` fails to typecheck, switch to child-based trigger and re-run.

- [ ] **Step 5: Commit**

```bash
git add nextjs/features/markdown/components/editor/link-dialog.tsx nextjs/__tests__/unit/features/markdown/components/link-dialog.test.tsx
git commit -m "feat(editor): add link insertion dialog component"
```

---

### Task 3: Wire the dialog into the editor toolbar

**Files:**
- Modify: `nextjs/features/markdown/components/editor/editor-toolbar.tsx`

- [ ] **Step 1: Update the toolbar**

In `nextjs/features/markdown/components/editor/editor-toolbar.tsx`:

1. Remove the `upsertLink` import (line 25: `import { upsertLink } from "@platejs/link";`).
2. Add import: `import { LinkDialog } from "./link-dialog";`.
3. Replace the Link `ToolbarButton` (lines 109-111) with:

```tsx
<LinkDialog editor={editor} />
```

4. Delete the `insertLink` function (lines 170-176, the `window.prompt` block).

- [ ] **Step 2: Verify no orphaned code**

Run (workdir `nextjs`): `rg -n "window.prompt|upsertLink|insertLink" features/markdown/components/editor/editor-toolbar.tsx`

Expected: no matches (the toolbar no longer references prompt or link helpers).

- [ ] **Step 3: Run lint and typecheck**

Run (workdir `nextjs`): `pnpm lint && pnpm typecheck`

Expected: both pass with no errors.

- [ ] **Step 4: Run the markdown feature unit tests**

Run (workdir `nextjs`): `pnpm vitest run __tests__/unit/features/markdown`

Expected: all existing + new tests pass.

- [ ] **Step 5: Commit**

```bash
git add nextjs/features/markdown/components/editor/editor-toolbar.tsx
git commit -m "feat(editor): open link dialog from toolbar instead of window.prompt"
```

---

### Task 4: Manual verification

**Files:** none (manual browser check)

- [ ] **Step 1: Start the dev server**

Run (workdir `nextjs`): `pnpm dev:plain`

- [ ] **Step 2: Verify the acceptance criteria**

1. Open an existing document's editor. Select some text, click the toolbar Link button.
   - Expected: an in-app modal opens with URL and Link text fields (Link text pre-filled with the selection); no browser `prompt`.
2. Enter `https://example.com`, click Insert link.
   - Expected: the selected text becomes a `_blank` link.
3. Deselect everything, click Link, enter a URL and a link text label, insert.
   - Expected: label + link inserted together.
4. Click Link, enter an invalid URL (`example.com`), insert.
   - Expected: inline error, dialog stays open, nothing inserted.
5. Click Link, click Cancel.
   - Expected: dialog closes, document unchanged.
6. Click Link, click Insert link with an empty URL.
   - Expected: dialog closes, document unchanged.

- [ ] **Step 3: Report results**

Report pass/fail per criterion in the chat thread before the ticket comment stage.

---

## Self-Review

**Spec coverage:** Objective (modal replaces prompt) — Task 2/3. URL + link-text fields — Task 2. Pre-filled editable selection — Task 2. No-selection insert — Task 1. `_blank` target — Task 1. Cancel/empty URL no-op — Tasks 1-2. Validation error — Task 2. No new deps — Task 2 (existing primitives only). Non-goals untouched (link tooltip, plugin config) — no tasks touch them.

**Placeholder scan:** No TBD/TODO; all code shown inline.

**Type consistency:** `insertLinkFromDialog(editor, url, text)` used identically in Task 1 implementation and Task 2 tests. `editor.api.string()` used in both `link-dialog-insert.ts` and `link-dialog.tsx`. `LinkDialog` prop `{ editor: PlateEditor }` matches toolbar usage.
