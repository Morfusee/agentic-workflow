# Code Style Guide (Derived from Repository)

## Overview

| Category | Details |
|---|---|
| **Language** | TypeScript 5 (`strict: true`, `target: ES2017`) |
| **Framework** | Next.js 16 (App Router, React 19) |
| **Styling** | Tailwind CSS 4 |
| **Database ORM** | Project-specific; apply the Drizzle and Prisma guidance below |
| **Auth** | better-auth |
| **Form handling** | react-hook-form + Zod (`@hookform/resolvers/zod`) |
| **Data fetching** | TanStack Query v5 (`@tanstack/react-query`) |
| **Table** | TanStack Table v8 (`@tanstack/react-table`) |
| **i18n** | next-intl (locales: `en`, `ar`, `fr`) |
| **URL state** | nuqs |
| **Package manager** | pnpm |
| **UI stories** | Ladle |
| **React optimisation** | React Compiler enabled (`reactCompiler: true`) |

No ESLint or Prettier configuration files are present in the repository. The `lint` script runs `tsc --noEmit`. Formatting is not enforced by tooling; the observed style below reflects what is consistently practiced manually.

---

## Naming Conventions

### Variables

- **camelCase** for all local variables, function parameters, and object properties.
- Boolean-state variables are prefixed with `is`: `isCustomer`, `isReadOnly`, `isEdit`, `isDeleting`, `isSubmitting`, `isPending`.
- Module-level exported config objects and lookup tables use **SCREAMING_SNAKE_CASE**: `TEMPLATE_FILES`, `ROLE_HOME`, `PAGE_CONFIG`, `VIEWS`.
- Query keys exported as module-level constants use **PascalCase** (treated as unique identifiers rather than literal values): `AuthSessionQueryKey`.

```ts
// Local booleans — src/features/users/components/user-form.tsx
const isCustomer = selectedRole === Roles.CUSTOMER;
const isReadOnly = mode === "view";
const isEdit = mode === "edit";

// SCREAMING_SNAKE_CASE constants — src/app/[locale]/(app)/(admin)/users/new/_components/batch-user-form.tsx
const TEMPLATE_FILES: Record<string, string> = {
  admin: "/templates/admin_batch_create_template.csv",
  sales: "/templates/sales_batch_create_template.csv",
  customer: "/templates/customer_create_batch_template.csv",
};

// SCREAMING_SNAKE_CASE constant — src/features/auth/role-redirect.ts
export const ROLE_HOME: Record<Role, string> = {
  [Roles.CUSTOMER]: "/orders",
  [Roles.SALES]:    "/customer-orders",
  [Roles.ADMIN]:    "/users",
};

// PascalCase query key — src/features/auth/queries/auth-session.query.ts
export const AuthSessionQueryKey = ["auth", "session"];
```

---

### Functions

All functions use **camelCase**. Naming follows a strict verb-first convention that encodes layer responsibility via the suffix.

| Layer | Pattern | Examples |
|---|---|---|
| Server Actions | `verbNounAction` | `createUserAction`, `updateUserAction`, `deleteOrderAction`, `addOrderItem` |
| Services | `verbNoun` for workflows; `verbNounRecord` for local database operations | `createUser`, `getDocumentAccess`, `findDocumentRecordById` |
| TanStack Query hooks (queries) | `useQueryNoun` | `useQueryOrderItems`, `useQueryAuthSession` |
| TanStack Query hooks (mutations) | `useVerbNoun` | `useAddOrderItem`, `useChangeOrderItemQuantity`, `useRemoveOrderItem` |
| Auth guards (throwing) | `assertVerb` | `assertAuthenticated`, `assertRole` |
| Auth guards (redirecting) | `requireVerb` | `requireRole` |
| `queryOptions` factory | `nounOptions` | `orderItemsOptions`, `authSessionOptions` |
| Utilities | `verbNoun` | `checkPagination`, `getQueryClient`, `makeQueryClient` |
| Internal helpers | `verbNoun` | `downloadTemplate`, `parseCSVLine`, `parseCSV`, `handleSort`, `handleDelete` |

