# LLMs.txt CMS Publishing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Payload-managed `llms-txt` collection and public `/llms.txt` endpoint that serves published active content as plain text with deterministic fallback behavior.

**Architecture:** Implement one new collection for authoring and activation state, one serializer utility for rich-text-to-plain-text mapping, one route handler for HTTP delivery, and focused tests that validate activation logic, serializer output, and route selection behavior. Keep behavior additive and aligned with existing `robots.ts` and Payload hook patterns.

**Tech Stack:** Next.js App Router, Payload CMS v3, TypeScript, Vitest

---

## File Structure

- Create: `src/collections/LLMsTxt.ts`
  - Defines `llms-txt` schema, drafts support, `isActive` field, and collection hooks.
- Create: `src/collections/LLMsTxt/enforceSingleActive.ts`
  - Encapsulates active-entry enforcement logic and pure helper for deterministic fallback.
- Create: `src/utilities/llmsTextSerializer.ts`
  - Converts Payload rich text JSON into plain text (`heading`, `paragraph`, bullets, links).
- Create: `src/utilities/llmsTextSerializer.test.ts`
  - Unit tests for serializer mapping and unknown-node resilience.
- Create: `src/collections/LLMsTxt/enforceSingleActive.test.ts`
  - Unit tests for single-active behavior and updatedAt fallback selection.
- Create: `src/app/llms.txt/route.ts`
  - Serves `/llms.txt` as `text/plain; charset=utf-8` from published entries only.
- Create: `src/app/llms.txt/route.test.ts`
  - Route tests for normal, empty, multiple-active, and failure responses.
- Modify: `src/payload.config.ts`
  - Registers the new `LLMsTxt` collection.
- Modify: `vitest.config.ts`
  - Adds a node/unit test workspace alongside existing Storybook browser tests.
- Modify: `package.json`
  - Adds `test:unit` script for deterministic local and CI execution.

---

### Task 1: Enable unit test workspace for backend logic

**Files:**
- Modify: `vitest.config.ts`
- Modify: `package.json`

- [ ] **Step 1: Add node/unit workspace to Vitest config**

```ts
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { defineConfig } from 'vitest/config'

import { storybookTest } from '@storybook/addon-vitest/vitest-plugin'

const dirname =
  typeof __dirname !== 'undefined' ? __dirname : path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  test: {
    workspace: [
      {
        extends: true,
        test: {
          name: 'unit',
          environment: 'node',
          include: ['src/**/*.test.ts'],
          exclude: ['src/**/*.stories.*'],
          clearMocks: true,
          restoreMocks: true,
        },
      },
      {
        extends: true,
        plugins: [storybookTest({ configDir: path.join(dirname, '.storybook') })],
        test: {
          name: 'storybook',
          browser: {
            enabled: true,
            headless: true,
            name: 'chromium',
            provider: 'playwright',
          },
          setupFiles: ['.storybook/vitest.setup.ts'],
        },
      },
    ],
  },
})
```

- [ ] **Step 2: Add unit test script in package.json**

```json
{
  "scripts": {
    "test:unit": "vitest run --project unit"
  }
}
```

- [ ] **Step 3: Verify unit workspace boots**

Run: `pnpm test:unit`

Expected: command exits `0` (even with no tests yet) and prints project name `unit`.

- [ ] **Step 4: Commit test harness setup**

```bash
git add vitest.config.ts package.json
git commit -m "test: add unit vitest workspace for server logic"
```

---

### Task 2: Implement `llms-txt` collection and activation enforcement

**Files:**
- Create: `src/collections/LLMsTxt/enforceSingleActive.ts`
- Create: `src/collections/LLMsTxt.ts`
- Modify: `src/payload.config.ts`
- Test: `src/collections/LLMsTxt/enforceSingleActive.test.ts`

- [ ] **Step 1: Write failing tests for selection and activation rules**

