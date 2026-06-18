# Typography Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a non-destructive typography v2 foundation with a temporary Hero verification opt-in for ClickUp ticket `86d36xz5f`.

**Architecture:** Keep typography v2 in `src/app/(frontend)/styles.css` as scoped Tailwind-compatible CSS layers. Do not remap existing Tailwind `text-*` utilities or globally activate the system. Prove the foundation works by adding removable `.typography-v2` and `.display-copy` classes to Hero only.

**Tech Stack:** Next.js 16, React 19, Payload CMS 3, Tailwind CSS 3, TypeScript, pnpm.

---

## Source Spec

Read before starting:

- `$HOME\Documents\Programming\agentic-workflow\memory\docs\2026-06-03-typography-improvements-design.md`
- ClickUp ticket: `86d36xz5f`

## File Structure

- Modify: `src/app/(frontend)/styles.css`
  - Owns typography v2 CSS tokens, scoped foundation, `.text-block`, and `.display-copy`.
- Modify: `src/blocks/Hero/Hero.component.tsx`
  - Adds the temporary Hero verification opt-in by applying `.typography-v2` and `.display-copy` classes.
- Do not modify: `tailwind.config.js`
  - Existing Tailwind font-size utilities must keep their current behavior.
- Do not modify: `src/blocks/RichText/RichText.renderer.tsx`
  - RichText rollout is deferred; this plan is foundation plus Hero verification only.
- Do not modify: Payload CMS schemas or generated files.

## Worktree Rules

- Base branch: `feat/v3-redesign`
- Feature branch: `feat/86d36xz5f`
- Prefer existing worktrees in this order:
  - `$HOME\Documents\Programming\website-worktree-1`
  - `$HOME\Documents\Programming\website-worktree-2`
- Reuse a dirty worktree only when dirty changes are minimal and do not touch `src/app/(frontend)/styles.css`, `src/blocks/Hero/Hero.component.tsx`, `tailwind.config.js`, Payload schemas, or generated Payload files.
- Preserve dirty changes. Do not reset, stash, delete, or checkout over user-owned work without explicit approval.
- If a candidate worktree has conflicting dirty changes, stop and ask.

## Task 1: Select Worktree And Prepare Branch

**Files:**
- Read-only: git metadata and candidate worktree status

- [ ] **Step 1: Inspect the main website repo worktrees**

Run:

```powershell
git -C "$HOME\Documents\Programming\website" worktree list
```

Expected: command prints the main worktree and any existing linked worktrees. If `website-worktree-1` or `website-worktree-2` is listed, prefer them in that order.

- [ ] **Step 2: Check whether preferred worktree 1 exists**

Run:

```powershell
Test-Path -LiteralPath "$HOME\Documents\Programming\website-worktree-1"
```

Expected: `True` or `False`.

- [ ] **Step 3: Inspect preferred worktree 1 if it exists**

Run only if Step 2 returned `True`:

```powershell
git -C "$HOME\Documents\Programming\website-worktree-1" status --short
git -C "$HOME\Documents\Programming\website-worktree-1" diff
git -C "$HOME\Documents\Programming\website-worktree-1" branch --show-current
```

Expected: use this worktree if dirty changes are empty or minimal and do not conflict with typography files.

- [ ] **Step 4: Check whether preferred worktree 2 exists if worktree 1 is unavailable or conflicting**

Run only if worktree 1 does not exist or is conflicting:

```powershell
Test-Path -LiteralPath "$HOME\Documents\Programming\website-worktree-2"
```

Expected: `True` or `False`.

- [ ] **Step 5: Inspect preferred worktree 2 if it exists**

Run only if Step 4 returned `True`:

```powershell
git -C "$HOME\Documents\Programming\website-worktree-2" status --short
git -C "$HOME\Documents\Programming\website-worktree-2" diff
git -C "$HOME\Documents\Programming\website-worktree-2" branch --show-current
```

Expected: use this worktree if dirty changes are empty or minimal and do not conflict with typography files.

- [ ] **Step 6: Create a new worktree only if neither preferred worktree is safe**

Run only if both preferred worktrees are unavailable or conflicting:

```powershell
git -C "$HOME\Documents\Programming\website" fetch origin feat/v3-redesign
git -C "$HOME\Documents\Programming\website" worktree add -b feat/86d36xz5f "$HOME\Documents\Programming\website-worktree-typography" origin/feat/v3-redesign
```