```ts
// Service — features/markdown/services/markdown.service.ts
export async function getDocumentAccess(documentId: string) { /* workflow */ }
async function findDocumentRecordById(documentId: string) { /* database operation */ }

// Action — src/features/users/actions/user.action.ts
export async function createUserAction({ data }: CreateUserActionData) { ... }

// Query hook — src/features/orders/queries/order-item.query.ts
export function useQueryOrderItems(orderId: string) { ... }
export function useSuspenseOrderItems(orderId: string) { ... }

// Mutation hook — src/features/orders/queries/order-item.mutation.ts
export function useAddOrderItem(orderId: string) { ... }

// Guard — src/features/auth/auth-guards.ts
export async function assertRole(roles: Role | Role[]) { ... }
export async function requireRole(roles: Role | Role[], redirectTo = "/login") { ... }
```

---

### Classes and Types

#### Error classes

- Named `[Domain]Error`, extending `AppError<[Domain]ErrorCode>`.
- Error code enums are named `[Domain]ErrorCode`.
- Enum **keys** are `SCREAMING_SNAKE_CASE`; enum **values** are `camelCase` strings.

```ts
// src/features/orders/errors/order.error.ts
export enum OrderErrorCode {
  NOT_FOUND       = "notFound",
  INVALID_STATUS  = "invalidStatus",
  NOT_SUBMITTABLE = "notSubmittable",
  NO_ITEMS        = "noItems",
}

export class OrderError extends AppError<OrderErrorCode> {
  constructor(code: OrderErrorCode, message?: string) {
    super(code, message);
  }
}
```

#### Interfaces and type aliases

| Kind | Pattern | Examples |
|---|---|---|
| DTOs (read model) | `NounDTO` | `UserDTO`, `CustomerDTO`, `CustomerDetailsDTO` |
| Service database input | `VerbNounRecordData` | `CreateMarkdownDraftRecordData`, `UpdateMarkdownDraftRecordData` |
| Service database queries | `VerbNounRecordsQuery` | `ListInfiniteMarkdownDocumentRecordsQuery` |
| Action payloads | `VerbNounActionData` | `CreateUserActionData`, `UpdateUserActionData` |
| Component props | `[ComponentName]Props` | `UsersTableProps`, `OrderFilterProps`, `AppSidebarProps` |
| Form data types (inferred from Zod) | `VerbNounFormData` | `CreateUserFormData`, `UpdateUserFormData` |
| Generic shared props | Semantic noun | `ClassNameProp`, `StyleProp`, `ClassProps<T>` |
| Page params | `AppPageProps<TParams, TSearch>` | defined in `src/types/page.props.ts` |

#### Zod schemas

- Schema constants exported as `camelCase` + `Schema` suffix: `createUserSchema`, `updateUserSchema`.
- Factory functions used when schema needs runtime arguments: `createLoginFormSchema(translate?)`.
- Inferred types exported alongside: `export type CreateUserFormData = z.infer<typeof createUserSchema>`.

#### `Roles` constant object

Roles are defined as a `const` object (not an enum) to produce literal string types:

```ts
// src/lib/better-auth/roles.ts
export const Roles = {
  CUSTOMER: "customer",
  SALES:    "sales",
  ADMIN:    "admin",
} as const;

export type Role = (typeof Roles)[keyof typeof Roles];
```

#### React components

- Component functions are **PascalCase**, declared with the `function` keyword.
- Internal sub-components within a file are also PascalCase and defined in the same file: `SortIndicator`, `UserTableWrapper`, `DraftOrdersList`, `RoleBadge`, `LoadingState`, `EmptyState`.

---

## File Naming

All non-component source files use **kebab-case dot-notation** with a layer suffix.

