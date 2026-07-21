# E2E Aborted Error Capture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist final Playwright attempt diagnostics for E2E runs that abort before their first check.

**Architecture:** Extend the side-effect-free E2E report mapper to collect non-empty report-level and final-attempt messages in a set. Preserve the existing aborted-only note assignment and verify behavior through focused Node tests.

**Tech Stack:** TypeScript, Node test runner, Playwright JSON report mapping

---

### Task 1: Add aborted-run mapper coverage

**Files:**
- Create: `playwright/server/runner/map-e2e-results.test.ts`

- [ ] Add a test report builder and tests for singular `error`, plural `errors`, cross-source deduplication, and completed runs without notes.
- [ ] Run `pnpm exec tsx --test server/runner/map-e2e-results.test.ts` from `playwright/` and verify the aborted-attempt tests fail before implementation.

### Task 2: Collect final-attempt diagnostics

**Files:**
- Modify: `playwright/server/runner/map-e2e-results.ts:138-140`
- Test: `playwright/server/runner/map-e2e-results.test.ts`

- [ ] Replace the report-level message array with a `Set<string>`.
- [ ] During test traversal, collect messages from the final attempt's non-empty `errors` array, falling back to singular `error`.
- [ ] Update aborted note assignment to use set size and join the deduplicated messages.
- [ ] Run `pnpm exec tsx --test server/runner/map-e2e-results.test.ts` and verify all focused tests pass.
- [ ] Run `pnpm test:unit` and `pnpm typecheck` from `playwright/`.
- [ ] Review `git diff` and confirm the pre-existing lockfile modification is preserved and no unrelated files changed.
