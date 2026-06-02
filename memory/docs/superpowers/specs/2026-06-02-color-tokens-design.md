# Color Tokens Design

## Ticket

ClickUp: `86d36yejy` - Color Tokens

## Goal

Add the new MMDC redesign color token layer without causing broad visual changes to existing production CMS-rendered pages.

The current site stores Payload page content as block data and renders it through the current React components and Tailwind classes at runtime or static export time. Saved CMS pages do not store snapshotted rendered CSS. Because of that, changing existing token values can change already-published pages. This design treats existing CMS-facing tokens as compatibility aliases and adds the redesign palette beside them.

## Approved Approach

Use an additive developer-facing token layer.

Do not remap existing aliases in this ticket. Do not expose the new tokens through existing generic CMS color dropdowns. New redesign implementation can opt into the new tokens explicitly through Tailwind classes or CSS variables.

## Compatibility Rules

Existing aliases must keep their current values:

| Existing Token | Current Value | Decision |
| --- | --- | --- |
| `primary` | `#1E3A8A` | Preserve for CMS/page compatibility |
| `secondary` | `#C02C36` | Preserve for CMS/page compatibility |
| `black` | `#000` | Preserve for CMS/page compatibility |
| `white` | `#FFF` | Preserve for CMS/page compatibility |
| `muted` | `#ebedf3` | Preserve for CMS/page compatibility |
| `background` | `#F5F5F5` | Preserve for CMS/page compatibility |

These values should remain unchanged in `src/utilities/index.ts` and `tailwind.config.js` unless a later migration ticket explicitly approves production visual changes.

## New Token Names

Add the following brand, accent, neutral, and semantic tokens for developer use:

| Token | Value | Use |
| --- | --- | --- |
| `brand-red` | `#ed0000` | MMDC brand red |
| `brand-blue` | `#102c66` | MMDC brand blue |
| `brand-black` | `#1c1c1c` | MMDC brand black |
| `yellow` | `#ffc700` | Accent yellow |
| `warm-gray` | `#f2db6b` | Accent warm gray |
| `cool-gray` | `#bbc2d6` | Accent cool gray |
| `ink` | `#1c1c1c` | Neutral text/content color |
| `line` | `#e2e8f0` | Borders and dividers |
| `surface` | `#ffffff` | Surface backgrounds |
| `canvas` | `#f8fafc` | Page/background canvas |
| `success` | `#16a34a` | Success state |
| `warning` | `#f59e0b` | Warning state |
| `danger` | `#dc2626` | Danger/destructive state |
| `info` | `#1d4ed8` | Informational state |

`brand-black` and `ink` intentionally share the same value. Use `brand-black` when referring to the brand palette and `ink` when referring to neutral text or content UI.

## Tailwind And CSS Variables

`tailwind.config.js` should define the new tokens alongside the preserved aliases. Tailwind opacity modifiers should handle opacity variants, for example `bg-brand-red/80`, `text-brand-blue/60`, and `border-brand-black/20`. Do not create separate `brand-red-80`, `brand-red-60`, `brand-red-20`, or `brand-red-5` token names.

`src/app/(frontend)/styles.css` should define matching `:root` CSS variables for the additive token layer. It should also define shadcn-style semantic variables used by existing UI components so classes such as `bg-destructive`, `bg-popover`, `text-popover-foreground`, `bg-accent`, `text-muted-foreground`, `bg-card`, `text-card-foreground`, and `border-ring` resolve consistently.

CSS variable mappings should use the new additive semantic/neutral layer without changing existing `primary`, `secondary`, `muted`, or `background` Tailwind aliases.

## CMS Safety

Do not add the new token names to `colorNames` in `src/utilities/index.ts` for this ticket.

`src/fields/Color.field.ts` derives existing Payload select options from `colorNames`. Leaving `colorNames` unchanged keeps generic CMS color dropdowns stable and avoids enabling accent or semantic colors everywhere existing color fields are used.

Future CMS-facing redesign work can opt into the new palette field-by-field with a separate approval and migration plan.

## Component And Hardcoded Color Handling

Production safety takes priority over removing every hardcoded color.

Allowed changes:

- Add token support in `tailwind.config.js`.
- Add CSS variables in `src/app/(frontend)/styles.css`.
- Wire undefined shadcn-style semantic variables used by `src/components/ui/button.tsx`, `src/components/ui/dropdown-menu.tsx`, and `src/components/ui/card.tsx`.
- Replace hardcoded colors only when the replacement is admin-only or visually equivalent.

Specific hardcoded color decisions:

| File | Existing Color | Decision |
| --- | --- | --- |
| `src/utilities/SyncToProd.tsx` | `#0070f3` | Safe to replace with `info` or a matching CSS variable because it is an admin/dashboard utility |
| `src/utilities/SyncFormSubmissions.tsx` | `#0070f3` | Safe to replace with `info` or a matching CSS variable because it is an admin/dashboard utility |
| `src/components/Image/ImagePageUsageTable.component.tsx` | `#2d8a2d` and green rgba values | Safe to replace with `success` semantics if this remains admin-only |
| `src/blocks/FinancialCalculator/FinancialCalculator.component.tsx` | `#E0E0E0` | Safe to replace with `line` because the value is visually close and semantically a divider/border |
| `src/blocks/File/PDFIndicators.tsx` | `#bf2c3666`, `#bf2c3699` | Skip unless a visible change is explicitly approved |
| `src/blocks/Carousel/Carousel.component.tsx` | `#FF8B7B` | Skip unless a visible accent change is explicitly approved |
| `src/blocks/TuitionCalculator/TuitionCalculator.component.tsx` | `#FFFF8A` | Skip because no approved token is a close visual equivalent |
| `src/components/FloatingButton/floatingButton.component.tsx` | `#DB5E66` | Skip unless a close equivalent is introduced or approved |

`src/blocks/Button/Button.component.tsx` should preserve current CMS-rendered button behavior. It can reference defined semantic variables only if the rendered output for existing variants remains effectively unchanged.

## Testing And Verification

Verification should prove that the new token layer exists and that compatibility aliases did not migrate.

Required checks:

- Confirm `tailwind.config.js` includes the new additive tokens.
- Confirm `tailwind.config.js` preserves existing alias values.
- Confirm `src/utilities/index.ts` preserves existing `Color`, `colors`, and `colorNames` behavior for CMS fields.
- Confirm `src/app/(frontend)/styles.css` defines additive CSS variables and shadcn-style semantic variables.
- Confirm `ColorField`-driven CMS dropdowns are not broadened by this ticket.
- Run the project type/build check available in the repo, or document why it could not be run.
- Review touched shared components to ensure existing `primary`, `secondary`, `muted`, and `background` behavior still resolves.

Optional checks:

- Smoke-test one existing CMS-rendered page that uses styled blocks.
- Smoke-test button, dropdown menu, and card UI behavior locally or in Storybook if the environment is already available.

## Non-Goals

- Do not implement dark mode variants.
- Do not build a contrast checker.
- Do not add CMS-driven color customization beyond existing select fields.
- Do not globally migrate production pages from old aliases to new brand values.
- Do not expose all new tokens in existing generic CMS color dropdowns.
- Do not replace hardcoded production colors when doing so would visibly change existing pages.

## Implementation Boundary

The implementation plan should be small and surgical. It should focus on token infrastructure and safe semantic variable wiring. It should not rewrite production blocks, CMS schemas, or shared renderers beyond the approved token support.
