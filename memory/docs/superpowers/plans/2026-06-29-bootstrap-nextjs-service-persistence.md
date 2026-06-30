# Bootstrap Next.js Service Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Next.js bootstrap baseline report-first, feature-oriented, explicitly YAGNI, and ORM-aware about repository layers.

**Architecture:** Keep the existing two-phase bootstrap flow and its docs-audit additions. Change the golden code and agent conventions so Drizzle persistence lives in services, Prisma repository boundaries receive contextual review, and reusable feature UI lives with its feature; then make the audit classify existing apps against those rules before any migration.

**Tech Stack:** Markdown skill instructions, Next.js App Router conventions, TypeScript, Drizzle ORM, Prisma ORM, Skill Creator validation

---

## File Map

- Modify `skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md`: own detailed UI, persistence, YAGNI, naming, layout, and evidence conventions.
- Modify `skills/frontend/bootstrap-nextjs-conventions/assets/AGENTS.md`: summarize the architecture and contribution constraints copied into bootstrapped apps.
- Modify `skills/frontend/bootstrap-nextjs-conventions/SKILL.md`: own report-first discovery, classification, migration, and verification behavior.
- Inspect `skills/frontend/bootstrap-nextjs-conventions/agents/openai.yaml`: keep it unchanged unless the revised skill makes its UI text inaccurate.

### Task 1: Replace Repository-First Code Style With ORM-Aware Services

**Files:**
- Modify: `skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md:60-99`
- Modify: `skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md:127-139`
- Modify: `skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md:168-196`
- Modify: `skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md:261-322`
- Modify: `skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md:459-468`
- Modify: `skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md:575-584`
- Modify: `skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md:693-702`
- Modify: `skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md:721-748`

- [ ] **Step 1: Remove repository-specific naming and import examples**

Delete the `Repositories` function/file rows, the `Repository input` and `Repository queries` type rows, and repository import/barrel examples. Replace the service examples with service-owned workflow and database-operation names:

```md
| Services | `verbNoun` for workflows; `verbNounRecord` for local database operations | `createUser`, `getDocumentAccess`, `findDocumentRecordById` |
```

Add `getDocumentAccess` as the public workflow example and `findDocumentRecordById` as the local database-operation example, sourced from `features/markdown/services/markdown.service.ts`.

Keep the existing alias and import-order rules, but make the within-feature example repository-free:

```ts
// features/markdown/services/markdown.service.ts
import { MarkdownError } from "../errors/markdown.error";
import type { MarkdownDraft } from "../types/markdown.types";
```

- [ ] **Step 2: Assign persistence responsibility by ORM**

Replace the layer table's repository and service rows with:

```md
| `services/` | Business workflows, domain rules, domain errors, and direct Drizzle reads/writes |
```

Add this immediately below the table:

```md
For Drizzle-backed features, do not add a `repositories/` folder. Keep database operations in the owning service. A Prisma-backed feature may use repositories when they provide a meaningful domain, testing, or integration boundary; assess that boundary case by case rather than removing it by default. Evaluate other persistence technologies from current evidence.
```

- [ ] **Step 3: Document bottom-of-file database operations**

Expand the service-layer section with this exact convention:

````md
For Drizzle-backed services, keep public workflow functions readable and place local database operations at the bottom of the service file:

```ts
// --- Database operations ------------------------------------------------------
```

Keep `getDocumentAccess` and `saveMarkdownDraft` above the separator. Keep `findDocumentRecordById` and `updateMarkdownDraftRecord` below it.
````

Rewrite the optional executor pattern so it applies to service-local database operations rather than repository functions.

- [ ] **Step 4: Add explicit YAGNI architecture rules**

Add a `YAGNI` subsection beside the folder/layer guidance containing:

```md
### YAGNI

- Do not create repository, use-case, helper, or other architectural layers without a current demonstrated need.
- Keep single-use database operations in the owning service file.
- Extract a helper only when it is reused across files or materially improves readability.
- Do not carry unused persistence functions forward during migrations.
- Do not create folders for anticipated future code.
- Do not introduce `use-cases/` as a replacement for repositories.
```

- [ ] **Step 5: Distinguish route-local UI from feature UI**

Replace the unconditional `_components/` wording with:

```md
Use a route `_components/` folder only for UI that is genuinely specific to that route. Place reusable or feature-owned UI under `features/<feature>/components/`, even when a route is its first consumer.
```

Use `features/markdown/components/library/markdown-library-page.tsx` as the feature-owned UI example. Keep a small `_components/` example only for route-specific page configuration or composition.

- [ ] **Step 6: Replace affected evidence rows**

Remove every repository evidence row and add:

```md
| Service-owned Drizzle operations | [features/markdown/services/markdown.service.ts](features/markdown/services/markdown.service.ts) |
| Collection persistence service | [features/markdown/services/collection.service.ts](features/markdown/services/collection.service.ts) |
| Authorization persistence service | [features/auth/services/authorization.service.ts](features/auth/services/authorization.service.ts) |
| Feature-owned library UI | [features/markdown/components/library/markdown-library-page.tsx](features/markdown/components/library/markdown-library-page.tsx) |
```

- [ ] **Step 7: Verify the golden code style**

Run:

```powershell
rg -n "repositories/|\.repo\.ts|Repository input|Repository queries|Repository with" skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md
```

Expected: no stale Drizzle repository convention or example. A Prisma-specific repository sentence may remain because it is conditional.

Run:

```powershell
rg -n "Database operations|YAGNI|Prisma|feature-owned|anticipated future" skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md
```

Expected: matches for the separator convention, all five YAGNI constraints, ORM-aware guidance, and feature-owned UI.

### Task 2: Align the Golden Agent Guide

**Files:**
- Modify: `skills/frontend/bootstrap-nextjs-conventions/assets/AGENTS.md:42-55`
- Modify: `skills/frontend/bootstrap-nextjs-conventions/assets/AGENTS.md:59-79`

- [ ] **Step 1: Remove repositories from the assumed Drizzle architecture**

Replace the repository context and feature inventory with:

```md
This is a TypeScript-first Next.js App Router application with server actions, route handlers, feature services, Drizzle-backed persistence, and React hooks-based UI architecture.
```

```md
- `src/features`: feature modules with actions, components, schemas, services, queries/hooks, errors, and types
```

- [ ] **Step 2: Add the ORM-aware persistence and UI constraints**

Replace the persistence sentence and augment the behavioral rules with:

```md
For API and persistence changes, keep request/response handling consistent with existing route handlers, server actions, services, and ORM helpers. For Drizzle, keep direct database operations in the owning service. Treat Prisma repository boundaries as case-by-case decisions rather than default deviations.
```

```md
Keep reusable or feature-owned UI under the feature; use route-local `_components/` only for genuinely route-specific UI.
Do not create speculative layers, helpers, folders, or unused persistence functions.
```

Leave the existing `Docs Audit Trail` section byte-for-byte unchanged.

- [ ] **Step 3: Verify the agent guide**

Run:

```powershell
rg -n "services, repositories|components, repositories|services, repositories|Drizzle|Prisma|feature-owned|speculative" skills/frontend/bootstrap-nextjs-conventions/assets/AGENTS.md
```

Expected: no unconditional repository inventory; positive matches for Drizzle, Prisma, feature-owned UI, and YAGNI.

### Task 3: Make the Bootstrap Audit Report the New Baseline

**Files:**
- Modify: `skills/frontend/bootstrap-nextjs-conventions/SKILL.md:45-53`
- Modify: `skills/frontend/bootstrap-nextjs-conventions/SKILL.md:55-60`
- Modify: `skills/frontend/bootstrap-nextjs-conventions/SKILL.md:63-80`
- Inspect: `skills/frontend/bootstrap-nextjs-conventions/agents/openai.yaml`

