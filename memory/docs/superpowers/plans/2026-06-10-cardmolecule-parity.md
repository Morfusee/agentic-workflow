# CardMolecule Parity Port — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current shadcn/ui-based CardMolecule with a full port of the website3.0-prototype CardMolecule, achieving visual/behavioral parity while preserving backward compatibility.

**Architecture:** Port the prototype's standalone CardMolecule (no shadcn/ui dependency), adapting imports to the website's existing atoms (Heading, Button, cn, motion). Create 3 new dependency atoms (Badge, Tag, Skeleton). Add prototype CSS utility classes (card-surface, lift, mesh-*, skel, m-track, media-zoom) to styles.css. Preserve legacy props (icon, description, actionLabel, selected, disabled, variant, onClick) via internal mapping to new props. TriageHero story icons use lucide-react directly — no TwoToneIcon atom needed.

**Tech Stack:** React 18, TypeScript (strict), Tailwind CSS, motion/react, class-variance-authority, Next.js Link, Storybook

**Worktree:** `C:\Users\mrqvp\Documents\Programming\worktrees\website-worktree-review` (branch `CU-86d36z2p8_Mobile-Navbar-OffCanvas`)

---

### Task 1: Add prototype CSS utility classes

**Files:**
- Modify: `src/app/(frontend)/styles.css`

- [ ] **Step 1: Append CSS utility classes**

Add the following to the end of `src/app/(frontend)/styles.css`:

```css
/* ─── Card Surface (prototype parity) ─────────────────────────────────────── */
.card-surface {
  @apply bg-white rounded-[16px] overflow-hidden;
}

/* ─── Interactive Card Lift ───────────────────────────────────────────────── */
.card-int {
  @apply cursor-pointer transition-all duration-300;
}
.card-int:hover {
  @apply -translate-y-0.5 shadow-md;
}

/* ─── Focus Ring ──────────────────────────────────────────────────────────── */
.focus-ring {
  @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-secondary focus-visible:ring-offset-2;
}

/* ─── Lift Transition ─────────────────────────────────────────────────────── */
.lift {
  @apply transition-shadow duration-200;
}

/* ─── Media Zoom (group-hover) ────────────────────────────────────────────── */
.media-zoom {
  @apply transition-transform duration-500;
}
.group:hover .media-zoom,
.group:focus-visible .media-zoom {
  @apply scale-105;
}

/* ─── Motion Track (animated underline) ───────────────────────────────────── */
.m-track {
  @apply relative;
}
.m-track::after {
  content: '';
  @apply absolute bottom-0 left-0 h-[2px] bg-mmdc-red w-0 transition-all duration-300;
}
.group:hover .m-track::after,
.group:focus-visible .m-track::after {
  @apply w-full;
}

/* ─── Mesh Patterns ───────────────────────────────────────────────────────── */
.mesh-1 {
  background-image: radial-gradient(ellipse at center, #102c66 0%, transparent 70%);
}
.mesh-2 {
  background-image: radial-gradient(circle at top left, #ed0000 0%, transparent 50%);
}
.mesh-brand {
  background-image: radial-gradient(ellipse at bottom right, #102c66 0%, #ed0000 50%, transparent 70%);
}

/* ─── Skeleton Shimmer ────────────────────────────────────────────────────── */
.skel {
  @apply bg-slate-200 rounded animate-pulse;
}

/* ─── Animate Shimmer Keyframe ────────────────────────────────────────────── */
@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}
.animate-shimmer {
  animation: shimmer 1.5s infinite;
}
```

- [ ] **Step 2: Commit**

```bash
git add src/app/\(frontend\)/styles.css
git commit -m "feat: add CardMolecule prototype CSS utilities (card-surface, lift, mesh, m-track, skel, shimmer)"
```

---

### Task 2: Create Badge atom

**Files:**
- Create: `src/components/Badge/Badge.component.tsx`
- Create: `src/components/Badge/Badge.stories.tsx`

- [ ] **Step 1: Write Badge component**

Create `src/components/Badge/Badge.component.tsx`:

