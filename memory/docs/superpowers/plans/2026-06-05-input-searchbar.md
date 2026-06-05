# Input SearchBar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reusable single-line `Input` atom and `SearchBar` molecule with Storybook coverage for ClickUp ticket `86d36z2p1`.

**Architecture:** Additive component work in `C:\Users\mrqvp\Documents\Programming\website` on branch `feat/86d36z2p1`. `Input` mirrors the existing `Textarea` atom's form structure and styling while rendering an HTML `<input>`. `SearchBar` composes `Input` and the existing `Button` atom, manages controlled/uncontrolled query state, and submits through Enter or button click.

**Tech Stack:** Next.js 16, React 19, TypeScript, Tailwind CSS tokens, Storybook 9, lucide-react, existing `cn` utility, existing `Button` and `Textarea/FormAtoms` components.

---

## File Structure

- Create `src/components/Input/Input.tsx`: single-line form atom with label, helper text, error text, native input props, Enter submit support, and Textarea-matched styling.
- Create `src/components/Input/Input.stories.tsx`: Storybook atom examples for default, helper text, focused, disabled, error, and controlled usage.
- Create `src/components/SearchBar/SearchBar.tsx`: search molecule composed from `Input`, existing `Button`, and decorative lucide `Search` icon.
- Create `src/components/SearchBar/SearchBar.stories.tsx`: Storybook molecule examples for default, compact/mobile, submit button, focused, disabled, error, controlled, uncontrolled, and no-icon states.
- Modify `src/components/index.ts`: add named default exports for `Input` and `SearchBar` so the new components are available through the existing component barrel.

## Preconditions

- Worktree: `C:\Users\mrqvp\Documents\Programming\website`
- Branch: `feat/86d36z2p1`
- Starting state: `git status` should report a clean working tree.
- Do not edit CMS schemas, Payload collections, existing blocks, global Storybook config, `Textarea`, or `Button`.

### Task 1: Create Input Atom

**Files:**
- Create: `src/components/Input/Input.tsx`

- [ ] **Step 1: Confirm branch and clean state**

Run:

```bash
git status
```

Expected:

```text
On branch feat/86d36z2p1
nothing to commit, working tree clean
```

- [ ] **Step 2: Create `src/components/Input/Input.tsx`**

Create the file with this exact implementation:

```tsx
'use client'

import { useId } from 'react'
import { cn } from '@/lib/utils'
import { Label, HelperText, ErrorMessage } from '../Textarea/FormAtoms'

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string
  helperText?: string
  error?: string
  wrapperClassName?: string
  onSubmit?: (value: string, event: React.KeyboardEvent<HTMLInputElement>) => void
}

export function Input({
  className,
  label,
  helperText,
  error,
  disabled,
  id: externalId,
  wrapperClassName,
  required,
  onKeyDown,
  onSubmit,
  ...props
}: InputProps) {
  const generatedId = useId()
  const id = externalId || generatedId
  const describedBy = [error ? `${id}-error` : null, helperText ? `${id}-helper` : null]
    .filter(Boolean)
    .join(' ')

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    onKeyDown?.(event)

    if (event.defaultPrevented || event.key !== 'Enter') return

    onSubmit?.(event.currentTarget.value, event)
  }

  return (
    <div className={cn('w-full flex flex-col gap-1.5', wrapperClassName)}>
      {label && (
        <Label htmlFor={id} required={required}>
          {label}
        </Label>
      )}

      <input
        id={id}
        className={cn(
          'w-full rounded-md border border-line bg-canvas px-3.5 py-2.5 text-sm text-ink placeholder-gray-400 transition-all focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50',
          error && 'border-brand-red focus:ring-brand-red',
          className,
        )}
        disabled={disabled}
        required={required}
        aria-invalid={!!error}
        aria-describedby={describedBy || undefined}
        onKeyDown={handleKeyDown}
        {...props}
      />

      {helperText && !error && <HelperText id={`${id}-helper`}>{helperText}</HelperText>}

      {error && <ErrorMessage id={`${id}-error`}>{error}</ErrorMessage>}
    </div>
  )
}

export default Input
```

- [ ] **Step 3: Run TypeScript/build check for Input syntax**

Run:

```bash
pnpm build:storybook
```

Expected:

```text
Storybook build completes successfully.
```

If it fails, inspect whether the error references `src/components/Input/Input.tsx`. Fix only errors caused by this new file.

- [ ] **Step 4: Commit Input atom**

Run:

```bash
git add src/components/Input/Input.tsx
git commit -m "feat: add input atom"
```

Expected:

```text
[feat/86d36z2p1 <hash>] feat: add input atom
```

