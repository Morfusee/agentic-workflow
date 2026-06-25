# Handoff: markdown2share Baseline Alignment

Date: 2026-06-25

## Context

The user wants the `Ordering-System` baseline files attached to this project and used as the source of truth for future implementation and structure.

Attached baseline files already read in this session:

- `C:\Users\mrqvp\Documents\Programming\Ordering-System\AGENTS.md`
- `C:\Users\mrqvp\Documents\Programming\Ordering-System\code-style.md`

Current repo:

- `$HOME/Documents/Programming/markdown2share`

Canonical memory path requested by the user:

- `$HOME/Documents/Programming/agentic-workflow/memory/memory/miscs/handoff/`

## User Requirements

The user explicitly asked to:

- Attach the missing baseline contribution guidance to this repo.
- Create/update `code-style.md` so it becomes part of this repo's source of truth.
- Update the code style guide to make `pnpm lint` run `tsc --noEmit` instead of documenting current ESLint behavior.
- Adapt the baseline guide to this project's intentional structure:
- Root folders instead of `src/*`.
- `@/*` maps to `./*`, not `./src/*`.
- `lib/db` is this project's mapped equivalent of baseline `lib/drizzle`.
- Address all remaining deviations thoroughly.
- If a spec plan is needed, use the `brainstorming` skill.

The user then said `go`, approving the proposed approach.

## Work Completed

`AGENTS.md` was updated in the working tree.

What changed:

- Replaced the short Next.js-only `AGENTS.md` with the baseline-style contribution guide.
- Preserved the existing Next.js agent rules at the bottom.
- Adapted repository context to this project:
- `app`, `components`, `features`, `lib`, `hooks`, `utils` root folders.
- `lib` mentions `auth`, `db`, TanStack Query, shared utils.
- Source-of-truth section now references `code-style.md`, `AGENTS.md`, and bundled Next.js docs.

Current modified file:

- `AGENTS.md`

No other file changes were successfully applied before the handoff request.

## Important Tool Notes

Two `apply_patch` calls were aborted because they were accidentally invoked with no patch body. They did not touch files. A later `apply_patch` with a valid patch successfully updated `AGENTS.md`.

The worktree was clean before the `AGENTS.md` edit. After the edit, expect `git status --short` to show only `AGENTS.md` modified unless something else changed outside this session.

## Findings From Audit

The previous audit found these conventions already followed:

- Next.js 16 App Router.
- TypeScript strict mode.
- Root-level `app`, `features`, `components`, `lib`, `hooks`, `utils` structure.
- Shared UI primitives under `components/ui`.
- Shared blocks under `components/blocks`.
- `@/*` imports mapped to repo root.
- Domain error base exists at `features/errors/app-error.ts`.
- Auth error exists at `features/auth/errors/auth.error.ts`.
- `ok` / `err` helpers exist at `utils/server-action-return.ts`.
- Auth guards exist at `features/auth/auth-guards.ts`.
- TanStack Query option factories and PascalCase query keys exist.
- Zod schemas live under feature schema folders.
- `DataTable` compound component pattern exists.
- `data-slot` attributes exist on UI primitives.

The audit found these remaining gaps:

- No local `code-style.md` yet.
- `package.json` has `"lint": "eslint"`; user wants the style guide to require `tsc --noEmit`, and the earlier approved approach was to update the script to match.
- No repository layer yet. No `repositories/` or `*.repo.ts` files were found.
- `features/markdown/services/markdown.service.ts` and `features/markdown/services/document-draft.service.ts` directly call Drizzle through `getDb()`.
- Services sometimes return result unions instead of throwing domain errors, especially `document-draft.service.ts`.
- Server actions sometimes return user-facing strings instead of typed domain/generic error codes.
- Server actions catch silently in some places, especially `markdown-files.action.ts` and `document-draft.action.ts`.
- No route-local `_components/` folders found.
- No shared `AppPageProps` type found.
- No `.skeleton.tsx` companion files found.
- No Ladle stories found.
- Formatting is inconsistent: some files omit semicolons, including `components/ui/button.tsx`, `components/auth/github-sign-in.tsx`, and `lib/db/index.ts`.
- Import ordering is mixed in places like `app/(public)/login/page.tsx`.
- `features/markdown/miscs` does not match the baseline's preferred feature folder taxonomy.