```tsx
'use client'

import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import { motion, useAnimation } from 'motion/react'
import { useEffect, useRef } from 'react'
import { useReducedMotion } from '@/hooks/useReducedMotion'

const EASE_NUDGE: [number, number, number, number] = [0.34, 1.56, 0.64, 1]

const badgeVariants = cva(
  'relative overflow-hidden inline-flex items-center gap-1 font-semibold whitespace-nowrap transition-colors duration-200',
  {
    variants: {
      variant: {
        success: 'bg-success/15 text-success',
        warning: 'bg-warning/15 text-warning',
        error: 'bg-danger/15 text-danger',
        info: 'bg-info/15 text-info',
        brand: 'bg-mmdc-blue text-white',
        brandRed: 'bg-mmdc-red text-white',
        count: 'bg-mmdc-red text-white',
        new: 'bg-mmdc-yellow text-ink',
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

export interface BadgeProps
  extends Omit<React.HTMLAttributes<HTMLSpanElement>, 'children'>,
    VariantProps<typeof badgeVariants> {
  children: React.ReactNode
  count?: number
}

export function Badge({
  className,
  variant,
  size,
  shape,
  count,
  children,
  ...props
}: BadgeProps) {
  const prefersReducedMotion = useReducedMotion()
  const controls = useAnimation()
  const prevCount = useRef(count)

  const isNew = variant === 'new'
  const isCount = variant === 'count' || count !== undefined

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
        transition: { duration: 0.3, ease: EASE_NUDGE },
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
```

- [ ] **Step 2: Write Badge stories**

Create `src/components/Badge/Badge.stories.tsx`:

```tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Badge } from './Badge.component'

const meta: Meta<typeof Badge> = {
  title: 'Components/Badge',
  component: Badge,
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

export const Brand: Story = { args: { children: 'New', variant: 'brand' } }
export const BrandRed: Story = { args: { children: 'Featured', variant: 'brandRed' } }
export const Success: Story = { args: { children: 'Verified', variant: 'success' } }
export const Warning: Story = { args: { children: 'Pending', variant: 'warning' } }
export const Error: Story = { args: { children: 'Failed', variant: 'error' } }
export const Info: Story = { args: { children: 'Info', variant: 'info' } }
export const NewShimmer: Story = { args: { children: 'Just In', variant: 'new' } }
export const Count: Story = { args: { children: '5', variant: 'count' } }
```

- [ ] **Step 3: Commit**

```bash
git add src/components/Badge/Badge.component.tsx src/components/Badge/Badge.stories.tsx
git commit -m "feat: add Badge atom (ported from website3.0-prototype)"
```

---

### Task 3: Create Tag atom

**Files:**
- Create: `src/components/Tag/Tag.component.tsx`
- Create: `src/components/Tag/Tag.stories.tsx`

- [ ] **Step 1: Write Tag component**

Create `src/components/Tag/Tag.component.tsx`:

```tsx
'use client'

import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import { motion } from 'motion/react'

const tagVariants = cva(
  'inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium whitespace-nowrap transition-colors duration-100',
  {
    variants: {
      variant: {
        neutral: 'bg-surface-hover text-ink',
        brand: 'bg-mmdc-blue/10 text-mmdc-blue',
        brandRed: 'bg-mmdc-red/10 text-mmdc-red',
        outline: 'border border-line bg-transparent text-muted',
      },
      interactive: {
        true: 'cursor-pointer hover:bg-line',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'neutral',
      interactive: false,
    },
  },
)

export interface TagProps
  extends React.HTMLAttributes<HTMLSpanElement | HTMLAnchorElement>,
    VariantProps<typeof tagVariants> {
  href?: string
}

export function Tag({
  className,
  variant,
  interactive,
  href,
  children,
  ...props
}: TagProps) {
  const isInteractive = interactive || !!href
  const Component = href ? motion.a : motion.span

  return (
    <Component
      href={href}
      className={cn(tagVariants({ variant, interactive: isInteractive, className }))}
      {...(props as Record<string, unknown>)}
    >
      <span>{children}</span>
    </Component>
  )
}
```

- [ ] **Step 2: Write Tag stories**

Create `src/components/Tag/Tag.stories.tsx`:

```tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Tag } from './Tag.component'

const meta: Meta<typeof Tag> = {
  title: 'Components/Tag',
  component: Tag,
  argTypes: {
    variant: {
      control: 'select',
      options: ['neutral', 'brand', 'brandRed', 'outline'],
    },
    interactive: { control: 'boolean' },
  },
}

export default meta
type Story = StoryObj<typeof Tag>

export const Neutral: Story = { args: { children: 'General', variant: 'neutral' } }
export const Brand: Story = { args: { children: 'MMDC', variant: 'brand' } }
export const BrandRed: Story = { args: { children: 'NEW', variant: 'brandRed' } }
export const Outline: Story = { args: { children: 'Tag', variant: 'outline' } }
export const Interactive: Story = { args: { children: 'Clickable', interactive: true } }
export const AsLink: Story = { args: { children: 'View All', href: '#' } }
```

- [ ] **Step 3: Commit**

```bash
git add src/components/Tag/Tag.component.tsx src/components/Tag/Tag.stories.tsx
git commit -m "feat: add Tag atom (ported from website3.0-prototype)"
```

---

### Task 4: Create Skeleton atom

