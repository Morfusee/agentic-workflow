# Badge Atom Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a reusable Badge atom component with 8 variants, 2 sizes, 2 shapes, shimmer/count animations, and Storybook coverage.

**Architecture:** Single `Badge.component.tsx` following the IconButton pattern — `cva` for variant styling, `motion/react` for animations, inlined reduced-motion detection. Exported via barrel at `src/components/index.ts`.

**Tech Stack:** React 19, TypeScript, motion/react v12.40, class-variance-authority v0.7.1, Tailwind CSS v3, Storybook with `@storybook/nextjs-vite`

---

### Task 1: Create Badge component

**Files:**
- Create: `src/components/Badge/Badge.component.tsx`

- [ ] **Step 1: Write the Badge component**

```tsx
'use client'

import { cn } from '@/lib/utils'
import { cva, type VariantProps } from 'class-variance-authority'
import { motion, useAnimation } from 'motion/react'
import { useEffect, useRef, useState } from 'react'

const badgeVariants = cva(
  'relative overflow-hidden inline-flex items-center gap-1 font-semibold whitespace-nowrap transition-colors duration-200',
  {
    variants: {
      variant: {
        success: 'bg-success/15 text-success',
        warning: 'bg-warning/15 text-warning',
        error: 'bg-danger/15 text-danger',
        info: 'bg-info/15 text-info',
        brand: 'bg-brand-blue text-white',
        brandRed: 'bg-brand-red text-white',
        count: 'bg-brand-red text-white',
        new: 'bg-yellow text-ink',
      },
      size: {
        sm: 'h-4 px-1.5 text-[10px]',
        md: 'h-5 px-2 text-xs',
      },
      shape: {
        pill: 'rounded-full',
        rounded: 'rounded-sm',
      },
    },
    defaultVariants: {
      variant: 'brand',
      size: 'md',
      shape: 'pill',
    },
  },
)

export type BadgeVariant = NonNullable<VariantProps<typeof badgeVariants>['variant']>
export type BadgeSize = NonNullable<VariantProps<typeof badgeVariants>['size']>
export type BadgeShape = NonNullable<VariantProps<typeof badgeVariants>['shape']>

export interface BadgeProps
  extends Omit<React.HTMLAttributes<HTMLSpanElement>, 'children'>,
    VariantProps<typeof badgeVariants> {
  children: React.ReactNode
  count?: number
}

const Badge = ({
  className,
  variant,
  size,
  shape,
  count,
  children,
  ...props
}: BadgeProps) => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)
  const controls = useAnimation()
  const prevCount = useRef(count)

  const isNew = variant === 'new'
  const isCount = variant === 'count' || count !== undefined

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const handler = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches)
    }

    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [])

  useEffect(() => {
    if (isNew && !prefersReducedMotion) {
      controls.start({
        x: ['-100%', '200%'],
        transition: { duration: 0.8, ease: 'easeInOut', delay: 0.1 },
      })
    }
  }, [isNew, prefersReducedMotion, controls])

  useEffect(() => {
    if (isCount && count !== undefined && prevCount.current !== count && !prefersReducedMotion) {
      controls.start({
        scale: [1, 1.15, 1],
        transition: { duration: 0.3, ease: [0.34, 1.56, 0.64, 1] },
      })
      prevCount.current = count
    }
  }, [count, isCount, prefersReducedMotion, controls])

  return (
    <motion.span
      className={cn(badgeVariants({ variant, size, shape, className }))}
      initial={isCount && !prefersReducedMotion ? { scale: 0 } : { scale: 1 }}
      animate={isCount && !prefersReducedMotion ? controls : { scale: 1 }}
      transition={{ type: 'spring', stiffness: 400, damping: 20 }}
      {...(props as React.ComponentProps<typeof motion.span>)}
    >
      <span className="flex items-center gap-1 relative z-10 w-full h-full justify-center">
        {children}
      </span>

      {isNew && (
        <motion.div
          animate={controls}
          initial={{ x: '-100%' }}
          className="absolute inset-0 z-20 w-1/2 bg-gradient-to-r from-transparent via-white/50 to-transparent skew-x-12"
        />
      )}
    </motion.span>
  )
}

Badge.displayName = 'Badge'

export default Badge
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `npx tsc --noEmit`
Expected: No errors related to Badge.component.tsx

- [ ] **Step 3: Commit**

```bash
git add src/components/Badge/Badge.component.tsx
git commit -m "feat(Badge): implement Badge atom component"
```

---

### Task 2: Create Badge stories

**Files:**
- Create: `src/components/Badge/Badge.stories.tsx`

- [ ] **Step 1: Write the stories file**

```tsx
import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'

import Badge from './Badge.component'

const meta: Meta<typeof Badge> = {
  title: 'Atoms/Badge',
  component: Badge,
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['success', 'warning', 'error', 'info', 'brand', 'brandRed', 'count', 'new'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md'],
    },
    shape: {
      control: 'select',
      options: ['pill', 'rounded'],
    },
  },
}

export default meta

type Story = StoryObj<typeof Badge>

export const Default: Story = {
  args: {
    children: 'Badge',
    variant: 'info',
  },
}

export const Variants: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-4">
      <Badge variant="brand">Brand</Badge>
      <Badge variant="brandRed">Brand Red</Badge>
      <Badge variant="success">Success</Badge>
      <Badge variant="warning">Warning</Badge>
      <Badge variant="error">Error</Badge>
      <Badge variant="info">Info</Badge>
      <Badge variant="new">NEW</Badge>
      <Badge variant="count">3</Badge>
    </div>
  ),
}

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Badge variant="info" size="sm">Small</Badge>
      <Badge variant="info" size="md">Medium</Badge>
    </div>
  ),
}

export const Shapes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Badge variant="info" shape="pill">Pill</Badge>
      <Badge variant="info" shape="rounded">Rounded</Badge>
    </div>
  ),
}

export const Shimmer: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Badge variant="new">NEW</Badge>
      <Badge variant="new">Featured</Badge>
    </div>
  ),
}

export const CountPulse: Story = {
  render: () => {
    const [count, setCount] = useState(1)

    return (
      <div className="flex flex-col items-center gap-4">
        <Badge variant="count" count={count}>
          {count > 9 ? '9+' : count}
        </Badge>
        <button
          onClick={() => setCount((c) => c + 1)}
          className="px-3 py-1 bg-surface border border-line rounded text-sm hover:bg-muted"
        >
          Increment
        </button>
      </div>
    )
  },
}
```

- [ ] **Step 2: Verify stories compile**

Run: `npx tsc --noEmit`
Expected: No errors related to Badge.stories.tsx

- [ ] **Step 3: Commit**

```bash
git add src/components/Badge/Badge.stories.tsx
git commit -m "docs(Badge): add Storybook stories"
```

---

### Task 3: Add Badge to barrel export

**Files:**
- Modify: `src/components/index.ts` — add Badge exports

- [ ] **Step 1: Read current barrel file**

Read `src/components/index.ts` to confirm the insertion point.

- [ ] **Step 2: Add Badge exports**

Insert after the IconButton export block:

```ts
export { default as Badge } from './Badge/Badge.component'
export type {
  BadgeProps,
  BadgeSize,
  BadgeShape,
  BadgeVariant,
} from './Badge/Badge.component'
```

- [ ] **Step 3: Verify TypeScript compiles**

Run: `npx tsc --noEmit`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add src/components/index.ts
git commit -m "feat(Badge): add Badge to barrel export"
```
