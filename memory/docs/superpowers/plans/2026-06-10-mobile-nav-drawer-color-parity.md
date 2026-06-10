# MobileNavDrawer Color Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update MobileNavDrawer card styles, Quick Links block, and drawer shell to match website3.0-prototype solid-card-background color scheme.

**Architecture:** Single-file style refactor in `MobileNavDrawer.component.tsx`. Three areas touched: the `cardStyles` object, the Quick Links inline block, and the drawer panel wrapper. No structural/behavioral changes — no new files, no new props, no logic changes.

**Tech Stack:** Tailwind CSS (utility classes using project tokens via `tailwind.config.js`), TypeScript, React

---

### Task 1: Refactor `cardStyles` object

**Files:**
- Modify: `src/components/MobileNavDrawer/MobileNavDrawer.component.tsx:54-85`

- [ ] **Step 1: Replace the `cardStyles` object**

Replace lines 54-85 (the entire `cardStyles` constant) with:

```tsx
const cardStyles = {
  yellow: {
    wrapper: 'bg-yellow text-ink',
    heading: 'border-b border-ink/10 text-ink',
    link: 'text-ink hover:text-brand-red',
  },
  blue: {
    wrapper: 'bg-brand-blue text-zinc-200',
    heading: 'border-b border-white/10 text-white font-semibold',
    link: 'text-zinc-200 hover:text-yellow',
  },
  black: {
    wrapper: 'bg-brand-black text-zinc-200',
    heading: 'border-b border-white/10 text-white font-semibold',
    link: 'text-zinc-200 hover:text-yellow',
  },
  red: {
    wrapper: 'bg-brand-red text-white',
    heading: 'border-b border-white/20 text-white font-semibold',
    link: 'text-white hover:text-yellow',
  },
  blueMuted: {
    wrapper: 'bg-brand-blue/90 text-zinc-200',
    heading: 'border-b border-white/10 text-white font-semibold',
    link: 'text-zinc-200 hover:text-yellow',
  },
  white: {
    wrapper: 'bg-white text-ink border border-line',
    heading: 'border-b border-line text-ink',
    link: 'text-ink hover:text-brand-red',
  },
}
```

- [ ] **Step 2: Commit**

```bash
git add src/components/MobileNavDrawer/MobileNavDrawer.component.tsx
git commit -m "refactor: update MobileNavDrawer cardStyles to solid-background variants"
```

---

### Task 2: Update Quick Links inline block to yellow card

**Files:**
- Modify: `src/components/MobileNavDrawer/MobileNavDrawer.component.tsx:231-256`

- [ ] **Step 1: Replace Quick Links wrapper and heading classes**

Replace lines 232 and 233-238 (the `<section>` opening tag through the `</Heading>`):

**Old (line 232):**
```tsx
            <section className="relative space-y-3.5 overflow-hidden rounded-xl border border-line bg-white p-[18px] pt-5 text-left text-ink shadow-sm before:absolute before:inset-x-0 before:top-0 before:h-1 before:bg-brand-blue">
```

**New:**
```tsx
            <section className="relative space-y-3.5 overflow-hidden rounded-xl bg-yellow p-[18px] pt-5 text-left text-ink">
```

**Old (lines 233-238):**
```tsx
              <Heading
                as="h2"
                size="h4"
                className="border-b border-line pb-2 font-display text-lg font-bold tracking-tight text-brand-blue"
              >
```

**New:**
```tsx
              <Heading
                as="h2"
                size="h4"
                className="border-b border-ink/10 pb-2 font-display text-lg font-bold tracking-tight text-ink"
              >
```

- [ ] **Step 2: Commit**

```bash
git add src/components/MobileNavDrawer/MobileNavDrawer.component.tsx
git commit -m "refactor: update MobileNavDrawer Quick Links to yellow card style"
```

---

### Task 3: Remove accent bar from section cards + update drawer shell

**Files:**
- Modify: `src/components/MobileNavDrawer/MobileNavDrawer.component.tsx:190, 265-268`

- [ ] **Step 1: Update drawer panel background and shadow**

Replace line 190:

**Old:**
```tsx
      <div className="flex h-full flex-col justify-between overflow-hidden bg-canvas shadow-[0_24px_48px_rgb(16_44_102_/_0.22)]">
```

**New:**
```tsx
      <div className="flex h-full flex-col justify-between overflow-hidden bg-zinc-50 shadow-[0_24px_48px_rgb(16_44_102_/_0.18)]">
```

- [ ] **Step 2: Remove accent bar classes from section `<section>` element**

Replace line 266 (the `className` on the `<section>` for section cards):

**Old:**
```tsx
                className={cn(
                  'relative space-y-3.5 overflow-hidden rounded-xl p-[18px] pt-5 text-left before:absolute before:inset-x-0 before:top-0 before:h-1',
                  styles.wrapper,
                )}
```

**New:**
```tsx
                className={cn(
                  'relative space-y-3.5 overflow-hidden rounded-xl p-[18px] pt-5 text-left',
                  styles.wrapper,
                )}
```

- [ ] **Step 3: Run Storybook to visually verify**

```bash
npx storybook dev -p 6006
```

Navigate to Components > MobileNavDrawer. Verify:
- All section cards have solid colored backgrounds (no more white cards with accent bars)
- Quick Links card is yellow
- Drawer panel is `bg-zinc-50`
- Dark cards have `text-zinc-200` links that hover to yellow
- Light cards have `text-ink` links that hover to red

- [ ] **Step 4: Commit**

```bash
git add src/components/MobileNavDrawer/MobileNavDrawer.component.tsx
git commit -m "refactor: remove accent bars and update MobileNavDrawer panel colors"
```