### Task 2: Add Input Storybook Stories

**Files:**
- Create: `src/components/Input/Input.stories.tsx`

- [ ] **Step 1: Create `src/components/Input/Input.stories.tsx`**

Create the file with this exact implementation:

```tsx
import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { Input } from './Input'

const meta: Meta<typeof Input> = {
  title: 'Atoms/Input',
  component: Input,
  args: {
    label: 'Search query',
    placeholder: 'Type a search term...',
  },
  argTypes: {
    disabled: { control: 'boolean' },
    required: { control: 'boolean' },
    error: { control: 'text' },
    helperText: { control: 'text' },
    placeholder: { control: 'text' },
  },
}

export default meta

type Story = StoryObj<typeof Input>

export const Default: Story = {}

export const WithHelperText: Story = {
  args: {
    label: 'Program search',
    helperText: 'Search by course, program, scholarship, or admissions topic.',
    placeholder: 'Search programs...',
  },
}

export const Focused: Story = {
  args: {
    label: 'Focused input',
    placeholder: 'This input receives focus on load...',
    autoFocus: true,
  },
}

export const Disabled: Story = {
  args: {
    label: 'Disabled input',
    defaultValue: 'Search is unavailable',
    disabled: true,
  },
}

export const ErrorState: Story = {
  args: {
    label: 'Search query',
    placeholder: 'Enter a query...',
    error: 'Please enter a search term.',
  },
}

export const Controlled: Story = {
  render: (args: React.ComponentProps<typeof Input>) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [value, setValue] = useState('Scholarships')

    return (
      <div className="w-full max-w-md space-y-2">
        <Input
          {...args}
          value={value}
          onChange={(event: React.ChangeEvent<HTMLInputElement>) => setValue(event.target.value)}
        />
        <p className="text-xs text-gray-500">
          Controlled value: <code className="bg-gray-100 px-1 rounded">{value}</code>
        </p>
      </div>
    )
  },
  args: {
    label: 'Controlled input',
    placeholder: 'Controlled...',
  },
}
```

- [ ] **Step 2: Build Storybook to verify Input stories**

Run:

```bash
pnpm build:storybook
```

Expected:

```text
Storybook build completes successfully and includes the Atoms/Input stories.
```

If it fails, inspect whether the error references `src/components/Input/Input.stories.tsx` or `src/components/Input/Input.tsx`. Fix only errors caused by this task.

- [ ] **Step 3: Commit Input stories**

Run:

```bash
git add src/components/Input/Input.stories.tsx
git commit -m "docs: add input stories"
```

Expected:

```text
[feat/86d36z2p1 <hash>] docs: add input stories
```

### Task 3: Create SearchBar Molecule

**Files:**
- Create: `src/components/SearchBar/SearchBar.tsx`

- [ ] **Step 1: Create `src/components/SearchBar/SearchBar.tsx`**

Create the file with this exact implementation:

```tsx
'use client'

import { useState } from 'react'
import { Search } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '../Button/Button.component'
import { Input } from '../Input/Input'

export interface SearchBarProps {
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

export function SearchBar({
  value,
  defaultValue = '',
  placeholder = 'Search...',
  submitLabel,
  buttonText,
  compact = false,
  showIcon = true,
  autoFocus,
  disabled,
  error,
  helperText,
  className,
  inputClassName,
  buttonClassName,
  name,
  onChange,
  onSubmit,
  onSearch,
}: SearchBarProps) {
  const [internalValue, setInternalValue] = useState(defaultValue)
  const isControlled = value !== undefined
  const currentValue = isControlled ? value : internalValue
  const resolvedSubmitLabel = submitLabel ?? buttonText ?? 'Search'

  const submit = (nextValue: string) => {
    if (disabled) return

    if (onSubmit) {
      onSubmit(nextValue)
      return
    }

    onSearch?.(nextValue)
  }

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!isControlled) {
      setInternalValue(event.target.value)
    }

    onChange?.(event)
  }

  return (
    <div className={cn('flex w-full items-start gap-2', compact && 'gap-1.5', className)}>
      <div className="relative min-w-0 flex-1">
        {showIcon && (
          <Search
            aria-hidden="true"
            className={cn(
              'pointer-events-none absolute left-3.5 top-1/2 z-10 h-4 w-4 -translate-y-1/2 text-muted-foreground',
              compact && 'left-3 h-3.5 w-3.5',
            )}
          />
        )}

        <Input
          name={name}
          value={currentValue}
          placeholder={placeholder}
          disabled={disabled}
          autoFocus={autoFocus}
          error={error}
          helperText={helperText}
          onChange={handleChange}
          onSubmit={submit}
          wrapperClassName="gap-1"
          className={cn(showIcon && 'pl-10', compact && 'py-2 text-sm', inputClassName)}
        />
      </div>

      <Button
        type="button"
        size={compact ? 'sm' : 'md'}
        disabled={disabled}
        onClick={() => submit(currentValue)}
        className={cn('shrink-0', buttonClassName)}
      >
        {resolvedSubmitLabel}
      </Button>
    </div>
  )
}

export default SearchBar
```

