# Playwright Windows E2E Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Playwright EnrollMate E2E package script run from Windows shells without changing its test selection or TypeScript loader.

**Architecture:** Replace the POSIX inline environment assignment with an explicit Node invocation of Playwright's installed CLI. Node loads `tsx` through its cross-platform `--import` option, so no dependency or lockfile change is required.

**Tech Stack:** Node.js, pnpm, tsx, Playwright

---

## File Structure

- Modify: `playwright/package.json` — defines the E2E package script.
- Preserve: `playwright/pnpm-lock.yaml` — contains pre-existing user work and requires no change.

### Task 1: Replace and verify the E2E command

**Files:**
- Modify: `playwright/package.json:9`

- [ ] **Step 1: Reproduce the Windows shell failure**

Run from `playwright/` in PowerShell:

```powershell
pnpm test:e2e -- --list
```

Expected before the fix: PowerShell attempts to execute `NODE_OPTIONS='--import` as a command and exits before Playwright lists tests.

- [ ] **Step 2: Replace the script with the platform-neutral Node invocation**

Set the `test:e2e` entry in `playwright/package.json` to:

```json
"test:e2e": "node --import tsx ./node_modules/@playwright/test/cli.js test tests/e2e --project=enrollmate"
```

Do not change dependencies or `playwright/pnpm-lock.yaml`.

- [ ] **Step 3: Verify the package script reaches Playwright on Windows**

Run from `playwright/` in PowerShell:

```powershell
pnpm test:e2e -- --list
```

Expected after the fix: exit code `0`; Playwright prints the EnrollMate E2E test list and no command-not-found error for `NODE_OPTIONS`.

- [ ] **Step 4: Verify TypeScript configuration remains valid**

Run from `playwright/`:

```powershell
pnpm typecheck
```

Expected: exit code `0` with no TypeScript errors.

- [ ] **Step 5: Review the scoped diff**

Run from the repository root:

```powershell
git diff -- playwright/package.json
git status --short
```

Expected: the package file has one changed script line; the existing `playwright/pnpm-lock.yaml` modification remains present but unchanged by this task.
