# MobileNavDrawer Color Parity Design

**Date:** 2026-06-10
**Context:** Align `MobileNavDrawer` card color scheme with website3.0-prototype `/organisms/navbar` mobile drawer.

---

## Goal

Update `src/components/MobileNavDrawer/MobileNavDrawer.component.tsx` to match the prototype's solid-card-background color scheme, replacing the current white-card-with-accent-bar design across all six variants. Also update drawer shell colors and the inline Quick Links block.

---

## Section 1: Card Styles (`cardStyles` object)

The `cardStyles` map (lines 54-85) is refactored. The `before:` accent bar is removed from all variants. Dark-background variants use light text with yellow hover; light-background variants use dark text with red hover.

| Variant | wrapper | heading | link |
|---|---|---|---|
| `yellow` | `bg-yellow text-ink` | `border-b border-ink/10 text-ink` | `text-ink hover:text-brand-red` |
| `blue` | `bg-brand-blue text-zinc-200` | `border-b border-white/10 text-white font-semibold` | `text-zinc-200 hover:text-yellow` |
| `black` | `bg-brand-black text-zinc-200` | `border-b border-white/10 text-white font-semibold` | `text-zinc-200 hover:text-yellow` |
| `red` | `bg-brand-red text-white` | `border-b border-white/20 text-white font-semibold` | `text-white hover:text-yellow` |
| `blueMuted` | `bg-brand-blue/90 text-zinc-200` | `border-b border-white/10 text-white font-semibold` | `text-zinc-200 hover:text-yellow` |
| `white` | `bg-white text-ink border border-line` | `border-b border-line text-ink` | `text-ink hover:text-brand-red` |

**Changes from current:**
- All variants: remove `border border-line bg-white shadow-sm before:bg-*`
- `white` variant: keeps `border border-line` but drops `before:bg-line` accent
- Dark variants (`blue`, `black`, `red`, `blueMuted`): `text-zinc-200` links, `hover:text-yellow`, white/white-10 heading borders
- `yellow` variant: `border-ink/10` heading border (subtle dark variant-appropriate border)

---

## Section 2: JSX Changes

### Remove accent bar from section cards
In the section map (lines 259-305), remove `before:absolute before:inset-x-0 before:top-0 before:h-1` from the section `<section>` element. This avoids conflicts with the new solid-background styles.

### Remove accent bar from Quick Links
In the Quick Links block (lines 231-256), remove `before:absolute before:inset-x-0 before:top-0 before:h-1 before:bg-brand-blue` and change the card to `bg-yellow text-ink` with `border-b border-ink/10` heading. Keep the `<TrendingUp>` icon and existing structure.

**Quick Links changes:**
- Wrapper: `bg-yellow` replaces `border border-line bg-white ... before:bg-brand-blue`
- Heading: `border-b border-ink/10 text-ink` replaces `border-b border-line text-brand-blue`
- Links: unchanged (`text-ink hover:text-brand-red`)

---

## Section 3: Drawer Shell

| Element | From | To |
|---|---|---|
| Panel background | `bg-canvas` (`#f8fafc`) | `bg-zinc-50` (`#fafafa`) |
| Panel shadow | `shadow-[0_24px_48px_rgb(16_44_102_/_0.22)]` | `shadow-[0_24px_48px_rgb(16_44_102_/_0.18)]` |

Header bar (`bg-white border-b border-line`), CTA footer (`bg-zinc-100 border-t border-line`), and overlay (`bg-black/40`) are unchanged.

---

## Files Affected

- `src/components/MobileNavDrawer/MobileNavDrawer.component.tsx` — all changes
- No new files, no new exports, no prop changes

---

## Verification

- Run existing Storybook stories (`Default`, `WithoutSearch`, `WithoutCTA`, `WithSelectedLink`) — all should render with new color scheme
- Visual check: each variant section should have a solid colored background matching the prototype
- Quick Links should render as a yellow card
