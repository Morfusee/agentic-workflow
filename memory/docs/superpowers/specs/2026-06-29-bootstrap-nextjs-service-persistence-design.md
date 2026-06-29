# Bootstrap Next.js Service Persistence Design

## Context

Update `bootstrap-nextjs-conventions` so new and previously bootstrapped Next.js apps are assessed against a feature-oriented UI convention, an ORM-aware persistence boundary, and explicit YAGNI constraints. Preserve the current uncommitted docs-audit changes in `SKILL.md`, `assets/AGENTS.md`, and `skills/process/`.

## Scope

Update only the bootstrap skill's existing contract files:

- `skills/frontend/bootstrap-nextjs-conventions/SKILL.md`
- `skills/frontend/bootstrap-nextjs-conventions/assets/AGENTS.md`
- `skills/frontend/bootstrap-nextjs-conventions/assets/code-style.md`
- `skills/frontend/bootstrap-nextjs-conventions/agents/openai.yaml` only if its interface text becomes inaccurate

Do not add migration scripts, use-case layers, helper modules, or new skill resources.

## Baseline Conventions

### Feature UI

Keep route-local components beside a route only when they are genuinely specific to that route. Place reusable or feature-owned UI under `features/<feature>/components/` rather than `app/**/_components/`.

### Persistence Boundaries

Apply the repository decision according to the persistence technology:

- For Drizzle, prefer service-owned persistence. Services may contain business workflows and direct Drizzle reads and writes. Treat a separate `repositories/` layer used only to wrap Drizzle operations as a deviation.
- For Prisma, do not recommend repository removal by default. Report the repository boundary as `Unclear` and evaluate whether it provides a meaningful domain, testing, or integration boundary.
- For other persistence approaches, assess the boundary case by case and report insufficient evidence as `Unclear`.

When services own database operations, keep the public workflow functions readable and place local database operations at the bottom of the service file after:

```ts
// --- Database operations ------------------------------------------------------
```

Do not introduce a `use-cases/` layer as a replacement for repositories.

### YAGNI

Make YAGNI an explicit architectural convention:

- Do not create repository, use-case, helper, or other layers without a current demonstrated need.
- Keep single-use database operations in the owning service file.
- Extract helpers only when they are reused across files or materially improve readability.
- Do not carry unused persistence functions forward during migrations.
- Do not create folders for anticipated future code.

## Bootstrap Behavior

Retain the existing two-phase safety model.

During Phase 1, copy the golden files, ensure the docs audit trail, and report findings without changing application code. Audit for:

- feature-owned UI incorrectly living in route-local component folders;
- Drizzle repository folders and imports that merely wrap database operations;
- Prisma repository boundaries that require contextual review;
- speculative repository, use-case, helper, or empty folders;
- unused persistence functions proposed for migration.

Classify Drizzle wrapper repositories as `Deviated`. Classify Prisma repository decisions and persistence boundaries without enough evidence as `Unclear`.

During Phase 2, modify application code only for findings the user explicitly approves. Preserve all pre-existing user-owned work and make the smallest migration necessary.

## Golden Asset Changes

Update `assets/code-style.md` to:

- remove Drizzle repository folder, file naming, import, type naming, layer responsibility, and evidence examples;
- assign direct Drizzle operations to services;
- document bottom-of-file database operations;
- add the explicit YAGNI rules;
- distinguish feature-owned UI from genuinely route-local UI;
- replace stale evidence with paths that demonstrate the revised conventions.

Update `assets/AGENTS.md` to remove repositories from the assumed Drizzle architecture and feature-module inventory. State the ORM-aware persistence rule without forbidding justified Prisma repositories.

Update `SKILL.md` so its audit procedure applies the same ORM-aware classifications and YAGNI checks. Keep the current docs-audit integration intact.

Update `agents/openai.yaml` only if the existing summary or default prompt no longer accurately represents the skill.

## Validation

Complete the update when:

1. Searches show no unconditional repository-layer guidance or stale Drizzle repository examples in the bootstrap skill.
2. Drizzle, Prisma, and other persistence cases have explicit report-first classifications.
3. The service database-operation separator and every YAGNI rule appear in the golden code style.
4. Feature-owned and route-local UI responsibilities are distinct.
5. Skill frontmatter, naming, and `agents/openai.yaml` pass Skill Creator validation.
6. The final diff contains the requested convention changes and preserves the existing docs-audit work without unrelated edits.
