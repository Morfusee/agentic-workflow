# Color Tokens Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the new MMDC redesign color token layer while preserving existing CMS-facing color aliases and production page behavior.

**Architecture:** Add brand, accent, neutral, and semantic tokens to Tailwind for developer use, and add matching CSS variables for non-Tailwind and shadcn-style semantic usage. Keep `src/utilities/index.ts` unchanged so `ColorField` and existing CMS dropdowns continue exposing only the current compatibility aliases.

**Tech Stack:** Payload 3, Next 16, React 19, Tailwind CSS 3, class-variance-authority, shadcn-style Radix UI components.

---

## Source Spec

Design spec: `docs/superpowers/specs/2026-06-02-color-tokens-design.md`

ClickUp ticket: `86d36yejy` - Color Tokens

## File Structure

- Modify: `tailwind.config.js`
  - Responsibility: define Tailwind color tokens and safelist generated CMS classes.
  - Additive changes only. Preserve `primary`, `secondary`, `black`, `white`, `muted`, and `background` values.
- Modify: `src/app/(frontend)/styles.css`
  - Responsibility: define CSS variables for additive tokens and shadcn-style semantic variables.
  - Add `:root` variables near the top of the file after Tailwind directives.
- Modify: `src/utilities/SyncToProd.tsx`
  - Responsibility: admin dashboard sync banner.
  - Replace admin-only hardcoded link blue with `var(--color-info)`.
- Modify: `src/utilities/SyncFormSubmissions.tsx`
  - Responsibility: admin dashboard form submission sync banner.
  - Replace admin-only hardcoded link blue with `var(--color-info)`.
- Modify: `src/components/Image/ImagePageUsageTable.component.tsx`
  - Responsibility: Payload admin image usage table.
  - Replace admin-only published status green values with success CSS variables.
- Modify: `src/blocks/FinancialCalculator/FinancialCalculator.component.tsx`
  - Responsibility: public financial calculator block.
  - Replace border `#E0E0E0` with `border-line` because the approved spec marks this as visually close and semantic.
- Do not modify: `src/utilities/index.ts`
  - Responsibility: CMS-facing color names and color values.
  - Existing aliases must remain unchanged to keep CMS dropdowns stable.
- Do not modify for this ticket: `src/blocks/File/PDFIndicators.tsx`, `src/blocks/Carousel/Carousel.component.tsx`, `src/blocks/TuitionCalculator/TuitionCalculator.component.tsx`, `src/components/FloatingButton/floatingButton.component.tsx`
  - These hardcoded colors were explicitly deferred because token replacements would be visible production changes or have no close approved equivalent.

## Pre-Flight

- [ ] **Step 1: Confirm worktree state and preserve unrelated changes**

Run:

```bash
git status --short
git diff
```

Expected: unrelated existing changes may appear in `docker-compose.yml`, `package.json`, `src/app/(payload)/admin/importMap.js`, `src/payload-types.ts`, and `tsconfig.json`. Do not revert, stage, or edit those files unless the user explicitly asks.

---

### Task 1: Add Tailwind Tokens

**Files:**
- Modify: `tailwind.config.js:19-40`

- [ ] **Step 1: Update Tailwind safelist and color config**

Replace the existing `safelist` color pattern and `theme.colors` block with this structure, preserving the surrounding config:

```js
  safelist: [
    ...safelist,
    {
      pattern:
        /^bg-(primary|secondary|black|white|muted|background|brand-red|brand-blue|brand-black|yellow|warm-gray|cool-gray|ink|line|surface|canvas|success|warning|danger|info)$/,
    },
    { pattern: /p[tlrb]-./ },
    { pattern: /max-w-./ },
    { pattern: /^col-span-(1[0-2]|[1-9])$/ },
  ],
  theme: {
    extend: {
      fontSize: {
        '2xs': '0.688rem',
      },
    },
    colors: {
      ...colors,
      primary: '#1E3A8A',
      secondary: '#C02C36',
      black: '#000',
      white: '#FFF',
      muted: {
        DEFAULT: '#ebedf3',
        foreground: 'rgb(var(--muted-foreground) / <alpha-value>)',
      },
      background: '#F5F5F5',
      'brand-red': '#ed0000',
      'brand-blue': '#102c66',
      'brand-black': '#1c1c1c',
      yellow: '#ffc700',
      'warm-gray': '#f2db6b',
      'cool-gray': '#bbc2d6',
      ink: '#1c1c1c',
      line: '#e2e8f0',
      surface: '#ffffff',
      canvas: '#f8fafc',
      success: '#16a34a',
      warning: '#f59e0b',
      danger: '#dc2626',
      info: '#1d4ed8',
      border: 'rgb(var(--border) / <alpha-value>)',
      ring: 'rgb(var(--ring) / <alpha-value>)',
      card: {
        DEFAULT: 'rgb(var(--card) / <alpha-value>)',
        foreground: 'rgb(var(--card-foreground) / <alpha-value>)',
      },
      popover: {
        DEFAULT: 'rgb(var(--popover) / <alpha-value>)',
        foreground: 'rgb(var(--popover-foreground) / <alpha-value>)',
      },
      accent: {
        DEFAULT: 'rgb(var(--accent) / <alpha-value>)',
        foreground: 'rgb(var(--accent-foreground) / <alpha-value>)',
      },
      destructive: {
        DEFAULT: 'rgb(var(--destructive) / <alpha-value>)',
        foreground: 'rgb(var(--destructive-foreground) / <alpha-value>)',
      },
    },
```

Keep the rest of `tailwind.config.js` unchanged.

- [ ] **Step 2: Verify old aliases and new tokens exist in Tailwind config**

Run:

```bash
rg "primary: '#1E3A8A'|secondary: '#C02C36'|black: '#000'|background: '#F5F5F5'|'brand-red': '#ed0000'|'brand-blue': '#102c66'|'brand-black': '#1c1c1c'" tailwind.config.js
```

Expected: all listed tokens appear. Existing alias values are unchanged.

- [ ] **Step 3: Commit Task 1**

Run:

```bash
git add tailwind.config.js
git commit -m "feat: add additive color tokens"
```

Expected: commit includes only `tailwind.config.js`.

---

### Task 2: Add CSS Variables

**Files:**
- Modify: `src/app/(frontend)/styles.css:1-20`

- [ ] **Step 1: Add additive color and semantic variables**

Insert this block immediately after the Tailwind directives:

```css
:root {
  --color-brand-red: #ed0000;
  --color-brand-blue: #102c66;
  --color-brand-black: #1c1c1c;
  --color-yellow: #ffc700;
  --color-warm-gray: #f2db6b;
  --color-cool-gray: #bbc2d6;
  --color-ink: #1c1c1c;
  --color-line: #e2e8f0;
  --color-surface: #ffffff;
  --color-canvas: #f8fafc;
  --color-success: #16a34a;
  --color-warning: #f59e0b;
  --color-danger: #dc2626;
  --color-info: #1d4ed8;

  --border: 226 232 240;
  --ring: 29 78 216;
  --card: 255 255 255;
  --card-foreground: 28 28 28;
  --popover: 255 255 255;
  --popover-foreground: 28 28 28;
  --accent: 248 250 252;
  --accent-foreground: 28 28 28;
  --muted-foreground: 100 116 139;
  --destructive: 220 38 38;
  --destructive-foreground: 255 255 255;
}
```

The top of the file should then look like:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --color-brand-red: #ed0000;
  --color-brand-blue: #102c66;
  --color-brand-black: #1c1c1c;
  --color-yellow: #ffc700;
  --color-warm-gray: #f2db6b;
  --color-cool-gray: #bbc2d6;
  --color-ink: #1c1c1c;
  --color-line: #e2e8f0;
  --color-surface: #ffffff;
  --color-canvas: #f8fafc;
  --color-success: #16a34a;
  --color-warning: #f59e0b;
  --color-danger: #dc2626;
  --color-info: #1d4ed8;

  --border: 226 232 240;
  --ring: 29 78 216;
  --card: 255 255 255;
  --card-foreground: 28 28 28;
  --popover: 255 255 255;
  --popover-foreground: 28 28 28;
  --accent: 248 250 252;
  --accent-foreground: 28 28 28;
  --muted-foreground: 100 116 139;
  --destructive: 220 38 38;
  --destructive-foreground: 255 255 255;
}