**Files:**
- Create: `src/components/Skeleton/Skeleton.component.tsx`
- Create: `src/components/Skeleton/Skeleton.stories.tsx`

- [ ] **Step 1: Write Skeleton component**

Create `src/components/Skeleton/Skeleton.component.tsx`:

```tsx
'use client'

import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import { motion } from 'motion/react'
import { useReducedMotion } from '@/hooks/useReducedMotion'

const skeletonVariants = cva('relative overflow-hidden bg-line', {
  variants: {
    variant: {
      text: 'h-4 w-full rounded',
      card: 'h-32 w-full rounded-lg',
      avatar: 'h-12 w-12 rounded-full',
      circle: 'rounded-full',
      rectangle: 'rounded-md',
    },
  },
  defaultVariants: {
    variant: 'text',
  },
})

export interface SkeletonProps extends VariantProps<typeof skeletonVariants> {
  className?: string
  width?: string | number
  height?: string | number
}

export function Skeleton({ variant, className, width, height }: SkeletonProps) {
  const prefersReducedMotion = useReducedMotion()

  return (
    <motion.div
      className={cn(skeletonVariants({ variant, className }))}
      style={{ width, height }}
      initial={prefersReducedMotion ? { opacity: 0.8 } : { opacity: 0.5 }}
      animate={prefersReducedMotion ? { opacity: 0.8 } : { opacity: 1 }}
      transition={{
        duration: 1.2,
        repeat: Infinity,
        repeatType: 'reverse',
        ease: 'easeInOut',
      }}
      aria-hidden="true"
    >
      {!prefersReducedMotion && (
        <div className="absolute inset-0 -translate-x-full animate-shimmer flex">
          <div className="flex-1 bg-gradient-to-r from-transparent via-white/30 to-transparent" />
        </div>
      )}
    </motion.div>
  )
}
```

- [ ] **Step 2: Write Skeleton stories**

Create `src/components/Skeleton/Skeleton.stories.tsx`:

```tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Skeleton } from './Skeleton.component'

const meta: Meta<typeof Skeleton> = {
  title: 'Components/Skeleton',
  component: Skeleton,
  argTypes: {
    variant: {
      control: 'select',
      options: ['text', 'card', 'avatar', 'circle', 'rectangle'],
    },
  },
}

export default meta
type Story = StoryObj<typeof Skeleton>

export const Text: Story = { args: { variant: 'text', width: 300 } }
export const Card: Story = { args: { variant: 'card', width: 320 } }
export const Avatar: Story = { args: { variant: 'avatar' } }
export const Circle: Story = { args: { variant: 'circle', width: 64, height: 64 } }
export const Rectangle: Story = { args: { variant: 'rectangle', width: 200, height: 24 } }
```

- [ ] **Step 3: Commit**

```bash
git add src/components/Skeleton/Skeleton.component.tsx src/components/Skeleton/Skeleton.stories.tsx
git commit -m "feat: add Skeleton atom (ported from website3.0-prototype)"
```

---

### Task 5: Rewrite CardMolecule component

**Files:**
- Modify: `src/components/CardMolecule/CardMolecule.component.tsx` (full rewrite)

- [ ] **Step 1: Replace CardMolecule with prototype port + legacy support**

Replace the entire contents of `src/components/CardMolecule/CardMolecule.component.tsx`:

```tsx
'use client'

import type { MouseEventHandler, ReactNode } from 'react'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Heading } from '@/components/Heading/Heading'
import { Tag } from '@/components/Tag/Tag.component'
import { Skeleton } from '@/components/Skeleton/Skeleton.component'

/* ─── Types ──────────────────────────────────────────────────────────────── */

export type CardMoleculeImageType =
  | 'none'
  | 'inset'
  | 'full-bleed'
  | 'overlay'
  | 'seam-straddle'

export type CardMoleculeVariant = 'default' | 'secondary' | 'outline'

export type CardMoleculeMesh = 'mesh-1' | 'mesh-2' | 'mesh-brand'

/* ─── Prototype props (new) ──────────────────────────────────────────────── */

export interface CardMoleculeProps
  extends React.HTMLAttributes<HTMLDivElement | HTMLAnchorElement> {
  kicker?: string
  title?: string
  tag?: string
  body?: ReactNode

  imageSrc?: string
  imageType?: CardMoleculeImageType
  imageBadge?: string
  imageActionIcon?: ReactNode
  iconStraddle?: ReactNode

  action?: string | ReactNode
  onAction?: () => void
  meta?: ReactNode
  metaIcon?: ReactNode

  orientation?: 'vertical' | 'horizontal'
  href?: string
  onClick?: MouseEventHandler<HTMLDivElement | HTMLAnchorElement>
  isHover?: boolean
  isFocus?: boolean
  isActive?: boolean
  isSkeleton?: boolean
  mesh?: CardMoleculeMesh

  /* ─── Legacy props (backward compatible) ──────────────────────────────── */
  /** @deprecated Use `iconStraddle` instead */
  icon?: ReactNode
  /** @deprecated Use `body` instead */
  description?: string
  /** @deprecated Use `action` instead */
  actionLabel?: string
  selected?: boolean
  disabled?: boolean
  variant?: CardMoleculeVariant
}

/* ─── Variant styling (legacy) ───────────────────────────────────────────── */

const variantClasses: Record<CardMoleculeVariant, string> = {
  default: '',
  secondary: '!bg-primary !text-white',
  outline: '!bg-transparent',
}

const selectedClasses =
  'ring-2 ring-secondary/40 shadow-md'

const disabledClasses =
  'cursor-not-allowed opacity-50 pointer-events-none'

/* ─── Component ──────────────────────────────────────────────────────────── */

export function CardMolecule({
  kicker,
  title,
  tag: tagText,
  body,
  imageSrc,
  imageType = 'none',
  imageBadge,
  imageActionIcon,
  iconStraddle,
  action,
  onAction,
  meta,
  metaIcon,
  orientation = 'vertical',
  href,
  onClick,
  isHover,
  isFocus,
  isActive,
  isSkeleton: skeleton,
  mesh = 'mesh-1',
  className,
  /* legacy */
  icon,
  description,
  actionLabel,
  selected = false,
  disabled = false,
  variant = 'default',
  ...props
}: CardMoleculeProps) {
  /* ─── Legacy prop resolution ────────────────────────────────────────── */
  const resolvedIconStraddle = iconStraddle ?? icon
  const resolvedBody: ReactNode =
    body ?? (description ? <p>{description}</p> : undefined)
  const resolvedAction = action ?? actionLabel

  /* ─── Derived values ────────────────────────────────────────────────── */
  const isHorizontal = orientation === 'horizontal'
  const interactive = !!href || !!onClick || !!onAction
  const hasMedia = imageType !== 'none'
  const isOverlay = imageType === 'overlay'
  const isInset = imageType === 'inset'
  const Component = href ? (Link as unknown as React.ElementType) : ('div' as React.ElementType)
  const linkProps = href ? { href } : {}

  return (
    <Component
      {...linkProps}
      onClick={disabled ? undefined : onClick}
      className={cn(
        'card-surface relative font-sans w-full',
        isHorizontal ? 'flex flex-col sm:flex-row items-stretch' : 'block',
        interactive && 'card-int focus-ring lift cursor-pointer',
        !interactive && 'shadow-subtle',
        isHover && 'is-hover',
        isFocus && 'is-focus',
        isActive && 'is-active',
        skeleton && 'pointer-events-none',
        selected && selectedClasses,
        disabled && disabledClasses,
        variantClasses[variant],
        className,
      )}
      {...(props as Record<string, unknown>)}
    >
      {/* ─── Skeleton overlay ──────────────────────────────────────────── */}
      {skeleton && (
        <div className="absolute inset-0 z-50 bg-white/50 backdrop-blur-sm flex flex-col justify-center p-5">
          <Skeleton variant="text" className="h-[2px] w-8 mb-4 !bg-slate-300" />
          <Skeleton variant="text" className="h-3 w-3/4 mb-3 !bg-slate-300" />
          <Skeleton variant="text" className="h-2 w-full mb-2 !bg-slate-300" />
          <Skeleton variant="text" className="h-2 w-2/3 !bg-slate-300" />
        </div>
      )}

      {/* ─── Media Section ─────────────────────────────────────────────── */}
      {hasMedia && (
        <div
          className={cn(
            'relative overflow-hidden shrink-0',
            mesh,
            isInset
              ? 'rounded-xl h-32 m-3 mb-0'
              : isHorizontal
                ? 'w-full sm:w-2/5 h-48 sm:h-auto'
                : 'h-48',
            isOverlay && 'absolute inset-0 z-0 h-full w-full',
            imageType === 'seam-straddle' && 'h-28',
          )}
        >
          {imageSrc ? (
            <img
              src={imageSrc}
              alt=""
              className={cn(
                'media-zoom h-full w-full object-cover',
                isOverlay && 'opacity-60 mix-blend-overlay',
              )}
            />
          ) : (
            <div
              className={cn(
                'media-zoom h-full w-full',
                isOverlay && 'opacity-60 mix-blend-overlay',
              )}
            />
          )}

          {isOverlay && (
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900/60 to-transparent" />
          )}

          {imageBadge && (
            <p className="absolute top-4 left-4 z-10 font-display text-[10px] font-bold text-white/70 uppercase tracking-widest">
              {imageBadge}
            </p>
          )}

          {imageActionIcon && (
            <button
              className="absolute top-4 right-4 h-8 w-8 flex items-center justify-center rounded-full bg-white/20 backdrop-blur-md border border-white/20 text-white hover:bg-white hover:text-slate-900 transition-colors z-[2]"
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
              }}
            >
              {imageActionIcon}
            </button>
          )}
        </div>
      )}

      {/* ─── Content Section ───────────────────────────────────────────── */}
      <div
        className={cn(
          'p-6 flex flex-col justify-center relative z-10 flex-1 min-w-0',
          isOverlay && 'pt-12 justify-end min-h-[220px]',
        )}
      >
        {resolvedIconStraddle && imageType === 'seam-straddle' && (
          <div className="-mt-12 h-14 w-14 rounded-2xl bg-white border border-slate-100 flex items-center justify-center text-mmdc-red shadow-md mb-4 relative z-10">
            {resolvedIconStraddle}
          </div>
        )}

        {/* Legacy icon (non-straddle) */}
        {resolvedIconStraddle && imageType !== 'seam-straddle' && !hasMedia && (
          <div className="mb-4 flex size-10 items-center justify-center rounded-full bg-primary/10 text-primary">
            {resolvedIconStraddle}
          </div>
        )}

        {kicker && (
          <p className="font-display text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-2">
            {kicker}
          </p>
        )}

        {interactive && (
          <div
            className="m-track"
            style={
              { '--color-mmdc-red': isOverlay ? '#fff' : '#ed0000' } as React.CSSProperties
            }
          />
        )}

        <div className="flex items-center gap-2 mb-2 flex-wrap">
          {title && (
            <Heading
              as={isOverlay ? 'h2' : 'h3'}
              size={isOverlay ? 'h1' : 'h3'}
              className={cn(
                'font-display font-bold tracking-tight leading-snug',
                isOverlay && 'text-white',
              )}
            >
              {title}
            </Heading>
          )}
          {tagText && (
            <Tag variant="brandRed" className="uppercase font-display tracking-wider text-[10px]">
              {tagText}
            </Tag>
          )}
        </div>

        {resolvedBody && (
          <div
            className={cn(
              'text-sm leading-relaxed font-body',
              isOverlay ? 'text-white/80' : 'text-slate-500',
            )}
          >
            {typeof resolvedBody === 'string' ? <p>{resolvedBody}</p> : resolvedBody}
          </div>
        )}

        {/* Legacy selected indicator */}
        {selected && (
          <div className="pt-2">
            <span className="text-xs font-semibold uppercase tracking-wide text-secondary">
              Selected
            </span>
          </div>
        )}
      </div>

      {/* ─── Footer Section ────────────────────────────────────────────── */}
      {(resolvedAction || meta) && !isOverlay && (
        <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between bg-slate-50/50 relative z-10">
          {resolvedAction && (
            <div className="shrink-0">
              {typeof resolvedAction === 'string' ? (
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    onAction?.()
                  }}
                  className="cta group inline-flex items-center gap-1.5 font-display font-bold text-sm text-mmdc-red"
                >
                  {resolvedAction}
                  <ArrowRight className="arr size-3.5 transition-transform group-hover:translate-x-1" />
                </button>
              ) : (
                resolvedAction
              )}
            </div>
          )}
          {meta && (
            <div className="shrink-0 ml-auto flex items-center gap-1.5 text-xs text-slate-400 font-display font-medium">
              {metaIcon}
              <span className="text-slate-600">{meta}</span>
            </div>
          )}
        </div>
      )}
    </Component>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add src/components/CardMolecule/CardMolecule.component.tsx
git commit -m "feat: rewrite CardMolecule with prototype parity and backward-compatible legacy props"
```

