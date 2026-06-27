# Create Collections Button Implementation Plan

> **For agentic workers:** Execute this plan task-by-task. Preserve existing work, follow the repository's `AGENTS.md` and `code-style.md`, and read the relevant bundled Next.js documentation before changing Server Actions.

**Goal:** Let authenticated users create root and nested collections from the library's existing Create menu.

**Architecture:** A route-local client component owns the existing Create dropdown and a collection dialog. It calls a typed Server Action that authenticates the user and delegates parent ownership checks to the collection service. The existing repository transaction creates the collection and owner role atomically, and TanStack Query refreshes the current library without navigation.

**Tech Stack:** Next.js 16 App Router, React 19, TypeScript, React Hook Form, Zod, TanStack Query, Drizzle ORM, PostgreSQL, and Playwright.

---

## Agent Guardrails

- Before editing, run `git status --short` and `git diff --` from the markdown2share repository.
- Treat every pre-existing change as user-owned. Do not revert, rewrite, or reformat it.
- Read `code-style.md` in full.
- Read `node_modules/next/dist/docs/01-app/01-getting-started/07-mutating-data.md` before editing the Server Action.
- Use the current codebase-memory index to confirm symbol names and callers before changing collection functions.
- Keep the implementation surgical. Do not add collection renaming, deleting, descriptions, icons, colors, drag-and-drop, or sibling-name uniqueness.
- Do not change the database schema or generate a migration; `collections.parentId` already exists.
- Do not change document creation behavior. The existing `/app/md/new` link and disabled Markdown upload item must remain intact.
- Use the existing `ok()`/`err()` action result convention, `MarkdownError`, repository/service boundaries, and form primitives.

## Success Criteria

- "Create collection" appears in the Create menu on the All and Folders root pages.
- It appears inside a collection only when the authenticated user owns the current collection.
- It does not appear anywhere in the Shared scope.
- The dialog accepts a trimmed name between 1 and 160 characters.
- Root collections persist `parentId: null`; nested collections persist the current collection ID.
- The server rejects malformed, missing, deleted, and non-owned parents.
- Collection creation and owner-role assignment remain in one database transaction.
- After success, the dialog closes and the new collection appears in the current table without navigation.
- Duplicate sibling names remain allowed because collection routes use UUIDs.
- `pnpm lint` and the focused Playwright workflow pass.

## File Map

Create:

- `features/markdown/schemas/collection.schema.ts` — shared client/server input contract.
- `features/markdown/actions/collection.action.ts` — authenticated Server Action and error mapping.
- `app/(auth)/app/_components/markdown-create-menu.tsx` — Create menu, dialog, form submission, and cache refresh.

Modify:

- `features/markdown/repositories/collection.repo.ts` — persist `parentId` and expose parent ownership.
- `features/markdown/services/collection.service.ts` — enforce parent existence and ownership.
- `features/markdown/types/collection.type.ts` — add breadcrumb ownership metadata.
- `app/(auth)/app/_components/markdown-library-page.tsx` — render the client menu with location context.
- `e2e/markdown-documents.spec.ts` — cover root, nested, validation, cancel, and Shared behavior.

Do not modify:

- `lib/db/schema.ts` or migration files.
- `/app/md/new` or editor save behavior.
- Library empty-state CTAs.
- Sharing or permission seed data.

---

## Task 1: Add Failing Browser Coverage

**Files:**

- Modify: `e2e/markdown-documents.spec.ts`

- [ ] **Step 1: Add a dialog-opening helper near the existing document helpers.**

```ts
async function openCreateCollectionDialog(page: Page) {
  await page.getByRole("button", { name: "Create" }).click();
  await page
    .getByRole("menuitem", { name: /Create collection/ })
    .click();

  await expect(
    page.getByRole("dialog", { name: "Create collection" }),
  ).toBeVisible();
}
```

- [ ] **Step 2: Add a root-creation test.**

```ts
test("creates a root collection from the library", async ({
  page,
}, testInfo) => {
  const name = uniqueTitle(testInfo, "root collection");

  await page.goto("/app");
  await openCreateCollectionDialog(page);
  await page.getByLabel("Collection name").fill(name);
  await page.getByRole("button", { name: "Create collection" }).click();

  await expect(
    page.getByRole("dialog", { name: "Create collection" }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("link", { name: `Open ${name}` }),
  ).toBeVisible({ timeout: 15000 });
});
```

- [ ] **Step 3: Add validation tests for empty and overlong names.**

