# Desktop Mega Menu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable Storybook-validated desktop mega-menu component under `src/components` without touching CMS/global Header code.

**Architecture:** Add a standalone `DesktopMegaMenu` component folder with local types, local mock data, the component implementation, and stories. The component owns click-only trigger state, close behavior, full-width desktop panel rendering, accessibility attributes, and overflow-safe layout while receiving all content through typed props.

**Tech Stack:** Next.js, React 19, TypeScript, Tailwind CSS, Storybook 9, `next/link`, `lucide-react`, existing `@/blocks/components` Button atom, existing `@/lib/utils` `cn` helper.

---

## File Structure

- Create: `src/components/DesktopMegaMenu/DesktopMegaMenu.types.ts`
  - Owns local component data contracts. It must not import Payload or `src/globals/Headers` types.
- Create: `src/components/DesktopMegaMenu/DesktopMegaMenu.mock.tsx`
  - Owns Storybook-only mock data for default, overflow, and simple-link scenarios.
- Create: `src/components/DesktopMegaMenu/DesktopMegaMenu.component.tsx`
  - Owns rendering, state, accessibility attributes, close handlers, and link behavior.
- Create: `src/components/DesktopMegaMenu/DesktopMegaMenu.stories.tsx`
  - Owns Storybook validation stories.
- Do not modify: `src/globals/Headers/*`
- Do not modify: `src/payload-types.ts`
- Do not modify: `src/payload.config.ts`
- Do not modify: `src/globals/Headers/MobileNavDrawer.component.tsx`
- Preserve existing unrelated changes in `package.json` and `pnpm-lock.yaml`.

## Pre-Flight

### Task 0: Branch And Worktree Safety

**Files:**
- Inspect only: repository status

- [ ] **Step 1: Confirm current website worktree state**

Run from `C:\Users\mrqvp\Documents\Programming\worktrees\website-worktree-review`:

```bash
git status --short --branch
git diff -- package.json pnpm-lock.yaml
```

Expected: current branch may not yet be `feat/CU-86d36z2nw_Implement-Navbar-desktop-mega-menu-component`; `package.json` and `pnpm-lock.yaml` may already be modified by user-owned work. Do not revert those files.

- [ ] **Step 2: Create or switch to the requested branch without discarding work**

Run:

```bash
git switch -c feat/CU-86d36z2nw_Implement-Navbar-desktop-mega-menu-component
```

Expected: branch is created. If Git reports the branch already exists, run this instead:

```bash
git switch feat/CU-86d36z2nw_Implement-Navbar-desktop-mega-menu-component
```

Expected: worktree switches without discarding the existing package changes.

- [ ] **Step 3: Confirm no forbidden files will be edited**

Run:

```bash
git status --short
```

Expected: only pre-existing package changes are present before implementation. During implementation, new files should be under `src/components/DesktopMegaMenu/` only.

---

### Task 1: Add Local Types

**Files:**
- Create: `src/components/DesktopMegaMenu/DesktopMegaMenu.types.ts`

- [ ] **Step 1: Create the component folder**

Run:

```powershell
New-Item -ItemType Directory -Path "src/components/DesktopMegaMenu" -Force
```

Expected: `src/components/DesktopMegaMenu` exists.

- [ ] **Step 2: Add local data contracts**

Create `src/components/DesktopMegaMenu/DesktopMegaMenu.types.ts` with this content:

```ts
import type { ReactNode } from 'react'

export type MegaMenuLink = {
  label: string
  href: string
  newTab?: boolean
  selected?: boolean
  description?: string
  icon?: ReactNode
}

export type MegaMenuCTA = {
  label: string
  href: string
  newTab?: boolean
  description?: string
}

export type MegaMenuViewAllLink = {
  label: string
  href: string
  newTab?: boolean
}

export type DesktopMegaMenuData = {
  items: DesktopMegaMenuItem[]
}

export type DesktopMegaMenuItem = {
  label: string
  href?: string
  selected?: boolean
  panel?: DesktopMegaMenuPanel
}

export type DesktopMegaMenuPanel = {
  leftPanel: DesktopMegaMenuLeftPanel
  categories: DesktopMegaMenuCategory[]
}

export type DesktopMegaMenuLeftPanel = {
  eyebrow?: string
  title: string
  description: string
  cta?: MegaMenuCTA
}

export type DesktopMegaMenuCategory = {
  title: string
  icon?: ReactNode
  links: MegaMenuLink[]
  viewAll?: MegaMenuViewAllLink
}
```