Expected: a new worktree exists at `$HOME\Documents\Programming\website-worktree-typography` on branch `feat/86d36xz5f`.

- [ ] **Step 7: Prepare the selected existing worktree branch**

Set `$worktree` to the selected path. If worktree 1 was selected, run:

```powershell
$worktree = "$HOME\Documents\Programming\website-worktree-1"
```

If worktree 2 was selected, run:

```powershell
$worktree = "$HOME\Documents\Programming\website-worktree-2"
```

If the newly created fallback worktree was selected, run:

```powershell
$worktree = "$HOME\Documents\Programming\website-worktree-typography"
```

Run these commands only if `$worktree` is not already on `feat/86d36xz5f`:

```powershell
git -C "$worktree" fetch origin feat/v3-redesign
git -C "$worktree" switch feat/86d36xz5f
```

If `git switch feat/86d36xz5f` fails because the branch does not exist locally, run:

```powershell
git -C "$worktree" switch -c feat/86d36xz5f origin/feat/v3-redesign
```

Expected: selected worktree is on `feat/86d36xz5f`. If Git refuses to switch because dirty files would be overwritten, stop and ask for approval instead of stashing or resetting.

- [ ] **Step 8: Confirm branch and baseline status**

Run:

```powershell
git -C "$worktree" branch --show-current
git -C "$worktree" status --short
git -C "$worktree" diff
```

Expected: current branch is `feat/86d36xz5f`. Any dirty changes are known, preserved, and non-conflicting.

## Task 2: Add Scoped Typography Foundation CSS

**Files:**
- Modify: `src/app/(frontend)/styles.css`

- [ ] **Step 1: Read the current stylesheet**

Run:

```powershell
git -C "$worktree" diff -- "src/app/(frontend)/styles.css"
```

Expected: no existing conflicting changes in `styles.css`. If this file is already dirty with unrelated user changes, read it and preserve those changes.

- [ ] **Step 2: Add typography v2 tokens after the existing color tokens**

Modify `src/app/(frontend)/styles.css` so the `:root` block includes these lines after `--color-info: #1d4ed8;`:

```css
  --typography-v2-body-size: clamp(1rem, 0.96rem + 0.2vw, 1.125rem);
  --typography-v2-body-line-height: 1.5;
  --typography-v2-display-size: clamp(1.75rem, 1.2rem + 2.75vw, 4rem);
  --typography-v2-display-line-height: 1.05;
  --typography-v2-text-block-width: 70ch;
  --typography-v2-display-width: 20ch;
```

Expected: root color tokens remain unchanged and the new typography tokens are additive.

- [ ] **Step 3: Add scoped typography layer before `@keyframes marquee`**

Add this block after the existing `@layer base` block and before `@keyframes marquee`:

```css
@layer components {
  .typography-v2 {
    text-align: left;
    overflow-wrap: break-word;
  }

  .typography-v2 :where(p, li) {
    font-size: var(--typography-v2-body-size);
    line-height: var(--typography-v2-body-line-height);
    overflow-wrap: break-word;
    text-align: left;
  }

  .typography-v2 :where(h1, h2, h3, h4, h5, h6) {
    overflow-wrap: break-word;
    text-align: left;
  }

  .typography-v2 :where(.text-block) {
    max-width: var(--typography-v2-text-block-width);
  }

  .text-block {
    max-width: var(--typography-v2-text-block-width);
    font-size: var(--typography-v2-body-size);
    line-height: var(--typography-v2-body-line-height);
    overflow-wrap: break-word;
    text-align: left;
  }

  .display-copy {
    max-width: var(--typography-v2-display-width);
    font-size: var(--typography-v2-display-size);
    line-height: var(--typography-v2-display-line-height);
    overflow-wrap: break-word;
    text-align: left;
  }
}
```

Expected: `.typography-v2`, `.text-block`, and `.display-copy` are available, but nothing is globally activated unless those classes are applied.

- [ ] **Step 4: Confirm Tailwind font-size tokens were not remapped**

Run:

```powershell
git -C "$worktree" diff -- "tailwind.config.js"
```

Expected: no diff.

- [ ] **Step 5: Review stylesheet diff**

Run:

```powershell
git -C "$worktree" diff -- "src/app/(frontend)/styles.css"
```

Expected: diff contains only additive typography tokens and scoped component-layer CSS.

- [ ] **Step 6: Commit the CSS foundation**

Run:

```powershell
git -C "$worktree" add -- "src/app/(frontend)/styles.css"
git -C "$worktree" commit -m "feat: add scoped typography foundation"
```

Expected: commit succeeds and includes only `src/app/(frontend)/styles.css`.

## Task 3: Add Temporary Hero Verification Opt-In

**Files:**
- Modify: `src/blocks/Hero/Hero.component.tsx`

- [ ] **Step 1: Confirm Hero has no conflicting dirty changes**

Run:

```powershell
git -C "$worktree" diff -- "src/blocks/Hero/Hero.component.tsx"
```

Expected: no unrelated changes. If the file is dirty, preserve existing changes and stop if they conflict with the class additions below.

- [ ] **Step 2: Add the temporary typography scope to the Hero wrapper**

In `src/blocks/Hero/Hero.component.tsx`, update the outer wrapper class list from:

```tsx
        'relative text-white overflow-hidden',
```

to:

```tsx
        'relative text-white overflow-hidden typography-v2',
```

Expected: every Hero instance becomes the temporary verification scope, but only Hero is affected.

- [ ] **Step 3: Add display-copy to Hero title**

In `src/blocks/Hero/Hero.component.tsx`, update:

```tsx
          <div className={cn(titleVariant(props))}>{props.title}</div>
```

to:

```tsx
          <div className={cn(titleVariant(props), 'display-copy')}>{props.title}</div>
```

Expected: Hero title uses the new display-copy max-width, fluid size, wrapping, and line-height.

- [ ] **Step 4: Add display-copy to Hero subtitle**

In `src/blocks/Hero/Hero.component.tsx`, update:

```tsx
          <div className={cn(subtitleVariant(props))}>{props.subtitle}</div>
```

to:

```tsx
          <div className={cn(subtitleVariant(props), 'display-copy')}>{props.subtitle}</div>
```

Expected: Hero subtitle also verifies display-copy behavior.

- [ ] **Step 5: Review Hero diff**

Run:

```powershell
git -C "$worktree" diff -- "src/blocks/Hero/Hero.component.tsx"
```

Expected: diff contains only the three class additions. No Hero variants, layout logic, CMS props, image behavior, or children rendering changed.

- [ ] **Step 6: Commit the Hero verification opt-in**

Run:

```powershell
git -C "$worktree" add -- "src/blocks/Hero/Hero.component.tsx"
git -C "$worktree" commit -m "feat: opt hero into typography verification"
```

Expected: commit succeeds and includes only `src/blocks/Hero/Hero.component.tsx`.

## Task 4: Static Verification

**Files:**
- Read-only: package scripts, source diffs, generated build/lint output

- [ ] **Step 1: Verify branch status**

Run:

```powershell
git -C "$worktree" branch --show-current
git -C "$worktree" status --short
```

Expected: branch is `feat/86d36xz5f`. Status is clean or only shows preserved pre-existing dirty changes that were intentionally not touched.

- [ ] **Step 2: Verify only intended files changed across the feature branch**

Run:

```powershell
git -C "$worktree" diff --name-only origin/feat/v3-redesign...HEAD
```

Expected output includes only:

```text
src/app/(frontend)/styles.css
src/blocks/Hero/Hero.component.tsx
```

If other files appear, inspect them and confirm they are pre-existing work or stop before proceeding.

- [ ] **Step 3: Confirm viewport zoom is not disabled**

Run:

```powershell
rg "user-scalable|maximum-scale|minimum-scale|viewport" "$worktree\src\app" -g "*.ts" -g "*.tsx"
```

Expected: no `user-scalable=no`, no restrictive `maximum-scale=1`, and no newly added viewport metadata that disables zoom.

- [ ] **Step 4: Confirm Tailwind font-size config remains unchanged**

Run:

```powershell
git -C "$worktree" diff origin/feat/v3-redesign...HEAD -- "tailwind.config.js"
```

Expected: no output.

- [ ] **Step 5: Run lint**

Run:

```powershell
pnpm lint
```

Workdir: `$worktree`