---

### Task 6: Rewrite CardMolecule stories

**Files:**
- Modify: `src/components/CardMolecule/CardMolecule.stories.tsx` (full rewrite)

- [ ] **Step 1: Replace stories with full prototype coverage + legacy coverage**

Replace the entire contents of `src/components/CardMolecule/CardMolecule.stories.tsx`:

```tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Sparkles, Bookmark, GraduationCap, MousePointerClick, Compass } from 'lucide-react'

import { CardMolecule } from './CardMolecule.component'

const meta: Meta<typeof CardMolecule> = {
  title: 'Components/CardMolecule',
  component: CardMolecule,
}

export default meta
type Story = StoryObj<typeof CardMolecule>

/* ─── Prototype: Standard Molecule ─────────────────────────────────────── */

export const StandardMolecule: Story = {
  args: {
    href: '#',
    imageSrc: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&q=80&w=800',
    imageType: 'inset',
    kicker: 'Academics',
    title: 'BS Information Technology',
    tag: 'NEW',
    body: 'Master the fundamentals of software engineering, data science, and cloud architecture in this comprehensive program.',
    action: 'View Curriculum',
  },
  decorators: [(Story) => <div className="w-[380px]">{Story()}</div>],
}

/* ─── Prototype: Overlay Mode ──────────────────────────────────────────── */

export const OverlayMode: Story = {
  args: {
    href: '#',
    imageSrc: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&q=80&w=800',
    imageType: 'overlay',
    kicker: 'Events',
    title: 'Campus Open House 2026',
    body: 'Join us for an immersive tour of our facilities and meet our distinguished faculty.',
  },
  decorators: [(Story) => <div className="w-[380px]">{Story()}</div>],
}

/* ─── Prototype: Seam-Straddle ─────────────────────────────────────────── */

export const SeamStraddle: Story = {
  args: {
    href: '#',
    imageSrc: 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&q=80&w=800',
    imageType: 'seam-straddle',
    imageBadge: 'Featured',
    iconStraddle: <Sparkles className="w-6 h-6" />,
    title: 'The Future of Work',
    body: 'How AI and machine learning are reshaping the modern workplace.',
    action: 'Read Article',
    meta: '5 min read',
  },
  decorators: [(Story) => <div className="w-[380px]">{Story()}</div>],
}

/* ─── Prototype: Interactive States ────────────────────────────────────── */

export const HoverState: Story = {
  args: {
    isHover: true,
    imageType: 'inset',
    title: 'Hover State',
    body: 'Notice the elevation lift, media zoom, and motion track expansion.',
  },
  decorators: [(Story) => <div className="w-[380px]">{Story()}</div>],
}

export const ActiveState: Story = {
  args: {
    isActive: true,
    imageType: 'inset',
    title: 'Active State',
    body: 'The card depresses slightly providing tactile feedback.',
  },
  decorators: [(Story) => <div className="w-[380px]">{Story()}</div>],
}

export const SkeletonState: Story = {
  args: {
    isSkeleton: true,
    imageType: 'inset',
    title: 'Loading State',
    body: 'This content is obscured by the skeleton overlay.',
  },
  decorators: [(Story) => <div className="w-[380px]">{Story()}</div>],
}

/* ─── Prototype: TriageHero CTA cards ──────────────────────────────────── */

export const TriageHeroUpskill: Story = {
  args: {
    href: '#upskill',
    body: (
      <div className="flex items-start gap-4">
        <GraduationCap className="size-8 mt-1 text-mmdc-red shrink-0" />
        <div className="flex flex-col gap-1.5">
          <h4 className="font-bold text-ink text-lg leading-tight">Upskill fast with a certificate</h4>
          <p className="text-slate-500 text-sm leading-snug">IBM, Google & Meta-backed · 3-5 months · from ₱990/mo</p>
        </div>
      </div>
    ),
    action: 'Browse certifications',
  },
  decorators: [(Story) => <div className="w-[380px]">{Story()}</div>],
}

export const TriageHeroDegree: Story = {
  args: {
    href: '#degree',
    body: (
      <div className="flex items-start gap-4">
        <GraduationCap className="size-8 mt-1 text-mmdc-blue shrink-0" />
        <div className="flex flex-col gap-1.5">
          <h4 className="font-bold text-ink text-lg leading-tight">Earn a Mapúa IT degree</h4>
          <p className="text-slate-500 text-sm leading-snug">CHED-accredited · built for working students · flexible payment</p>
        </div>
      </div>
    ),
    action: 'Explore college programs',
  },
  decorators: [(Story) => <div className="w-[380px]">{Story()}</div>],
}

export const TriageHeroPathfinder: Story = {
  args: {
    href: '#pathfinder',
    body: (
      <div className="flex items-start gap-4">
        <Compass className="size-8 mt-1 text-mmdc-red shrink-0" />
        <div className="flex flex-col gap-1.5">
          <h4 className="font-bold text-ink text-lg leading-tight">Not sure yet?</h4>
          <p className="text-slate-500 text-sm leading-snug">Take the 30-second Pathfinder Quiz and we'll match you.</p>
        </div>
      </div>
    ),
    action: 'Find your path',
  },
  decorators: [(Story) => <div className="w-[380px]">{Story()}</div>],
}

export const TriageHeroGrid: Story = {
  render: () => (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
      <CardMolecule
        href="#upskill"
        body={
          <div className="flex items-start gap-4">
            <GraduationCap className="size-8 mt-1 text-mmdc-red shrink-0" />
            <div className="flex flex-col gap-1.5">
              <h4 className="font-bold text-ink text-lg leading-tight">Upskill fast with a certificate</h4>
              <p className="text-slate-500 text-sm leading-snug">IBM, Google & Meta-backed · 3-5 months · from ₱990/mo</p>
            </div>
          </div>
        }
        action="Browse certifications"
      />
      <CardMolecule
        href="#degree"
        body={
          <div className="flex items-start gap-4">
            <GraduationCap className="size-8 mt-1 text-mmdc-blue shrink-0" />
            <div className="flex flex-col gap-1.5">
              <h4 className="font-bold text-ink text-lg leading-tight">Earn a Mapúa IT degree</h4>
              <p className="text-slate-500 text-sm leading-snug">CHED-accredited · built for working students · flexible payment</p>
            </div>
          </div>
        }
        action="Explore college programs"
      />
      <CardMolecule
        href="#pathfinder"
        body={
          <div className="flex items-start gap-4">
            <Compass className="size-8 mt-1 text-mmdc-red shrink-0" />
            <div className="flex flex-col gap-1.5">
              <h4 className="font-bold text-ink text-lg leading-tight">Not sure yet?</h4>
              <p className="text-slate-500 text-sm leading-snug">Take the 30-second Pathfinder Quiz and we'll match you.</p>
            </div>
          </div>
        }
        action="Find your path"
      />
    </div>
  ),
}

/* ─── Legacy backward-compatible stories ───────────────────────────────── */

export const LegacyDefault: Story = {
  args: {
    icon: <GraduationCap className="size-5" />,
    title: 'Explore Programs',
    description: 'Find the right MMDC program based on your goals and interests.',
    actionLabel: 'Learn more',
  },
  decorators: [(Story) => <div className="w-[360px]">{Story()}</div>],
}

export const LegacyClickableLink: Story = {
  args: {
    href: '/college-programs',
    icon: <GraduationCap className="size-5" />,
    title: 'College Programs',
    description: 'View available business and technology programs.',
    actionLabel: 'View programs',
  },
  decorators: [(Story) => <div className="w-[360px]">{Story()}</div>],
}

export const LegacyClickableButton: Story = {
  args: {
    icon: <MousePointerClick className="size-5" />,
    title: 'Choose this path',
    description: 'This card uses button semantics through onClick.',
    actionLabel: 'Choose',
    onClick: () => console.log('Button card clicked'),
  },
  decorators: [(Story) => <div className="w-[360px]">{Story()}</div>],
}

export const LegacySelected: Story = {
  args: {
    icon: <MousePointerClick className="size-5" />,
    title: 'Selected Path',
    description: 'This option is currently selected in the Hero CTA flow.',
    actionLabel: 'Continue',
    selected: true,
    onClick: () => console.log('Selected card clicked'),
  },
  decorators: [(Story) => <div className="w-[360px]">{Story()}</div>],
}

export const LegacyDisabled: Story = {
  args: {
    icon: <GraduationCap className="size-5" />,
    title: 'Coming Soon',
    description: 'This CTA option is currently unavailable.',
    actionLabel: 'Unavailable',
    disabled: true,
  },
  decorators: [(Story) => <div className="w-[360px]">{Story()}</div>],
}

export const LegacySecondary: Story = {
  args: {
    variant: 'secondary',
    icon: <GraduationCap className="size-5" />,
    title: 'Apply Now',
    description: 'Start your MMDC application today.',
    actionLabel: 'Apply',
  },
  decorators: [(Story) => <div className="w-[360px]">{Story()}</div>],
}

export const LegacyResponsiveGrid: Story = {
  render: () => (
    <div className="grid w-[720px] grid-cols-1 gap-4 sm:grid-cols-2">
      <CardMolecule
        icon={<GraduationCap className="size-5" />}
        title="College Programs"
        description="Explore degree programs."
        actionLabel="View"
        href="/college-programs"
      />
      <CardMolecule
        icon={<MousePointerClick className="size-5" />}
        title="Admissions"
        description="Learn how to enroll."
        actionLabel="Start"
        href="/admissions"
      />
    </div>
  ),
}

/* ─── Prototype: Horizontal orientation ────────────────────────────────── */

export const Horizontal: Story = {
  args: {
    orientation: 'horizontal',
    href: '#',
    imageSrc: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&q=80&w=800',
    imageType: 'inset',
    title: 'BS Information Technology',
    body: 'A comprehensive program covering software engineering and cloud architecture.',
    action: 'View Program',
    meta: '4 years',
  },
  decorators: [(Story) => <div className="w-[640px]">{Story()}</div>],
}

/* ─── Prototype: Mesh variants ─────────────────────────────────────────── */

export const Mesh1: Story = {
  args: {
    mesh: 'mesh-1',
    imageType: 'inset',
    title: 'mesh-1 Background',
    body: 'Default blue radial gradient pattern.',
  },
  decorators: [(Story) => <div className="w-[380px]">{Story()}</div>],
}

export const Mesh2: Story = {
  args: {
    mesh: 'mesh-2',
    imageType: 'inset',
    title: 'mesh-2 Background',
    body: 'Red-toned radial gradient pattern.',
  },
  decorators: [(Story) => <div className="w-[380px]">{Story()}</div>],
}

export const MeshBrand: Story = {
  args: {
    mesh: 'mesh-brand',
    imageType: 'inset',
    title: 'mesh-brand Background',
    body: 'Blue-to-red diagonal gradient pattern.',
  },
  decorators: [(Story) => <div className="w-[380px]">{Story()}</div>],
}
```