Expected: types are local to `src/components/DesktopMegaMenu` and contain no `Payload`, CMS, or global Header imports.

- [ ] **Step 3: Run TypeScript-adjacent lint check for the new file**

Run:

```bash
pnpm lint
```

Expected: no new lint errors caused by `DesktopMegaMenu.types.ts`. If existing unrelated lint issues appear, record them and continue only if they are unrelated to this task.

- [ ] **Step 4: Commit local types**

Run:

```bash
git add src/components/DesktopMegaMenu/DesktopMegaMenu.types.ts
git commit -m "feat(nav): add desktop mega menu types"
```

Expected: commit includes only `DesktopMegaMenu.types.ts`.

---

### Task 2: Add Storybook Mock Data

**Files:**
- Create: `src/components/DesktopMegaMenu/DesktopMegaMenu.mock.tsx`

- [ ] **Step 1: Add representative mock data**

Create `src/components/DesktopMegaMenu/DesktopMegaMenu.mock.tsx` with this content:

```tsx
import { Award, BookOpen, Calendar, CreditCard, GraduationCap, Info, Newspaper } from 'lucide-react'

import type { DesktopMegaMenuData } from './DesktopMegaMenu.types'

export const desktopMegaMenuMock = {
  items: [
    {
      label: 'Home',
      href: '/',
    },
    {
      label: 'College Programs',
      panel: {
        leftPanel: {
          eyebrow: 'MMDC Options',
          title: 'College Programs',
          description:
            'Transform your career with modern, industry-aligned college degrees built for the future.',
          cta: {
            label: 'View all college programs',
            href: '/programs',
          },
        },
        categories: [
          {
            title: 'Information Technology',
            icon: <GraduationCap className="size-5" aria-hidden="true" />,
            links: [
              { label: 'AI Specialist', href: '/programs/it-ai' },
              { label: 'Web Development', href: '/programs/it-web' },
              { label: 'Cyber Security', href: '/programs/it-cyber' },
            ],
            viewAll: {
              label: 'View all IT programs',
              href: '/programs/it',
            },
          },
          {
            title: 'Business Administration',
            icon: <BookOpen className="size-5" aria-hidden="true" />,
            links: [
              { label: 'Digital Marketing', href: '/programs/ba-marketing' },
              { label: 'Entrepreneurship', href: '/programs/ba-entrepreneur' },
              { label: 'Business Management', href: '/programs/ba-management' },
            ],
            viewAll: {
              label: 'View all Business programs',
              href: '/programs/ba',
            },
          },
        ],
      },
    },
    {
      label: 'Certification Program',
      panel: {
        leftPanel: {
          eyebrow: 'MMDC Options',
          title: 'Professional Certifications',
          description:
            'Fast-track your skills with expert-led, short-term certification courses and bootcamps.',
          cta: {
            label: 'Browse all certifications',
            href: '/certifications',
          },
        },
        categories: [
          {
            title: 'Technology & AI',
            icon: <Award className="size-5" aria-hidden="true" />,
            links: [
              { label: 'AI & ML Basics', href: '/certifications/ai-basics' },
              { label: 'Web Dev Bootcamp', href: '/certifications/web-bootcamp' },
              { label: 'Cloud Computing Essentials', href: '/certifications/cloud' },
            ],
            viewAll: {
              label: 'View all tech certifications',
              href: '/certifications/tech',
            },
          },
          {
            title: 'Marketing & Services',
            icon: <Calendar className="size-5" aria-hidden="true" />,
            links: [
              { label: 'Virtual Assistant Program', href: '/certifications/va' },
              { label: 'SEO & Content Marketing', href: '/certifications/seo' },
              { label: 'Event Management', href: '/certifications/events' },
            ],
            viewAll: {
              label: 'View all marketing courses',
              href: '/certifications/marketing',
            },
          },
        ],
      },
    },
    {
      label: 'Admission',
      panel: {
        leftPanel: {
          eyebrow: 'MMDC Options',
          title: 'Admissions & Tuition',
          description:
            'Everything you need to secure your spot at MMDC, from admissions pathways to fees and scholarships.',
          cta: {
            label: 'Apply online now',
            href: '/admission/apply',
          },
        },
        categories: [
          {
            title: 'Costs & Financials',
            icon: <CreditCard className="size-5" aria-hidden="true" />,
            links: [
              { label: 'Scholarships & Grants', href: '/admission/scholarships' },
              { label: 'Fees and Tuition', href: '/admission/fees' },
              { label: 'Payment Options', href: '/admission/payment' },
            ],
            viewAll: {
              label: 'View financial details',
              href: '/admission/costs',
            },
          },
          {
            title: 'Process & Guides',
            icon: <Info className="size-5" aria-hidden="true" />,
            links: [
              { label: 'Admission Requirements', href: '/admission/requirements' },
              { label: 'How to Apply', href: '/admission/apply-guide' },
              { label: 'Academic Calendar', href: '/admission/calendar' },
            ],
            viewAll: {
              label: 'Explore the process',
              href: '/admission/process',
            },
          },
        ],
      },
    },
    {
      label: 'News & Events',
      panel: {
        leftPanel: {
          eyebrow: 'MMDC Options',
          title: 'News & Publications',
          description:
            'Stay in the loop with student lifestyle tips, announcements, blogs, and official press releases.',
          cta: {
            label: 'Go to newsroom',
            href: '/news',
          },
        },
        categories: [
          {
            title: 'MMDC Media',
            icon: <Newspaper className="size-5" aria-hidden="true" />,
            links: [
              { label: 'MMDC in the News', href: '/news/in-the-news' },
              { label: 'Official Announcements', href: '/news/announcements' },
              { label: 'Press Releases', href: '/news/press' },
            ],
            viewAll: {
              label: 'Explore press stories',
              href: '/news/media',
            },
          },
          {
            title: 'Resources & Stories',
            icon: <BookOpen className="size-5" aria-hidden="true" />,
            links: [
              { label: 'Blogs & Articles', href: '/news/blog' },
              { label: 'Lifestyle Tips', href: '/news/lifestyle' },
              { label: 'Student Stories', href: '/news/student-life' },
            ],
            viewAll: {
              label: 'Read student blogs',
              href: '/news/resources',
            },
          },
        ],
      },
    },
    {
      label: 'FAQ',
      href: '/faq',
    },
    {
      label: 'About Us',
      href: '/about',
    },
  ],
} satisfies DesktopMegaMenuData

export const desktopMegaMenuOverflowMock = {
  items: [
    ...desktopMegaMenuMock.items,
    { label: 'Student Life', href: '/student-life' },
    { label: 'Careers', href: '/careers' },
    { label: 'Alumni', href: '/alumni' },
    { label: 'Contact', href: '/contact' },
    {
      label: 'Resources',
      panel: {
        leftPanel: {
          eyebrow: 'Explore More',
          title: 'Student Resources',
          description: 'A dense menu state for validating top-level and panel overflow behavior.',
          cta: {
            label: 'View all resources',
            href: '/resources',
          },
        },
        categories: [
          {
            title: 'Popular Resources',
            icon: <BookOpen className="size-5" aria-hidden="true" />,
            links: Array.from({ length: 14 }, (_, index) => ({
              label: `Resource Link ${index + 1}`,
              href: `/resources/link-${index + 1}`,
            })),
            viewAll: {
              label: 'View all popular resources',
              href: '/resources/popular',
            },
          },
          {
            title: 'Admissions Help',
            icon: <Info className="size-5" aria-hidden="true" />,
            links: Array.from({ length: 12 }, (_, index) => ({
              label: `Admissions Topic ${index + 1}`,
              href: `/resources/admissions-${index + 1}`,
            })),
          },
          {
            title: 'Payment Guides',
            icon: <CreditCard className="size-5" aria-hidden="true" />,
            links: Array.from({ length: 10 }, (_, index) => ({
              label: `Payment Guide ${index + 1}`,
              href: `/resources/payment-${index + 1}`,
            })),
          },
        ],
      },
    },
  ],
} satisfies DesktopMegaMenuData

export const desktopMegaMenuSimpleLinksMock = {
  items: [
    { label: 'Home', href: '/' },
    { label: 'Programs', href: '/programs' },
    { label: 'Admission', href: '/admission' },
    { label: 'News', href: '/news' },
    { label: 'FAQ', href: '/faq' },
    { label: 'About Us', href: '/about' },
  ],
} satisfies DesktopMegaMenuData
```

