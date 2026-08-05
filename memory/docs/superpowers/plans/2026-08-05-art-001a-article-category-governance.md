# ART-001A Article Category Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use $subagent-driven-development (recommended) or $executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the governed `article-categories` Payload collection, system-managed redirect history, two-level hierarchy validation, draft/publish governance, reusable fixtures, generated types, a reversible PostgreSQL migration, and automated tests without adding Article or public archive behavior.

**Architecture:** Keep Payload collection files declarative and put business rules in small pure functions under `src/lib/article-categories/`. Thin collection hooks load the minimum related records, call those functions, and persist redirect history inside the originating Payload transaction. PostgreSQL unique indexes remain the final protection for unique code, slug, introduction, and redirect sources.

**Tech Stack:** TypeScript 6, Payload CMS 3.87, Next.js 16 App Router, PostgreSQL 17 through `@payloadcms/db-postgres`, Vitest 4, pnpm 11.

---

## Scope and authoritative references

Read these before editing:

- Repository `AGENTS.md`.
- `docs/specs/data-model.md`, especially sections 5.1–5.3 and 13.2.
- `docs/specs/information-architecture-and-pages.md`, especially sections 5.2–5.3 and 13.2.
- `docs/specs/06-technical-foundation.md`, especially section 24.
- `docs/epics/article-publishing-v1.md`, ART-001 acceptance criteria.
- Approved design: `$HOME/Documents/Programming/agentic-workflow/memory/docs/superpowers/specs/2026-08-05-art-001a-article-category-governance-design.md`.

Do not add Article records, ArticleBody, archive routes, public queries, counts, pagination, preview, navigation, SEO, redirect resolution, search indexing, or sitemap behavior.

## Locked file map

### Create

- `src/lib/article-categories/archiveOnwardPath.ts`: complete four-intent contract and currently selectable intents.
- `src/lib/article-categories/validation.ts`: pure normalization and governance validation.
- `src/lib/article-categories/validation.test.ts`: unit tests for values, dates, drafts, publication, lifecycle, and hierarchy.
- `src/lib/article-categories/paths.ts`: canonical Category/Subcategory path construction and redirect-plan helpers.
- `src/lib/article-categories/paths.test.ts`: path and redirect-plan unit tests.
- `src/lib/article-categories/hooks.ts`: Payload adapters for normalization, hierarchy lookups, publication checks, and transactional redirect writes.
- `src/lib/article-categories/hooks.test.ts`: hook tests with a narrow mocked Payload request.
- `src/collections/ArticleCategories.ts`: Payload schema, access, Admin behavior, drafts, and hooks.
- `src/collections/ArticleCategories.test.ts`: collection-configuration tests.
- `src/collections/Redirects.ts`: system-managed redirect schema and access.
- `src/collections/Redirects.test.ts`: redirect collection-configuration tests.
- `src/test/fixtures/articleCategories.ts`: deterministic root, child, draft, published, and archived fixture builders.
- `src/lib/article-categories/integration.test.ts`: PostgreSQL-backed Payload integration coverage.
- `src/migrations/20260805_000000_article_category_governance.ts`: generated migration renamed to a deterministic reviewed name.
- `src/migrations/20260805_000000_article_category_governance.json`: generated schema snapshot renamed with the migration.

### Modify

- `src/payload.config.ts`: register `ArticleCategories` and `Redirects`.
- `src/payload-types.ts`: regenerate with Payload; never edit by hand.
- `src/migrations/index.ts`: register the new migration after initial foundation.

No package dependency change is expected. `package.json`, `pnpm-lock.yaml`, and `pnpm-workspace.yaml` must remain unchanged.

---

### Task 1: Protect the worktree and establish a clean baseline

**Files:**

- Preserve without editing: `AGENTS.md`
- Inspect only: all existing modified and untracked files

- [ ] **Step 1: Inspect user-owned work before changing branches or files**

Run:

```powershell
git status --short --branch
git diff
git log -5 --oneline --decorate
```

Expected: detached `HEAD`; untracked `AGENTS.md`; no tracked application diff. If additional changes exist, record them and keep them out of every later `git add` command.

- [ ] **Step 2: Create the repository-approved feature branch from development**

Run:

```powershell
git switch -c feature/art-001a-category-governance origin/development
git status --short --branch
```

Expected: branch `feature/art-001a-category-governance`; the untracked `AGENTS.md` remains present and unchanged.

- [ ] **Step 3: Install exactly the locked dependencies and run the baseline gate**

Run:

```powershell
pnpm install --frozen-lockfile
pnpm check
```

Expected: install reports an unchanged lockfile; format, lint, typecheck, and existing tests pass. Stop and report any pre-existing failure rather than hiding it in ART-001A.

---

### Task 2: Build the pure governance rules with TDD

**Files:**

- Create: `src/lib/article-categories/archiveOnwardPath.ts`
- Create: `src/lib/article-categories/validation.ts`
- Create: `src/lib/article-categories/validation.test.ts`

- [ ] **Step 1: Write failing tests for the intent contract and Unicode counting**

Create `src/lib/article-categories/validation.test.ts` with focused assertions:

```ts
import { describe, expect, it } from 'vitest'

import {
  ARCHIVE_ONWARD_INTENTS,
  AVAILABLE_ARCHIVE_ONWARD_INTENTS,
} from './archiveOnwardPath'
import {
  countUnicodeCharacters,
  normalizeArticleCategoryInput,
  validateArticleCategory,
} from './validation'

const now = new Date('2026-08-05T00:00:00.000Z')

describe('Article Category governance', () => {
  it('defines all governed intents but exposes only registered targets', () => {
    expect(ARCHIVE_ONWARD_INTENTS).toEqual([
      'programs',
      'pathfinder',
      'qualified_taxonomy',
      'offering',
    ])
    expect(AVAILABLE_ARCHIVE_ONWARD_INTENTS).toEqual(['programs', 'pathfinder'])
  })

  it('counts Unicode code points instead of UTF-16 code units', () => {
    expect(countUnicodeCharacters('A😀B')).toBe(3)
  })

  it('trims strings, lowercases slugs, and removes empty optional text', () => {
    expect(
      normalizeArticleCategoryInput({
        code: ' CAT-01 ',
        landingIntro: '   ',
        name: ' Careers ',
        slug: 'CAREERS',
      }),
    ).toEqual({
      code: 'CAT-01',
      landingIntro: undefined,
      name: 'Careers',
      slug: 'careers',
    })
  })
})
```

- [ ] **Step 2: Run the focused test and verify the expected failure**