```ts
test("validates collection names", async ({ page }) => {
  await page.goto("/app");
  await openCreateCollectionDialog(page);

  await page.getByRole("button", { name: "Create collection" }).click();
  await expect(
    page.getByText("Collection name is required."),
  ).toBeVisible();

  await page.getByLabel("Collection name").fill("x".repeat(161));
  await page.getByRole("button", { name: "Create collection" }).click();
  await expect(
    page.getByText("Collection name must be 160 characters or fewer."),
  ).toBeVisible();
});
```

- [ ] **Step 4: Add a nested-creation test.**

```ts
test("creates a collection inside the current owned collection", async ({
  page,
}, testInfo) => {
  const parentName = uniqueTitle(testInfo, "parent collection");
  const childName = uniqueTitle(testInfo, "child collection");

  await page.goto("/app");
  await openCreateCollectionDialog(page);
  await page.getByLabel("Collection name").fill(parentName);
  await page.getByRole("button", { name: "Create collection" }).click();

  await page.getByRole("link", { name: `Open ${parentName}` }).click();
  await expect(page).toHaveURL(/\/app\/[a-f0-9-]+$/);

  await openCreateCollectionDialog(page);
  await page.getByLabel("Collection name").fill(childName);
  await page.getByRole("button", { name: "Create collection" }).click();

  await expect(
    page.getByRole("link", { name: `Open ${childName}` }),
  ).toBeVisible({ timeout: 15000 });
});
```

- [ ] **Step 5: Add cancellation and Shared-scope tests.**

```ts
test("cancels collection creation", async ({ page }, testInfo) => {
  const name = uniqueTitle(testInfo, "cancelled collection");

  await page.goto("/app");
  await openCreateCollectionDialog(page);
  await page.getByLabel("Collection name").fill(name);
  await page.getByRole("button", { name: "Cancel" }).click();

  await expect(
    page.getByRole("dialog", { name: "Create collection" }),
  ).toHaveCount(0);
  await expect(page.getByText(name, { exact: true })).toHaveCount(0);
});

test("does not offer collection creation in Shared", async ({ page }) => {
  await page.goto("/app/shared");
  await page.getByRole("button", { name: "Create" }).click();

  await expect(
    page.getByRole("menuitem", { name: /Create collection/ }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("menuitem", { name: /Create new file/ }),
  ).toBeVisible();
});
```

- [ ] **Step 6: Run the focused tests and confirm they fail for the missing feature.**

```powershell
pnpm test e2e/markdown-documents.spec.ts --grep "collection"
```

Expected: the new tests fail because the Create menu has no "Create collection" item. Existing tests should not acquire new failures.

---

## Task 2: Define the Collection Input Contract

**Files:**

- Create: `features/markdown/schemas/collection.schema.ts`

- [ ] **Step 1: Create the shared Zod schema and inferred types.**

```ts
import { z } from "zod";

export const CREATE_COLLECTION_MAX_NAME_LENGTH = 160;

export const createCollectionSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "Collection name is required.")
    .max(
      CREATE_COLLECTION_MAX_NAME_LENGTH,
      `Collection name must be ${CREATE_COLLECTION_MAX_NAME_LENGTH} characters or fewer.`,
    ),
  parentId: z.uuid().nullish(),
});

export type CreateCollectionActionInput = z.input<
  typeof createCollectionSchema
>;

export type CreateCollectionFormData = z.infer<
  typeof createCollectionSchema
>;
```

Contract behavior:

```text
input name = "  Product Docs  "  -> parsed name = "Product Docs"
input name = "   "                -> field error
input name length = 161            -> field error
parentId = null or undefined       -> root collection
parentId = valid UUID              -> nested collection candidate
parentId = malformed string        -> field error before service execution
```

- [ ] **Step 2: Run the type checker.**

```powershell
pnpm lint
```

Expected: exit code `0`.

---

## Task 3: Extend Repository Persistence

**Files:**

- Modify: `features/markdown/repositories/collection.repo.ts`

- [ ] **Step 1: Extend the repository input without breaking default collection creation.**

```ts
export type CreateCollectionRecordData = {
  description?: string | null;
  name: string;
  ownerId: string;
  parentId?: string | null;
};
```

- [ ] **Step 2: Include ownership in the existing breadcrumb record lookup.**

```ts
return getDb().query.collections.findFirst({
  columns: {
    id: true,
    name: true,
    ownerId: true,
    parentId: true,
  },
  where: (collections, { and, eq, isNull }) =>
    and(eq(collections.id, id.data), isNull(collections.deletedAt)),
});
```