- [ ] **Step 2: Commit**

```bash
git add src/components/CardMolecule/CardMolecule.stories.tsx
git commit -m "feat: rewrite CardMolecule stories with full prototype + legacy coverage"
```

---

### Task 7: Update barrel export

**Files:**
- Modify: `src/components/index.ts`

- [ ] **Step 1: Add new atom exports**

Replace the `CardMolecule` export line and add new atoms. The current file is:

```ts
export { default as Pagination } from './Pagination/Pagination.component'
export { default as Form } from './Form/Form.component'
export { default as BackgroundTexture } from './BackgroundTexture/BackgroundTexture.component'
export { default as CardMolecule } from './CardMolecule/CardMolecule.component'
export { default as Input } from './Input/Input'
export { default as SearchBar } from './SearchBar/SearchBar'
export { default as MobileNavDrawer } from './MobileNavDrawer/MobileNavDrawer.component'
```

Change the `CardMolecule` line from default re-export to named re-export, and add the new atoms:

```ts
export { default as Pagination } from './Pagination/Pagination.component'
export { default as Form } from './Form/Form.component'
export { default as BackgroundTexture } from './BackgroundTexture/BackgroundTexture.component'
export { CardMolecule } from './CardMolecule/CardMolecule.component'
export type { CardMoleculeProps, CardMoleculeVariant, CardMoleculeImageType, CardMoleculeMesh } from './CardMolecule/CardMolecule.component'
export { default as Input } from './Input/Input'
export { default as SearchBar } from './SearchBar/SearchBar'
export { default as MobileNavDrawer } from './MobileNavDrawer/MobileNavDrawer.component'
export { Badge } from './Badge/Badge.component'
export { Tag } from './Tag/Tag.component'
export { Skeleton } from './Skeleton/Skeleton.component'
```