Expected: mock data imports only local types and visual icons. It does not import `src/globals/Headers/mega-menu.mock.tsx`.

- [ ] **Step 2: Run lint**

Run:

```bash
pnpm lint
```

Expected: no new lint errors caused by the mock file.

- [ ] **Step 3: Commit mock data**

Run:

```bash
git add src/components/DesktopMegaMenu/DesktopMegaMenu.mock.tsx
git commit -m "feat(nav): add desktop mega menu mock data"
```

Expected: commit includes only `DesktopMegaMenu.mock.tsx`.

---

### Task 3: Implement DesktopMegaMenu Component

**Files:**
- Create: `src/components/DesktopMegaMenu/DesktopMegaMenu.component.tsx`

- [ ] **Step 1: Add the component implementation**

Create `src/components/DesktopMegaMenu/DesktopMegaMenu.component.tsx` with this content:

```tsx
'use client'

import Link from 'next/link'
import { ChevronDown } from 'lucide-react'
import { useEffect, useId, useRef, useState, type KeyboardEvent, type MouseEvent } from 'react'

import { Button } from '@/blocks/components'
import { cn } from '@/lib/utils'

import type { DesktopMegaMenuItem, MegaMenuCTA, MegaMenuLink, MegaMenuViewAllLink } from './DesktopMegaMenu.types'

export type DesktopMegaMenuProps = {
  items: DesktopMegaMenuItem[]
  initialOpenIndex?: number
  className?: string
  ariaLabel?: string
}

const isExternalHref = (href: string) => /^https?:\/\//i.test(href)

const linkTargetProps = (newTab?: boolean) => ({
  target: newTab ? '_blank' : undefined,
  rel: newTab ? 'noopener noreferrer' : undefined,
})

const linkClassName = cn(
  'rounded-lg text-sm font-semibold text-ink transition-colors hover:text-primary',
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-secondary focus-visible:ring-offset-2',
)

export const DesktopMegaMenu: React.FC<DesktopMegaMenuProps> = ({
  items,
  initialOpenIndex,
  className,
  ariaLabel = 'Desktop navigation',
}) => {
  const componentId = useId()
  const menuRef = useRef<HTMLDivElement>(null)
  const triggerRefs = useRef<Array<HTMLButtonElement | null>>([])
  const [openIndex, setOpenIndex] = useState<number | undefined>(initialOpenIndex)

  const activeItem = openIndex !== undefined ? items[openIndex] : undefined
  const activePanel = activeItem?.panel

  const closeMenu = (focusTrigger = false) => {
    const trigger = openIndex !== undefined ? triggerRefs.current[openIndex] : undefined

    setOpenIndex(undefined)

    if (focusTrigger) {
      window.requestAnimationFrame(() => trigger?.focus())
    }
  }

  useEffect(() => {
    if (openIndex === undefined) return

    const handlePointerDown = (event: PointerEvent) => {
      if (!menuRef.current?.contains(event.target as Node)) {
        setOpenIndex(undefined)
      }
    }

    document.addEventListener('pointerdown', handlePointerDown)

    return () => {
      document.removeEventListener('pointerdown', handlePointerDown)
    }
  }, [openIndex])

  if (!items.length) return null

  const handleTriggerClick = (index: number) => {
    setOpenIndex((currentIndex) => (currentIndex === index ? undefined : index))
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Escape' && openIndex !== undefined) {
      event.preventDefault()
      closeMenu(true)
    }
  }

  const handleMouseLeave = () => {
    if (openIndex !== undefined) {
      closeMenu()
    }
  }

  return (
    <div
      ref={menuRef}
      className={cn('relative hidden w-full xl:block', className)}
      onKeyDown={handleKeyDown}
      onMouseLeave={handleMouseLeave}
    >
      <nav aria-label={ariaLabel}>
        <ul className="flex items-center justify-center gap-1 overflow-x-auto px-2 py-1">
          {items.map((item, index) => {
            const panelId = `${componentId}-panel-${index}`
            const isOpen = openIndex === index

            if (item.panel) {
              return (
                <li key={`${item.label}-${index}`} className="shrink-0">
                  <button
                    ref={(node) => {
                      triggerRefs.current[index] = node
                    }}
                    type="button"
                    className={cn(
                      'inline-flex min-h-11 items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold text-secondary transition-colors',
                      'hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-secondary focus-visible:ring-offset-2',
                      isOpen && 'bg-muted text-primary',
                    )}
                    aria-expanded={isOpen}
                    aria-controls={panelId}
                    onClick={() => handleTriggerClick(index)}
                  >
                    {item.label}
                    <ChevronDown
                      className={cn('size-4 transition-transform', isOpen && 'rotate-180')}
                      aria-hidden="true"
                    />
                  </button>
                </li>
              )
            }

            if (item.href) {
              return (
                <li key={`${item.label}-${index}`} className="shrink-0">
                  <DesktopMegaMenuTopLink item={item} />
                </li>
              )
            }

            return null
          })}
        </ul>
      </nav>

      {activePanel && openIndex !== undefined ? (
        <div
          id={`${componentId}-panel-${openIndex}`}
          className="absolute left-1/2 top-full z-50 w-screen -translate-x-1/2 border-t bg-white shadow-xl"
        >
          <div className="mx-auto grid max-h-[calc(100vh-8rem)] max-w-7xl grid-cols-[minmax(18rem,24rem)_1fr] overflow-y-auto px-8 py-8">
            <aside className="rounded-3xl bg-secondary p-8 text-white">
              {activePanel.leftPanel.eyebrow ? (
                <p className="mb-4 text-xs font-bold uppercase tracking-[0.2em] text-white/70">
                  {activePanel.leftPanel.eyebrow}
                </p>
              ) : null}
              <h2 className="text-3xl font-bold leading-tight">{activePanel.leftPanel.title}</h2>
              <p className="mt-4 text-sm leading-6 text-white/80">
                {activePanel.leftPanel.description}
              </p>
              {activePanel.leftPanel.cta ? (
                <MegaMenuCTAButton cta={activePanel.leftPanel.cta} onClick={() => closeMenu()} />
              ) : null}
            </aside>

            <div className="grid gap-5 pl-8 lg:grid-cols-2 xl:grid-cols-3">
              {activePanel.categories.map((category) => (
                <section key={category.title} className="rounded-2xl border bg-white p-5 shadow-sm">
                  <div className="mb-4 flex items-center gap-3">
                    {category.icon ? (
                      <span className="inline-flex size-10 items-center justify-center rounded-full bg-primary/10 text-primary">
                        {category.icon}
                      </span>
                    ) : null}
                    <h3 className="text-base font-bold text-secondary">{category.title}</h3>
                  </div>

                  {category.links.length > 0 ? (
                    <ul className="space-y-2">
                      {category.links.map((link) => (
                        <li key={link.href}>
                          <MegaMenuInlineLink link={link} onClick={() => closeMenu()} />
                        </li>
                      ))}
                    </ul>
                  ) : null}

                  {category.viewAll ? (
                    <div className="mt-4 border-t pt-4">
                      <MegaMenuViewAllLink link={category.viewAll} onClick={() => closeMenu()} />
                    </div>
                  ) : null}
                </section>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}

const DesktopMegaMenuTopLink: React.FC<{ item: DesktopMegaMenuItem }> = ({ item }) => {
  if (!item.href) return null

  return (
    <Link
      href={item.href}
      className={cn(
        'inline-flex min-h-11 items-center rounded-full px-4 py-2 text-sm font-semibold text-secondary transition-colors',
        'hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-secondary focus-visible:ring-offset-2',
        item.selected && 'bg-muted text-primary',
      )}
      prefetch={process.env.NEXT_PUBLIC_BUILD_MODE !== 'static'}
    >
      {item.label}
    </Link>
  )
}

const MegaMenuInlineLink: React.FC<{ link: MegaMenuLink; onClick: (event: MouseEvent<HTMLAnchorElement>) => void }> = ({
  link,
  onClick,
}) => {
  const targetProps = linkTargetProps(link.newTab)

  if (isExternalHref(link.href)) {
    return (
      <a href={link.href} {...targetProps} className={cn('block px-2 py-1.5', linkClassName)} onClick={onClick}>
        <span>{link.label}</span>
        {link.description ? <span className="mt-1 block text-xs font-normal text-ink/60">{link.description}</span> : null}
      </a>
    )
  }

  return (
    <Link
      href={link.href}
      {...targetProps}
      className={cn('block px-2 py-1.5', linkClassName)}
      onClick={onClick}
      prefetch={process.env.NEXT_PUBLIC_BUILD_MODE !== 'static'}
    >
      <span>{link.label}</span>
      {link.description ? <span className="mt-1 block text-xs font-normal text-ink/60">{link.description}</span> : null}
    </Link>
  )
}

const MegaMenuViewAllLink: React.FC<{
  link: MegaMenuViewAllLink
  onClick: (event: MouseEvent<HTMLAnchorElement>) => void
}> = ({ link, onClick }) => {
  const targetProps = linkTargetProps(link.newTab)

  if (isExternalHref(link.href)) {
    return (
      <a href={link.href} {...targetProps} className={cn('inline-flex px-2 py-1.5 text-primary', linkClassName)} onClick={onClick}>
        {link.label}
      </a>
    )
  }

  return (
    <Link
      href={link.href}
      {...targetProps}
      className={cn('inline-flex px-2 py-1.5 text-primary', linkClassName)}
      onClick={onClick}
      prefetch={process.env.NEXT_PUBLIC_BUILD_MODE !== 'static'}
    >
      {link.label}
    </Link>
  )
}

const MegaMenuCTAButton: React.FC<{ cta: MegaMenuCTA; onClick: () => void }> = ({ cta, onClick }) => (
  <div className="mt-8">
    <Button variant="inverse" link={cta.href} newTab={cta.newTab} onClick={onClick}>
      {cta.label}
    </Button>
    {cta.description ? <p className="mt-3 text-xs leading-5 text-white/70">{cta.description}</p> : null}
  </div>
)

export default DesktopMegaMenu
```