```ts
import { describe, expect, it, vi } from 'vitest'

import { pickActiveOrLatestUpdated } from './enforceSingleActive'

describe('pickActiveOrLatestUpdated', () => {
  it('returns undefined for empty input', () => {
    expect(pickActiveOrLatestUpdated([])).toBeUndefined()
  })

  it('returns the single active doc when only one is active', () => {
    const result = pickActiveOrLatestUpdated([
      { id: '1', isActive: true, updatedAt: '2026-05-21T01:00:00.000Z' },
      { id: '2', isActive: false, updatedAt: '2026-05-21T02:00:00.000Z' },
    ])

    expect(result?.id).toBe('1')
  })

  it('falls back to newest updatedAt when multiple active docs exist', () => {
    const result = pickActiveOrLatestUpdated([
      { id: '1', isActive: true, updatedAt: '2026-05-21T01:00:00.000Z' },
      { id: '2', isActive: true, updatedAt: '2026-05-21T03:00:00.000Z' },
    ])

    expect(result?.id).toBe('2')
  })
})

describe('enforceSingleActive hook', () => {
  it('deactivates other docs when current doc is active', async () => {
    const update = vi.fn().mockResolvedValue(undefined)

    const hookModule = await import('./enforceSingleActive')
    await hookModule.enforceSingleActiveAfterChange({
      doc: { id: 'current', isActive: true },
      req: {
        payload: {
          find: vi.fn().mockResolvedValue({ docs: [{ id: 'a' }, { id: 'b' }] }),
          update,
        },
      },
      operation: 'update',
    } as never)

    expect(update).toHaveBeenCalledTimes(2)
  })
})
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `pnpm test:unit -- src/collections/LLMsTxt/enforceSingleActive.test.ts`

Expected: FAIL with module/file-not-found errors for `enforceSingleActive.ts`.

- [ ] **Step 3: Implement activation helper and afterChange hook**

```ts
import type { CollectionAfterChangeHook } from 'payload'

type CandidateDoc = {
  id: string
  isActive?: boolean | null
  updatedAt?: string | null
}

export const pickActiveOrLatestUpdated = <T extends CandidateDoc>(docs: T[]): T | undefined => {
  if (!docs.length) return undefined

  const active = docs.filter((doc) => Boolean(doc.isActive))

  if (active.length === 1) return active[0]

  if (active.length > 1) {
    return [...active].sort((a, b) => {
      const left = new Date(a.updatedAt ?? 0).getTime()
      const right = new Date(b.updatedAt ?? 0).getTime()
      return right - left
    })[0]
  }

  return undefined
}

export const enforceSingleActiveAfterChange: CollectionAfterChangeHook = async ({
  doc,
  req,
  operation,
}) => {
  if (!doc?.isActive) return doc
  if (operation !== 'create' && operation !== 'update') return doc

  const result = await req.payload.find({
    collection: 'llms-txt',
    depth: 0,
    limit: 100,
    where: {
      and: [
        { id: { not_equals: doc.id } },
        { isActive: { equals: true } },
      ],
    },
    draft: false,
  })

  await Promise.all(
    result.docs.map((item) =>
      req.payload.update({
        collection: 'llms-txt',
        id: item.id,
        data: { isActive: false },
        depth: 0,
        context: { disableRevalidate: true },
      }),
    ),
  )

  return doc
}
```

- [ ] **Step 4: Implement collection schema and register it**

```ts
// src/collections/LLMsTxt.ts
import type { CollectionConfig } from 'payload'
import { enforceSingleActiveAfterChange } from './LLMsTxt/enforceSingleActive'