* {
  box-sizing: border-box;
}
```

- [ ] **Step 2: Verify variables were added**

Run:

```bash
rg "--color-brand-red|--color-brand-blue|--color-brand-black|--color-info|--destructive|--card-foreground|--popover-foreground|--muted-foreground" "src/app/(frontend)/styles.css"
```

Expected: all listed variables appear in `:root`.

- [ ] **Step 3: Commit Task 2**

Run:

```bash
git add "src/app/(frontend)/styles.css"
git commit -m "feat: define color token variables"
```

Expected: commit includes only `src/app/(frontend)/styles.css`.

---

### Task 3: Replace Admin-Only Hardcoded Status Colors

**Files:**
- Modify: `src/utilities/SyncToProd.tsx:56-64`
- Modify: `src/utilities/SyncFormSubmissions.tsx:73-81`
- Modify: `src/components/Image/ImagePageUsageTable.component.tsx:122-127`

- [ ] **Step 1: Replace sync banner link colors**

In `src/utilities/SyncToProd.tsx`, change:

```tsx
              color: '#0070f3',
```

to:

```tsx
              color: 'var(--color-info)',
```

In `src/utilities/SyncFormSubmissions.tsx`, change:

```tsx
            color: '#0070f3',
```

to:

```tsx
            color: 'var(--color-info)',
```

- [ ] **Step 2: Replace image usage published status colors**

In `src/components/Image/ImagePageUsageTable.component.tsx`, replace the published status style values:

```tsx
                      backgroundColor:
                        page.status === 'published'
                          ? 'rgba(0, 128, 0, 0.1)'
                          : 'var(--theme-elevation-150)',
                      color: page.status === 'published' ? '#2d8a2d' : 'var(--theme-elevation-500)',
                      border: `1px solid ${page.status === 'published' ? 'rgba(0, 128, 0, 0.2)' : 'transparent'}`,
```

with:

```tsx
                      backgroundColor:
                        page.status === 'published'
                          ? 'color-mix(in srgb, var(--color-success) 10%, transparent)'
                          : 'var(--theme-elevation-150)',
                      color:
                        page.status === 'published'
                          ? 'var(--color-success)'
                          : 'var(--theme-elevation-500)',
                      border: `1px solid ${page.status === 'published' ? 'color-mix(in srgb, var(--color-success) 20%, transparent)' : 'transparent'}`,
```

- [ ] **Step 3: Verify removed admin-only hardcoded colors**

Run:

```bash
rg "#0070f3|#2d8a2d|rgba\(0, 128, 0" src/utilities/SyncToProd.tsx src/utilities/SyncFormSubmissions.tsx src/components/Image/ImagePageUsageTable.component.tsx
```

Expected: no matches.

- [ ] **Step 4: Commit Task 3**

Run:

```bash
git add src/utilities/SyncToProd.tsx src/utilities/SyncFormSubmissions.tsx src/components/Image/ImagePageUsageTable.component.tsx
git commit -m "refactor: use semantic admin status colors"
```

Expected: commit includes only the three admin-related files.

---

### Task 4: Replace Approved Visual-Equivalent Public Border

**Files:**
- Modify: `src/blocks/FinancialCalculator/FinancialCalculator.component.tsx:283`

- [ ] **Step 1: Replace hardcoded divider border with `line` token**

Change:

```tsx
        <div className="w-full py-3 mt-10 text-lg text-primary text-center font-bold border-y-2 border-[#E0E0E0]">
```

to:

```tsx
        <div className="w-full py-3 mt-10 text-lg text-primary text-center font-bold border-y-2 border-line">
