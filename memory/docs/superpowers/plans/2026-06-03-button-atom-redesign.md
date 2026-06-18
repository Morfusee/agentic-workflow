# Button Atom Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an isolated, backwards-compatible redesigned Button atom under `src/components/Button` and expose it in Storybook without integrating it into production usage.

**Architecture:** The new atom is a standalone client component that normalizes legacy CMS-shaped props into redesigned variants before rendering. It owns link rendering, disabled/loading behavior, icons, sizing, and styles; Storybook imports it directly so the existing CMS block stays untouched.

**Tech Stack:** Next.js, React 19, TypeScript, Tailwind CSS, class-variance-authority, Storybook, existing `sanitizeLink` and `injectQueries` utilities.

---

## File Structure

- Create: `src/components/Button/Button.component.tsx`
- Create: `src/components/Button/Button.stories.tsx`
- Do not modify: `src/blocks/Button/Button.component.tsx`
- Do not modify: `src/blocks/Button/Button.block.ts`
- Do not modify: `src/components/ui/button.tsx`
- Do not modify: Payload generated files

`Button.component.tsx` is responsible for the atom API, compatibility normalization, styling variants, loading state, icons, and link/button rendering.

`Button.stories.tsx` is responsible for isolated visual review under `Atoms/Button` and must not import from `src/blocks/components`.

## Pre-Flight

- [ ] **Step 1: Confirm the website worktree state**

Run from `$HOME\Documents\Programming\website`:

```bash
git status --short
```

Expected: existing user-owned generated Payload changes may still appear:

```txt
 M src/app/(payload)/admin/importMap.js
 M src/payload-types.ts
```

Do not stage, modify, or revert those files while implementing this plan.

- [ ] **Step 2: Confirm the current diff before editing**

Run:

```bash
git diff
```

Expected: only the pre-existing Payload generated diff is present. If other files are modified, preserve them unless they directly conflict with creating `src/components/Button`.

---

### Task 1: Create The Isolated Button Atom

**Files:**
- Create: `src/components/Button/Button.component.tsx`

- [ ] **Step 1: Add the Button component file**

Create `src/components/Button/Button.component.tsx` with this content:

```tsx
'use client'

import { cn } from '@/lib/utils'
import { injectQueries, sanitizeLink } from '@/utilities/link'
import { cva, type VariantProps } from 'class-variance-authority'
import Link from 'next/link'
import * as React from 'react'

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'quiet' | 'ghost' | 'inverse'
type LegacyButtonVariant = 'default' | 'outlined' | 'text' | 'icon'
type ButtonColor = 'primary' | 'secondary' | 'black' | 'white'

const buttonVariants = cva(
  [
    'relative inline-flex shrink-0 items-center justify-center gap-2 overflow-hidden rounded-md',
    'font-bold uppercase tracking-wide transition-[background-color,border-color,color,box-shadow,opacity]',
    'focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-blue',
    'disabled:pointer-events-none disabled:opacity-55',
    '[&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=size-])]:size-4',
  ].join(' '),
  {
    variants: {
      variant: {
        primary: 'bg-brand-red text-white hover:bg-brand-red/90',
        secondary: 'bg-brand-blue text-white hover:bg-brand-blue/90',
        outline: 'border-2 border-brand-red bg-transparent text-brand-red hover:bg-brand-red/10',
        quiet: 'bg-transparent text-brand-red hover:bg-brand-red/10',
        ghost: 'bg-transparent text-ink hover:bg-ink/10',
        inverse: 'border-2 border-white bg-transparent text-white hover:bg-white/10',
      },
      size: {
        sm: 'min-h-11 min-w-11 px-3 py-1.5 text-sm',
        md: 'min-h-11 min-w-11 px-4 py-2 text-base',
        lg: 'min-h-[52px] min-w-[52px] px-6 py-3 text-lg',
      },
      fullWidth: {
        true: 'w-full',
      },
      fullHeight: {
        true: 'h-full',
      },
      iconOnly: {
        true: 'aspect-square px-0',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  },
)

export interface ButtonProps
  extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'color' | 'onClick'>,
    Omit<VariantProps<typeof buttonVariants>, 'variant'> {
  variant?: ButtonVariant | LegacyButtonVariant
  color?: ButtonColor
  isLoading?: boolean
  leadingIcon?: React.ReactNode
  trailingIcon?: React.ReactNode
  link?: string
  newTab?: boolean
  buttonId?: string
  text?: string
  ariaLabel?: string
  onClick?: React.MouseEventHandler<HTMLElement>
}

const normalizeVariant = (variant?: ButtonProps['variant'], color?: ButtonColor): ButtonVariant => {
  if (variant === 'secondary') return 'secondary'
  if (variant === 'outline' || variant === 'outlined') return color === 'white' ? 'inverse' : 'outline'
  if (variant === 'quiet' || variant === 'text') return color === 'white' ? 'inverse' : 'quiet'
  if (variant === 'ghost' || variant === 'icon') return 'ghost'
  if (variant === 'inverse') return 'inverse'

  if (color === 'secondary') return 'secondary'
  if (color === 'black') return 'ghost'
  if (color === 'white') return 'inverse'

  return 'primary'
}

const isExternalLink = (href: string) => /^https?:\/\//i.test(href)

export const Button: React.FC<ButtonProps> = ({
  variant,
  color,
  size = 'md',
  fullWidth,
  fullHeight,
  isLoading = false,
  leadingIcon,
  trailingIcon,
  link,
  newTab,
  buttonId,
  text,
  ariaLabel,
  children,
  className,
  disabled,
  onClick,
  type = 'button',
  ...buttonProps
}) => {
    const normalizedVariant = normalizeVariant(variant, color)
    const content = children ?? text
    const iconOnly = !content && Boolean(leadingIcon || trailingIcon)
    const isDisabled = disabled || isLoading

    const buttonClassName = cn(
      buttonVariants({
        variant: normalizedVariant,
        size,
        fullWidth,
        fullHeight,
        iconOnly,
      }),
      className,
    )

    const innerContent = (
      <>
        {isLoading ? (
          <span
            aria-hidden="true"
            className="size-4 animate-spin rounded-full border-2 border-current border-r-transparent"
          />
        ) : null}
        {!isLoading && leadingIcon ? (
          <span aria-hidden="true" className="inline-flex shrink-0">
            {leadingIcon}
          </span>
        ) : null}
        {content ? <span>{content}</span> : null}
        {!isLoading && trailingIcon ? (
          <span aria-hidden="true" className="inline-flex shrink-0">
            {trailingIcon}
          </span>
        ) : null}
      </>
    )

    const handleClick: React.MouseEventHandler<HTMLElement> = (event) => {
      if (isDisabled) {
        event.preventDefault()
        return
      }

      onClick?.(event)
    }

    if (!link) {
      return (
        <button
          {...buttonProps}
          id={buttonId}
          type={type}
          className={buttonClassName}
          disabled={isDisabled}
          aria-busy={isLoading || undefined}
          aria-label={ariaLabel}
          onClick={handleClick}
        >
          {innerContent}
        </button>
      )
    }

    const sanitized = sanitizeLink(link)
    const baseUrl =
      typeof window !== 'undefined' ? window.location.origin : process.env.NEXT_PUBLIC_BASE_URL || ''
    const href = sanitized.startsWith(baseUrl) ? injectQueries(sanitized) : sanitized
    const target = newTab ? '_blank' : undefined
    const rel = newTab ? 'noopener noreferrer' : undefined
    const linkClassName = cn(fullWidth && 'w-full', fullHeight && 'h-full')

    if (isExternalLink(href)) {
      return (
        <a
          id={buttonId}
          href={isDisabled ? undefined : href}
          target={target}
          rel={rel}
          className={cn(linkClassName, buttonClassName, isDisabled && 'pointer-events-none opacity-55')}
          aria-disabled={isDisabled || undefined}
          aria-busy={isLoading || undefined}
          aria-label={ariaLabel}
          onClick={handleClick}
        >
          {innerContent}
        </a>
      )
    }

    return (
      <Link
        href={href}
        target={target}
        rel={rel}
        className={cn(linkClassName, buttonClassName, isDisabled && 'pointer-events-none opacity-55')}
        prefetch={process.env.NEXT_PUBLIC_BUILD_MODE !== 'static'}
        aria-disabled={isDisabled || undefined}
        aria-busy={isLoading || undefined}
        aria-label={ariaLabel}
        id={buttonId}
        onClick={handleClick}
      >
        {innerContent}
      </Link>
    )
}

Button.displayName = 'Button'
```

- [ ] **Step 2: Confirm the component file exists**

Run:

```bash
git status --short src/components/Button/Button.component.tsx
```

Expected:

```txt
?? src/components/Button/Button.component.tsx
```

- [ ] **Step 3: Commit the isolated atom**

Run:

```bash
git add -- src/components/Button/Button.component.tsx
git commit -m "feat(button): add redesigned button atom"
```

Expected: a commit containing only `src/components/Button/Button.component.tsx`.

---

### Task 2: Add Storybook Coverage

**Files:**
- Create: `src/components/Button/Button.stories.tsx`

- [ ] **Step 1: Add the Storybook file**

Create `src/components/Button/Button.stories.tsx` with this content:

```tsx
import type { Meta, StoryObj } from '@storybook/react'
import { ArrowRight, Search } from 'lucide-react'

import { Button } from './Button.component'

const meta = {
  title: 'Atoms/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'outline', 'quiet', 'ghost', 'inverse', 'default', 'outlined', 'text', 'icon'],
    },
    color: {
      control: 'select',
      options: ['primary', 'secondary', 'black', 'white'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
  },
  args: {
    children: 'Apply Now',
  },
} satisfies Meta<typeof Button>

export default meta

type Story = StoryObj<typeof meta>

export const Default: Story = {}

export const Variants: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-3">
      <Button>Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="quiet">Quiet</Button>
      <Button variant="ghost">Ghost</Button>
      <div className="bg-brand-blue p-4">
        <Button variant="inverse">Inverse</Button>
      </div>
    </div>
  ),
}

export const Sizes: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-3">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
}

export const WithIcons: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-3">
      <Button trailingIcon={<ArrowRight />}>Learn More</Button>
      <Button variant="secondary" leadingIcon={<Search />}>
        Search
      </Button>
      <Button variant="ghost" ariaLabel="Search">
        <Search />
      </Button>
    </div>
  ),
}

export const FullWidth: Story = {
  parameters: {
    layout: 'padded',
  },
  render: () => (
    <div className="w-full max-w-md">
      <Button fullWidth>Mobile Drawer CTA</Button>
    </div>
  ),
}

export const DisabledAndLoading: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-3">
      <Button disabled>Disabled</Button>
      <Button isLoading>Submitting</Button>
      <Button variant="secondary" isLoading>
        Loading
      </Button>
    </div>
  ),
}

export const Links: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-3">
      <Button link="/search" variant="quiet" trailingIcon={<ArrowRight />}>
        Internal Link
      </Button>
      <Button link="https://www.mmdc.mcl.edu.ph" newTab variant="secondary">
        External Link
      </Button>
    </div>
  ),
}

export const LegacyCompatibility: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-3">
      <Button variant="default" color="secondary">
        CMS Secondary
      </Button>
      <Button variant="outlined" color="primary">
        CMS Outlined
      </Button>
      <Button variant="text" color="secondary">
        CMS Text
      </Button>
      <div className="bg-brand-blue p-4">
        <Button variant="outlined" color="white">
          CMS White
        </Button>
      </div>
    </div>
  ),
}
```

- [ ] **Step 2: Confirm Storybook discovers the story file**

Run:

```bash
git status --short src/components/Button/Button.stories.tsx
```

Expected:

```txt
?? src/components/Button/Button.stories.tsx
```

- [ ] **Step 3: Commit the Storybook coverage**

Run:

```bash
git add -- src/components/Button/Button.stories.tsx
git commit -m "test(button): add atom storybook examples"
```

Expected: a commit containing only `src/components/Button/Button.stories.tsx`.

---

### Task 3: Verify Storybook And Type Safety

**Files:**
- Verify: `src/components/Button/Button.component.tsx`
- Verify: `src/components/Button/Button.stories.tsx`

- [ ] **Step 1: Build Storybook**

Run:

```bash
pnpm build:storybook
```

Expected: Storybook builds successfully and includes `Atoms/Button`.

If the command fails because the new Button code has TypeScript or JSX errors, fix only `src/components/Button/Button.component.tsx` or `src/components/Button/Button.stories.tsx`.

- [ ] **Step 2: Run lint**

Run:

```bash
pnpm lint
```

Expected: lint completes successfully.

If lint fails because `next lint` is unavailable in this Next.js version or because of pre-existing unrelated lint issues, record the exact failure in the final implementation summary and do not modify unrelated files.

- [ ] **Step 3: Inspect the final diff**

Run:

```bash
git diff HEAD~2..HEAD -- src/components/Button/Button.component.tsx src/components/Button/Button.stories.tsx
```

Expected: the diff includes only the new atom and its Storybook examples.

- [ ] **Step 4: Confirm production files were not touched**

Run:

```bash
git diff -- src/blocks/Button/Button.component.tsx src/blocks/Button/Button.block.ts src/components/ui/button.tsx
```

Expected: no output.

- [ ] **Step 5: Commit verification fixes if needed**

If Steps 1 or 2 required fixes, run:

```bash
git add -- src/components/Button/Button.component.tsx src/components/Button/Button.stories.tsx
git commit -m "fix(button): resolve atom storybook verification issues"
```

Expected: a small commit containing only verification fixes for the new atom or story.

If no fixes were needed, do not create a commit for this step.

---

## Final Review Checklist

- [ ] `src/components/Button/Button.component.tsx` exists.
- [ ] `src/components/Button/Button.stories.tsx` exists.
- [ ] Storybook title is `Atoms/Button`.
- [ ] Existing `Layout/Button` stories are unchanged.
- [ ] Existing CMS block files are unchanged.
- [ ] New atom accepts `link`, `newTab`, `buttonId`, `text`, `variant`, `color`, `fullWidth`, `fullHeight`, `disabled`, `isLoading`, `leadingIcon`, `trailingIcon`, and `ariaLabel`.
- [ ] Legacy variants normalize as `default -> primary`, `outlined -> outline`, `text -> quiet`, and `icon -> ghost`.
- [ ] Link rendering preserves current `sanitizeLink` and query injection behavior.
- [ ] `pnpm build:storybook` result is recorded.
- [ ] `pnpm lint` result is recorded.
- [ ] Pre-existing generated Payload changes remain preserved and unstaged unless the user separately requests otherwise.

## Self-Review Notes

- Spec coverage: the plan covers isolated atom creation, CMS-compatible props, no production integration, Storybook examples, link behavior, disabled/loading states, color-token styling, and verification.
- Placeholder scan: the plan contains no placeholder sections and no undefined implementation steps.
- Type consistency: the prop names in the component code match the Storybook examples and the approved design spec.
