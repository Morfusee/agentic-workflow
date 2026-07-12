# Portless App URL Source Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Make the runtime application URL resolve from `PORTLESS_URL` for Portless worktrees, otherwise from `APP_URL`, and remove the obsolete `BETTER_AUTH_URL` fallback without changing the emulate.dev scope.

**Architecture:** Keep `nextjs/lib/app-url.config.ts` as the single runtime URL source. `PORTLESS_URL` takes precedence so a worktree URL overrides any configured production/local `APP_URL`; when Portless is not active, `APP_URL` must be set by the environment. The Playwright GitHub redirect test will inspect the origin it actually loaded instead of importing a static environment-derived URL.

**Tech Stack:** Next.js 16 App Router, Better Auth, Portless, Playwright, pnpm, TypeScript.

---

### Task 1: Update the runtime URL resolver

**Files:**
- Modify: `nextjs/lib/app-url.config.ts`
- Modify: `nextjs/.env.example`

- [ ] **Step 1: Replace the compatibility fallback.**

Change the resolver to use only `PORTLESS_URL` and `APP_URL`, and throw a clear error when neither exists:

```ts
const resolvedAppUrl = process.env.PORTLESS_URL ?? process.env.APP_URL;

if (!resolvedAppUrl) {
  throw new Error("PORTLESS_URL or APP_URL must be configured.");
}

export const APP_URL = resolvedAppUrl;
export const APP_HOSTNAME = new URL(APP_URL).hostname;
```

- [ ] **Step 2: Make the local environment fallback explicit.**

Keep `APP_URL` documented in `nextjs/.env.example` with `http://localhost:3000`. Remove any `BETTER_AUTH_URL` documentation.

- [ ] **Step 3: Run the typecheck.**

Run from `nextjs/`:

```text
pnpm lint
```

Expected: TypeScript passes with no errors.

### Task 2: Remove the Playwright test’s static URL dependency

**Files:**
- Modify: `nextjs/__tests__/e2e/login.spec.ts`

- [ ] **Step 1: Derive the origin from the loaded page.**

Remove the `APP_URL` import and compute the origin after `beforeEach` has navigated to `/login`:

```ts
const appOrigin = new URL(page.url()).origin;
```

Keep the existing redirect predicate so the test passes when the provider is external or when the emulator is mounted on the same origin at a non-login path.

- [ ] **Step 2: Run the focused Playwright test.**

Run from `nextjs/`:

```text
pnpm exec playwright test __tests__/e2e/login.spec.ts -g "GitHub sign-in initiates OAuth redirect"
```

Expected: the test starts through Portless and passes using the current worktree origin.

### Task 3: Align repository instructions and migration documentation

**Files:**
- Modify: `nextjs/README.md`
- Modify: `docs/plans/2026-07-12-portless-app-url-plan.md`

- [ ] **Step 1: Update local setup instructions.**

Document that `APP_URL` is the non-Portless/production override, `PORTLESS_URL` is injected automatically by Portless, and `PORTLESS_URL` wins when both are present. Remove instructions that require setting `APP_URL` solely for the Portless main checkout.

- [ ] **Step 2: Remove obsolete Better Auth URL references.**

Update the existing Portless plan so it no longer describes `BETTER_AUTH_URL` as a compatibility fallback or treats a static `APP_URL` environment value as the only local source.

- [ ] **Step 3: Review the focused diff.**

Run:

```text
git diff -- nextjs/lib/app-url.config.ts nextjs/.env.example nextjs/__tests__/login.spec.ts nextjs/README.md docs/plans/2026-07-12-portless-app-url-plan.md
```

Expected: only the URL precedence, environment instructions, Playwright assertion, and directly related documentation have changed.

### Task 4: Final verification

**Files:**
- Verify: all changed files above

- [ ] **Step 1: Check for obsolete references.**

Run:

```text
rg -n "BETTER_AUTH_URL|DEFAULT_APP_URL" nextjs docs
```

Expected: no active source or documentation references remain.

- [ ] **Step 2: Run the required checks.**

Run from `nextjs/`:

```text
pnpm lint
pnpm test:e2e
```

Expected: typecheck and the existing Playwright suite pass. If the suite requires the local database or Portless trust setup, report that environmental prerequisite rather than changing unrelated code.

- [ ] **Step 3: Confirm the final diff is scoped.**

Run:

```text
git status --short
git diff --stat
git diff
```

Expected: the prior clean worktree remains clean except for the intentional URL migration files, with no emulate.dev dependencies or routes included.
