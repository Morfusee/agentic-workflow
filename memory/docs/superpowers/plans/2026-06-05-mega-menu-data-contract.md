# Mega Menu Data Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a CMS-independent, source-of-truth TypeScript contract and Storybook-friendly mock data for desktop mega-menu and mobile grouped navigation consumers.

**Architecture:** Add two focused files under `src/globals/Headers`: one `.ts` file for reusable type contracts and one `.tsx` file for JSX icon mock data. Do not wire these files into current production components; this ticket is contract-only and must leave existing navigation and Payload schema behavior unchanged.

**Tech Stack:** Next.js, React 19, TypeScript 5.7, lucide-react, pnpm.

---

## File Structure

- Create: `src/globals/Headers/mega-menu.types.ts`
- Responsibility: Own exported, CMS-independent desktop mega-menu and mobile grouped-navigation type contracts.
- Create: `src/globals/Headers/mega-menu.mock.tsx`
- Responsibility: Export Storybook-friendly mock data that demonstrates every contract field using prototype-inspired MMDC content.
- Do not modify: `src/collections/Menu.ts`, `src/globals/Headers/Header.global.ts`, `src/globals/Headers/Nav.component.tsx`, `src/globals/Headers/MobileNavDrawer.component.tsx`, `src/globals/Headers/Submenu.component.tsx`.

## Task 1: Add The Type Contract

**Files:**
- Create: `src/globals/Headers/mega-menu.types.ts`

- [ ] **Step 1: Confirm the website worktree is clean enough to start**

Run:

```bash
git status --short
git diff
```

Expected: either no output, or only unrelated user-owned changes. Do not revert unrelated changes.

- [ ] **Step 2: Create the contract file**

Create `src/globals/Headers/mega-menu.types.ts` with exactly this content:

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

export type MobileGroupedNavData = {
  search?: MobileNavSearchConfig
  quickLinks?: MegaMenuLink[]
  sections: MobileNavSection[]
  cta?: MegaMenuCTA
}

export type MobileNavSearchConfig = {
  enabled?: boolean
  placeholder?: string
  buttonLabel?: string
  popularSuggestions?: string[]
}

export type MobileNavSectionTone = 'default' | 'highlight' | 'brand' | 'dark' | 'danger' | 'muted'

export type MobileNavSection = {
  title?: string
  tone?: MobileNavSectionTone
  links: MegaMenuLink[]
}
```

- [ ] **Step 3: Run TypeScript validation for the new type file**

Run:

```bash
pnpm exec tsc --noEmit --pretty false
```

Expected: command exits with code `0`, or fails only with pre-existing unrelated project errors. If it fails, save the full output for review and do not change unrelated files.

- [ ] **Step 4: Inspect the diff**

Run:

```bash
git diff -- src/globals/Headers/mega-menu.types.ts
```

Expected: only the new `mega-menu.types.ts` file appears.

- [ ] **Step 5: Commit the type contract**

Run:

```bash
git add src/globals/Headers/mega-menu.types.ts
git commit -m "feat(headers): add mega menu data contract"
```

Expected: commit succeeds and includes only `src/globals/Headers/mega-menu.types.ts`.

## Task 2: Add Storybook-Friendly Mock Data

**Files:**
- Create: `src/globals/Headers/mega-menu.mock.tsx`

- [ ] **Step 1: Confirm only intended files are pending**

Run:

```bash
git status --short
git diff
```

Expected: no pending changes after Task 1 commit, or only unrelated user-owned changes. Do not modify unrelated changes.

- [ ] **Step 2: Create the mock data file**

Create `src/globals/Headers/mega-menu.mock.tsx` with exactly this content:

```tsx
import { Award, BookOpen, Calendar, CreditCard, GraduationCap, Info, Newspaper } from 'lucide-react'

import type { DesktopMegaMenuData, MobileGroupedNavData } from './mega-menu.types'

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

export const mobileGroupedNavMock = {
  search: {
    enabled: true,
    placeholder: 'Search courses, articles...',
    buttonLabel: 'Go',
    popularSuggestions: ['AI Specialist', 'Scholarships', 'Tuition Fee', 'Virtual Assistant'],
  },
  quickLinks: [
    { label: 'College Programs', href: '/programs' },
    { label: 'Certification', href: '/certifications' },
    { label: 'Tuition Fee', href: '/admission/fees' },
    { label: 'Scholarship', href: '/admission/scholarships' },
  ],
  sections: [
    {
      title: 'College Programs',
      tone: 'brand',
      links: [
        { label: 'AI Specialist', href: '/programs/it-ai' },
        { label: 'Web Development', href: '/programs/it-web' },
        { label: 'Cyber Security', href: '/programs/it-cyber' },
        { label: 'Digital Marketing', href: '/programs/ba-marketing' },
        { label: 'Entrepreneurship', href: '/programs/ba-entrepreneur' },
        { label: 'Business Management', href: '/programs/ba-management' },
      ],
    },
    {
      title: 'Certifications',
      tone: 'dark',
      links: [
        { label: 'AI & ML Basics', href: '/certifications/ai-basics' },
        { label: 'Web Dev Bootcamp', href: '/certifications/web-bootcamp' },
        { label: 'Cloud Computing Essentials', href: '/certifications/cloud' },
        { label: 'Virtual Assistant Program', href: '/certifications/va' },
        { label: 'SEO & Content Marketing', href: '/certifications/seo' },
        { label: 'Event Management', href: '/certifications/events' },
      ],
    },
    {
      title: 'Admissions',
      tone: 'danger',
      links: [
        { label: 'Scholarships & Grants', href: '/admission/scholarships' },
        { label: 'Fees and Tuition', href: '/admission/fees' },
        { label: 'Admission Requirements', href: '/admission/requirements' },
        { label: 'Academic Calendar', href: '/admission/calendar' },
      ],
    },
    {
      title: 'News & Publications',
      tone: 'muted',
      links: [
        { label: 'Blogs & Articles', href: '/news/blog' },
        { label: 'Lifestyle Tips', href: '/news/lifestyle' },
        { label: 'Student Stories', href: '/news/student-life' },
        { label: 'Official Announcements', href: '/news/announcements' },
      ],
    },
    {
      title: 'Quick Links',
      tone: 'highlight',
      links: [
        { label: 'Apply Now', href: '/admission/apply' },
        { label: 'Payment Options', href: '/admission/payment' },
      ],
    },
    {
      tone: 'default',
      links: [
        { label: 'Home', href: '/' },
        { label: 'FAQ', href: '/faq' },
        { label: 'About Us', href: '/about' },
      ],
    },
  ],
  cta: {
    label: 'Apply Now',
    href: '/admission/apply',
  },
} satisfies MobileGroupedNavData

