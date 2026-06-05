# Input and SearchBar Component Design

Date: 2026-06-05
Ticket: ClickUp `86d36z2p1` - Implement Input and SearchBar molecule
Target repo: `C:\Users\mrqvp\Documents\Programming\website`

## Context

The current `website` repo already has Storybook configured through `.storybook/main.ts`, with stories discovered from `../src/**/*.stories.@(js|jsx|mjs|ts|tsx)`. Existing component examples include `src/components/Button/Button.component.tsx`, `src/components/Button/Button.stories.tsx`, `src/components/Textarea/Textarea.tsx`, and `src/components/Textarea/Textarea.stories.tsx`.

The ClickUp ticket asks for an additive reusable `Input` atom and `SearchBar` molecule. The user clarified that implementation belongs in the current `website` repo, not `website3.0-prototype`. The prototype `SearchBar.tsx` remains a behavioral reference, and the current repo's `Textarea` is the visual/API reference for the new single-line input.

## Goals

- Add a reusable single-line `Input` atom that looks and behaves like the existing `Textarea`, but renders an HTML `<input>`.
- Add a reusable `SearchBar` molecule composed from the new `Input` and existing `Button` atom.
- Support keyboard Enter submission and button submission.
- Support controlled and uncontrolled usage for `SearchBar`.
- Document default, compact/mobile, submit button, focused, disabled, error, controlled, and uncontrolled states in Storybook.
- Keep implementation additive and avoid CMS/schema/production block rewrites.

## Non-Goals

- No CMS integration or Payload schema work.
- No migration of existing Navbar, Hero, or other production blocks in this ticket.
- No Storybook setup changes, because Storybook already exists.
- No `IconButton` dependency. The user confirmed only `Button` is needed for this SearchBar based on the Kitchen Sink patterns.

## Component Structure

Create these files:

```text
src/components/Input/Input.tsx
src/components/Input/Input.stories.tsx
src/components/SearchBar/SearchBar.tsx
src/components/SearchBar/SearchBar.stories.tsx
```

Optionally update `src/components/index.ts` only if the project expects these components to be exported from the shared component barrel. This should be done as an additive export only.

## Input Atom Design

`Input` will be a client component with a typed props interface extending native input attributes while omitting incompatible or unnecessary props if needed.

Required custom props:

```ts
interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string
  helperText?: string
  error?: string
  wrapperClassName?: string
  onSubmit?: (value: string, event: React.KeyboardEvent<HTMLInputElement>) => void
}
```

Native input props cover `name`, `value`, `defaultValue`, `placeholder`, `disabled`, `autoFocus`, `onChange`, `required`, and standard accessibility attributes.

Behavior:

- Render an HTML `<input>`, not a `<textarea>`.
- Generate an id with `useId()` when no id is supplied.
- Render `Label`, `HelperText`, and `ErrorMessage` from `src/components/Textarea/FormAtoms.tsx` to match the existing Textarea form UI.
- Set `aria-invalid` when `error` is present.
- Set `aria-describedby` to helper and/or error ids when those messages are rendered.
- If `onSubmit` is provided, pressing Enter while the input is focused calls `onSubmit(e.currentTarget.value, e)`.
- Do not add multiline behavior such as rows, resize, auto-grow, or character counter.

Styling should mirror `Textarea` as closely as possible:

```text
w-full rounded-md border border-line bg-canvas px-3.5 py-2.5 text-sm text-ink
placeholder-gray-400 transition-all focus:outline-none focus:ring-2
focus:ring-brand-blue focus:border-transparent disabled:cursor-not-allowed
disabled:opacity-50
```

Error styling uses `border-brand-red focus:ring-brand-red`.

## SearchBar Molecule Design

`SearchBar` will compose `Input` and `Button`. It should use the prototype SearchBar behavior as a reference while using current repo components and tokens.

Props:

```ts
interface SearchBarProps {
  value?: string
  defaultValue?: string
  placeholder?: string
  submitLabel?: string
  buttonText?: string
  compact?: boolean
  showIcon?: boolean
  autoFocus?: boolean
  disabled?: boolean
  error?: string
  helperText?: string
  className?: string
  inputClassName?: string
  buttonClassName?: string
  name?: string
  onChange?: React.ChangeEventHandler<HTMLInputElement>
  onSubmit?: (value: string) => void
  onSearch?: (value: string) => void
}
```

Behavior:

- If `value` is provided, the component is controlled and uses `value` as the displayed query.
- If `value` is not provided, initialize internal query from `defaultValue` and update it on typing.
- Call `onChange` whenever the input changes.
- Submit on Enter inside the input.
- Submit on button click.
- Submit the raw current value; consumers decide whether to trim, validate, or preserve whitespace.
- Use `onSubmit` when provided. If only `onSearch` is provided, use it as a compatibility alias.
- Disable both the input and submit button when `disabled` is true.
- Pass `error` and `helperText` to `Input`.
- Default `showIcon` to true.
- Use `Search` from `lucide-react` as a decorative icon inside the input area when `showIcon` is true.
- Do not introduce an `IconButton` dependency.

Layout:

- Default layout is a full-width horizontal row with a flexible input and trailing submit button.
- Compact mode tightens spacing and sizing for navbar overlay and mobile drawer contexts while preserving accessible 44px touch targets through the existing `Button` size behavior.
- If `submitLabel` is omitted, use `buttonText` if supplied, otherwise default to `Search`.

## Storybook Design

No Storybook config changes are needed. The new story files will be auto-discovered.

`Input.stories.tsx` stories:

- `Default`
- `WithHelperText`
- `Focused`
- `Disabled`
- `ErrorState`
- `Controlled`

`SearchBar.stories.tsx` stories:

- `Default`
- `CompactMobile`
- `WithSubmitButton`
- `Focused`
- `Disabled`
- `ErrorState`
- `Controlled`
- `Uncontrolled`
- `NoIcon`

Controlled stories should follow the existing `Textarea.stories.tsx` pattern by using a `render` function with local `useState` and showing the current value or submitted query below the component.

## Error Handling And Accessibility

- `Input` associates label, helper text, and error text using generated ids.
- `Input` sets `aria-invalid` only when error text is present.
- Search icon is decorative and should be `aria-hidden`.
- Search button text remains visible unless a future design explicitly asks for icon-only search.
- `Button` should use `type="button"` to avoid accidental parent form submission side effects.
- Disabled state prevents both keyboard and button submission.

## Verification

Run these checks when implementation is complete:

```text
pnpm build:storybook
pnpm build
```

If a check fails because of unrelated existing project issues, capture the error and confirm whether the new `Input` and `SearchBar` files are implicated.

## Scope Guardrails

- Additive files only, except for an optional additive component barrel export.
- Do not modify CMS schemas, Payload collections, existing blocks, or production Navbar/Hero code in this ticket.
- Do not refactor `Textarea`, `Button`, or global Storybook setup.
- Preserve existing repo state and avoid unrelated formatting churn.