export const LLMsTxt: CollectionConfig = {
  slug: 'llms-txt',
  labels: {
    singular: 'LLMs TXT Entry',
    plural: 'LLMs TXT Entries',
  },
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'isActive', 'updatedAt'],
    description:
      'Manage public llms.txt content. Content appears on production after publish and deploy/sync.',
  },
  fields: [
    {
      name: 'title',
      type: 'text',
      required: true,
    },
    {
      name: 'isActive',
      type: 'checkbox',
      defaultValue: false,
    },
    {
      name: 'content',
      type: 'richText',
      required: true,
    },
  ],
  versions: {
    drafts: {
      autosave: false,
      schedulePublish: true,
    },
    maxPerDoc: 25,
  },
  hooks: {
    afterChange: [enforceSingleActiveAfterChange],
  },
}
```

```ts
// src/payload.config.ts (imports + collections array)
import { LLMsTxt } from './collections/LLMsTxt'

collections: [
  Users,
  Media,
  Pages,
  Menu,
  Quiz,
  Images,
  Articles,
  Press,
  Categories,
  Files,
  BachelorPrograms,
  LLMsTxt,
],
```

- [ ] **Step 5: Run focused tests and commit**

Run: `pnpm test:unit -- src/collections/LLMsTxt/enforceSingleActive.test.ts`

Expected: PASS with all tests green.

```bash
git add src/collections/LLMsTxt.ts src/collections/LLMsTxt/enforceSingleActive.ts src/collections/LLMsTxt/enforceSingleActive.test.ts src/payload.config.ts
git commit -m "feat(cms): add llms txt collection with single active enforcement"
```

---

### Task 3: Build rich-text-to-plain-text serializer with tests

**Files:**
- Create: `src/utilities/llmsTextSerializer.ts`
- Test: `src/utilities/llmsTextSerializer.test.ts`

- [ ] **Step 1: Write failing serializer tests from agreed formatting rules**

```ts
import { describe, expect, it } from 'vitest'

import { serializeLLMsRichTextToPlain } from './llmsTextSerializer'

describe('serializeLLMsRichTextToPlain', () => {
  it('serializes heading and paragraph lines', () => {
    const result = serializeLLMsRichTextToPlain({
      root: {
        type: 'root',
        children: [
          { type: 'heading', children: [{ type: 'text', text: 'MMDC' }] },
          { type: 'paragraph', children: [{ type: 'text', text: 'Digital-first college.' }] },
        ],
      },
    })

    expect(result).toContain('MMDC')
    expect(result).toContain('Digital-first college.')
  })

  it('serializes list items with dash prefix', () => {
    const result = serializeLLMsRichTextToPlain({
      root: {
        type: 'root',
        children: [
          {
            type: 'list',
            listType: 'bullet',
            children: [{ type: 'listitem', children: [{ type: 'text', text: 'Scholarships' }] }],
          },
        ],
      },
    })

    expect(result).toContain('- Scholarships')
  })

  it('serializes links as Label: URL', () => {
    const result = serializeLLMsRichTextToPlain({
      root: {
        type: 'root',
        children: [
          {
            type: 'paragraph',
            children: [
              {
                type: 'link',
                fields: { url: 'https://mmdc.mcl.edu.ph' },
                children: [{ type: 'text', text: 'Website' }],
              },
            ],
          },
        ],
      },
    })

    expect(result).toContain('Website: https://mmdc.mcl.edu.ph')
  })

  it('returns empty string for unknown node trees', () => {
    const result = serializeLLMsRichTextToPlain({
      root: { type: 'root', children: [{ type: 'mystery-node' }] },
    })

    expect(result).toBe('')
  })
})
```

- [ ] **Step 2: Run tests and confirm they fail first**

Run: `pnpm test:unit -- src/utilities/llmsTextSerializer.test.ts`

Expected: FAIL with import-not-found for `llmsTextSerializer.ts`.

- [ ] **Step 3: Implement serializer utility**

```ts
type RichNode = {
  type?: string
  text?: string
  listType?: string
  fields?: { url?: string }
  children?: RichNode[]
}

type RichTextValue = {
  root?: {
    children?: RichNode[]
  }
}

