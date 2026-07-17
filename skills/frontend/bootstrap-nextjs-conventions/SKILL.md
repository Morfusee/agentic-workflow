---
name: bootstrap-nextjs-conventions
description: Bootstrap and audit Next.js applications against the MIHC-derived AGENTS.md and code-style.md baseline. Use when initializing or reviewing a Next.js app's structure, conventions, or workflow boundaries.
---

# Bootstrap Next.js Conventions

Use this skill only for Next.js applications. If the target is not a Next.js app, stop and report that the convention baseline is Next.js-only.

The baseline reflects the MIHC `nextjs/` app: Next.js 16 App Router, root-level or `src/`-scoped layouts, the `@/*` alias, Drizzle with PostgreSQL, TanStack Form with Zod, TanStack Query and Table, better-auth, Ladle, and ESLint.

Before changing a target app, read the relevant installed Next.js guide under `node_modules/next/dist/docs/` and heed its deprecation notices. Treat the target's installed Next.js version and existing layout as authoritative where the baseline permits variants.

## Golden Files

Treat these bundled assets as the golden standard:

- `assets/AGENTS.md`
- `assets/code-style.md`

They are synchronized from the MIHC repository's checked-out `nextjs/` app. Copy them byte-for-byte into each selected target app during phase 1. Do not edit the bundled assets or the original source files unless the user explicitly asks to refresh the golden standard.

Also invoke `$docs-audit-trail` during phase 1 for each selected app. Preserve the relative docs paths expressed by the copied `AGENTS.md`; the docs audit trail step is idempotent.

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
   - If either destination already exists, replace it only for the selected app and record that replacement in the report.
   - Complete when both destination files match the bundled assets byte-for-byte for every selected app.

4. Ensure the docs audit trail:
   - Read the relevant project docs, starting with the path named by `AGENTS.md` such as `../docs/README.md` when present.
   - Invoke `$docs-audit-trail` for each selected app.
   - Complete when the required docs directories exist and the copied `AGENTS.md` contains the docs audit trail directive exactly once.

5. Audit each app against the convention:
   - Read the copied `AGENTS.md` and `code-style.md` before classifying findings.
   - Inspect the package manager and scripts, installed Next.js version, `next.config.*`, ESLint and TypeScript configuration, router shape, aliases, root-level or `src/` layout, route-local `_components/`, shared UI, feature modules, actions, services, repositories, queries, schemas, types, errors, hooks, stories, tests, and representative persistence operations.
   - Compare observed code to the golden conventions using the app's existing path mappings and nearby implementation patterns.
   - Treat a `repositories/` layer as supported when it contains raw Drizzle calls, accepts an optional transaction/executor where needed, and leaves business rules to services. Report it as a deviation only when it contains business logic or is speculative.
   - Treat route-specific UI in `_components/` as followed. Report reusable or feature-owned UI placed there as a deviation.
   - Audit speculative layers, single-use helpers split into separate files, empty future-facing folders, and unused persistence functions when the evidence shows they conflict with the copied conventions.
   - Complete when findings cover every target's followed conventions, deviations, unknowns, evidence, and smallest reasonable recommendations.

6. Report phase 1 results:
   - List copied files and whether they were created or replaced.
   - List docs audit trail directories created or already present.
   - Report `Followed`, `Deviated`, and `Unclear` findings.
   - For each deviation, include the convention, observed evidence, affected paths, risk, and the smallest reasonable change.
   - Do not classify a Drizzle repository boundary as deviated solely because the boundary exists.
   - Classify Prisma or other persistence boundaries from current evidence; use `Unclear` when the evidence does not justify a convention.
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
   - Keep raw Drizzle calls in repositories and business workflows in services; pass the transaction/executor through when the surrounding operation requires it.
   - Avoid broad refactors, unrelated cleanup, speculative abstractions, `use-cases/`, future-facing folders, and unused migrated functions.
   - Keep feature-owned UI in the feature and genuinely route-specific UI in route-local `_components/` folders.

3. Verify:
   - Run the target app's available checks from `package.json`, preferring the configured package manager's lint, typecheck, and test scripts.
   - Re-run `git diff`.
   - Confirm the approved changes are present, unapproved deviations remain untouched, and user-owned changes are preserved.

4. Report completion:
   - Summarize intentional changes only.
   - Include validation results and any remaining deviations the user chose to drop or defer.