Expected: component is desktop-only via `hidden xl:block`, returns `null` for empty items, skips invalid items, uses local types, and does not import `src/globals/Headers`.

- [ ] **Step 2: Run lint and fix only component-caused errors**

Run:

```bash
pnpm lint
```

Expected: no lint errors from `DesktopMegaMenu.component.tsx`. If `@typescript-eslint` complains about long type lines, break the type across lines without changing behavior.

- [ ] **Step 3: Confirm forbidden files are untouched**

Run:

```bash
git diff --name-only
```

Expected: implementation changes are still limited to `src/components/DesktopMegaMenu/*`, plus any pre-existing user-owned package files.

- [ ] **Step 4: Commit component implementation**

Run:

```bash
git add src/components/DesktopMegaMenu/DesktopMegaMenu.component.tsx
git commit -m "feat(nav): implement desktop mega menu component"
```

Expected: commit includes only `DesktopMegaMenu.component.tsx`.

---

### Task 4: Add Storybook Stories

**Files:**
- Create: `src/components/DesktopMegaMenu/DesktopMegaMenu.stories.tsx`

- [ ] **Step 1: Add default, overflow, simple-link, and pre-open stories**

Create `src/components/DesktopMegaMenu/DesktopMegaMenu.stories.tsx` with this content:

```tsx
import type { Meta, StoryObj } from '@storybook/react'

import { DesktopMegaMenu } from './DesktopMegaMenu.component'
import {
  desktopMegaMenuMock,
  desktopMegaMenuOverflowMock,
  desktopMegaMenuSimpleLinksMock,
} from './DesktopMegaMenu.mock'

const meta = {
  title: 'Components/DesktopMegaMenu',
  component: DesktopMegaMenu,
  parameters: {
    layout: 'fullscreen',
  },
  decorators: [
    (Story) => (
      <div className="min-h-screen bg-muted/40 pt-8">
        <div className="mx-auto max-w-7xl rounded-t-3xl bg-white px-6 py-3 shadow">
          <Story />
        </div>
      </div>
    ),
  ],
} satisfies Meta<typeof DesktopMegaMenu>

export default meta

type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    items: desktopMegaMenuMock.items,
  },
}

export const Overflow: Story = {
  args: {
    items: desktopMegaMenuOverflowMock.items,
    initialOpenIndex: desktopMegaMenuOverflowMock.items.length - 1,
  },
}

export const SimpleLinksOnly: Story = {
  args: {
    items: desktopMegaMenuSimpleLinksMock.items,
  },
}

export const PreOpenPanel: Story = {
  args: {
    items: desktopMegaMenuMock.items,
    initialOpenIndex: 1,
  },
}
```

