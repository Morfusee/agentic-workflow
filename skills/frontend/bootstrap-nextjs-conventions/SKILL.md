---
name: bootstrap-nextjs-conventions
description: Bootstrap and audit Next.js apps against the bundled AGENTS.md and code-style.md convention baseline.
disable-model-invocation: true
---

# Bootstrap Next.js Conventions

Use this skill only for Next.js projects. If the target is not a Next.js app, stop and report that the convention baseline is Next.js-only.

## Golden Files

Treat these bundled assets as the golden standard:

- `assets/AGENTS.md`
- `assets/code-style.md`

Copy them byte-for-byte into each target Next.js app during phase 1. Do not edit the bundled assets or the original source files unless the user explicitly asks to update the golden standard.

Also invoke `$docs-audit-trail` during phase 1 for each selected app. The docs audit trail step is idempotent: it must create missing `docs/`, `docs/brainstorm/`, and `docs/plans/` folders, and it must leave an already-compliant `AGENTS.md` unchanged.

## Phase 1: Provision And Audit

1. Identify target apps:
   - Use user-provided app paths when present.
   - Otherwise discover Next.js apps by checking `package.json` files for `next` in `dependencies` or `devDependencies`, and by checking for `next.config.*`, `app/`, or `src/app/`.
   - In monorepos, treat each discovered Next.js app as a separate target and report the app list before changing files if discovery is ambiguous.
   - Complete when every intended target app is named with its absolute path.

2. Protect existing work:
   - Run `git status` and `git diff` in the target repository before edits.
   - Identify modified files and user-owned changes.
   - Preserve those changes while copying and auditing.
   - Complete when the existing-change summary is known.

3. Copy the golden markdown files:
   - Copy `assets/AGENTS.md` to `<app>/AGENTS.md`.
   - Copy `assets/code-style.md` to `<app>/code-style.md`.
   - If either destination already exists, replace it with the golden file only for the selected app and record that replacement in the report.
   - Complete when both destination files match the bundled assets byte-for-byte for every selected app.

4. Ensure the docs audit trail:
   - Invoke `$docs-audit-trail` for each selected app.
   - Complete when `docs/`, `docs/brainstorm/`, and `docs/plans/` exist and `AGENTS.md` contains the docs audit trail directive exactly once.

5. Audit the app against the convention:
   - Read the copied `AGENTS.md` and `code-style.md`.
   - Identify the app's ORM or persistence approach before classifying its boundaries.
   - Inspect the app structure, package manager, TypeScript config, Next.js router shape, aliases, route-local and feature-owned UI, feature folders, components, actions, services, repository or use-case layers, hooks, schemas, errors, stories, and representative persistence operations.
   - Audit speculative layers, single-use helpers split into separate files, empty future-facing folders, and unused persistence functions.
   - Compare observed code to the golden conventions using the app's existing path mappings where equivalent paths are already clear.
   - Complete when findings cover followed conventions, deviations, unknowns, and recommended changes for each selected app.

6. Report phase 1 results:
   - List copied files and whether they were created or replaced.
   - List docs audit trail directories created or already present.
   - Report `Followed`, `Deviated`, and `Unclear` findings.
   - For each deviation, include the convention, observed evidence, affected paths, risk, and the smallest reasonable change.
   - Report a Drizzle `repositories/` layer as `Deviated`; recommend folding used operations into the owning service.
   - Report a Prisma repository boundary as `Unclear`; explain its observed value and do not recommend removal by default.
   - Report other persistence boundaries as `Unclear` when current evidence does not justify a convention.
   - Report reusable or feature-owned UI in a route `_components/` folder and explicit YAGNI violations as `Deviated`.
   - Do not implement deviation fixes in phase 1 unless the user explicitly asked for automatic fixes.

## Phase 2: Apply User Decisions

Proceed only after the user chooses which findings to execute, drop, or change.

For each approved decision:

1. Decide the target of change:
   - Edit markdown files when the convention itself should change.
   - Edit code, folders, or filenames when the app should conform to the copied convention.
   - Stop and explain conflicts where an approved change would remove or rewrite user-owned work from earlier diffs.

2. Implement surgically:
   - Match existing project style while moving toward the approved convention.
   - Avoid broad refactors, unrelated cleanup, or speculative abstractions.
   - Keep each app's changes scoped to the selected findings.
   - For an approved Drizzle migration, move only currently used database operations into the owning service, place them below `// --- Database operations ------------------------------------------------------`, update imports, then remove repository files only after no callers remain.
   - Do not introduce `use-cases/`, speculative helper files, future-facing folders, or unused migrated functions.
   - Move feature-owned UI into the feature without changing genuinely route-specific components.

3. Verify:
   - Run the app's available checks, preferring `pnpm lint`, `pnpm typecheck`, or the scripts defined in `package.json`.
   - Re-run `git diff`.
   - Confirm the approved changes are present, unapproved deviations remain untouched, and user-owned changes are preserved.

4. Report completion:
   - Summarize intentional changes only.
   - Include validation results and any remaining deviations the user chose to drop or defer.