```

- [ ] **Step 2: Verify public border replacement**

Run:

```bash
rg "#E0E0E0|border-line" src/blocks/FinancialCalculator/FinancialCalculator.component.tsx
```

Expected: `border-line` appears and `#E0E0E0` does not appear.

- [ ] **Step 3: Commit Task 4**

Run:

```bash
git add src/blocks/FinancialCalculator/FinancialCalculator.component.tsx
git commit -m "refactor: use line token for calculator divider"
```

Expected: commit includes only `src/blocks/FinancialCalculator/FinancialCalculator.component.tsx`.

---

### Task 5: Verify CMS Compatibility And Deferred Colors

**Files:**
- Read-only verification: `src/utilities/index.ts`
- Read-only verification: `src/fields/Color.field.ts`
- Read-only verification: deferred hardcoded color files

- [ ] **Step 1: Confirm CMS color source is unchanged**

Run:

```bash
rg "export type Color = 'muted' \| 'primary' \| 'white' \| 'secondary' \| 'black' \| 'background'|primary: '#1E3A8A'|secondary: '#C02C36'|muted: '#ebedf3'|background: '#F5F5F5'|export const colorNames = Object.keys\(colors\)" src/utilities/index.ts
```

Expected: all existing CMS-facing aliases and values appear unchanged.

- [ ] **Step 2: Confirm ColorField still uses `colorNames`**

Run:

```bash
rg "import \{ colorNames \} from '@/utilities'|options: colorNames" src/fields/Color.field.ts
```

Expected: `ColorField` still imports and uses `colorNames`; no new color list is introduced.

- [ ] **Step 3: Confirm intentionally deferred production colors remain untouched**

Run:

```bash
rg "#bf2c3666|#bf2c3699|#FF8B7B|#FFFF8A|#DB5E66" src/blocks/File/PDFIndicators.tsx src/blocks/Carousel/Carousel.component.tsx src/blocks/TuitionCalculator/TuitionCalculator.component.tsx src/components/FloatingButton/floatingButton.component.tsx
```

Expected: these values still appear. They are intentionally deferred to avoid visible production changes.

- [ ] **Step 4: Commit Task 5 only if verification docs are added**

No commit is needed if this task only runs read-only checks. If the implementer adds a short verification note to an existing PR description instead of the repo, do not create a commit.

---

### Task 6: Run Build Verification

**Files:**
- No planned file changes.

- [ ] **Step 1: Run TypeScript/build check**

Run:

```bash
pnpm build
```

Expected: Next build completes successfully. If the build fails because of pre-existing local environment/configuration issues, capture the exact error and do not hide it.

- [ ] **Step 2: Run targeted token searches**

Run:

```bash
rg "brand-red|brand-blue|brand-black|warm-gray|cool-gray|text-card-foreground|bg-popover|bg-accent|text-muted-foreground|border-ring|border-line" tailwind.config.js "src/app/(frontend)/styles.css" src/components/ui src/blocks/FinancialCalculator/FinancialCalculator.component.tsx
```

Expected: new tokens and semantic classes are present in config/CSS or existing UI components.

- [ ] **Step 3: Inspect final diff before handoff**

Run:

```bash
git status --short
git diff
git log --oneline -8
```

Expected: only the planned files are modified by this implementation. Unrelated user-owned changes that existed before implementation may still appear; do not revert or stage them.

---

## Self-Review Notes

- Spec coverage: Tasks 1 and 2 implement additive Tailwind/CSS token support. Task 3 covers safe admin-only hardcoded replacements. Task 4 covers the approved visual-equivalent public border replacement. Task 5 verifies CMS dropdown compatibility and deferred hardcoded colors. Task 6 verifies the build and final diff.
- Scope check: This is one focused token infrastructure plan. It does not include CMS migration, dark mode, contrast checking, or broad production block redesign.
- Type consistency: New token names use `brand-*` in Tailwind and `--color-brand-*` for direct CSS variables. Existing CMS `Color` type and `colorNames` remain unchanged.
