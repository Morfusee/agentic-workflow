# Handoff: Fix Playwright e2e failures — Share-dialog fallback race

- **Date:** 2026-08-01
- **Subject:** GitHub PR #3 `refactor(trpc): migrate backend to native tRPC` (https://github.com/Morfusee/markdown2share/pull/3) — branch `refactor/native-trpc-backend-rewrite`
- **Next-session focus:** Fix the 25 failing Playwright e2e tests (Share-dialog instability), then verify the suite goes green and report back.

## Handoff instructions (for the fresh agent)

Follow the `handoff` skill workflow: read this document, gather the referenced artifacts, then continue the work. Do not re-review what has already been reviewed or re-read what is referenced by path. Keep the next session focused on the objective below. When you reach a decision point, surface it to the user instead of guessing.

---

## 1. Where things stand

The branch lives in a git worktree: `$HOME/.codex/worktrees/465c/markdown2share` (branch `refactor/native-trpc-backend-rewrite`, base `main`, PR #3 is DRAFT).

Prior session completed an intensive multi-reviewer audit of PR #3 (requirements, security/correctness, code quality, React quality) and applied follow-up fixes on the branch. All fixes are committed and verified:

| Commit | What |
|---|---|
| `cf3232b` | chore(ci): remove quality workflow (also swept in the staged playwright.config.ts + relocated init test — cosmetic misattribution only, content correct) |
| `3747413` | fix(trpc): repoint test mocks at lib/trpc paths |
| `4fdc164` | refactor(trpc): centralize permission error factories |
| `7a4ec79` | refactor(documents): share next-revision insertion across save and publish |
| `5ee8290` | refactor(trpc): remove dead exports and schema aliases |
| `90c686d` | docs(trpc): point references at lib/trpc after relocation |

Full review record (checks, evidence, resolution notes): `$HOME/Documents/Programming/agentic-workflow/memory/reviews/2026-08-01-pr3-native-trpc-backend-review.md`

Verification state on the branch (all PASS): `pnpm typecheck`, `pnpm lint` (0 errors, 24 pre-existing warnings in untouched files), `pnpm test` (33 files / 200 tests), `pnpm build`. The nextCookies removal was validated with a manual browser e2e pass (signup/login/session-persistence/signout/anonymous-gate all work via native Better Auth routes).

## 2. The bug to fix

**Playwright e2e: 25 failed / 35 passed.** Every failure is a Share-dialog locator timeout:

- `getByRole('dialog', { name: /Share/ }).getByText('Owner', { exact: true })` never visible, or
- Clicking the dialog's `Copy link` button loops on "element was detached from the DOM, retrying" until timeout.

The suite had **no green baseline before today**: CI was blocked at `db:test:setup` (missing `DATABASE_RESET_CONFIRM` env var — see guard `nextjs/lib/db/database-reset-safety.ts`), and locally the Portless worktree-prefix 404 blocked everything (`playwright.config.ts` now derives the prefix — commit `cf3232b`). So these 25 failures are newly surfaced, not regressions from the review fixes (a representative failing test passes in isolation both at PR head and with all follow-up changes applied).

### Diagnosis (evidence-backed, medium-high confidence)

Chain of causation:

1. `createMarkdownDocument` (nextjs/__tests__/e2e/markdown-documents.spec.ts:989) saves a new doc from `/app/md/new`, then races `waitForURL(/app/md/<id>/)` (30s) against the "Saved" toast. The URL only changes when the editor's save handler runs `router.replace("/app/md/<id>")` (nextjs/features/documents/components/editor/markdown-rich-editor.tsx:389).
2. Under suite conditions (parallel workers hitting one Next dev server), the save → `router.replace` → RSC re-render cycle is slow enough that the URL race is **lost**, so the helper falls back to `openSavedDocumentFromShareLink` (spec line 1239) — which opens the Share dialog **on the `/app/md/new` page, where `documentId === undefined`**.
3. With no `documentId`, `hasDocument` is false → members/publish queries are disabled (`enabled: hasDocument`, document-share-dialog.tsx:89-97) → `displayMembers` stays `[]` → the `Owner` chip the test waits for **cannot render** until the canonical-route replace lands.
4. The in-flight RSC refresh replaces the client tree → the open dialog unmounts/remounts → Playwright's detach retry loop → timeout. The timeout snapshot shows the editor page with the dialog already gone.
5. Alone, the race is won: fast dev server → `router.replace` lands in time → no fallback → test passes.

### Proposed fix (start here)

Primary: make `createMarkdownDocument` stop depending on the Share dialog:

- After clicking Save, wait for the "Saved" toast, then `waitForURL` with a longer timeout (e.g. 60s).
- If the URL still never flips, replace the fallback with a deterministic path: navigate via the library (`/app` → search/click the new document) instead of the Share-dialog copy-link flow. The document id is queryable from the library table row link.
- Remove `openSavedDocumentFromShareLink` (or keep it only for genuinely share-flow tests, which have a real `documentId`).

Optional deeper fix (product, bigger scope — only if the suite stays flaky after the spec fix): the editor's post-save `router.replace`/`router.refresh()` replacing the tree while the Share dialog is open is the underlying remount driver; consider not refreshing while the dialog is mounted, or keying the dialog's member list so it survives refreshes.

### Environment notes (needed to run the suite)

- Infra: `just docker up` (PgDog on 6432). Postgres superuser in container: `ThisIsMorfusee` (role list via `docker exec docker-app-postgres-1 psql -U markdown2share -d markdown2share -c "SELECT rolname FROM pg_roles"`).
- The repo `.env` is gitignored; a working copy lives in the MAIN checkout (`$HOME/Documents/Programming/markdown2share/nextjs/.env`). The worktree `.env` currently points `DATABASE_URL` at the default dev DB and `DATABASE_URL_TEST` at `markdown2share-test` (both routed through PgDog).
- Reset guard contract: destructive DB ops require `DATABASE_RESET_CONFIRM` to exactly equal the decoded database name. For the e2e/test DB: `$env:DATABASE_RESET_CONFIRM='markdown2share-test'`. The guard also blocks `markdown2share` (reserved name) — a documented limitation, not in scope.
- Playwright runs its own Portless instance per run; ensure no other Portless proxy is running first (they shadow each other: check for `portless`/`next dev` processes and kill leftovers).
- Run commands from `nextjs/`: `pnpm db:test:setup`, then `pnpm test:e2e`. Locally, `PLAYWRIGHT_WORKERS=4` produced the same 25/35 split as full parallelism — the failures are deterministic in-suite, not worker-count flakiness.

### Acceptance criteria

- `pnpm test:e2e` (with `DATABASE_RESET_CONFIRM=markdown2share-test`, no other Portless instance running) passes all specs, or the residual failures are a documented, distinct root cause.
- `pnpm test` (unit + integration) stays green; no production code changes unless the optional deeper fix is approved.
- Commit with a conventional message (`fix(e2e): ...` / `test(e2e): ...`) using the git-commit skill.

## 3. Suggested skills

- `agent-browser` — reproduce the Share-dialog detach live and inspect the DOM/re-render behavior while debugging the fix.
- `writing-plans` — only if the fix grows beyond the spec-level change (e.g., the optional product-level dialog fix).
- `git-commit` — commit the fix per repo convention (Conventional Commits, scoped messages).
- `executing-plans` — if a written plan is produced, execute it with review checkpoints.
- `review-orchestrator` (with `requirements-reviewer` + `thermos`) — post-fix verification pass on the new diff before handing back.
- `handoff` — when done, write the next handoff to the same directory.

## 4. Reference artifacts (do not re-read content already captured there)

- PR #3: https://github.com/Morfusee/markdown2share/pull/3 (DRAFT; body contains the author's original validation claims)
- Review record: `$HOME/Documents/Programming/agentic-workflow/memory/reviews/2026-08-01-pr3-native-trpc-backend-review.md`
- Operation inventory: `docs/plans/2026-07-31-native-trpc-operation-inventory.md` (in-repo)
- Code style contract: `nextjs/code-style.md` (rewritten in this PR)
- e2e spec under investigation: `nextjs/__tests__/e2e/markdown-documents.spec.ts` (`createMarkdownDocument` ~line 989, `openSavedDocumentFromShareLink` ~line 1239)

## 5. Sensitive data

None in this document. Do not paste values from `nextjs/.env` (contains database credentials and `BETTER_AUTH_SECRET`); reference it by path only. The `.env` files are gitignored and must not be committed.