Run:

```powershell
pnpm test -- src/lib/article-categories/validation.test.ts
```

Expected: FAIL because `archiveOnwardPath.ts` and `validation.ts` do not exist.

- [ ] **Step 3: Implement the intent constants and normalization primitives**

Create `src/lib/article-categories/archiveOnwardPath.ts`:

```ts
export const ARCHIVE_ONWARD_INTENTS = [
  'programs',
  'pathfinder',
  'qualified_taxonomy',
  'offering',
] as const

export type ArchiveOnwardIntent = (typeof ARCHIVE_ONWARD_INTENTS)[number]

export const AVAILABLE_ARCHIVE_ONWARD_INTENTS = ['programs', 'pathfinder'] as const satisfies readonly ArchiveOnwardIntent[]

export type AvailableArchiveOnwardIntent = (typeof AVAILABLE_ARCHIVE_ONWARD_INTENTS)[number]
```

Start `src/lib/article-categories/validation.ts` with explicit input and error contracts:

```ts
import {
  AVAILABLE_ARCHIVE_ONWARD_INTENTS,
  type ArchiveOnwardIntent,
} from './archiveOnwardPath'

export type RelationshipID = number | string

export type ArchiveOnwardPathInput = {
  heading?: null | string
  intent?: ArchiveOnwardIntent | null
  summary?: null | string
}

export type ArticleCategoryInput = {
  _status?: 'draft' | 'published' | null
  archiveOnwardPath?: ArchiveOnwardPathInput | null
  code?: null | string
  displayOrder?: null | number
  landingIntro?: null | string
  name?: null | string
  owner?: null | RelationshipID | { id: RelationshipID }
  parent?: null | RelationshipID | { id: RelationshipID }
  reviewedAt?: null | string
  reviewDueAt?: null | string
  slug?: null | string
  status?: 'active' | 'archived' | null
}

export type ValidationIssue = { message: string; path: string }

export const countUnicodeCharacters = (value: string): number => Array.from(value).length

const trimRequired = (value: null | string | undefined): null | string | undefined =>
  typeof value === 'string' ? value.trim() : value

const trimOptional = (value: null | string | undefined): string | undefined => {
  const trimmed = trimRequired(value)
  return trimmed ? trimmed : undefined
}

export const normalizeArticleCategoryInput = (data: ArticleCategoryInput): ArticleCategoryInput => ({
  ...data,
  code: trimRequired(data.code),
  landingIntro: trimOptional(data.landingIntro),
  name: trimRequired(data.name),
  slug: typeof data.slug === 'string' ? data.slug.trim().toLowerCase() : data.slug,
  archiveOnwardPath: data.archiveOnwardPath
    ? {
        ...data.archiveOnwardPath,
        heading: trimOptional(data.archiveOnwardPath.heading),
        summary: trimOptional(data.archiveOnwardPath.summary),
      }
    : data.archiveOnwardPath,
})
```

- [ ] **Step 4: Add failing tests for values, immutability, hierarchy, draft, publish, and archive behavior**

Append test cases that assert these exact outcomes:

```ts
it.each([
  ['Upper Case', 'Slug must use lowercase ASCII kebab case.'],
  ['double--hyphen', 'Slug must use lowercase ASCII kebab case.'],
  ['-leading', 'Slug must use lowercase ASCII kebab case.'],
])('rejects invalid slug %s', (slug, message) => {
  expect(validateArticleCategory({ current: { slug }, now })).toContainEqual({
    message,
    path: 'slug',
  })
})

it('rejects a 241-character landing introduction but accepts 240 emoji', () => {
  expect(
    validateArticleCategory({ current: { landingIntro: '😀'.repeat(240) }, now }),
  ).not.toContainEqual(expect.objectContaining({ path: 'landingIntro' }))
  expect(
    validateArticleCategory({ current: { landingIntro: '😀'.repeat(241) }, now }),
  ).toContainEqual(expect.objectContaining({ path: 'landingIntro' }))
})

it('allows incomplete archive governance in a draft', () => {
  expect(
    validateArticleCategory({ current: { _status: 'draft', status: 'active' }, now }),
  ).toEqual([])
})

it('requires complete governance for publication', () => {
  const issues = validateArticleCategory({
    current: { _status: 'published', status: 'active' },
    now,
  })
  expect(issues.map(({ path }) => path)).toEqual([
    'landingIntro',
    'owner',
    'reviewedAt',
    'reviewDueAt',
    'archiveOnwardPath.heading',
    'archiveOnwardPath.summary',
    'archiveOnwardPath.intent',
  ])
})

it('rejects future reviewed dates and non-future active review due dates', () => {
  const issues = validateArticleCategory({
    current: {
      _status: 'published',
      archiveOnwardPath: { heading: 'Next', intent: 'programs', summary: 'Browse programs.' },
      landingIntro: 'Career guidance.',
      owner: 1,
      reviewedAt: '2026-08-06T00:00:00.000Z',
      reviewDueAt: '2026-08-05T00:00:00.000Z',
      status: 'active',
    },
    now,
  })
  expect(issues).toEqual(
    expect.arrayContaining([
      expect.objectContaining({ path: 'reviewedAt' }),
      expect.objectContaining({ path: 'reviewDueAt' }),
    ]),
  )
})

it('allows an archived published record to retain an overdue due date', () => {
  expect(
    validateArticleCategory({
      current: {
        _status: 'published',
        archiveOnwardPath: { heading: 'Next', intent: 'pathfinder', summary: 'Try Pathfinder.' },
        landingIntro: 'Historical guidance.',
        owner: 1,
        reviewedAt: '2025-01-01T00:00:00.000Z',
        reviewDueAt: '2026-01-01T00:00:00.000Z',
        status: 'archived',
      },
      now,
    }),
  ).toEqual([])
})

it('rejects immutable code changes', () => {
  expect(
    validateArticleCategory({ current: { code: 'NEW' }, original: { code: 'OLD' }, now }),
  ).toContainEqual({ message: 'Code cannot be changed after creation.', path: 'code' })
})

it.each([
  [{ id: 7, parentId: 7 }, 'A Category cannot be its own parent.'],
  [{ id: 7, parentId: 8, parentParentId: 9 }, 'A Subcategory parent must be a root Category.'],
  [{ hasChildren: true, id: 7, parentId: 8 }, 'A Category with Subcategories cannot become a Subcategory.'],
])('rejects invalid hierarchy %#', (hierarchy, message) => {
  expect(validateArticleCategory({ current: {}, hierarchy, now })).toContainEqual(
    expect.objectContaining({ message, path: 'parent' }),
  )
})
```