const extractInlineText = (node: RichNode): string => {
  if (node.type === 'text') return node.text ?? ''

  if (node.type === 'link') {
    const label = (node.children ?? []).map(extractInlineText).join('').trim()
    const url = node.fields?.url?.trim() ?? ''
    if (!label && !url) return ''
    if (!label) return url
    if (!url) return label
    return `${label}: ${url}`
  }

  return (node.children ?? []).map(extractInlineText).join('')
}

const toLines = (node: RichNode): string[] => {
  if (node.type === 'heading' || node.type === 'paragraph') {
    const line = (node.children ?? []).map(extractInlineText).join('').trim()
    return line ? [line] : []
  }

  if (node.type === 'list') {
    return (node.children ?? [])
      .filter((child) => child.type === 'listitem')
      .map((item) => (item.children ?? []).map(extractInlineText).join('').trim())
      .filter(Boolean)
      .map((item) => `- ${item}`)
  }

  return (node.children ?? []).flatMap(toLines)
}

export const serializeLLMsRichTextToPlain = (value: RichTextValue | null | undefined): string => {
  const children = value?.root?.children ?? []
  const lines = children.flatMap(toLines).map((line) => line.trim()).filter(Boolean)
  return lines.join('\n\n')
}
```

- [ ] **Step 4: Run serializer tests and commit**

Run: `pnpm test:unit -- src/utilities/llmsTextSerializer.test.ts`

Expected: PASS with 4 passing tests.

```bash
git add src/utilities/llmsTextSerializer.ts src/utilities/llmsTextSerializer.test.ts
git commit -m "feat(llms): add rich text to plain text serializer"
```

---

### Task 4: Implement `/llms.txt` route with deterministic selection

**Files:**
- Create: `src/app/llms.txt/route.ts`
- Test: `src/app/llms.txt/route.test.ts`

- [ ] **Step 1: Write failing route tests with Payload mocks**

```ts
import { beforeEach, describe, expect, it, vi } from 'vitest'

const findMock = vi.fn()

vi.mock('payload', () => ({
  getPayload: vi.fn().mockResolvedValue({ find: findMock }),
}))

vi.mock('@payload-config', () => ({ default: {} }))

vi.mock('@/utilities/llmsTextSerializer', () => ({
  serializeLLMsRichTextToPlain: vi.fn().mockReturnValue('Serialized content'),
}))

describe('GET /llms.txt', () => {
  beforeEach(() => {
    findMock.mockReset()
  })

  it('returns serialized active published content', async () => {
    findMock.mockResolvedValue({
      docs: [{ id: '1', isActive: true, updatedAt: '2026-05-21T03:00:00.000Z', content: {} }],
    })

    const { GET } = await import('./route')
    const response = await GET()

    expect(response.status).toBe(200)
    expect(response.headers.get('content-type')).toContain('text/plain')
    await expect(response.text()).resolves.toBe('Serialized content')
  })

  it('returns empty body when no published docs are available', async () => {
    findMock.mockResolvedValue({ docs: [] })

    const { GET } = await import('./route')
    const response = await GET()

    expect(response.status).toBe(200)
    await expect(response.text()).resolves.toBe('')
  })

  it('returns 500 when payload query throws', async () => {
    findMock.mockRejectedValue(new Error('db down'))

    const { GET } = await import('./route')
    const response = await GET()

    expect(response.status).toBe(500)
  })
})
```

- [ ] **Step 2: Run route tests and verify initial failure**

Run: `pnpm test:unit -- src/app/llms.txt/route.test.ts`

Expected: FAIL with module-not-found for `route.ts`.

- [ ] **Step 3: Implement route using published-only query and fallback rules**

```ts
import configPromise from '@payload-config'
import { getPayload } from 'payload'

import { pickActiveOrLatestUpdated } from '@/collections/LLMsTxt/enforceSingleActive'
import { serializeLLMsRichTextToPlain } from '@/utilities/llmsTextSerializer'