export const megaMenuMockData = {
  desktop: desktopMegaMenuMock,
  mobile: mobileGroupedNavMock,
}
```

- [ ] **Step 3: Run TypeScript validation for JSX mock data**

Run:

```bash
pnpm exec tsc --noEmit --pretty false
```

Expected: command exits with code `0`, or fails only with pre-existing unrelated project errors. If it fails because of the new files, fix only `src/globals/Headers/mega-menu.types.ts` or `src/globals/Headers/mega-menu.mock.tsx`.

- [ ] **Step 4: Inspect the diff**

Run:

```bash
git diff -- src/globals/Headers/mega-menu.mock.tsx src/globals/Headers/mega-menu.types.ts
```

Expected: only the new mock file appears if Task 1 was committed. If Task 1 was not committed, both new files may appear.

- [ ] **Step 5: Commit the mock data**

Run:

```bash
git add src/globals/Headers/mega-menu.mock.tsx
git commit -m "feat(headers): add mega menu mock data"
```

Expected: commit succeeds and includes only `src/globals/Headers/mega-menu.mock.tsx`.

## Task 3: Final Verification

**Files:**
- Verify: `src/globals/Headers/mega-menu.types.ts`
- Verify: `src/globals/Headers/mega-menu.mock.tsx`
- Verify unchanged: `src/collections/Menu.ts`
- Verify unchanged: `src/globals/Headers/Header.global.ts`
- Verify unchanged: `src/globals/Headers/Nav.component.tsx`
- Verify unchanged: `src/globals/Headers/MobileNavDrawer.component.tsx`
- Verify unchanged: `src/globals/Headers/Submenu.component.tsx`

- [ ] **Step 1: Run TypeScript validation**

Run:

```bash
pnpm exec tsc --noEmit --pretty false
```

Expected: command exits with code `0`, or reports only unrelated pre-existing project errors that are documented in the handoff.

- [ ] **Step 2: Run lint**

Run:

```bash
pnpm lint
```

Expected: command exits with code `0`, or reports only unrelated pre-existing project errors that are documented in the handoff.

- [ ] **Step 3: Confirm forbidden files were not changed**

Run:

```bash
git diff -- src/collections/Menu.ts src/globals/Headers/Header.global.ts src/globals/Headers/Nav.component.tsx src/globals/Headers/MobileNavDrawer.component.tsx src/globals/Headers/Submenu.component.tsx
```

Expected: no output.

- [ ] **Step 4: Confirm final working tree state**

Run:

```bash
git status --short
```

Expected: no output after the implementation commits, or only unrelated user-owned changes that existed before execution.

- [ ] **Step 5: Prepare final handoff summary**

Report these facts:

```text
Implemented:
- Added src/globals/Headers/mega-menu.types.ts as the CMS-independent source-of-truth contract.
- Added src/globals/Headers/mega-menu.mock.tsx with Storybook-friendly desktop, mobile, and combined mock exports.

Verified:
- TypeScript validation result: command exit code and the exact terminal output from pnpm exec tsc --noEmit --pretty false.
- Lint result: command exit code and the exact terminal output from pnpm lint.
- Forbidden production/CMS files changed: no
```

## Self-Review

- Spec coverage: Tasks 1 and 2 cover the colocated contract, hybrid desktop/mobile types, ReactNode icons, prototype-supported fields, Storybook-friendly mocks, and contract-only scope. Task 3 covers type safety, lint, and forbidden-file non-regression.
- Placeholder scan: The only use of the word `placeholder` refers to the `MobileNavSearchConfig.placeholder` field and search copy; it is not an unfinished plan placeholder.
- Type consistency: `DesktopMegaMenuData`, `MobileGroupedNavData`, `MegaMenuLink`, `MegaMenuCTA`, `MegaMenuViewAllLink`, `DesktopMegaMenuItem`, `DesktopMegaMenuPanel`, `DesktopMegaMenuLeftPanel`, `DesktopMegaMenuCategory`, `MobileNavSearchConfig`, `MobileNavSectionTone`, and `MobileNavSection` are consistently named across the type file and mock file.