| Layer | Pattern | Examples |
|---|---|---|
| Services | `noun-queries.service.ts` / `noun-mutations.service.ts` / `noun.service.ts` | `user-queries.service.ts`, `user-mutations.service.ts`, `auth.service.ts` |
| Actions | `noun.action.ts` or `noun.actions.ts` | `user.action.ts`, `order.actions.ts`, `auth.actions.ts` |
| Schemas | `verb-noun.schema.ts` | `create-user.schema.ts`, `update-user.schema.ts`, `login.schema.ts` |
| Types | `noun.types.ts` or `noun.type.ts` | `user.types.ts`, `order-item.type.ts` |
| Errors | `noun.error.ts` | `customer.error.ts`, `order.error.ts`, `app-error.ts`, `generic.error.ts` |
| TanStack queries | `noun.query.ts` | `order-item.query.ts`, `auth-session.query.ts` |
| TanStack mutations | `noun.mutation.ts` | `order-item.mutation.ts` |
| Utilities | `noun.util.ts` | `pagination.util.ts`, `csv.util.ts` |
| Config modules | `noun.config.ts` | `page.config.ts` |
| Stories | `noun.stories.tsx` | `button.stories.tsx`, `form.stories.tsx` |

**React component files** use **kebab-case** across feature, route-local, and shared component folders:

- `features/[feature]/components/` → `order-filter.tsx`, `order-status-badge.tsx`, `user-form.tsx`
- `app/` routes and `components/` shared → `create-user-form.tsx`, `users-table.tsx`, `users-table.skeleton.tsx`, `data-table.tsx`, `field-input.tsx`

**Skeleton variants** of table/list components are named `[component].skeleton.tsx`:
`users-table.skeleton.tsx`, `data-table-skeleton.tsx`

**Column definitions** co-located with the table: `users-table-columns.tsx`

**Next.js file conventions** apply for pages and layouts: `page.tsx`, `layout.tsx`, `route.ts`

---

## Folder Structure

The project uses a **feature-based architecture** under `src/features/`, with a separate `src/app/` layer for routing and `src/components/` for shared UI.

```
src/
├── app/
│   ├── [locale]/
│   │   ├── (app)/            # Authenticated app shell
│   │   │   └── users/
│   │   │       ├── page.tsx
│   │   │       ├── _components/   # Route-local components
│   │   │       └── [id]/
│   │   │           ├── page.tsx
│   │   │           └── _components/
│   │   ├── (auth)/           # Route group — auth pages
│   │   └── page.tsx          # Locale root entry
│   └── api/
│       ├── auth/
│       ├── orders/[orderId]/items/route.ts
│       └── products/route.ts
│
├── components/
│   ├── ui/                   # Primitive UI components (shadcn/ui style)
│   └── blocks/
│       ├── data-table/       # Compound data table
│       ├── form/             # Compound form wrappers
│       ├── loading/          # Loading skeletons / spinners
│       ├── modals/           # Modal utilities
│       └── page/
│
├── features/
│   ├── auth/
│   │   ├── actions/          # "use server" functions
│   │   ├── components/
│   │   ├── errors/
│   │   ├── queries/          # TanStack Query hooks
│   │   ├── schemas/          # Zod schemas
│   │   ├── services/         # Business logic
│   │   ├── auth-guards.ts    # assertRole / requireRole
│   │   └── role-redirect.ts
│   ├── orders/               # Same structure as auth
│   ├── products/
│   └── users/
│
├── lib/
│   ├── better-auth/          # Auth client + server config, roles
│   ├── database/             # ORM client, schema, pagination helpers
│   ├── resend/               # Email integration
│   ├── tanstack-query/       # QueryClient factory + providers
│   └── nuqs/
│
├── types/                    # Shared TypeScript types
├── utils/                    # Pure utility functions
├── errors/                   # Global error base classes
├── hooks/                    # Shared React hooks
├── i18n/                     # next-intl routing + request config
├── messages/                 # Translation JSON files (en, ar, fr)
└── stories/                  # Ladle component stories
```

**Layer responsibilities observed:**

| Layer | Responsibility |
|---|---|
| `services/` | Business workflows, domain rules, domain errors, and direct Drizzle reads/writes |
| `actions/` | Server actions: validate auth, call services, return `ok()`/`err()`, revalidate cache |
| `queries/` | TanStack Query hooks for client-side data fetching (call API routes or server actions) |
| `errors/` | Domain-specific error classes |
| `schemas/` | Zod schemas for input validation; inferred types exported alongside |
| `types/` | DTOs and TypeScript interfaces (no logic) |
| `components/` | Feature UI components only |

