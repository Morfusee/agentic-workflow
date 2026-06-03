# Partners Section Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update `/partners` so each partner category renders as its own full-width page section with `Why NGnair`-style spacing and background rhythm.

**Architecture:** Keep the existing `/partners` route composition intact: hero, `PartnerDirectory`, CTA banner. Make a focused in-place update to `PartnerDirectory` so it maps partner categories directly into full-width sections, removes the redundant overview heading, preserves logo data and dark-mode behavior, and alternates the Sponsor Banks background with `bg-muted/30`.

**Tech Stack:** Next.js 16 App Router, React 19, TypeScript, Tailwind CSS, `next/image`, existing NGnair shared components.

---

## Existing Context

The website repository has user-owned changes that must be preserved:

- Added `docs/network-partners-missing-logos.md`.
- Added `docs/superpowers/plans/2026-06-02-network-partners-page.md`.
- Added `docs/superpowers/specs/2026-06-02-network-partners-page-design.md`.
- Modified `package.json` with a `packageManager` field.
- Untracked `gh`.
- Untracked `repomix-output.xml`.

Do not revert, delete, stage, or modify those files unless the user explicitly asks.

## File Structure

**Modify:**

- `src/components/partners/partner-directory.tsx` - render partner categories as page-level sections and preserve the existing logo grid behavior.

**Read-only verification context:**

- `src/app/(main)/partners/page.tsx` - confirm route order stays hero, `PartnerDirectory`, CTA banner.
- `src/data/network-partners.ts` - confirm category data remains unchanged.
- `src/components/why-ngnair/how-failover-works.tsx` - reference `bg-muted/30` section rhythm.

No files should be created in the website repository for this implementation.

---

### Task 1: Preserve Current Worktree State

**Files:**

- Read: repository status and diff only.

- [ ] **Step 1: Check current status**

Run from `C:\Users\mrqvp\Documents\Programming\website-ngnair`:

```powershell
git status --short
```

Expected: any pre-existing user-owned changes remain visible. Do not clean, reset, or remove them.

- [ ] **Step 2: Check current diff**

Run from `C:\Users\mrqvp\Documents\Programming\website-ngnair`:

```powershell
git diff
```

Expected: the known `package.json` `packageManager` diff may appear. Preserve it.

---

### Task 2: Convert Partner Directory Into Page-Level Sections

**Files:**

- Modify: `src/components/partners/partner-directory.tsx`

- [ ] **Step 1: Replace the component body with category-level sections**

Update `src/components/partners/partner-directory.tsx` to exactly this implementation:

```tsx
import Image from "next/image";
import { networkPartnerCategories } from "@/data/network-partners";

export default function PartnerDirectory() {
  return (
    <>
      {networkPartnerCategories.map((category, index) => {
        const categoryId = category.title
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/(^-|-$)/g, "");
        const sectionBackground = index === 1 ? "bg-muted/30" : "";

        return (
          <section
            key={category.title}
            aria-labelledby={categoryId}
            className={["w-full py-20 md:py-32", sectionBackground].join(" ")}
          >
            <div className="container mx-auto px-4 md:px-6">
              <div className="mx-auto max-w-3xl text-center">
                <h2
                  id={categoryId}
                  className="text-3xl font-bold tracking-tight md:text-4xl"
                >
                  {category.title}
                </h2>
                <p className="mt-4 text-lg text-muted-foreground">
                  {category.description}
                </p>
              </div>

              {category.partners.length > 0 ? (
                <div className="mt-12 grid grid-cols-2 gap-x-8 gap-y-10 md:grid-cols-4 lg:grid-cols-5 lg:gap-x-12">
                  {category.partners.map((partner) => (
                    <div
                      key={partner.name}
                      className="flex min-h-28 items-center justify-center px-2 py-4 md:min-h-32"
                    >
                      <div className="flex h-24 w-full items-center justify-center rounded-2xl px-5 py-4 backdrop-blur-sm transition-colors md:h-28">
                        <Image
                          src={partner.logo}
                          alt={`${partner.name} logo`}
                          width={220}
                          height={110}
                          className={[
                            "max-h-16 w-auto max-w-full object-contain drop-shadow-[0_1px_2px_rgba(0,0,0,0.45)] md:max-h-20",
                            partner.whiteOnDark
                              ? "dark:brightness-0 dark:invert"
                              : "",
                          ].join(" ")}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          </section>
        );
      })}
    </>
  );
}
```