- [ ] **Step 3: Validate and persist the optional parent inside the existing transaction.**

Implementation pseudocode:

```ts
export async function createCollectionRecord({
  description = null,
  name,
  ownerId,
  parentId = null,
}: CreateCollectionRecordData) {
  const parsedOwnerId = markdownFileIdOnlySchema.safeParse(ownerId);
  const parsedParentId = parentId
    ? markdownFileIdOnlySchema.safeParse(parentId)
    : null;

  if (!parsedOwnerId.success) return undefined;
  if (parsedParentId && !parsedParentId.success) return undefined;

  return getDb().transaction(async (tx) => {
    const [collection] = await tx
      .insert(collections)
      .values({
        description,
        name,
        ownerId: parsedOwnerId.data,
        parentId: parsedParentId?.data ?? null,
      })
      .returning({ id: collections.id });

    const ownerRole = await tx.query.roles.findFirst({
      columns: { id: true },
      orderBy: (roles) => [desc(roles.rank)],
    });

    if (!ownerRole) throw new Error("Owner role not found");

    await tx.insert(userRoles).values({
      userId: parsedOwnerId.data,
      roleId: ownerRole.id,
      collectionId: collection.id,
    });

    return collection;
  });
}
```

Preserve the transaction so a collection cannot exist without its owner-role assignment. Keep `getDefaultCollectionId()` compatible: its current call may omit `parentId` and continue passing a description.

- [ ] **Step 4: Run the type checker.**

```powershell
pnpm lint
```

Expected: exit code `0`.

---

## Task 4: Add Service Authorization and Breadcrumb Ownership

**Files:**

- Modify: `features/markdown/services/collection.service.ts`
- Modify: `features/markdown/types/collection.type.ts`

- [ ] **Step 1: Add ownership metadata to the breadcrumb type.**

```ts
export type CollectionBreadcrumb = {
  href: string;
  id: string;
  isOwnedByCurrentUser: boolean;
  title: string;
};
```

- [ ] **Step 2: Populate the ownership flag while building breadcrumbs.**

```ts
breadcrumbs.push({
  id: collection.id,
  title: collection.name,
  href: `/app/${breadcrumbs
    .map((item) => item.id)
    .concat(collection.id)
    .join("/")}`,
  isOwnedByCurrentUser: collection.ownerId === userId,
});
```

- [ ] **Step 3: Add the service input and mutation.**

```ts
export type CreateCollectionInput = {
  name: string;
  parentId?: string | null;
  userId: string;
};

export async function createCollection({
  name,
  parentId = null,
  userId,
}: CreateCollectionInput) {
  if (parentId) {
    const parent = await findCollectionForBreadcrumbRecord(parentId);

    if (!parent) {
      throw new MarkdownError(MarkdownErrorCode.NOT_FOUND);
    }

    if (parent.ownerId !== userId) {
      throw new MarkdownError(MarkdownErrorCode.FORBIDDEN);
    }
  }

  const collection = await createCollectionRecord({
    description: null,
    name,
    ownerId: userId,
    parentId,
  });

  if (!collection) {
    throw new MarkdownError(MarkdownErrorCode.NOT_FOUND);
  }

  return collection;
}
```

Authorization algorithm:

```text
authenticated root request
  -> no parent lookup
  -> create top-level collection owned by authenticated user

authenticated nested request
  -> load active parent by UUID
  -> missing/deleted parent: NOT_FOUND
  -> parent.ownerId != authenticated user: FORBIDDEN
  -> otherwise create child owned by authenticated user
```

Do not use view permission as create-child permission. Do not silently move rejected children to the root.

- [ ] **Step 4: Run the type checker.**

```powershell
pnpm lint
```

Expected: exit code `0`.

---

## Task 5: Add the Authenticated Server Action

**Files:**

- Create: `features/markdown/actions/collection.action.ts`

- [ ] **Step 1: Implement validation, authentication, service delegation, and stable errors.**