For Drizzle-backed features, do not add a `repositories/` folder. Keep database operations in the owning service. A Prisma-backed feature may use repositories when they provide a meaningful domain, testing, or integration boundary; assess that boundary case by case rather than removing it by default. Evaluate other persistence technologies from current evidence.

### YAGNI

- Do not create repository, use-case, helper, or other architectural layers without a current demonstrated need.
- Keep single-use database operations in the owning service file.
- Extract a helper only when it is reused across files or materially improves readability.
- Do not carry unused persistence functions forward during migrations.
- Do not create folders for anticipated future code.
- Do not introduce `use-cases/` as a replacement for repositories.

---

## Import Conventions

### Path alias

`@/` maps to `src/`. All imports of non-adjacent files use `@/`.

```json
// tsconfig.json
"paths": { "@/*": ["./src/*"] }
```

### Relative vs absolute

- **Within a feature**, relative imports are used when referencing sibling directories:
  ```ts
  // features/markdown/services/markdown.service.ts
  import { MarkdownError } from "../errors/markdown.error";
  import type { MarkdownDraft } from "../types/markdown.types";
  ```
- **Cross-feature and cross-layer**, `@/` is used:
  ```ts
  import { assertRole } from "@/features/auth/auth-guards";
  import { getDb } from "@/lib/db";
  import { Paginated } from "@/features/pagination/types/paginate";
  ```

### Import ordering

There is no ESLint import-order rule. The observed order is generally:

1. External npm packages
2. Internal `@/` imports (lib, types, utils, other features)
3. Relative imports to sibling modules within the same feature

This ordering is not strictly enforced — some files intermix `@/` and npm imports.

### No barrel exports

No `index.ts` barrel files are used. All imports reference the specific file path:

```ts
// Correct — observed throughout
import { MarkdownError } from "../errors/markdown.error";

// Not present — no barrel pattern
import { MarkdownError } from "../errors";
```

---

## Formatting Rules

Observed from consistently applied patterns across all source files:

| Rule | Value |
|---|---|
| **Indentation** | 2 spaces |
| **Quotes** | Double quotes (`"`) |
| **Semicolons** | Yes, at end of statements |
| **Trailing commas** | Yes, in multi-line object literals, arrays, and function parameters |
| **Bracket spacing** | Yes: `{ key: value }` |
| **Arrow functions** | Used for simple utilities, callbacks, and inline handlers |
| **`function` keyword** | Used for named component functions and complex async functions |
| **Max line length** | Not enforced |

```ts
// 2-space indent, double quotes, trailing commas
export async function listAllUsers(
  {
    search,
    roles,
    limit,
    page,
    sortType = "createdAt",
    sortOrder = "desc",
  }: ListAllUsersQuery,
  tx: DbExecutor = db,
) {
  const [usersResult, meta] = await paginateTable(tx, users)
    .paginate({
      where: and(filter, searchFilter),
      orderBy: orderByClause,
      select: {
        id: true,
        name: true,
        email: true,
      },
    })
    .withPages({ ...checkPagination({ limit, page }), includePageCount: true });
  ...
}
```

**Multi-line interface declarations**: Each property on its own line:

```ts
interface CreateUserInternal extends CreateUserBase {
  role: "admin" | "sales";
}
```

**`extends` across multiple lines** when the interface has multiple bases:

```ts
interface CreateUserCustomer
  extends
    CreateUserBase,
    Omit<CreateCustomerRecordData, "userId" | "name" | "email"> {
  role: "customer";
}
```

---

## Error Handling

### Domain error architecture

All domain errors extend an abstract generic base class:

```ts
// src/errors/app-error.ts
export abstract class AppError<T extends string> extends Error {
  public readonly code: T;
  constructor(code: T, message?: string) {
    super(message ?? code);
    this.code = code;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}
```

Domain features define an error code **enum** and concrete **error class** when they need typed domain failures:

```ts
// src/features/orders/errors/order.error.ts
export enum OrderErrorCode {
  NOT_FOUND       = "notFound",
  NOT_SUBMITTABLE = "notSubmittable",
  NO_ITEMS        = "noItems",
}
export class OrderError extends AppError<OrderErrorCode> {
  constructor(code: OrderErrorCode, message?: string) {
    super(code, message);
  }
}
```

### Server action return convention

Server actions never throw. They catch all errors and return a typed discriminated union:

```ts
// src/utils/server-action-return.ts
export function ok<T>(data: T) { return { ok: true, data } as const; }
export function err<T>(error: T) { return { ok: false, error } as const; }
```

```ts
// Typical action pattern — src/features/orders/actions/order.actions.ts
export async function deleteOrderAction({ orderId }: { orderId: string }) {
  try {
    const user = await assertRole(Roles.CUSTOMER);
    await deleteCustomerDraftOrder({ id: orderId, customerId: user.id });
    return ok({});
  } catch (error) {
    console.error(error);
    if (error instanceof OrderError) return err(error.code);
    return err(GenericErrorCode.INTERNAL_SERVER_ERROR);
  }
}
```

### Calling actions on the client

The caller checks `res.ok` before using `res.data`:

```ts
const res = await createUserAction({ data: values.data });
if (!res.ok) return;
router.push(`/users`);
```

### Service layer

Services throw domain errors directly; they do not return error objects:

```ts
// src/features/orders/services/order-mutations.service.ts
if (!order) throw new OrderError(OrderErrorCode.NOT_FOUND);
if (order.status !== OrderStatus.draft)
  throw new OrderError(OrderErrorCode.NOT_SUBMITTABLE);
```

For Drizzle-backed services, keep public workflow functions readable and place local database operations at the bottom of the service file:

```ts
export async function getDocumentAccess(documentId: string) { /* workflow */ }
export async function saveMarkdownDraft(documentId: string) { /* workflow */ }

// --- Database operations ------------------------------------------------------

async function findDocumentRecordById(documentId: string) { /* database operation */ }
async function updateMarkdownDraftRecord(documentId: string) { /* database operation */ }
```

### Auth guards

- `assertRole` (throws `AuthError`): used in server actions and API route handlers.
- `requireRole` (catches and redirects): used in page server components.

```ts
// src/features/auth/auth-guards.ts
export async function requireRole(roles: Role | Role[], redirectTo = "/login") {
  try {
    return await assertRole(roles);
  } catch {
    redirect(redirectTo);
  }
}
```

### Logging

`console.error()` is used for non-fatal errors inside `catch` blocks, primarily in server actions and integration helpers. `console.log()` appears occasionally in non-critical action and story code.

---

## Comments & Documentation

### Inline comments

Short explanatory comments describe **why** something is done, not what:

```ts
// register user via betterauth
// create customer details and then link it to the registered user
// Submit should only work in draft orders
// If the root db client is used, wrap this operation in a transaction
```

### Section dividers

Two visual separator styles are used in complex files:

**Style 1 — unicode rule** (used in component files with embedded utilities):

```ts
// ─── CSV parser ───────────────────────────────────────────────────────────────
```

**Style 2 — equals rule** (used in context/provider files with multiple sections):

```ts
// ============================================================================
// CONTEXTS
// ============================================================================
```

### Note comments

Block-level explanatory notes use `// NOTE:`:

```ts
// NOTE: Avoid useState when initializing the query client if you don't
//       have a suspense boundary between this and the code that may
//       suspend...
```

### JSDoc

JSDoc is used sparingly for more complex client-side helpers where the intent, side effects, or workflow steps are not obvious from the function name alone. Do not add JSDoc for simple components or self-explanatory utilities.

### Removed code

Deleted or superseded code should be removed rather than preserved in source folders unless there is an explicit reason to keep it.

---

## Testing Conventions

No test files (`.test.ts`, `.test.tsx`, `.spec.ts`, `.spec.tsx`) exist in the repository.