Expected: Storybook stories use local mock data and do not require CMS data or production Header rendering.

- [ ] **Step 2: Run Storybook build**

Run:

```bash
pnpm build:storybook
```

Expected: Storybook builds successfully. If the build fails because of unrelated existing stories, record the failing story path and confirm `DesktopMegaMenu.stories.tsx` is not the cause.

- [ ] **Step 3: Run lint**

Run:

```bash
pnpm lint
```

Expected: no new lint errors from the Storybook file.

- [ ] **Step 4: Commit stories**

Run:

```bash
git add src/components/DesktopMegaMenu/DesktopMegaMenu.stories.tsx
git commit -m "feat(nav): add desktop mega menu stories"
```

Expected: commit includes only `DesktopMegaMenu.stories.tsx`.

---

### Task 5: Manual Behavior Validation

**Files:**
- Inspect: `src/components/DesktopMegaMenu/DesktopMegaMenu.component.tsx`
- Inspect: `src/components/DesktopMegaMenu/DesktopMegaMenu.stories.tsx`

- [ ] **Step 1: Start Storybook**

Run:

```bash
pnpm storybook
```

Expected: Storybook starts on `http://localhost:6006`.

- [ ] **Step 2: Validate the Default story**

Open `Components/DesktopMegaMenu/Default` and confirm:

```text
Click College Programs: panel opens.
Click College Programs again: panel closes.
Click Certification Program: certification panel opens and replaces the previous panel.
Click Home or FAQ: the item is a link, not a menu trigger.
```

Expected: click-only behavior works; hover alone does not open a panel.

- [ ] **Step 3: Validate close behavior**

In the Default story, confirm:

```text
Open a panel, press Escape: panel closes and focus returns to the trigger.
Open a panel, click outside the menu: panel closes.
Open a panel, move the mouse outside the full menu/panel region: panel closes.
Open a panel, click a panel link: panel closes before navigation.
```

Expected: all requested close behaviors work.

- [ ] **Step 4: Validate accessibility basics**

In the Default story, use keyboard navigation and browser devtools to confirm:

```text
Top-level triggers are reachable by Tab.
Open trigger has aria-expanded="true".
Closed triggers have aria-expanded="false".
Open trigger has aria-controls matching the visible panel id.
Links and triggers show visible focus styles.
```

Expected: keyboard and ARIA requirements are satisfied.

- [ ] **Step 5: Validate overflow and simple-link stories**

Open `Components/DesktopMegaMenu/Overflow` and `Components/DesktopMegaMenu/SimpleLinksOnly` and confirm:

```text
Overflow: top-level items remain reachable and dense panel content scrolls instead of clipping.
SimpleLinksOnly: all items render as links and no empty panel appears.
```

Expected: L1 and L2 overflow can be validated through mock data.

---

### Task 6: Final Verification And Handoff

**Files:**
- Inspect: git status and final diff

- [ ] **Step 1: Run final static checks**

Run:

```bash
pnpm lint
pnpm build:storybook
```

Expected: both commands pass, or any unrelated pre-existing failures are documented with file paths and why they are unrelated.

- [ ] **Step 2: Confirm no forbidden files changed**

Run:

```bash
git diff --name-only HEAD~3..HEAD
git status --short
```

Expected committed implementation files are:

```text
src/components/DesktopMegaMenu/DesktopMegaMenu.types.ts
src/components/DesktopMegaMenu/DesktopMegaMenu.mock.tsx
src/components/DesktopMegaMenu/DesktopMegaMenu.component.tsx
src/components/DesktopMegaMenu/DesktopMegaMenu.stories.tsx
```

Expected no committed changes under:

```text
src/globals/Headers/
src/payload-types.ts
src/payload.config.ts
```

- [ ] **Step 3: Prepare final summary**

Summarize:

```text
Added standalone desktop mega-menu under src/components/DesktopMegaMenu.
Added local types and Storybook mock data.
Added default, overflow, simple-links-only, and pre-open Storybook stories.
Validated click-only opening, close behavior, keyboard basics, overflow behavior, lint, and Storybook build.
No CMS/global Header files were touched.
```

Expected: final handoff clearly states whether `pnpm lint` and `pnpm build:storybook` passed.

## Self-Review Notes

- Spec coverage: covered component location, local types, mock data, Storybook scenarios, click-only opening, outside click, mouse leave, Escape, link-selection close, focus visibility, overflow, no CMS/Header changes, and preserving package changes.
- Red flag scan: no deferred-work tasks remain; every code-writing step includes exact file content.
- Type consistency: all component, mock, and story imports use `DesktopMegaMenu.*` names under `src/components/DesktopMegaMenu`.