```ts
"use server";

import { revalidatePath } from "next/cache";

import { assertAuthenticated } from "@/features/auth/auth-guards";
import {
  MarkdownError,
  MarkdownErrorCode,
} from "@/features/markdown/errors/markdown.error";
import {
  createCollectionSchema,
  type CreateCollectionActionInput,
} from "@/features/markdown/schemas/collection.schema";
import { createCollection } from "@/features/markdown/services/collection.service";
import { err, ok } from "@/utils/server-action-return";

export async function createCollectionAction(
  input: CreateCollectionActionInput,
) {
  const parsed = createCollectionSchema.safeParse(input);

  if (!parsed.success) {
    return err({
      fieldErrors: parsed.error.flatten().fieldErrors,
      message: "Check the collection name and try again.",
    });
  }

  try {
    const user = await assertAuthenticated();
    const collection = await createCollection({
      ...parsed.data,
      userId: user.id,
    });

    revalidatePath("/app");
    return ok(collection);
  } catch (error) {
    console.error(error);

    if (error instanceof MarkdownError) {
      if (error.code === MarkdownErrorCode.NOT_FOUND) {
        return err({
          message: "The parent collection no longer exists.",
        });
      }

      if (error.code === MarkdownErrorCode.FORBIDDEN) {
        return err({
          message:
            "You can only create collections inside collections you own.",
        });
      }
    }

    return err({
      message: "We could not create this collection. Try again in a moment.",
    });
  }
}
```

Security invariants:

```text
UI ownership flag = presentation hint only
submitted parentId = untrusted input
Server Action = authenticate and validate
service = authorize parent ownership
repository = persist atomically
```

- [ ] **Step 2: Run the type checker.**

```powershell
pnpm lint
```

Expected: exit code `0`.

---

## Task 6: Build the Create Menu and Dialog

**Files:**

- Create: `app/(auth)/app/_components/markdown-create-menu.tsx`

- [ ] **Step 1: Create a client component with the location contract.**

```ts
type MarkdownCreateMenuProps = {
  canCreateCollection: boolean;
  parentId?: string | null;
};
```

- [ ] **Step 2: Move the existing Create dropdown into this component without changing existing document actions.**

Required menu order:

```text
Create
  Create collection       (only when canCreateCollection)
  -------------------     (only when canCreateCollection)
  Upload Markdown         (still disabled)
  -------------------
  Create new file         (still links to /app/md/new)
```

Menu pseudocode:

```tsx
<DropdownMenu>
  <DropdownMenuTrigger className={existingTriggerClasses}>
    <PlusIcon aria-hidden className="size-4" />
    Create
    <ChevronDownIcon aria-hidden className="size-4" />
  </DropdownMenuTrigger>
  <DropdownMenuContent align="end" className="w-64">
    <DropdownMenuLabel>Create</DropdownMenuLabel>

    {canCreateCollection ? (
      <>
        <DropdownMenuItem onClick={() => setIsDialogOpen(true)}>
          <FolderPlusIcon aria-hidden className="size-4" />
          <div>
            <p className="font-medium">Create collection</p>
            <p className="text-xs text-muted-foreground">
              Add a folder in this location
            </p>
          </div>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
      </>
    ) : null}

    {/* Preserve the existing Upload Markdown and Create new file items. */}
  </DropdownMenuContent>
</DropdownMenu>
```

- [ ] **Step 3: Add the controlled dialog and form using existing form blocks.**

```tsx
<Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Create collection</DialogTitle>
      <DialogDescription>
        Add a collection to organize Markdown documents.
      </DialogDescription>
    </DialogHeader>

    <FormContext
      id="create-collection-form"
      defaultValues={{ name: "", parentId }}
      resolver={zodResolver(createCollectionSchema)}
      onSubmit={handleCreate}
    >
      <FormInput
        autoFocus
        label="Collection name"
        name="name"
        placeholder="Collection name"
      />
      <FormRootError />
      <CreateCollectionDialogActions
        onCancel={() => setIsDialogOpen(false)}
      />
    </FormContext>
  </DialogContent>
</Dialog>
```

- [ ] **Step 4: Implement action submission and error mapping.**

```ts
const handleCreate: FormOnSubmit<CreateCollectionFormData> = async ({
  data,
  reset,
  setError,
}) => {
  const result = await createCollectionAction({
    name: data.name,
    parentId,
  });

  if (!result.ok) {
    const nameError =
      "fieldErrors" in result.error
        ? result.error.fieldErrors?.name?.[0]
        : undefined;

    if (nameError) {
      setError("name", { message: nameError });
    }

    setError("root", { message: result.error.message });
    return;
  }

  const queryClient = getQueryClient();

  await queryClient.invalidateQueries({
    queryKey: MarkdownFilesTableQueryKey,
  });

  reset();
  setIsDialogOpen(false);
  router.refresh();
};
```

The `in` check is required because generic error results do not all contain `fieldErrors`. Do not replace it with `any` or an unsafe assertion.

- [ ] **Step 5: Add pending-aware footer controls.**

