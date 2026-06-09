# Badge Atom Design Spec

**Date:** 2026-06-10  
**Ticket:** [CU-86d39pyt8](https://app.clickup.com/t/86d39pyt8)  
**Reference:** `website3.0-prototype/src/components/atoms/Badge.tsx`

## Overview

Implement a reusable `Badge` atom in the website repo for semantic status labels, indicators, counts, and "new" badges. The component follows `website3.0-prototype` as the Kitchen Sink reference while adapting to the website repo's token system, component patterns (`cva`, `cn`, `motion/react`), and Storybook conventions.

## Component API

```ts
interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  children: React.ReactNode
  variant?: 'success' | 'warning' | 'error' | 'info' | 'brand' | 'brandRed' | 'count' | 'new'
  size?: 'sm' | 'md'
  shape?: 'pill' | 'rounded'
  count?: number  // triggers increment pulse on change (for 'count' variant)
}
```

- Renders a `<motion.span>` (from `motion/react`)
- Defaults: `variant="brand"`, `size="md"`, `shape="pill"`
- Extends native `span` attributes; `className` and other HTML props passthrough
- `count` prop is optional; when variant is `count`, changing the value triggers a scale pulse

## Token Mapping

Prototype tokens mapped to website repo Tailwind tokens:

| Prototype Token | Website Token | Color Value |
|---|---|---|
| `mmdc-blue` | `brand-blue` | `#102c66` |
| `mmdc-red` | `brand-red` | `#ed0000` |
| `mmdc-yellow` | `yellow` | `#ffc700` |
| `success` | `success` | `#16a34a` |
| `warning` | `warning` | `#f59e0b` |
| `danger` | `danger` | `#dc2626` |
| `info` | `info` | `#1d4ed8` |
| `ink` | `ink` | `#1c1c1c` |

Prototype `dark:` variants are dropped (website has no dark mode).

## Variant Styling

| Variant | Background | Text |
|---|---|---|
| `success` | `bg-success/15` | `text-success` |
| `warning` | `bg-warning/15` | `text-warning` |
| `error` | `bg-danger/15` | `text-danger` |
| `info` | `bg-info/15` | `text-info` |
| `brand` | `bg-brand-blue` | `text-white` |
| `brandRed` | `bg-brand-red` | `text-white` |
| `count` | `bg-brand-red` | `text-white` |
| `new` | `bg-yellow` | `text-ink` |

## Sizes

| Size | Height | Padding X | Font Size |
|---|---|---|---|
| `sm` | `h-4` (16px) | `px-1.5` | `text-[10px]` |
| `md` (default) | `h-5` (20px) | `px-2` | `text-xs` |

## Shapes

| Shape | Class |
|---|---|
| `pill` (default) | `rounded-full` |
| `rounded` | `rounded-sm` |

## Base Classes

`inline-flex items-center gap-1 font-semibold whitespace-nowrap overflow-hidden`

## Animations

### Shimmer (`variant="new"`)

- On mount, an absolutely-positioned half-width `<motion.div>` sweeps across the badge
- Gradient: `from-transparent via-white/50 to-transparent skew-x-12`
- Animates `x` from `"-100%"` to `"200%"` over 0.8s with a 0.1s delay, runs once
- Skipped if `prefers-reduced-motion: reduce`

### Count Pulse (`variant="count"`)

- When `count` prop changes: scales `1 → 1.15 → 1` over 0.3s with easing `[0.34, 1.56, 0.64, 1]` (the "nudge" curve)
- Initial mount: spring animation from `scale: 0` (`stiffness: 400, damping: 20`)
- Skipped if `prefers-reduced-motion: reduce`

### Reduced Motion Detection

Inlined in the component via `useState` + `useEffect` with `window.matchMedia("(prefers-reduced-motion: reduce)")` — no separate hook file.

## Files to Create

| File | Purpose |
|---|---|
| `src/components/Badge/Badge.component.tsx` | Badge atom implementation |
| `src/components/Badge/Badge.stories.tsx` | Storybook stories |

## Files to Modify

| File | Change |
|---|---|
| `src/components/index.ts` | Add Badge default export and type exports |

## Storybook Stories

| Story | Description |
|---|---|
| `Default` | `variant="info"`, `children="Badge"` — minimal example |
| `Variants` | Grouped render of all 8 variants in flex wrap |
| `Sizes` | `md` and `sm` side by side, `variant="info"` |
| `Shapes` | `pill` and `rounded` side by side, `variant="info"` |
| `Shimmer` | `variant="new"` with text "NEW" and "Featured" |
| `CountPulse` | Interactive: `variant="count"` with increment button showing spring mount + pulse |

Story title: `'Atoms/Badge'`

## Dependencies

- `motion/react` (already installed, v12.40.0, also used by `Heading.tsx`)
- `class-variance-authority` (already installed, v0.7.1)
- `clsx` + `tailwind-merge` via `@/lib/utils` `cn()` helper

## What's Not in Scope

- CardMolecule integration (ticket states Badge is "available" but CardMolecule currently uses Tag — integration is future work)
- `useReducedMotion` hook file (inlined instead)
- Dark mode variants (none exist in the website repo)