- [ ] **Step 2: Commit**

```bash
git add src/components/index.ts
git commit -m "feat: update barrel exports for CardMolecule rewrite and new atoms"
```

---

### Task 8: Verify — build check

- [ ] **Step 1: Run TypeScript check**

```bash
npx tsc --noEmit 2>&1 | head -40
```

Expected: No new TypeScript errors introduced. Fix any errors from the new files.

- [ ] **Step 2: Run linter**

```bash
pnpm run lint 2>&1
```

Expected: No new lint errors from CardMolecule, Badge, Tag, Skeleton, TwoToneIcon.

- [ ] **Step 3: Verify existing stories still render**

Run Storybook and visually confirm:
- All legacy CardMolecule stories render correctly
- All new prototype stories render correctly
- TriageHeroGrid story matches the prototype's `TriageHero` layout in `MMDCOrganisms.tsx`

- [ ] **Step 4: Commit any fixes**

```bash
git add -A
git commit -m "fix: address typecheck and lint issues from CardMolecule parity port"
```

---

### Task 9: Add CSS color tokens (if missing)

Check that the website's Tailwind config defines these tokens used by the new CSS:
- `mmdc-red` (`#ed0000`)
- `mmdc-blue` (`#102c66`)
- `mmdc-yellow`
- `success`, `warning`, `danger`, `info`
- `surface-hover`, `line`
- `shadow-subtle`

- [ ] **Step 1: Check tailwind.config.js for missing tokens**

Read `tailwind.config.js` and verify the following are present under `theme.extend.colors`:
```
mmdc-red, mmdc-blue, mmdc-yellow, success, warning, danger, info, surface-hover, line
```

- [ ] **Step 2: Add any missing tokens to tailwind.config.js**

If any are missing, add them under `theme.extend.colors`. Example:
```js
mmdc: {
  red: '#ed0000',
  blue: '#102c66',
  yellow: '#f5c518',
},
```

- [ ] **Step 3: Commit**

```bash
git add tailwind.config.js
git commit -m "fix: ensure Tailwind color tokens for CardMolecule parity"
```
