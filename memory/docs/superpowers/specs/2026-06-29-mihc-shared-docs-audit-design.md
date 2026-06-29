# MIHC Shared Docs Audit Design

## Context

The `mihc` monorepo already has a shared root `docs/` directory and project-specific instructions under `nextjs/`. Durable brainstorms and plans should remain shared at the monorepo root rather than being duplicated inside `nextjs/docs/`.

The current `nextjs/AGENTS.md` and `nextjs/code-style.md` were intentionally added for this repository. Preserve both as user-owned project guidance. In particular, retain the Next.js 16 warning and leave `nextjs/code-style.md` unchanged.

## Scope

Change only the documentation audit trail:

- create `$HOME/Documents/Programming/mihc/docs/brainstorm/`;
- create `$HOME/Documents/Programming/mihc/docs/plans/`;
- update `$HOME/Documents/Programming/mihc/nextjs/AGENTS.md` with one docs audit directive that points to the shared root `../docs/` directory.

Do not create `nextjs/docs/`. Do not edit `nextjs/code-style.md` or application code. Do not address the previously reported convention deviations as part of this change.

## AGENTS.md Behavior

Preserve all existing content, including the generated Next.js 16 warning. Add the audit directive once and make the relative paths unambiguous from `nextjs/AGENTS.md`:

- shared project references and durable notes live under `../docs/`;
- brainstorms live under `../docs/brainstorm/`;
- plans live under `../docs/plans/`;
- agents check relevant shared docs before planning or implementation;
- concrete agreements should be offered for capture in the appropriate shared docs subdirectory;
- this repository-local rule overrides global or parent instructions that would place these artifacts outside the repository.

## Directory Handling

Create the two requested directories without placeholder files. Git does not track empty directories, so the only tracked repository change will initially be `nextjs/AGENTS.md`. The directories remain available locally for the first brainstorm or plan artifact.

## Validation

The change is complete when:

1. `docs/brainstorm/` and `docs/plans/` exist at the monorepo root.
2. No `nextjs/docs/` directory is created.
3. `nextjs/AGENTS.md` contains exactly one shared docs audit directive and still contains its existing Next.js 16 warning and contribution rules.
4. `nextjs/code-style.md` and all application files are unchanged.
5. The final diff contains only the intentional `nextjs/AGENTS.md` edit; all prior user-owned work remains present.