- [ ] **Step 2: Build Storybook to verify SearchBar syntax**

Run:

```bash
pnpm build:storybook
```

Expected:

```text
Storybook build completes successfully.
```

If it fails, inspect whether the error references `src/components/SearchBar/SearchBar.tsx`, `src/components/Input/Input.tsx`, or `src/components/Button/Button.component.tsx`. Fix only errors caused by this task.

- [ ] **Step 3: Commit SearchBar molecule**

Run:

```bash
git add src/components/SearchBar/SearchBar.tsx
git commit -m "feat: add searchbar molecule"
```

Expected:

```text
[feat/86d36z2p1 <hash>] feat: add searchbar molecule
```

### Task 4: Add SearchBar Storybook Stories

**Files:**
- Create: `src/components/SearchBar/SearchBar.stories.tsx`

- [ ] **Step 1: Create `src/components/SearchBar/SearchBar.stories.tsx`**

Create the file with this exact implementation:

```tsx
import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { SearchBar } from './SearchBar'

const meta: Meta<typeof SearchBar> = {
  title: 'Molecules/SearchBar',
  component: SearchBar,
  parameters: {
    layout: 'padded',
  },
  args: {
    placeholder: 'Search programs, scholarships, and admissions...',
  },
  argTypes: {
    compact: { control: 'boolean' },
    showIcon: { control: 'boolean' },
    autoFocus: { control: 'boolean' },
    disabled: { control: 'boolean' },
    error: { control: 'text' },
    helperText: { control: 'text' },
    placeholder: { control: 'text' },
    submitLabel: { control: 'text' },
    buttonText: { control: 'text' },
  },
}

export default meta

type Story = StoryObj<typeof SearchBar>

const SubmittedPreview = ({ value }: { value: string }) => (
  <p className="text-xs text-gray-500">
    Submitted query: <code className="bg-gray-100 px-1 rounded">{value || 'None yet'}</code>
  </p>
)

export const Default: Story = {
  render: (args: React.ComponentProps<typeof SearchBar>) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [submitted, setSubmitted] = useState('')

    return (
      <div className="w-full max-w-2xl space-y-2">
        <SearchBar {...args} onSubmit={setSubmitted} />
        <SubmittedPreview value={submitted} />
      </div>
    )
  },
}

export const CompactMobile: Story = {
  render: (args: React.ComponentProps<typeof SearchBar>) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [submitted, setSubmitted] = useState('')

    return (
      <div className="w-full max-w-sm space-y-2 rounded-xl border border-line bg-white p-4">
        <SearchBar {...args} compact onSubmit={setSubmitted} />
        <SubmittedPreview value={submitted} />
      </div>
    )
  },
  args: {
    placeholder: 'Search courses...',
    submitLabel: 'Go',
  },
}

export const WithSubmitButton: Story = {
  render: (args: React.ComponentProps<typeof SearchBar>) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [submitted, setSubmitted] = useState('')

    return (
      <div className="w-full max-w-2xl space-y-2">
        <SearchBar {...args} onSubmit={setSubmitted} />
        <SubmittedPreview value={submitted} />
      </div>
    )
  },
  args: {
    placeholder: 'Enter a domain or keyword...',
    submitLabel: 'Query',
  },
}

export const Focused: Story = {
  args: {
    autoFocus: true,
    placeholder: 'This search input receives focus on load...',
  },
}

export const Disabled: Story = {
  args: {
    defaultValue: 'Search disabled',
    disabled: true,
  },
}

export const ErrorState: Story = {
  args: {
    placeholder: 'Enter a search term...',
    error: 'Please enter a search term before submitting.',
  },
}

export const Controlled: Story = {
  render: (args: React.ComponentProps<typeof SearchBar>) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [value, setValue] = useState('Scholarships')
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [submitted, setSubmitted] = useState('')

    return (
      <div className="w-full max-w-2xl space-y-2">
        <SearchBar
          {...args}
          value={value}
          onChange={(event: React.ChangeEvent<HTMLInputElement>) => setValue(event.target.value)}
          onSubmit={setSubmitted}
        />
        <p className="text-xs text-gray-500">
          Controlled value: <code className="bg-gray-100 px-1 rounded">{value}</code>
        </p>
        <SubmittedPreview value={submitted} />
      </div>
    )
  },
}

export const Uncontrolled: Story = {
  render: (args: React.ComponentProps<typeof SearchBar>) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [submitted, setSubmitted] = useState('')

    return (
      <div className="w-full max-w-2xl space-y-2">
        <SearchBar {...args} defaultValue="Admissions" onSubmit={setSubmitted} />
        <SubmittedPreview value={submitted} />
      </div>
    )
  },
}

export const NoIcon: Story = {
  render: (args: React.ComponentProps<typeof SearchBar>) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [submitted, setSubmitted] = useState('')

    return (
      <div className="w-full max-w-2xl space-y-2">
        <SearchBar {...args} showIcon={false} onSubmit={setSubmitted} />
        <SubmittedPreview value={submitted} />
      </div>
    )
  },
}
```