This removes the outer `Our Partner Network` wrapper, promotes each category to a full-width section, uses `bg-muted/30` only for the second category, and keeps the existing logo rendering behavior.

- [ ] **Step 2: Inspect the focused diff**

Run:

```powershell
git diff -- "src/components/partners/partner-directory.tsx"
```

Expected:

- The old outer `<section className="w-full bg-section py-20 md:py-28">` is removed.
- The `Our Partner Network` heading and paragraph are removed.
- Each category renders as a full-width `<section>` with `py-20 md:py-32`.
- The second category receives `bg-muted/30` through `sectionBackground`.
- Logo `Image` props, alt text, grid breakpoints, and `whiteOnDark` dark-mode class remain present.

---

### Task 3: Verify Code Quality

**Files:**

- Verify: full project.

- [ ] **Step 1: Run lint**

Run from `C:\Users\mrqvp\Documents\Programming\website-ngnair`:

```powershell
pnpm lint
```

Expected: command completes successfully with no new lint errors from `src/components/partners/partner-directory.tsx`.

- [ ] **Step 2: Run production build**

Run from `C:\Users\mrqvp\Documents\Programming\website-ngnair`:

```powershell
pnpm build
```

Expected: Next.js build completes successfully and `/partners` remains part of the static/app route output.

---

### Task 4: Browser Verification

**Files:**

- Verify: `/partners` rendered page.

- [ ] **Step 1: Start the development server if one is not already running**

Run from `C:\Users\mrqvp\Documents\Programming\website-ngnair`:

```powershell
pnpm dev
```

Expected: dev server starts on port `9999` based on the project script.

- [ ] **Step 2: Check the page flow**

Open:

```text
http://localhost:9999/partners
```

Expected:

- The page renders the existing hero first.
- The next visible body section is `Banking Partners`.
- The standalone `Our Partner Network` heading is not present.
- `Sponsor Banks` has a muted background.
- `Technology & Platform Partners` returns to the default background.
- The bottom CTA banner still renders after the partner sections.

- [ ] **Step 3: Check responsive logo grids**

Use browser responsive widths:

```text
390px mobile
768px tablet
1280px desktop
```

Expected:

- Mobile shows 2 logo columns.
- Tablet shows 4 logo columns.
- Desktop shows 5 logo columns where space permits.
- Logos remain centered, legible, and not clickable.
- Dark mode does not make `whiteOnDark` logos illegible.

---

### Task 5: Final Diff Review And Optional Commit

**Files:**

- Review: full repository diff.
- Optional commit: `src/components/partners/partner-directory.tsx` only.

- [ ] **Step 1: Review final status**

Run:

```powershell
git status --short
```

Expected: `src/components/partners/partner-directory.tsx` is modified. Pre-existing user-owned changes remain visible and unchanged.

- [ ] **Step 2: Review final diff**

Run:

```powershell
git diff
```

Expected: the intentional diff includes only the focused partner directory update plus any pre-existing user-owned changes that were already present before implementation.

- [ ] **Step 3: Commit only the intentional component change if the user asks for a commit**

Run only if the user explicitly asks to commit:

```powershell
git add "src/components/partners/partner-directory.tsx"
git commit -m "refactor: section partners page categories"
```

Expected: commit includes only `src/components/partners/partner-directory.tsx`. Do not stage `package.json`, `docs/*`, `gh`, or `repomix-output.xml` unless the user explicitly asks.

---

## Self-Review Notes

Spec coverage:

- Category-as-section rendering is covered in Task 2.
- Removal of `Our Partner Network` is covered in Task 2 and Task 4.
- Background rhythm with `bg-muted/30` for Sponsor Banks is covered in Task 2 and Task 4.
- Route composition preservation is covered by the file structure and Task 4.
- Data and logo behavior preservation is covered in Task 2 and Task 3.
- Lint, build, and responsive browser checks are covered in Tasks 3 and 4.
- User-owned work preservation is covered in Tasks 1 and 5.

Red-flag scan: no incomplete work remains. Every code-changing step includes the exact replacement code.

Type consistency: the plan uses existing `networkPartnerCategories`, `category.title`, `category.description`, `category.partners`, `partner.name`, `partner.logo`, and `partner.whiteOnDark` names from the current data module.