export const GET = async () => {
  try {
    const payload = await getPayload({ config: configPromise })

    const result = await payload.find({
      collection: 'llms-txt',
      depth: 0,
      limit: 100,
      draft: false,
    })

    const selected = pickActiveOrLatestUpdated(result.docs as Array<{
      id: string
      isActive?: boolean
      updatedAt?: string
      content?: unknown
    }>)

    const body = selected?.content ? serializeLLMsRichTextToPlain(selected.content as never) : ''

    return new Response(body, {
      status: 200,
      headers: {
        'content-type': 'text/plain; charset=utf-8',
      },
    })
  } catch (error) {
    console.error('Failed to resolve llms.txt content', error)

    return new Response('Internal Server Error', {
      status: 500,
      headers: {
        'content-type': 'text/plain; charset=utf-8',
      },
    })
  }
}
```

- [ ] **Step 4: Run route tests and commit**

Run: `pnpm test:unit -- src/app/llms.txt/route.test.ts`

Expected: PASS with 3 passing tests.

```bash
git add src/app/llms.txt/route.ts src/app/llms.txt/route.test.ts
git commit -m "feat(llms): add public llms txt route"
```

---

### Task 5: End-to-end validation and integration checks

**Files:**
- Modify (if needed): `src/collections/LLMsTxt/enforceSingleActive.ts`
- Modify (if needed): `src/utilities/llmsTextSerializer.ts`
- Modify (if needed): `src/app/llms.txt/route.ts`

- [ ] **Step 1: Run complete unit test set for this feature**

Run:

```bash
pnpm test:unit -- src/collections/LLMsTxt/enforceSingleActive.test.ts src/utilities/llmsTextSerializer.test.ts src/app/llms.txt/route.test.ts
```

Expected: PASS with all feature tests green.

- [ ] **Step 2: Run lint on touched files**

Run: `pnpm lint`

Expected: No new lint errors in changed files.

- [ ] **Step 3: Generate Payload types and import map if schema changed**

Run:

```bash
pnpm generate:types
pnpm generate:importmap
```

Expected: Generated files update cleanly and TypeScript references resolve.

- [ ] **Step 4: Manual smoke test for endpoint behavior**

Run app: `pnpm start:dev` (or project-standard dev command)

Manual checks:

1. Publish one active `llms-txt` entry in Payload admin.
2. Open `http://localhost:3000/llms.txt`.
3. Confirm plain text output and `200` response.
4. Create second published active entry; verify first entry auto-deactivates.
5. Temporarily deactivate all entries; verify endpoint returns `200` with empty body.

- [ ] **Step 5: Commit integration updates**

```bash
git add src/collections/LLMsTxt.ts src/collections/LLMsTxt/enforceSingleActive.ts src/collections/LLMsTxt/enforceSingleActive.test.ts src/utilities/llmsTextSerializer.ts src/utilities/llmsTextSerializer.test.ts src/app/llms.txt/route.ts src/app/llms.txt/route.test.ts src/payload.config.ts vitest.config.ts package.json src/payload-types.ts src/app/(payload)/admin/importMap.js
git commit -m "feat(llms): complete llms txt cms publishing flow"
```

---

## Spec Coverage Check

- Collection-based CMS management: covered in Task 2.
- Manual content ownership (not auto-generated): covered by collection + serializer flow in Tasks 2-4.
- Published-only public behavior: covered in Task 4 query and tests.
- Empty-body `200` fallback: covered in Task 4 tests.
- Rich-text to plain-text conventions: covered in Task 3 tests and serializer implementation.
- Single-active enforcement with auto-deactivate: covered in Task 2 hook and tests.
- Multi-active fallback by newest `updatedAt`: covered in Task 2 helper tests and Task 4 usage.
- Testing expectations: covered by Tasks 1, 3, 4, and 5.

## Plan Quality Check

- Placeholder scan: no `TODO`, `TBD`, or deferred implementation markers.
- Internal consistency: function names and file paths are consistent across tasks.
- Scope fit: plan is focused on one subsystem (`llms.txt` CMS publishing) and stays additive.