- [ ] **Step 5: Implement the complete pure validator**

Add `HierarchyFacts` and `validateArticleCategory` to `validation.ts`. Keep validation order deterministic so Admin and tests receive stable errors:

```ts
export type HierarchyFacts = {
  hasChildren?: boolean
  id?: RelationshipID
  parentId?: RelationshipID
  parentParentId?: RelationshipID
}

type ValidateArgs = {
  current: ArticleCategoryInput
  hierarchy?: HierarchyFacts
  now: Date
  original?: ArticleCategoryInput
}

const addRequired = (
  issues: ValidationIssue[],
  path: string,
  value: null | string | undefined,
): void => {
  if (!value) issues.push({ message: 'This field is required to publish.', path })
}

export const validateArticleCategory = ({
  current,
  hierarchy = {},
  now,
  original,
}: ValidateArgs): ValidationIssue[] => {
  const issues: ValidationIssue[] = []

  if (current.slug && !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(current.slug)) {
    issues.push({ message: 'Slug must use lowercase ASCII kebab case.', path: 'slug' })
  }
  if (current.landingIntro && countUnicodeCharacters(current.landingIntro) > 240) {
    issues.push({ message: 'Landing introduction cannot exceed 240 characters.', path: 'landingIntro' })
  }
  if (current.archiveOnwardPath?.heading && countUnicodeCharacters(current.archiveOnwardPath.heading) > 80) {
    issues.push({ message: 'Onward heading cannot exceed 80 characters.', path: 'archiveOnwardPath.heading' })
  }
  if (current.archiveOnwardPath?.summary && countUnicodeCharacters(current.archiveOnwardPath.summary) > 180) {
    issues.push({ message: 'Onward summary cannot exceed 180 characters.', path: 'archiveOnwardPath.summary' })
  }
  if (current.displayOrder != null && (!Number.isInteger(current.displayOrder) || current.displayOrder < 0)) {
    issues.push({ message: 'Display order must be a non-negative whole number.', path: 'displayOrder' })
  }
  if (original?.code && current.code !== original.code) {
    issues.push({ message: 'Code cannot be changed after creation.', path: 'code' })
  }
  if (hierarchy.id != null && hierarchy.parentId === hierarchy.id) {
    issues.push({ message: 'A Category cannot be its own parent.', path: 'parent' })
  } else if (hierarchy.parentId != null && hierarchy.parentParentId != null) {
    issues.push({ message: 'A Subcategory parent must be a root Category.', path: 'parent' })
  } else if (hierarchy.parentId != null && hierarchy.hasChildren) {
    issues.push({ message: 'A Category with Subcategories cannot become a Subcategory.', path: 'parent' })
  }

  if (current._status !== 'published') return issues

  addRequired(issues, 'landingIntro', current.landingIntro)
  if (!current.owner) issues.push({ message: 'An owner is required to publish.', path: 'owner' })
  addRequired(issues, 'reviewedAt', current.reviewedAt)
  addRequired(issues, 'reviewDueAt', current.reviewDueAt)
  addRequired(issues, 'archiveOnwardPath.heading', current.archiveOnwardPath?.heading)
  addRequired(issues, 'archiveOnwardPath.summary', current.archiveOnwardPath?.summary)
  if (!current.archiveOnwardPath?.intent) {
    issues.push({ message: 'An onward intent is required to publish.', path: 'archiveOnwardPath.intent' })
  } else if (!AVAILABLE_ARCHIVE_ONWARD_INTENTS.includes(current.archiveOnwardPath.intent as 'programs' | 'pathfinder')) {
    issues.push({
      message: 'This onward intent is unavailable until its target collection is registered.',
      path: 'archiveOnwardPath.intent',
    })
  }

  const reviewedAt = current.reviewedAt ? new Date(current.reviewedAt) : null
  const reviewDueAt = current.reviewDueAt ? new Date(current.reviewDueAt) : null
  if (reviewedAt && (!Number.isFinite(reviewedAt.valueOf()) || reviewedAt > now)) {
    issues.push({ message: 'Reviewed date cannot be in the future.', path: 'reviewedAt' })
  }
  if (reviewDueAt && !Number.isFinite(reviewDueAt.valueOf())) {
    issues.push({ message: 'Review due date must be valid.', path: 'reviewDueAt' })
  } else if (reviewedAt && reviewDueAt && reviewDueAt <= reviewedAt) {
    issues.push({ message: 'Review due date must be after the reviewed date.', path: 'reviewDueAt' })
  } else if (reviewDueAt && current.status !== 'archived' && reviewDueAt <= now) {
    issues.push({ message: 'Review due date must be in the future.', path: 'reviewDueAt' })
  }

  return issues
}
```

- [ ] **Step 6: Run the unit tests and commit**

Run:

```powershell
pnpm test -- src/lib/article-categories/validation.test.ts
pnpm typecheck
git add src/lib/article-categories/archiveOnwardPath.ts src/lib/article-categories/validation.ts src/lib/article-categories/validation.test.ts
git commit -m "feat: add article category governance rules"
```

Expected: focused tests and typecheck pass; commit contains only the three files.

---

### Task 3: Add canonical path helpers with TDD

**Files:**

- Create: `src/lib/article-categories/paths.ts`
- Create: `src/lib/article-categories/paths.test.ts`

- [ ] **Step 1: Write failing path and redirect-plan tests**

Create `paths.test.ts`:

```ts
import { describe, expect, it } from 'vitest'

import { buildCategoryPath, buildRedirectPlan, relationshipID } from './paths'

describe('Article Category paths', () => {
  it('builds root and direct-child archive paths', () => {
    expect(buildCategoryPath({ slug: 'careers' })).toBe('/articles/category/careers')
    expect(buildCategoryPath({ parentSlug: 'careers', slug: 'technology' })).toBe(
      '/articles/category/careers/technology',
    )
  })

  it('extracts IDs from Payload relationship values', () => {
    expect(relationshipID(5)).toBe(5)
    expect(relationshipID({ id: 'abc' })).toBe('abc')
    expect(relationshipID(null)).toBeUndefined()
  })

  it('plans no redirect for an unchanged path', () => {
    expect(buildRedirectPlan({ destination: 3, nextPath: '/a', previousPath: '/a' })).toEqual([])
  })

  it('plans a permanent identity redirect for a moved path', () => {
    expect(buildRedirectPlan({ destination: 3, nextPath: '/b', previousPath: '/a' })).toEqual([
      { destination: 3, nextPath: '/b', sourcePath: '/a' },
    ])
  })
})
```