- [ ] **Step 2: Build Storybook to verify SearchBar stories**

Run:

```bash
pnpm build:storybook
```

Expected:

```text
Storybook build completes successfully and includes the Molecules/SearchBar stories.
```

If it fails, inspect whether the error references `src/components/SearchBar/SearchBar.stories.tsx`, `src/components/SearchBar/SearchBar.tsx`, or `src/components/Input/Input.tsx`. Fix only errors caused by this task.

- [ ] **Step 3: Commit SearchBar stories**

Run:

```bash
git add src/components/SearchBar/SearchBar.stories.tsx
git commit -m "docs: add searchbar stories"
```

Expected:

```text
[feat/86d36z2p1 <hash>] docs: add searchbar stories
```

### Task 5: Add Component Barrel Exports

**Files:**
- Modify: `src/components/index.ts`

- [ ] **Step 1: Update `src/components/index.ts`**

Replace the file content with this exact content:

```ts
export { default as Pagination } from './Pagination/Pagination.component'
export { default as Form } from './Form/Form.component'
export { default as BackgroundTexture } from './BackgroundTexture/BackgroundTexture.component'
export { default as CardMolecule } from './CardMolecule/CardMolecule.component'
export { default as Input } from './Input/Input'
export { default as SearchBar } from './SearchBar/SearchBar'
```

- [ ] **Step 2: Build Storybook to verify barrel export does not break imports**

Run:

```bash
pnpm build:storybook
```

Expected:

```text
Storybook build completes successfully.
```

If it fails, inspect whether the error references `src/components/index.ts`. Fix only errors caused by this task.

- [ ] **Step 3: Commit barrel exports**

Run:

```bash
git add src/components/index.ts
git commit -m "chore: export input and searchbar components"
```

Expected:

```text
[feat/86d36z2p1 <hash>] chore: export input and searchbar components
```

### Task 6: Final Verification

**Files:**
- Verify: all files changed by Tasks 1-5

- [ ] **Step 1: Run final Storybook build**

Run:

```bash
pnpm build:storybook
```

Expected:

```text
Storybook build completes successfully.
```

- [ ] **Step 2: Run production build**

Run:

```bash
pnpm build
```

Expected:

```text
Next.js build completes successfully.
```

If this fails because of unrelated existing project issues, capture the full failing command and the specific error. Confirm whether any error references these new or modified files:

```text
src/components/Input/Input.tsx
src/components/Input/Input.stories.tsx
src/components/SearchBar/SearchBar.tsx
src/components/SearchBar/SearchBar.stories.tsx
src/components/index.ts
```

- [ ] **Step 3: Inspect final diff**

Run:

```bash
git diff origin/feat/v3-redesign...HEAD -- src/components/Input src/components/SearchBar src/components/index.ts
```

Expected: diff contains only the new `Input`, new `SearchBar`, their stories, and additive barrel exports.

- [ ] **Step 4: Confirm clean working tree**

Run:

```bash
git status
```

Expected:

```text
On branch feat/86d36z2p1
nothing to commit, working tree clean
```

## Self-Review Checklist

- Spec coverage: Tasks 1 and 2 cover the `Input` atom and Input stories. Tasks 3 and 4 cover `SearchBar`, controlled/uncontrolled behavior, Enter/button submission, compact/no-icon/error/disabled/focused states, and Storybook examples. Task 5 covers additive shared exports. Task 6 covers requested verification.
- Placeholder scan: this plan contains no deferred implementation notes or unresolved placeholders.
- Type consistency: `InputProps`, `SearchBarProps`, callback names, and file names are consistent across implementation and stories.
- Scope check: no CMS schemas, production blocks, Navbar/Hero code, Storybook config, `Textarea`, or `Button` files are modified.