```tsx
function CreateCollectionDialogActions({
  onCancel,
}: {
  onCancel: () => void;
}) {
  const { control } = useFormContext<CreateCollectionFormData>();
  const { isSubmitting } = useFormState({ control });

  return (
    <DialogFooter>
      <Button
        disabled={isSubmitting}
        onClick={onCancel}
        type="button"
        variant="outline"
      >
        Cancel
      </Button>
      <Button disabled={isSubmitting} type="submit">
        {isSubmitting ? "Creating..." : "Create collection"}
      </Button>
    </DialogFooter>
  );
}
```

Accessibility requirements:

- The dialog has an accessible title and description.
- The input label is exactly "Collection name".
- Icons are `aria-hidden`.
- Pending controls are disabled.
- Root errors use the existing alert semantics.
- Cancel does not submit.
- Closing and reopening shows a clean form.

- [ ] **Step 6: Run the type checker.**

```powershell
pnpm lint
```

Expected: exit code `0`.

---

## Task 7: Integrate the Menu With the Library Page

**Files:**

- Modify: `app/(auth)/app/_components/markdown-library-page.tsx`

- [ ] **Step 1: Remove only the dropdown imports and JSX now owned by `MarkdownCreateMenu`.**

Keep the page as a Server Component. Do not add `"use client"` to `markdown-library-page.tsx`.

- [ ] **Step 2: Calculate creation availability from scope and breadcrumb ownership.**

```ts
const currentCollection = breadcrumbs.at(-1);

const canCreateCollection =
  scope !== "shared" &&
  (!currentCollection || currentCollection.isOwnedByCurrentUser);
```

- [ ] **Step 3: Render the menu with current location context.**

```tsx
<div className="sm:ml-auto">
  <MarkdownCreateMenu
    canCreateCollection={canCreateCollection}
    parentId={currentCollection?.id ?? null}
  />
</div>
```

Expected matrix:

| Location | Create collection | Submitted parent |
|---|---:|---|
| `/app` | Visible | `null` |
| `/app/folders` | Visible | `null` |
| `/app/shared` | Hidden | None |
| Owned nested collection | Visible | Current collection UUID |
| Non-owned nested collection | Hidden | None |
| Any nested collection in Shared | Hidden | None |

- [ ] **Step 4: Run the type checker.**

```powershell
pnpm lint
```

Expected: exit code `0`.

---

## Task 8: Complete Behavioral Verification

**Files:**

- Verify: all files listed in the File Map

- [ ] **Step 1: Run the focused collection tests.**

```powershell
pnpm test e2e/markdown-documents.spec.ts --grep "collection"
```

Expected: all root, nested, validation, cancel, and Shared-scope collection tests pass.

- [ ] **Step 2: Run the complete Markdown workflow file.**

```powershell
pnpm test e2e/markdown-documents.spec.ts
```

Expected: all existing document tests and new collection tests pass.

- [ ] **Step 3: Run the required type check.**

```powershell
pnpm lint
```

Expected: exit code `0`.

- [ ] **Step 4: Perform manual smoke validation.**

```text
1. Open /app.
2. Open Create and choose Create collection.
3. Submit whitespace and confirm the required error.
4. Create a valid root collection and confirm it appears immediately.
5. Open the root collection.
6. Create a child and confirm it appears inside that parent.
7. Cancel another creation and confirm no row is added.
8. Open /app/shared and confirm Create collection is absent.
9. Confirm Create new file still navigates to /app/md/new.
10. Confirm Upload Markdown remains disabled.
```

- [ ] **Step 5: Inspect the final diff.**

```powershell
git status --short
git diff --
```

Confirm:

- Every changed line traces to collection creation.
- No pre-existing user work was removed.
- No migration, generated schema snapshot, or unrelated formatting change appeared.
- No debug logging, commented-out code, or dead imports remain.
- The server repeats validation and authorization even though the UI hides forbidden actions.

---

## Suggested Commit Boundaries

If the user requests commits, create them only after verification:

```text
feat(collections): add authorized collection creation
feat(collections): add create collection dialog
test(collections): cover collection creation workflow
```

Do not commit automatically unless the active request authorizes it.

## Assumptions and Locked Decisions

- Collection descriptions are omitted and stored as `null`.
- Duplicate sibling names are permitted.
- Root creation is available from All and Folders.
- Shared is read-only for collection creation.
- Only a collection owner may create children under it.
- A rejected nested creation never falls back to the root.
- Success keeps the user on the current page.
- Query invalidation, not an optimistic row, refreshes the table.
- No database migration is required.
- The markdown2share worktree and codebase-memory index were clean when this plan was prepared.