- [ ] **Step 1: Expand the Phase 1 audit evidence**

Replace the current generic repository inspection wording with:

```md
- Identify the app's ORM or persistence approach before classifying its boundaries.
- Inspect route-local and feature-owned UI, feature folders, components, actions, services, repository or use-case layers, hooks, schemas, errors, stories, and representative persistence operations.
- Audit speculative layers, single-use helpers split into separate files, empty future-facing folders, and unused persistence functions.
```

- [ ] **Step 2: Add report-first ORM classifications**

Add these completion rules to Phase 1 reporting:

```md
- Report a Drizzle `repositories/` layer as `Deviated`; recommend folding used operations into the owning service.
- Report a Prisma repository boundary as `Unclear`; explain its observed value and do not recommend removal by default.
- Report other persistence boundaries as `Unclear` when current evidence does not justify a convention.
- Report reusable or feature-owned UI in a route `_components/` folder and explicit YAGNI violations as `Deviated`.
```

Keep the existing prohibition on implementing fixes during Phase 1.

- [ ] **Step 3: Constrain approved Phase 2 migrations**

Add these surgical migration rules:

```md
- For an approved Drizzle migration, move only currently used database operations into the owning service, place them below the standard database-operations separator, update imports, then remove repository files only after no callers remain.
- Do not introduce `use-cases/`, speculative helper files, future-facing folders, or unused migrated functions.
- Move feature-owned UI into the feature without changing genuinely route-specific components.
```

- [ ] **Step 4: Keep interface metadata stable**

Read `agents/openai.yaml`. Expected: its description and prompt still accurately say the skill copies and audits the golden convention, so do not edit it.

- [ ] **Step 5: Verify report-first behavior**

Run:

```powershell
rg -n "Drizzle|Prisma|Unclear|Deviated|feature-owned|YAGNI|use-cases|Database operations" skills/frontend/bootstrap-nextjs-conventions/SKILL.md
```

Expected: every classification and migration guard appears, while Phase 1 still says not to implement fixes without approval.

### Task 4: Validate the Skill and Preserve Existing Work

**Files:**
- Validate: `skills/frontend/bootstrap-nextjs-conventions/`
- Preserve: `skills/process/`

- [ ] **Step 1: Run Skill Creator validation**

Run:

```powershell
python "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" skills/frontend/bootstrap-nextjs-conventions
```

Expected: validation succeeds. If the current environment cannot run the validator, report the exact runtime limitation without changing unrelated frontmatter.

- [ ] **Step 2: Run focused content checks**

Run:

```powershell
rg -n "repositories/|\.repo\.ts" skills/frontend/bootstrap-nextjs-conventions
rg -n "Drizzle|Prisma|YAGNI|Database operations|feature-owned" skills/frontend/bootstrap-nextjs-conventions
```

Expected: repository paths and `.repo.ts` examples are absent; conditional Prisma repository language may remain; every new convention appears in the appropriate contract files.

- [ ] **Step 3: Review the complete diff**

Run:

```powershell
git diff -- skills/frontend/bootstrap-nextjs-conventions
git status --short
```

Expected: only intentional changes appear in the three bootstrap contract files; `agents/openai.yaml` remains unchanged unless it became inaccurate; the pre-existing docs-audit additions and `skills/process/` work remain present.

- [ ] **Step 4: Commit only the bootstrap convention update if requested**

After reading `CONTRIBUTING.md`, stage only the three intentional bootstrap files:

```powershell
git add -- skills/frontend/bootstrap-nextjs-conventions/SKILL.md skills/frontend/bootstrap-nextjs-conventions/assets/AGENTS.md skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md
git commit -m "feat(skills): revise nextjs persistence conventions"
```

Do not stage or commit `skills/process/` or any unrelated user-owned work.
