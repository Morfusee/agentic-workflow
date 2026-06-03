# Button Atom Redesign Design

## Context

ClickUp ticket `86d36z2nm` asks for a redesigned reusable Button atom for Navbar, Hero, search submit, and future redesign components. The existing production CMS-compatible Button block lives in `src/blocks/Button/Button.component.tsx`. There is also a deprecated UI button at `src/components/ui/button.tsx`.

This ticket will introduce the new atom under `src/components/Button` and expose it in Storybook for visual review. It will not integrate the atom into production components yet.

## Goals

- Add a new isolated Button atom at `src/components/Button/Button.component.tsx`.
- Add Storybook coverage at `src/components/Button/Button.stories.tsx` under `Atoms/Button`.
- Keep the existing CMS Button block, Payload schema, and production usages unchanged.
- Make the atom backwards compatible with existing CMS-shaped button props so later integration can be additive.
- Support primary, secondary, outline, quiet/text, ghost/icon, inverse, full-width, disabled, loading, and link examples in Storybook.

## Non-Goals

- Do not replace or rewrite `src/blocks/Button/Button.component.tsx` in this ticket.
- Do not add, remove, or rename Payload CMS fields.
- Do not migrate Navbar, Hero, search, or other production usage yet.
- Do not add the prototype's motion dependency or completion animation system.
- Do not modify unrelated design tokens or global styling.

## Component Location

The new atom will live at:

```txt
src/components/Button/Button.component.tsx
src/components/Button/Button.stories.tsx
```

No barrel export is required for this ticket. Storybook should import the atom directly from the component file.

## Public API

The atom should accept redesign-friendly props and CMS-compatible props:

```ts
type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'quiet' | 'ghost' | 'inverse'
type LegacyButtonVariant = 'default' | 'outlined' | 'text' | 'icon'
type ButtonColor = 'primary' | 'secondary' | 'black' | 'white'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant | LegacyButtonVariant
  color?: ButtonColor
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  fullHeight?: boolean
  disabled?: boolean
  isLoading?: boolean
  leadingIcon?: React.ReactNode
  trailingIcon?: React.ReactNode
  link?: string
  newTab?: boolean
  buttonId?: string
  text?: string
  ariaLabel?: string
  children?: React.ReactNode
}
```

If both `children` and `text` are present, `children` wins. `buttonId` maps to the rendered interactive element `id`.

## Compatibility Mapping

Legacy values should normalize before styling:

```txt
default -> primary
outlined -> outline
text -> quiet
icon -> ghost
```

The current CMS `color` prop remains accepted:

```txt
color="primary" with default/primary behavior -> primary treatment
color="secondary" with default/primary behavior -> secondary treatment
color="black" with default/primary behavior -> ghost treatment with ink text
color="white" with outlined/text behavior -> inverse treatment
```

New code should prefer the redesigned `variant` names. Compatibility mapping exists so the atom can later receive existing CMS-shaped props without schema changes.

## Rendering Behavior

The atom renders a button when `link` is absent. It renders a link path when `link` is present:

- Internal links use `next/link`.
- External links use `<a>`.
- Existing link utilities, including `sanitizeLink` and the current same-origin query injection behavior, should be reused to preserve current CMS behavior.
- `newTab` sets `target="_blank"` and safe `rel="noopener noreferrer"` for anchors.

Disabled and loading states should prevent interaction. Loading should also set `aria-busy` and preserve the button's general dimensions.

## Styling

Use existing repo color tokens and Tailwind color names instead of hard-coded ad hoc values:

```txt
primary: brand red background, white text
secondary: brand blue background, white text
outline: brand red border and text
quiet: transparent background, brand red text, subtle hover treatment
ghost: minimal icon/text treatment using ink
inverse: white border/text for dark or image backgrounds
```

The component should keep touch-friendly sizing. Recommended sizes:

```txt
sm: minimum 44px target, compact horizontal padding
md: minimum 44px target, default padding
lg: minimum 52px target, larger padding
```

Focus styles should use the existing blue/focus token direction from the redesign work and remain visible on all variants.

## Accessibility

- The interactive element should receive `aria-label` from `ariaLabel`.
- Icon-only Storybook examples must demonstrate `ariaLabel` usage.
- Loading state should set `aria-busy="true"`.
- Disabled button rendering should use the native `disabled` attribute.
- Link rendering should use `aria-disabled` when disabled or loading, and block click behavior.

## Storybook Coverage

Storybook should add a new `Atoms/Button` entry with examples for:

- Default primary
- Secondary
- Outline
- Quiet/text
- Ghost/icon
- Inverse
- Full-width
- Disabled
- Loading
- Internal link
- External link/new tab

The existing `Layout/Button` stories for the CMS block remain unchanged.

## Verification

Implementation should be verified with:

```txt
pnpm build:storybook
pnpm lint
```

If lint is unavailable or blocked by existing repo configuration, note the blocker instead of changing unrelated files.

## Expected File Changes

The implementation should be limited to:

```txt
src/components/Button/Button.component.tsx
src/components/Button/Button.stories.tsx
```

Only add an adjacent export or small Storybook adjustment if the implementation requires it.