Expected: lint passes. If dependencies are missing, run `pnpm i` only after confirming this is acceptable for the selected worktree, then rerun `pnpm lint`.

- [ ] **Step 6: Run a production build if feasible**

Run:

```powershell
pnpm build
```

Workdir: `$worktree`

Expected: build passes. If environment secrets are required and unavailable, record the exact failure and proceed to browser/dev verification if possible.

## Task 5: Browser Verification

**Files:**
- Read-only: rendered frontend

- [ ] **Step 1: Start the development server if environment is available**

Run:

```powershell
pnpm start:dev
```

Workdir: `$worktree`

Expected: Next.js dev server starts. If Infisical credentials or environment variables are unavailable, record the exact blocker.

- [ ] **Step 2: Verify Hero at normal zoom**

Open a page that renders the Hero block.

Expected:

- Hero title and subtitle wrap within the display-copy width.
- Text remains left-aligned inside the typography scope.
- Hero image, aspect ratio, buttons, children, and logos still render.
- No unexpected changes outside Hero.

- [ ] **Step 3: Verify Hero at mobile width**

Use browser responsive mode around `390px` width.

Expected:

- Hero title and subtitle remain readable.
- No horizontal scrolling is introduced.
- Long words or long copy wrap instead of overflowing.

- [ ] **Step 4: Verify Hero at 200% zoom**

Set browser zoom to 200% on the same Hero page.

Expected:

- Page remains usable.
- Hero title and subtitle wrap without creating horizontal overflow.
- Browser zoom remains available.

- [ ] **Step 5: Verify non-opted surfaces remain unchanged**

Inspect a non-Hero text-heavy surface that does not have `.typography-v2`, `.text-block`, or `.display-copy`.

Expected: it keeps existing Tailwind typography behavior.

## Task 6: Final Documentation And Handoff Notes

**Files:**
- No repository file changes planned. The notes in this task belong in the final implementation response and PR description.

- [ ] **Step 1: Capture removal note for temporary Hero opt-in**

Include this exact note in the final implementation response and PR description:

```markdown
Temporary Hero verification opt-in removal:
To disable the Hero sample, remove `typography-v2` from the Hero wrapper class and remove `display-copy` from the Hero title/subtitle class names in `src/blocks/Hero/Hero.component.tsx`. Leave the typography foundation in `src/app/(frontend)/styles.css`; without those opt-in classes, the foundation remains available but inactive for Hero.
```

- [ ] **Step 2: Capture future rollout note**

Include this exact note in the final implementation response and PR description:

```markdown
Future rollout:
Move `.typography-v2` upward only after visual QA. Start with individual sections, then page wrappers, then `main`, and only move to `body` after migrated components are confirmed compatible. Add `.text-block` to prose containers and `.display-copy` to display surfaces as separate reversible migration steps.
```

- [ ] **Step 3: Final status and diff review**

Run:

```powershell
git -C "$worktree" status --short
git -C "$worktree" diff origin/feat/v3-redesign...HEAD --stat
git -C "$worktree" diff origin/feat/v3-redesign...HEAD -- "src/app/(frontend)/styles.css" "src/blocks/Hero/Hero.component.tsx"
```

Expected: only intended typography CSS and Hero class additions are present in the feature branch diff.

- [ ] **Step 4: Skip repository documentation commit**

No repository documentation file is planned for Task 6. Keep the removal and future-rollout notes in the final implementation response and PR description only.

Expected: no additional commit is created for Task 6.

## Self-Review

Spec coverage:

- Fluid typography tokens: Task 2.
- Body text floor and line-height: Task 2 `.typography-v2 :where(p, li)` and `.text-block`.
- Prose width and `.text-block`: Task 2.
- Display width and `.display-copy`: Task 2 and Task 3.
- Left alignment and no justification inside scope: Task 2.
- Zoom not disabled: Task 4.
- 200% zoom wrapping: Task 2 and Task 5.
- Non-destructive rollout: Tasks 1, 2, 3, and 4.
- Branch/worktree requirements: Task 1.
- Removal note: Task 6.

Placeholder scan: This plan contains explicit commands, file paths, code snippets, and expected results. The selected worktree is captured in the `$worktree` variable after Task 1 chooses a safe path.

Type consistency: CSS class names are consistent across tasks: `.typography-v2`, `.text-block`, and `.display-copy`.
