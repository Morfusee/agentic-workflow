# CardMolecule Parity Port — Design Spec

**Date:** 2026-06-10
**Ticket:** [CU-86d36z2p3](https://app.clickup.com/t/86d36z2p3) — Implement Card molecule for interactive Hero CTAs
**Branch:** `CU-86d36z2p8_Mobile-Navbar-OffCanvas`
**Prototype reference:** `C:\Users\mrqvp\Documents\Programming\website3.0-prototype\src\components\molecules\CardMolecule.tsx`

## Objective

Replace the current `CardMolecule` (shadcn/ui Card wrapper with minimal features) with a full port of the prototype `CardMolecule` from `website3.0-prototype`, achieving visual and behavioral parity while preserving backward compatibility with existing consumers.

## Motivation

The current CardMolecule does not match the prototype in:
- Styling (rounded-xl vs rounded-[16px], shadow treatment, typography)
- Feature set (no images, no kicker/tag/meta, no skeleton, no mesh, no orientation)
- Composition (uses shadcn CardTitle vs Heading atom)
- Footer layout (full Button vs simple cta link with meta)

The prototype CardMolecule is the designated "Kitchen Sink" reference for how MMDC cards should look and behave.

## Props (final target)

| Prop | Type | Default | Source |
|---|---|---|---|
| `kicker` | `string` | — | Prototype |
| `title` | `string` | — | Both (rendered via `<Heading>`) |
| `tag` | `string` | — | Prototype |
| `body` | `ReactNode` | — | Prototype (replaces `description: string`) |
| `imageSrc` | `string` | — | Prototype |
| `imageType` | `"none" \| "inset" \| "full-bleed" \| "overlay" \| "seam-straddle"` | `"none"` | Prototype |
| `imageBadge` | `string` | — | Prototype |
| `imageActionIcon` | `ReactNode` | — | Prototype |
| `iconStraddle` | `ReactNode` | — | Prototype |
| `action` | `string \| ReactNode` | — | Prototype (replaces `actionLabel: string`) |
| `onAction` | `() => void` | — | Prototype |
| `meta` | `ReactNode` | — | Prototype |
| `metaIcon` | `ReactNode` | — | Prototype |
| `orientation` | `"vertical" \| "horizontal"` | `"vertical"` | Prototype |
| `href` | `string` | — | Both |
| `isHover` | `boolean` | — | Prototype |
| `isFocus` | `boolean` | — | Prototype |
| `isActive` | `boolean` | — | Prototype |
| `isSkeleton` | `boolean` | — | Prototype |
| `mesh` | `"mesh-1" \| "mesh-2" \| "mesh-brand"` | `"mesh-1"` | Prototype |
| `className` | `string` | — | Both |
| `icon` | `ReactNode` | — | Legacy (maps to iconStraddle behavior) |
| `description` | `string` | — | Legacy (maps to body as `<p>`) |
| `actionLabel` | `string` | — | Legacy (maps to action) |
| `selected` | `boolean` | `false` | Legacy (kept, prototype has no equivalent) |
| `disabled` | `boolean` | `false` | Legacy (kept, prototype has no equivalent) |
| `variant` | `"default" \| "secondary" \| "outline"` | `"default"` | Legacy (kept, adds color themes) |
| `onClick` | `MouseEventHandler` | — | Legacy (maps to root onClick, separate from onAction) |

## Component Structure

```
CardMolecule
├── Root element (<a> if href, <div> otherwise)
│   ├── card-surface, card-int, focus-ring, lift CSS classes
│   ├── orientation layout (vertical stack vs horizontal flex)
│   ├── State classes: is-hover, is-focus, is-active, is-skeleton
│   │
│   ├── [Skeleton overlay] (when isSkeleton)
│   │   └── Shimmer placeholders via <Skeleton> atom
│   │
│   ├── [Image section] (when imageType !== "none")
│   │   ├── mesh background pattern
│   │   ├── <img> or placeholder div
│   │   ├── imageBadge text overlay
│   │   ├── imageActionIcon button
│   │   └── Gradient overlay (overlay mode only)
│   │
│   ├── Content section
│   │   ├── iconStraddle (seam-straddle mode)
│   │   ├── kicker text
│   │   ├── <Heading> + <Tag> (title row)
│   │   ├── m-track (animated underline, interactive only)
│   │   └── body (ReactNode)
│   │
│   └── [Footer section] (when action or meta, and not overlay)
│       ├── border-t, bg-slate-50/50
│       ├── action (cta link or custom node)
│       └── meta + metaIcon
```

## Legacy Prop Mapping

To preserve existing consumers (Storybook stories, barrel export):

| Legacy Prop | Maps To |
|---|---|
| `icon` | Renders in content section as icon circle (like prototype's icon treatment for non-straddle) |
| `description` | Wrapped as `<p>{description}</p>` passed to `body` |
| `actionLabel` | Passed to `action` as string |
| `selected` | Adds `ring-2 ring-secondary/40` styling (kept independent) |
| `disabled` | Adds `cursor-not-allowed opacity-50 pointer-events-none` |
| `variant` | Overrides color scheme: `secondary` → white text on primary bg; `outline` → transparent bg |
| `onClick` | Attached to root element's onClick, separate from `onAction` (which is footer-specific) |

## Dependencies to Create

### New Atoms (port from prototype)

| File | Lines (est.) | Description |
|---|---|---|
| `src/components/Badge/Badge.component.tsx` | ~15 | Simple pill/badge with variant colors |
| `src/components/Badge/Badge.stories.tsx` | ~30 | Storybook |
| `src/components/Tag/Tag.component.tsx` | ~15 | Small colored text tag |
| `src/components/Tag/Tag.stories.tsx` | ~30 | Storybook |
| `src/components/Skeleton/Skeleton.component.tsx` | ~20 | Shimmer placeholder |
| `src/components/Skeleton/Skeleton.stories.tsx` | ~30 | Storybook |
| `src/components/TwoToneIcon/TwoToneIcon.component.tsx` | ~40 | Two-color icon component |
| `src/components/TwoToneIcon/TwoToneIcon.stories.tsx` | ~30 | Storybook |

### Existing Atoms (adapt imports)

| Prototype import | Website equivalent |
|---|---|
| `../atoms/Heading` | `@/components/Heading/Heading` |
| `../atoms/Button` | `@/components/Button/Button.component` |
| `../../lib/cn` | `@/lib/utils` (`cn`) |

### CSS Classes to Define

Add to `src/app/(frontend)/styles.css`:

```css
/* Card surface base */
.card-surface { @apply bg-white rounded-[16px] overflow-hidden; }
/* Interactive card lift */
.card-int { @apply cursor-pointer transition-all duration-300; }
.card-int:hover { @apply -translate-y-0.5 shadow-md; }
/* Focus ring */
.focus-ring { @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-secondary focus-visible:ring-offset-2; }
/* Lift transition */
.lift { @apply transition-shadow duration-200; }
/* Media zoom on hover */
.media-zoom { @apply transition-transform duration-500; }
.group:hover .media-zoom { @apply scale-105; }
/* Motion track (animated underline) */
.m-track { @apply relative; }
.m-track::after {
  content: '';
  @apply absolute bottom-0 left-0 h-[2px] bg-[var(--color-mmdc-red)] w-0 transition-all duration-300;
}
.group:hover .m-track::after { @apply w-full; }
/* Mesh patterns */
.mesh-1 { @apply bg-[radial-gradient(ellipse_at_center,var(--color-brand-blue)_0%,transparent_70%)]; }
.mesh-2 { @apply bg-[radial-gradient(circle_at_top_left,var(--color-brand-red)_0%,transparent_50%)]; }
.mesh-brand { @apply bg-[radial-gradient(ellipse_at_bottom_right,var(--color-brand-blue)_0%,var(--color-brand-red)_50%,transparent_70%)]; }
/* Skeleton shimmer */
.skel { @apply bg-slate-200 rounded animate-pulse; }
```

### Barrel Export

Update `src/components/index.ts` to include new atoms:
```ts
export { default as Badge } from './Badge/Badge.component'
export { default as Tag } from './Tag/Tag.component'
export { default as TwoToneIcon } from './TwoToneIcon/TwoToneIcon.component'
export { Skeleton } from './Skeleton/Skeleton.component'
```

## Files Changed/Created Summary

| File | Action |
|---|---|
| `src/components/CardMolecule/CardMolecule.component.tsx` | Rewrite |
| `src/components/CardMolecule/CardMolecule.stories.tsx` | Rewrite |
| `src/components/Badge/Badge.component.tsx` | Create |
| `src/components/Badge/Badge.stories.tsx` | Create |
| `src/components/Tag/Tag.component.tsx` | Create |
| `src/components/Tag/Tag.stories.tsx` | Create |
| `src/components/Skeleton/Skeleton.component.tsx` | Create |
| `src/components/Skeleton/Skeleton.stories.tsx` | Create |
| `src/components/TwoToneIcon/TwoToneIcon.component.tsx` | Create |
| `src/components/TwoToneIcon/TwoToneIcon.stories.tsx` | Create |
| `src/components/index.ts` | Update (add exports) |
| `src/app/(frontend)/styles.css` | Update (add CSS classes) |

## Acceptance Criteria

1. All existing CardMolecule stories render without visual regressions
2. New stories cover all prototype states: standard, overlay, seam-straddle, horizontal, skeleton, hover/focus/active, mesh variants
3. CardMolecule used in a TriageHero-like grid matches the prototype MMDCOrganisms.tsx layout
4. `body` prop accepts ReactNode (TriageHero passes TwoToneIcon + heading + description)
5. `action` renders as a simple cta link (red text + arrow), not a full Button, when passed as string
6. Keyboard navigation and focus indicators work on interactive cards
7. Existing production pages are unaffected (additive change only)