**Ladle** is used for interactive component stories. Stories live in `src/stories/` and follow:

```ts
// src/stories/button.stories.tsx
import type { Story } from "@ladle/react";
import { Button } from "@/components/ui/button";

export const ButtonStory: Story = () => <Button variant="default">Dawg</Button>;
```

- Story exports are named `[DescriptiveName]Story` or `[DescriptiveName]Form` (PascalCase).
- Stories use `satisfies` to type `defaultValues` without widening.
- No mocking infrastructure, no test assertions.

---

## Observed Patterns

### 1. `"use server"` / `"use client"` directive

Always the first line of the file, no imports before it:

```ts
"use server";

import { assertRole } from "@/features/auth/auth-guards";
```

### 2. Optional Drizzle executor parameter

Service-local database operations may accept a `tx` parameter defaulting to the singleton Drizzle `db` client. This allows them to participate in a larger transaction without changes at the call site:

```ts
async function findDocumentRecordById(
  { documentId }: { documentId: string },
  tx: DbExecutor = db,
) { ... }
```

### 3. `queryOptions` factory + `useQuery` wrapper

TanStack Query options objects are defined once and reused for both SSR prefetching and client hooks:

```ts
export const orderItemsOptions = (orderId: string) =>
  queryOptions({
    queryKey: ["orders", orderId, "items"],
    queryFn: async () => { ... },
    staleTime: 60 * 1000,
  });

export function useQueryOrderItems(orderId: string) {
  return useQuery(orderItemsOptions(orderId));
}
export function useSuspenseOrderItems(orderId: string) {
  return useSuspenseQuery(orderItemsOptions(orderId));
}
```

### 4. Query key convention

TanStack Query keys follow an `[resource, id, subresource]` array structure:

```ts
["orders", orderId, "items"]
["auth", "session"]
```

### 5. `_components/` co-location

Use a route `_components/` folder only for UI that is genuinely specific to that route. Place reusable or feature-owned UI under `features/<feature>/components/`, even when a route is its first consumer.

```
features/markdown/components/library/
├── markdown-library-page.tsx
├── markdown-files-table.tsx
└── document-row-actions.tsx

app/(auth)/app/
├── page.tsx
└── _components/
    └── page.config.ts
```

### 6. Skeleton companion components

Significant data-fetching components often have a `.skeleton.tsx` sibling used as the `<Suspense fallback>`:

```ts
<Suspense fallback={<UsersTableSkeleton />}>
  <UserTableWrapper ... />
</Suspense>
```

### 7. Discriminated union form schemas

Multi-variant forms use `z.discriminatedUnion("role", [...])` to model mutually exclusive field sets:

```ts
export const createUserSchema = z.discriminatedUnion("role", [
  salesSchema,
  adminSchema,
  customerSchema,
]);
```

### 8. Compound component pattern

Shared compound components (DataTable, FieldController) expose a `Namespace.Part` API:

```tsx
<DataTable.Provider state={...} actions={...}>
  <DataTable.TabFilter />
  <DataTable.Table />
  <DataTable.Pagination />
</DataTable.Provider>
```

### 9. `data-slot` HTML attributes on UI primitives

All primitive UI components attach a `data-slot` attribute for CSS targeting and debugging:

```tsx
<button data-slot="button" data-variant={variant} data-size={size} ... />
<div data-slot="empty" ... />
<fieldset data-slot="field-set" ... />
```

### 10. `AppPageProps` for page components

Pages use the shared `AppPageProps<TParams, TSearch>` type:

```ts
// src/types/page.props.ts
export interface AppPageProps<
  TParams = Record<string, string>,
  TSearch = Record<string, string | string[] | undefined> | undefined,
> {
  params: Promise<TParams>;
  searchParams?: Promise<TSearch>;
}
```

### 11. Feature-internal interface exports

Interfaces associated with data-layer functions are exported alongside the function:

```ts
// features/markdown/services/markdown.service.ts
export type ListInfiniteMarkdownDocumentRecordsQuery =
  PaginationParams & SortQuery<Document>;

async function listInfiniteMarkdownDocumentRecords(
  query: ListInfiniteMarkdownDocumentRecordsQuery,
) { /* database operation */ }
```