## Proposed Next Steps

Continue with the previously approved design, but keep the diff surgical.

1. Create `code-style.md` from the baseline and adapt only project-specific mappings:
- Root folders instead of `src/*`.
- `@/*` maps to `./*`.
- `lib/db` instead of `lib/drizzle`.
- `pnpm lint` should run TypeScript checking via `tsc --noEmit`.
- Keep the rest as baseline standards rather than merely documenting current deviations.

2. Update `package.json`:
- Change `"lint": "eslint"` to `"lint": "tsc --noEmit"`.
- Consider leaving `eslint.config.mjs` in place unless the user explicitly wants it removed. Removing it would be broader and was not explicitly requested.

3. Add a markdown repository layer:
- Likely under `features/markdown/repositories/`.
- Extract Drizzle reads/writes from `markdown.service.ts` and `document-draft.service.ts`.
- Keep business/permission decisions in services.

4. Add markdown domain errors:
- Likely `features/markdown/errors/markdown.error.ts` or `document.error.ts`.
- Use enum code keys in `SCREAMING_SNAKE_CASE` and camelCase string values.
- Services should throw domain errors for not found/forbidden cases where appropriate.

5. Refactor actions:
- Keep server action validation at action boundary.
- Catch errors, `console.error(error)`, return `err(code)` or existing action result shape if the UI requires messages.
- Be careful: existing UI consumes `message` from `saveDocumentDraftAction` and `deleteDocumentDraftAction`. Avoid breaking UI contracts unless updating callers too.

6. Add shared page props:
- Likely `types/page.props.ts` with `AppPageProps<TParams, TSearch>`.
- Update narrow page files where already touched or easy, such as `app/(auth)/app/[...collectionPath]/page.tsx` and `app/(auth)/app/md/[documentId]/page.tsx`.

7. Avoid broad route `_components/` moves unless user wants a larger migration:
- Moving route-local components changes many imports and is not necessary for the immediate source-of-truth attachment.
- Mention as remaining follow-up if not addressed.

8. Run verification:
- `pnpm lint`
- If confidence is low or changes touch behavior significantly, consider `pnpm test` per `AGENTS.md`.
- Finish with `git diff` and `git status --short`.

## Suggested Skills

- `writing-plans`: Use before implementation if the next agent wants a formal step-by-step plan after the approved design.
- `backend-dev-guidelines`: Use while extracting Drizzle calls into repositories and keeping service/repository boundaries clean.
- `requirements-reviewer`: Use after implementation to verify the diff against the user's stated baseline-alignment requirements.
- `react-quality-review`: Use only if action result shape changes require UI caller updates.

## Files To Inspect First

- `AGENTS.md`
- `package.json`
- `tsconfig.json`
- `features/markdown/services/markdown.service.ts`
- `features/markdown/services/document-draft.service.ts`
- `features/markdown/actions/markdown-files.action.ts`
- `features/markdown/actions/document-draft.action.ts`
- `features/markdown/types/markdown.type.ts`
- `features/auth/services/authorization.service.ts`
- `lib/db/index.ts`
- `lib/db/schema.ts`

## Safety Notes

- Do not revert the modified `AGENTS.md`; it is intentional user-requested work.
- Preserve the root-based path mapping. Do not introduce `src/`.
- Preserve `@/* -> ./*`.
- Preserve `lib/db` as the Drizzle-backed persistence location.
- Do not remove ESLint config unless explicitly requested.
- No secrets were included in this handoff.