- [ ] **Step 2: Run the test to verify it fails**

Run `pnpm test -- src/lib/article-categories/paths.test.ts`.

Expected: FAIL because `paths.ts` does not exist.

- [ ] **Step 3: Implement the minimal path module**

Create `paths.ts`:

```ts
import type { RelationshipID } from './validation'

export const relationshipID = (
  value: null | RelationshipID | undefined | { id: RelationshipID },
): RelationshipID | undefined => {
  if (value == null) return undefined
  return typeof value === 'object' ? value.id : value
}

export const buildCategoryPath = ({
  parentSlug,
  slug,
}: {
  parentSlug?: string
  slug: string
}): string =>
  parentSlug
    ? `/articles/category/${parentSlug}/${slug}`
    : `/articles/category/${slug}`

export type RedirectPlan = {
  destination: RelationshipID
  nextPath: string
  sourcePath: string
}

export const buildRedirectPlan = ({
  destination,
  nextPath,
  previousPath,
}: {
  destination: RelationshipID
  nextPath: string
  previousPath: string
}): RedirectPlan[] =>
  previousPath === nextPath ? [] : [{ destination, nextPath, sourcePath: previousPath }]
```

- [ ] **Step 4: Verify and commit**

Run:

```powershell
pnpm test -- src/lib/article-categories/paths.test.ts
git add src/lib/article-categories/paths.ts src/lib/article-categories/paths.test.ts
git commit -m "feat: define article category archive paths"
```

Expected: focused test passes.

---

### Task 4: Define the two Payload collections and Admin behavior with TDD

**Files:**

- Create: `src/collections/ArticleCategories.ts`
- Create: `src/collections/ArticleCategories.test.ts`
- Create: `src/collections/Redirects.ts`
- Create: `src/collections/Redirects.test.ts`
- Create initially: `src/lib/article-categories/hooks.ts`

- [ ] **Step 1: Write failing collection-configuration tests**

The Article Category test must locate fields by name and assert:

```ts
import { describe, expect, it } from 'vitest'

import { ArticleCategories } from './ArticleCategories'

const field = (name: string) => ArticleCategories.fields.find((candidate) => 'name' in candidate && candidate.name === name)

describe('ArticleCategories collection', () => {
  it('uses drafts and useful Admin labels and columns', () => {
    expect(ArticleCategories.slug).toBe('article-categories')
    expect(ArticleCategories.labels).toEqual({ plural: 'Article Categories', singular: 'Article Category' })
    expect(ArticleCategories.admin).toMatchObject({
      defaultColumns: ['code', 'name', 'parent', 'status', '_status', 'updatedAt'],
      useAsTitle: 'name',
    })
    expect(ArticleCategories.versions).toEqual({ drafts: { validate: true } })
  })

  it('defines unique identity fields and root-only parent selection', async () => {
    expect(field('code')).toMatchObject({ index: true, required: true, type: 'text', unique: true })
    expect(field('slug')).toMatchObject({ index: true, required: true, type: 'text', unique: true })
    expect(field('landingIntro')).toMatchObject({ index: true, type: 'textarea', unique: true })
    expect(field('parent')).toMatchObject({ relationTo: 'article-categories', type: 'relationship' })
  })
})
```

The Redirect test must assert system-only writes and a polymorphic destination:

```ts
import { describe, expect, it } from 'vitest'

import { Redirects } from './Redirects'

describe('Redirects collection', () => {
  it('stores unique sources and a permanent Article Category destination', () => {
    expect(Redirects.slug).toBe('redirects')
    expect(Redirects.access?.create?.({} as never)).toBe(false)
    expect(Redirects.access?.update?.({} as never)).toBe(false)
    expect(Redirects.access?.delete?.({} as never)).toBe(false)
    expect(Redirects.fields).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ name: 'sourcePath', required: true, unique: true }),
        expect.objectContaining({ name: 'destination', relationTo: ['article-categories'] }),
      ]),
    )
  })
})
```

- [ ] **Step 2: Run both tests and verify failure**

Run:

```powershell
pnpm test -- src/collections/ArticleCategories.test.ts src/collections/Redirects.test.ts
```

Expected: FAIL because both collection files are missing.

- [ ] **Step 3: Create a typed no-op hook export so the collection compiles during this task**

Create `hooks.ts`:

```ts
import type {
  CollectionAfterChangeHook,
  CollectionBeforeChangeHook,
  CollectionBeforeValidateHook,
} from 'payload'

export const normalizeArticleCategory: CollectionBeforeValidateHook = ({ data }) => data
export const validateArticleCategoryChange: CollectionBeforeChangeHook = ({ data }) => data
export const recordArticleCategoryRedirects: CollectionAfterChangeHook = ({ doc }) => doc
```

- [ ] **Step 4: Implement `ArticleCategories.ts`**

Use `CollectionConfig`, authenticated access, denied routine deletion, root-only picker filtering, and these exact schema choices:

```ts
import type { Access, CollectionConfig, Where } from 'payload'

import { AVAILABLE_ARCHIVE_ONWARD_INTENTS } from '@/lib/article-categories/archiveOnwardPath'
import {
  normalizeArticleCategory,
  recordArticleCategoryRedirects,
  validateArticleCategoryChange,
} from '@/lib/article-categories/hooks'

const authenticated: Access = ({ req }) => Boolean(req.user)

export const ArticleCategories: CollectionConfig = {
  slug: 'article-categories',
  labels: { plural: 'Article Categories', singular: 'Article Category' },
  access: {
    create: authenticated,
    delete: () => false,
    read: authenticated,
    update: authenticated,
    readVersions: authenticated,
  },
  admin: {
    defaultColumns: ['code', 'name', 'parent', 'status', '_status', 'updatedAt'],
    group: 'Articles',
    useAsTitle: 'name',
  },
  versions: { drafts: { validate: true } },
  hooks: {
    beforeValidate: [normalizeArticleCategory],
    beforeChange: [validateArticleCategoryChange],
    afterChange: [recordArticleCategoryRedirects],
  },
  fields: [
    { name: 'code', type: 'text', required: true, unique: true, index: true, admin: { description: 'Stable business code. It cannot be changed after creation.' } },
    { name: 'name', type: 'text', required: true, admin: { description: 'Public Category or Subcategory name.' } },
    { name: 'slug', type: 'text', required: true, unique: true, index: true, admin: { description: 'Lowercase kebab-case public path segment.' } },
    { name: 'landingIntro', type: 'textarea', unique: true, index: true, admin: { description: 'Unique archive introduction. Maximum 240 Unicode characters.' } },
    {
      name: 'parent',
      type: 'relationship',
      relationTo: 'article-categories',
      maxDepth: 1,
      filterOptions: ({ id }): Where => ({
        and: [
          { parent: { exists: false } },
          ...(id == null ? [] : [{ id: { not_equals: id } }]),
        ],
      }),
      admin: { allowCreate: false, allowEdit: false, description: 'Leave empty for a root Category. Select one root for a Subcategory.' },
    },
    { name: 'displayOrder', type: 'number', required: true, defaultValue: 0, min: 0, admin: { description: 'Non-negative whole number used for governed ordering.' } },
    { name: 'owner', type: 'relationship', relationTo: 'users', maxDepth: 0, admin: { allowCreate: false, description: 'MMDC user accountable for this Category.' } },
    { name: 'reviewedAt', type: 'date', admin: { date: { pickerAppearance: 'dayAndTime' } } },
    { name: 'reviewDueAt', type: 'date', admin: { date: { pickerAppearance: 'dayAndTime' } } },
    {
      name: 'archiveOnwardPath',
      type: 'group',
      admin: { description: 'One governed next step for the future archive page.' },
      fields: [
        { name: 'heading', type: 'text', admin: { description: 'Maximum 80 Unicode characters.' } },
        { name: 'summary', type: 'textarea', admin: { description: 'Maximum 180 Unicode characters.' } },
        {
          name: 'intent',
          type: 'select',
          options: AVAILABLE_ARCHIVE_ONWARD_INTENTS.map((value) => ({
            label: value === 'programs' ? 'Programs' : 'Pathfinder',
            value,
          })),
        },
      ],
    },
    {
      name: 'status',
      type: 'select',
      required: true,
      defaultValue: 'active',
      options: [
        { label: 'Active', value: 'active' },
        { label: 'Archived', value: 'archived' },
      ],
    },
  ],
}
```

- [ ] **Step 5: Implement `Redirects.ts`**

```ts
import type { Access, CollectionConfig } from 'payload'

const authenticated: Access = ({ req }) => Boolean(req.user)

export const Redirects: CollectionConfig = {
  slug: 'redirects',
  labels: { plural: 'Redirects', singular: 'Redirect' },
  access: {
    create: () => false,
    delete: () => false,
    read: authenticated,
    update: () => false,
  },
  admin: {
    defaultColumns: ['sourcePath', 'destination', 'reason', 'createdAt'],
    group: 'System',
    useAsTitle: 'sourcePath',
  },
  fields: [
    { name: 'sourcePath', type: 'text', required: true, unique: true, index: true, admin: { readOnly: true } },
    { name: 'destination', type: 'relationship', relationTo: ['article-categories'], required: true, maxDepth: 0, admin: { readOnly: true } },
    { name: 'redirectType', type: 'select', required: true, defaultValue: 'permanent', options: [{ label: 'Permanent', value: 'permanent' }], admin: { readOnly: true } },
    { name: 'reason', type: 'select', required: true, options: [{ label: 'Slug change', value: 'slug_change' }, { label: 'Parent change', value: 'parent_change' }], admin: { readOnly: true } },
    { name: 'createdBy', type: 'relationship', relationTo: 'users', maxDepth: 0, admin: { readOnly: true } },
  ],
}
```

- [ ] **Step 6: Run tests, format, and commit**

Run:

```powershell
pnpm test -- src/collections/ArticleCategories.test.ts src/collections/Redirects.test.ts
pnpm format
pnpm typecheck
git add src/collections/ArticleCategories.ts src/collections/ArticleCategories.test.ts src/collections/Redirects.ts src/collections/Redirects.test.ts src/lib/article-categories/hooks.ts
git commit -m "feat: define article category collections"
```

Expected: collection tests and typecheck pass. Payload 3.87 exposes `access.readVersions`; keep it authenticated and assert it alongside ordinary read access.

---

### Task 5: Connect hierarchy and publication validation through hooks

**Files:**

- Modify: `src/lib/article-categories/hooks.ts`
- Create: `src/lib/article-categories/hooks.test.ts`

- [ ] **Step 1: Write failing hook tests using a narrow request mock**

Test these observable behaviors:

```ts
import { describe, expect, it, vi } from 'vitest'

import { normalizeArticleCategory, validateArticleCategoryChange } from './hooks'

describe('Article Category hooks', () => {
  it('normalizes incoming values before Payload field validation', async () => {
    await expect(
      normalizeArticleCategory({ data: { code: ' CAT ', name: ' Careers ', slug: 'CAREERS' } } as never),
    ).resolves.toMatchObject({ code: 'CAT', name: 'Careers', slug: 'careers' })
  })

  it('loads the selected parent and rejects a third level', async () => {
    const findByID = vi.fn().mockResolvedValue({ id: 2, parent: 1 })
    const find = vi.fn().mockResolvedValue({ docs: [] })
    await expect(
      validateArticleCategoryChange({
        data: { _status: 'draft', parent: 2 },
        operation: 'update',
        originalDoc: { id: 3, code: 'CHILD', parent: null },
        req: { payload: { find, findByID } },
      } as never),
    ).rejects.toMatchObject({ name: 'ValidationError' })
    expect(findByID).toHaveBeenCalledWith(expect.objectContaining({ collection: 'article-categories', id: 2 }))
  })

  it('rejects turning a root with children into a Subcategory', async () => {
    const findByID = vi.fn().mockResolvedValue({ id: 9, parent: null })
    const find = vi.fn().mockResolvedValue({ docs: [{ id: 4 }] })
    await expect(
      validateArticleCategoryChange({
        data: { _status: 'draft', parent: 9 },
        operation: 'update',
        originalDoc: { id: 3, code: 'ROOT', parent: null },
        req: { payload: { find, findByID } },
      } as never),
    ).rejects.toMatchObject({ name: 'ValidationError' })
  })
})
```

- [ ] **Step 2: Run the hook tests and verify failure**

Run `pnpm test -- src/lib/article-categories/hooks.test.ts`.

Expected: normalization assertion fails and validation hooks do not query or reject.

- [ ] **Step 3: Implement normalization, related-record facts, and Payload validation errors**

Replace the no-op `beforeValidate` and `beforeChange` hooks. The final hook logic must:

```ts
import {
  ValidationError,
  type CollectionAfterChangeHook,
  type CollectionBeforeChangeHook,
  type CollectionBeforeValidateHook,
} from 'payload'

import { normalizeArticleCategoryInput, validateArticleCategory } from './validation'
import { relationshipID } from './paths'

export const normalizeArticleCategory: CollectionBeforeValidateHook = ({ data }) =>
  data ? normalizeArticleCategoryInput(data) : data

export const validateArticleCategoryChange: CollectionBeforeChangeHook = async ({
  data,
  operation,
  originalDoc,
  req,
}) => {
  const current = { ...(originalDoc ?? {}), ...data }
  const id = originalDoc?.id
  const parentId = relationshipID(current.parent)
  const parent = parentId == null
    ? null
    : await req.payload.findByID({
        collection: 'article-categories',
        id: parentId,
        depth: 0,
        draft: false,
        req,
      })
  const children = id == null
    ? { docs: [] }
    : await req.payload.find({
        collection: 'article-categories',
        depth: 0,
        draft: false,
        limit: 1,
        pagination: false,
        req,
        where: { parent: { equals: id } },
      })

  const issues = validateArticleCategory({
    current,
    hierarchy: {
      hasChildren: children.docs.length > 0,
      id,
      parentId,
      parentParentId: relationshipID(parent?.parent),
    },
    now: new Date(),
    original: operation === 'update' ? originalDoc : undefined,
  })

  if (issues.length > 0) {
    throw new ValidationError({
      collection: 'article-categories',
      id,
      req,
      errors: issues,
    })
  }

  return data
}
```

Catch Payload's not-found result for the candidate parent and throw a `ValidationError` with path `parent` and message `Selected parent does not exist.`.

- [ ] **Step 4: Add tests for self-parent, code immutability, incomplete draft, valid publish, and invalid publish**

Use the same narrow mock and assert exact error paths from `ValidationError.data.errors`. Include a valid published active record with dates based on a fake timer:

```ts
vi.useFakeTimers()
vi.setSystemTime(new Date('2026-08-05T00:00:00.000Z'))
```

Restore real timers in `afterEach`.

- [ ] **Step 5: Run focused and regression tests, then commit**

Run:

```powershell
pnpm test -- src/lib/article-categories/validation.test.ts src/lib/article-categories/hooks.test.ts
pnpm typecheck
git add src/lib/article-categories/hooks.ts src/lib/article-categories/hooks.test.ts
git commit -m "feat: enforce article category governance"
```

Expected: all focused tests pass.

---

### Task 6: Add transactional redirect recording with TDD

**Files:**

- Modify: `src/lib/article-categories/hooks.ts`
- Modify: `src/lib/article-categories/hooks.test.ts`

- [ ] **Step 1: Write failing tests for published-only redirect behavior**

Add hook tests proving:

1. A draft-only slug edit performs no redirect writes.
2. Publishing `old-slug` as `new-slug` creates `/articles/category/old-slug` pointing to the same Category identity.
3. Moving a published child from root `old-root` to `new-root` records the old child path with reason `parent_change`.
4. Renaming a published root also records old paths for each published direct child.
5. A source already owned by another destination raises `ValidationError` before any redirect write.
6. Returning to the same Category's historical path deletes that obsolete redirect and records the path being left.

The create assertion must require the original transaction request:

```ts
expect(create).toHaveBeenCalledWith(
  expect.objectContaining({
    collection: 'redirects',
    overrideAccess: true,
    req,
    data: {
      createdBy: 11,
      destination: { relationTo: 'article-categories', value: 3 },
      reason: 'slug_change',
      redirectType: 'permanent',
      sourcePath: '/articles/category/old-slug',
    },
  }),
)
```

- [ ] **Step 2: Run the hook tests and verify redirect cases fail**

Run `pnpm test -- src/lib/article-categories/hooks.test.ts`.

Expected: governance tests pass; redirect tests fail because `recordArticleCategoryRedirects` is still a no-op.

- [ ] **Step 3: Capture the last live paths in `beforeChange`**

Use Payload's draft behavior deliberately: a normal `findByID({ draft: false })` reads the live main-table document while newer drafts remain only in the versions table. When the incoming merged record has `_status: 'published'`:

- Load the current live version before the write.
- Ignore it if it has never been published.
- Resolve its old parent at depth zero.
- Build the old and new paths.
- For a root rename, load direct children from the live table with `_status: published` and collect their old paths.
- Store the resulting plans on `context.articleCategoryRedirectPlans` for `afterChange`.

Use a local type rather than untyped context values:

```ts
type CategoryRedirectPlan = {
  destination: number | string
  nextPath: string
  reason: 'parent_change' | 'slug_change'
  sourcePath: string
}
```

Before returning from `beforeChange`, query `redirects` for each `nextPath`. A match for another destination is a validation error. A match for the same destination is saved on context for removal after the Category write.

- [ ] **Step 4: Persist redirect changes in `afterChange` using the same transaction**

Implement `recordArticleCategoryRedirects` so it:

- exits unless `doc._status === 'published'`;
- deletes only obsolete redirect records explicitly captured for this same Category;
- creates or updates one unique redirect per source path;
- passes `req` and `overrideAccess: true` to every Local API write;
- stores a polymorphic identity relationship, never a raw destination URL;
- uses `req.user?.id` for `createdBy` when available;
- awaits every write so an error rolls the entire Category update back.

The core write shape is:

```ts
await req.payload.create({
  collection: 'redirects',
  overrideAccess: true,
  req,
  data: {
    createdBy: req.user?.id,
    destination: {
      relationTo: 'article-categories',
      value: plan.destination,
    },
    reason: plan.reason,
    redirectType: 'permanent',
    sourcePath: plan.sourcePath,
  },
})
```

- [ ] **Step 5: Run tests and commit**

Run:

```powershell
pnpm test -- src/lib/article-categories/hooks.test.ts src/lib/article-categories/paths.test.ts
pnpm typecheck
git add src/lib/article-categories/hooks.ts src/lib/article-categories/hooks.test.ts
git commit -m "feat: record article category redirects"
```

Expected: all hook and path tests pass; mocked writes show the original request object.

---

### Task 7: Register collections and add reusable integration fixtures

**Files:**

- Modify: `src/payload.config.ts`
- Create: `src/test/fixtures/articleCategories.ts`
- Create: `src/lib/article-categories/integration.test.ts`

- [ ] **Step 1: Add deterministic fixture builders**

Create a builder that accepts an owner ID and a unique suffix so parallel or repeated runs do not collide:

```ts
export const buildArticleCategoryFixtures = ({
  owner,
  suffix,
}: {
  owner: number | string
  suffix: string
}) => {
  const reviewedAt = '2026-08-01T00:00:00.000Z'
  const reviewDueAt = '2030-08-01T00:00:00.000Z'

  const publishedRoot = {
    _status: 'published' as const,
    archiveOnwardPath: {
      heading: 'Find your next step',
      intent: 'programs' as const,
      summary: 'Browse MMDC programs related to this subject.',
    },
    code: `ROOT-${suffix}`,
    displayOrder: 10,
    landingIntro: `Root introduction ${suffix}`,
    name: `Root ${suffix}`,
    owner,
    reviewedAt,
    reviewDueAt,
    slug: `root-${suffix}`,
    status: 'active' as const,
  }

  return {
    archived: { ...publishedRoot, code: `ARCH-${suffix}`, landingIntro: `Archived introduction ${suffix}`, name: `Archived ${suffix}`, reviewDueAt: '2026-08-02T00:00:00.000Z', slug: `archived-${suffix}`, status: 'archived' as const },
    draft: { code: `DRAFT-${suffix}`, displayOrder: 30, name: `Draft ${suffix}`, slug: `draft-${suffix}`, status: 'active' as const },
    publishedChild: { ...publishedRoot, code: `CHILD-${suffix}`, displayOrder: 20, landingIntro: `Child introduction ${suffix}`, name: `Child ${suffix}`, slug: `child-${suffix}` },
    publishedRoot,
  }
}
```

- [ ] **Step 2: Register both collections in Payload config**

Add imports and preserve existing order:

```ts
import { ArticleCategories } from '@/collections/ArticleCategories'
import { Media } from '@/collections/Media'
import { Redirects } from '@/collections/Redirects'
import { Users } from '@/collections/Users'
```

Use:

```ts
collections: [Users, Media, ArticleCategories, Redirects],
```

- [ ] **Step 3: Write the failing PostgreSQL-backed integration suite**

The suite must dynamically load `.env` before importing Payload config:

```ts
import { existsSync } from 'node:fs'
import { afterAll, beforeAll, describe, expect, it } from 'vitest'
import type { Payload } from 'payload'

import { buildArticleCategoryFixtures } from '@/test/fixtures/articleCategories'

let payload: Payload
let userID: number | string
const suffix = `art001a-${process.pid}`

beforeAll(async () => {
  if (existsSync('.env')) process.loadEnvFile('.env')
  const [{ getPayload }, { default: config }] = await Promise.all([
    import('payload'),
    import('@payload-config'),
  ])
  payload = await getPayload({ config })
  const user = await payload.create({
    collection: 'users',
    data: { email: `${suffix}@example.test`, password: 'integration-only-password' },
  })
  userID = user.id
})

afterAll(async () => {
  if (payload) {
    await payload.delete({ collection: 'redirects', where: { sourcePath: { contains: suffix } } })
    await payload.delete({ collection: 'article-categories', where: { code: { contains: suffix } } })
    await payload.delete({ collection: 'users', id: userID })
    await payload.destroy()
  }
})
```

Add tests for:

- authenticated root draft creation with incomplete governance;
- authenticated valid root publication;
- valid direct-child publication;
- self-parent rejection;
- selecting a child as parent rejection;
- root-with-child reparent rejection;
- code immutability;
- unique code, slug, and landing introduction enforced by PostgreSQL;
- invalid publish fields rejected with named paths;
- archived overdue record accepted;
- deletion denied with `overrideAccess: false` and an authenticated user;
- slug change redirect record;
- child reparent redirect record;
- root rename creates root and child redirect records;
- draft-only slug change produces no redirect until publish;
- Category writes contain no Article relationship or URL field.

Use `overrideAccess: false, user` for access tests. Cleanup intentionally uses Payload's default override access and targets only the unique fixture suffix.

- [ ] **Step 4: Run integration tests against a disposable local database and fix only implementation defects**

Start local services with the repository workflow, create a disposable `mmdc_art001a_test` database, and derive its URL from the ignored local `.env` without printing the credential. Never use a shared or production database.

Run:

```powershell
pnpm local:up
docker compose --env-file .env -f compose.local.yml exec -T postgres sh -lc 'createdb -U "$POSTGRES_USER" mmdc_art001a_test'
$localDatabaseUrl = (Get-Content .env | Where-Object { $_ -like 'DATABASE_URL=*' } | Select-Object -First 1).Substring('DATABASE_URL='.Length)
$testDatabaseUrl = $localDatabaseUrl -replace '/[^/?]+(\?.*)?$', '/mmdc_art001a_test$1'
$env:APP_ENV='local'
$env:PAYLOAD_DB_PUSH='true'
$env:DATABASE_URL=$testDatabaseUrl
pnpm test -- src/lib/article-categories/integration.test.ts
```

Expected: `createdb` succeeds and the integration suite passes. If the database already exists, verify its exact name is `mmdc_art001a_test`, keep `DATABASE_URL` pointed to it, and continue without dropping any database.

- [ ] **Step 5: Run all Category tests and commit**

Run:

```powershell
pnpm test -- src/collections/ArticleCategories.test.ts src/collections/Redirects.test.ts src/lib/article-categories
git add src/payload.config.ts src/test/fixtures/articleCategories.ts src/lib/article-categories/integration.test.ts
git commit -m "test: cover article category governance"
```

Expected: all Category unit, config, hook, and integration tests pass.

---

### Task 8: Generate Payload types and the reversible migration

**Files:**

- Modify by generator: `src/payload-types.ts`
- Create by generator, then rename: `src/migrations/20260805_000000_article_category_governance.ts`
- Create by generator, then rename: `src/migrations/20260805_000000_article_category_governance.json`
- Modify: `src/migrations/index.ts`

- [ ] **Step 1: Regenerate Payload types and inspect the generated contract**

Run:

```powershell
pnpm generate:types
git diff -- src/payload-types.ts
```

Expected generated types:

- `Config.collections` contains `'article-categories'` and `redirects`.
- `ArticleCategory` contains all approved fields plus `_status` and timestamps.
- `Redirect` contains a polymorphic Article Category destination.
- `archiveOnwardPath.intent` contains only `programs | pathfinder` in the current schema.
- No Article, Offering, taxonomy target, public URL, label, image, layout, or temporary target type appears.

- [ ] **Step 2: Create the migration from the new schema**

Run:

```powershell
pnpm migrate:create -- article-category-governance
Get-ChildItem src/migrations/*article_category_governance* -File
```