### 12. `PAGE_CONFIG` pattern

Per-page static configuration (tab labels, rows-per-page options) is extracted into a `page.config.ts` file:

```ts
// src/app/[locale]/(app)/(admin)/users/_components/page.config.ts
export const PAGE_CONFIG = {
  rowsPerPage: [5, 10, 25, 100],
  tabs: (t: ...) => [
    { label: t("roles.customer"), value: Roles.CUSTOMER },
    ...
  ],
};
```

---

## Evidence

| Convention | File |
|---|---|
| Abstract error base | [src/errors/app-error.ts](src/errors/app-error.ts) |
| Domain error + enum | [src/features/orders/errors/order.error.ts](src/features/orders/errors/order.error.ts) |
| `ok` / `err` utilities | [src/utils/server-action-return.ts](src/utils/server-action-return.ts) |
| Server action pattern | [src/features/users/actions/user.action.ts](src/features/users/actions/user.action.ts) |
| Service with domain throws | [src/features/orders/services/order-mutations.service.ts](src/features/orders/services/order-mutations.service.ts) |
| Service-owned Drizzle operations | [features/markdown/services/markdown.service.ts](features/markdown/services/markdown.service.ts) |
| Collection persistence service | [features/markdown/services/collection.service.ts](features/markdown/services/collection.service.ts) |
| Authorization persistence service | [features/auth/services/authorization.service.ts](features/auth/services/authorization.service.ts) |
| `assertRole` / `requireRole` | [src/features/auth/auth-guards.ts](src/features/auth/auth-guards.ts) |
| `queryOptions` + `useQuery` | [src/features/orders/queries/order-item.query.ts](src/features/orders/queries/order-item.query.ts) |
| Mutation hook pattern | [src/features/orders/queries/order-item.mutation.ts](src/features/orders/queries/order-item.mutation.ts) |
| Zod discriminated union | [src/features/users/schemas/create-user.schema.ts](src/features/users/schemas/create-user.schema.ts) |
| DTO interface | [src/features/users/types/user.types.ts](src/features/users/types/user.types.ts) |
| `Roles` const object | [src/lib/better-auth/roles.ts](src/lib/better-auth/roles.ts) |
| `SCREAMING_SNAKE_CASE` constants | [src/features/auth/role-redirect.ts](src/features/auth/role-redirect.ts) |
| Feature-owned library UI | [features/markdown/components/library/markdown-library-page.tsx](features/markdown/components/library/markdown-library-page.tsx) |
| Skeleton companion | [src/app/[locale]/(app)/(admin)/users/_components/users-table.skeleton.tsx](src/app/%5Blocale%5D/(app)/(admin)/users/_components/users-table.skeleton.tsx) |
| `PAGE_CONFIG` pattern | [src/app/[locale]/(app)/(admin)/users/_components/page.config.ts](src/app/%5Blocale%5D/(app)/(admin)/users/_components/page.config.ts) |
| `data-slot` attributes | [src/components/ui/button.tsx](src/components/ui/button.tsx) |
| Compound component | [src/components/blocks/data-table/data-table-context.tsx](src/components/blocks/data-table/data-table-context.tsx) |
| `AppPageProps` type | [src/types/page.props.ts](src/types/page.props.ts) |
| API route handler | [src/app/api/orders/[orderId]/items/route.ts](src/app/api/orders/%5BorderId%5D/items/route.ts) |
| Ladle stories | [src/stories/form.stories.tsx](src/stories/form.stories.tsx) |
| Section divider comments | [src/app/[locale]/(app)/(admin)/users/new/_components/batch-user-form.tsx](src/app/%5Blocale%5D/(app)/(admin)/users/new/_components/batch-user-form.tsx) |
| `DbExecutor` transaction type | [src/types/db-transaction.ts](src/types/db-transaction.ts) |
| Feature-level components (kebab-case) | [src/features/orders/components/order-status-badge.tsx](src/features/orders/components/order-status-badge.tsx) |
