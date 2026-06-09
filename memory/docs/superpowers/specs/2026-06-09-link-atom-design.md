# Link Atom Design

## Context

ClickUp ticket `86d39f67h` asks for a reusable Link atom in the main `website` repo, using `website3.0-prototype` as the Kitchen Sink reference. The implementation target is the main worktree at `C:\Users\mrqvp\Documents\Programming\website`, with `feat/v3-redesign` as the currently checked-out base branch and `feat/CU-86d39f67h` as the feature branch name.

The prototype reference is `C:\Users\mrqvp\Documents\Programming\website3.0-prototype\src\components\atoms\Link.tsx` and `LinkPage.tsx`. It defines variants for inline, standalone, arrow, quiet, and inverse links, plus external-link icon behavior and reduced-motion-aware arrow motion.

The website repo already has atom-style components under `src/components/*`, Storybook coverage titled under `Atoms/*`, shared `cn` and `cva` usage, `next/link`, `lucide-react`, and `motion`. Current navigation code still uses raw `next/link`; this ticket will not migrate those consumers.

## Scope

Create a reusable Link atom and Storybook documentation only.

The ticket will not migrate existing navigation, footer, pagination, card, block, or Button link usages. The atom should be ready for those consumers in later work without forcing that adoption in this ticket.

Existing generated or user-owned changes, including `src/payload-types.ts` in the website worktree and unrelated package/lock changes in other worktrees, must be preserved.

## Architecture

Add a new component folder under `src/components/Link/`.

The main component file should follow current atom patterns, similar to `Button`, `Input`, `Textarea`, and `Heading`: a focused component implementation and a nearby Storybook file. The Storybook title should be `Atoms/Link`.

The Link atom should be Next-aware:

- Internal links render through `next/link`.
- External HTTP(S) links render as `<a>`.
- Static-build prefetch behavior should follow the repo pattern by disabling prefetch when `NEXT_PUBLIC_BUILD_MODE` is `static`.
- External link handling should be centralized so consumers do not repeat target, rel, and icon behavior.

The implementation should adapt the Kitchen Sink design to the website repo tokens and utilities: `brand-blue`, `brand-red`, `ink`, `surface`, `cn`, `cva`, `lucide-react`, and `motion`.

## Component API

The component should expose this practical API:

```ts
type LinkVariant = 'inline' | 'standalone' | 'with-arrow' | 'quiet' | 'inverse'
type LinkSize = 'sm' | 'md'

type LinkProps = {
  href: string
  children?: React.ReactNode
  label?: string
  variant?: LinkVariant
  size?: LinkSize
  external?: boolean
  newTab?: boolean
  active?: boolean
  disabled?: boolean
  leadingIcon?: React.ReactNode
  trailingIcon?: React.ReactNode
  ariaLabel?: string
  className?: string
  prefetch?: boolean
}
```

`children` is the preferred visible content. `label` exists for simple data-driven consumers and renders when `children` is not provided.

`external` may be explicit, but HTTP(S) URLs should also be inferred as external when they do not point to internal app routes. External links opened in a new tab must get `target="_blank"` and `rel="noopener noreferrer"`.

`active` should set `aria-current="page"` by default and apply active styling.

`disabled` should prevent navigation, omit the actionable `href`, add `aria-disabled`, suppress click navigation behavior, and apply disabled visual styling.

`with-arrow` should render a default trailing `ArrowRight`, or `ExternalLink` for external destinations, unless a custom `trailingIcon` is supplied.

## Styling And States

Variants should match the prototype direction while using website repo tokens:

- `inline`: semibold blue text with underline, red hover color and underline.
- `standalone`: bold blue text, red hover, directional cue by default.
- `with-arrow`: bold blue text with explicit directional cue for nav/list CTAs.
- `quiet`: ink text with red hover and underline for low-emphasis navigation.
- `inverse`: white text and underline for dark backgrounds.

The component must cover default, hover, active, focus-visible, and disabled states.

Focus-visible styling should follow the Button pattern with a visible brand-blue outline. Active styling should be visible through red text or underline treatment. Disabled styling should use pointer suppression and opacity while keeping `aria-disabled` available to assistive technology.

## Accessibility

Enabled links must remain keyboard-focusable and work with native link semantics.

The component should support both `ariaLabel` and native `aria-label`. Decorative icons should be `aria-hidden`. Icon-only links require an accessible label from the consumer.

External links opened in a new tab must include safe `rel` attributes. Disabled links should not navigate.

## Motion

The Kitchen Sink prototype uses `motion.a` and reduced-motion handling for arrow nudges. The website repo already includes `motion`, so the atom may keep a small reduced-motion-aware icon nudge on hover/focus.

Do not add a new shared motion utility unless one already exists and clearly fits. If no reusable utility exists, keep the motion behavior local to the Link component to keep the ticket self-contained.

## Storybook Coverage

Add Storybook coverage consistent with other atoms. Stories should demonstrate:

- Default inline link.
- All variants.
- Supported sizes.
- Leading and trailing icons.
- Active state.
- Disabled state.
- External link behavior.
- Inverse variant on a dark background.

## Verification

Implementation verification should include `pnpm lint` if usable in the repo.

If practical, run `pnpm build:storybook` or another Storybook check. If a full Storybook build is too expensive or blocked, manually verify that the story compiles structurally and documents the requested states.

Manual/static review should confirm:

- Internal links use `next/link`.
- External links use safe target and rel behavior when opened in a new tab.
- Disabled links do not navigate.
- Focus-visible classes are present.
- The component can be consumed later by navigation without duplicating styling or external-link behavior.

## Approved Approach

Use the recommended Next-aware Link atom approach. This satisfies the ticket by creating the shared primitive and documentation while avoiding broader consumer migrations in this change.