Expected: one TypeScript migration and one JSON snapshot. Before renaming, verify both generated paths resolve inside the repository's `src/migrations` directory.

- [ ] **Step 3: Rename the generated pair to the deterministic reviewed filenames**

Resolve the two generated files from the immediately preceding command, verify there is exactly one `.ts` and one `.json`, then rename them within `src/migrations/` to:

```text
src/migrations/20260805_000000_article_category_governance.ts
src/migrations/20260805_000000_article_category_governance.json
```

Do not overwrite existing files. Stop if either destination already exists.

- [ ] **Step 4: Register the migration explicitly**

Update `src/migrations/index.ts` to:

```ts
import * as migration_20260803_144731_initial_foundation from './20260803_144731_initial_foundation'
import * as migration_20260805_000000_article_category_governance from './20260805_000000_article_category_governance'

export const migrations = [
  {
    up: migration_20260803_144731_initial_foundation.up,
    down: migration_20260803_144731_initial_foundation.down,
    name: '20260803_144731_initial_foundation',
  },
  {
    up: migration_20260805_000000_article_category_governance.up,
    down: migration_20260805_000000_article_category_governance.down,
    name: '20260805_000000_article_category_governance',
  },
]
```

- [ ] **Step 5: Inspect migration structure before running it**

Confirm the `up` migration creates:

- `article_categories` and its version table;
- Article Category relationships to parent and owner;
- `redirects` and its relationship table for the polymorphic destination;
- unique indexes for Category code, slug, non-null introduction, and redirect source;
- indexes for timestamps and relationship foreign keys;
- `_status`, `status`, review dates, display order, and onward-path columns.

Confirm the `down` migration drops only the tables, relationships, enum types, and indexes created by this migration. It must not drop Users, Media, Payload preferences, locks, or the migrations table.

- [ ] **Step 6: Verify up, down, and up on a disposable database**

With `DATABASE_URL` still pointing only to `mmdc_art001a_test`, run:

```powershell
$env:APP_ENV='local'
$env:PAYLOAD_DB_PUSH='false'
pnpm migrate
pnpm migrate:status
pnpm payload migrate:down
pnpm migrate:status
pnpm migrate
pnpm migrate:status
```

Expected sequence: both migrations applied; new migration rolled back; both migrations applied again. Never run `migrate:down`, `migrate:reset`, `migrate:refresh`, or `migrate:fresh` against the normal local database or a shared environment.

- [ ] **Step 7: Verify generated stability and commit**

Run:

```powershell
pnpm generate:types
git diff --exit-code -- src/payload-types.ts
pnpm format
git add src/payload-types.ts src/migrations/20260805_000000_article_category_governance.ts src/migrations/20260805_000000_article_category_governance.json src/migrations/index.ts
git commit -m "feat: migrate article category governance"
```

Expected: the second type generation produces no drift; commit includes only generated types and migration artifacts.

---

### Task 9: Run full quality and scope gates

**Files:**

- Inspect all ART-001A changes
- Modify only files that fail an established gate for an ART-001A reason

- [ ] **Step 1: Run all repository quality gates**

Run:

```powershell
pnpm check
pnpm build
docker build --tag mmdc-v3:art-001a .
```

Expected: formatting, lint, typecheck, all Vitest tests, production build, and production container build pass.

- [ ] **Step 2: Verify generated Admin artifacts do not drift**

Run:

```powershell
pnpm generate:importmap
pnpm exec prettier --write 'src/app/(payload)/admin/importMap.js'
git diff --exit-code -- 'src/app/(payload)/admin/importMap.js'
```

Expected: no import-map diff because ART-001A adds no custom Admin component.

- [ ] **Step 3: Audit the final diff and prohibited scope**

Run:

```powershell
git status --short
git diff origin/development...HEAD --stat
git diff origin/development...HEAD
rg -n "articles/category|generateMetadata|sitemap|eligibleArticle|ArticlePreview|pageSize|pagination" src --glob '!src/lib/article-categories/paths.ts' --glob '!src/lib/article-categories/paths.test.ts'
```

Expected:

- `AGENTS.md` is still untracked and unchanged.
- Every changed line maps to Article Category schema, redirect persistence, tests, fixtures, generated types, or migration.
- The only canonical archive path strings are in the path helper and its tests.
- No route, page, Article collection, eligible count, pagination, navigation, SEO, redirect handler, or sitemap behavior exists.
- `package.json` and `pnpm-lock.yaml` have no diff.

- [ ] **Step 4: Confirm acceptance criteria from tests and generated schema**

Record a pass/fail checklist in the implementation handoff for:

- root without parent;
- direct child with one root parent;
- self-parent, cycle, and third-level rejection;
- immutable unique code;
- unique slug and governed published-slug redirect history;
- 240-Unicode-character introduction limit;
- incomplete drafts;
- complete active publication governance;
- archived lifecycle and denied routine deletion;
- parent/slug operations never touch Article URLs;
- Admin labels, controls, types, fixtures, migration, and tests;
- every ART-001B behavior absent.

- [ ] **Step 5: Commit any gate-only correction separately**

If and only if a gate required an ART-001A correction, inspect the diff, then stage only this fixed allowlist of ART-001A paths (Git ignores unchanged paths):

```powershell
git add src/collections/ArticleCategories.ts src/collections/ArticleCategories.test.ts src/collections/Redirects.ts src/collections/Redirects.test.ts src/lib/article-categories/archiveOnwardPath.ts src/lib/article-categories/validation.ts src/lib/article-categories/validation.test.ts src/lib/article-categories/paths.ts src/lib/article-categories/paths.test.ts src/lib/article-categories/hooks.ts src/lib/article-categories/hooks.test.ts src/lib/article-categories/integration.test.ts src/test/fixtures/articleCategories.ts src/payload.config.ts src/payload-types.ts src/migrations/20260805_000000_article_category_governance.ts src/migrations/20260805_000000_article_category_governance.json src/migrations/index.ts
git commit -m "fix: satisfy article category quality gates"
```

Never use `git add .` in this worktree. If no correction was needed, do not create an empty commit.

---

## Final implementation handoff

Report:

- branch and commit list;
- exact changed files;
- migration name and up/down/up result;
- `pnpm check`, `pnpm build`, and Docker build results;
- explicit confirmation that `AGENTS.md` and all prior user-owned work remain untouched;
- explicit confirmation that ART-001B and Article behavior were not implemented;
- any environment-only limitation, with the exact command the user can run to close it.
