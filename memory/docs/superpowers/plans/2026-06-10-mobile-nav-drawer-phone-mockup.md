# MobileNavDrawer Phone Mockup Story Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `PhoneMockup` story to `MobileNavDrawer.stories.tsx` that renders the drawer inside a polished smartphone device frame with a hamburger toggle.

**Architecture:** A single `ControlledPhoneMockup` wrapper component added to the existing stories file — uses `useState` for open/close state, `IconButton` (with `Menu`/`X` icons) as toggle, and an inline Tailwind phone frame matching the Kitchen Sink prototype pattern. No new files, no new deps, no component changes.

**Tech Stack:** React, TypeScript, Tailwind CSS, Storybook 8, lucide-react, existing `IconButton` component

---

### File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `src/components/MobileNavDrawer/MobileNavDrawer.stories.tsx` | Modify | Add phone mockup wrapper + `PhoneMockup` story |

---

### Task 1: Add `PhoneMockup` story

**Files:**
- Modify: `src/components/MobileNavDrawer/MobileNavDrawer.stories.tsx`

- [ ] **Step 1: Add new imports**

Add `useState` from React, `Menu` and `X` from lucide-react, and the `IconButton` component import at the top of the file.

Replace the existing import block at lines 1-4:

```tsx
import { useState } from 'react'
import type { Meta, StoryObj } from '@storybook/react'
import { expect, fn, userEvent, within } from 'storybook/test'
```

With:

```tsx
import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import type { Meta, StoryObj } from '@storybook/react'
import { expect, fn, userEvent, within } from 'storybook/test'
```

And add the `IconButton` import after the `MobileNavDrawer` import (after line 4):

```tsx
import MobileNavDrawer from './MobileNavDrawer.component'
import { IconButton } from '@/components/IconButton/IconButton.component'
```

Resulting imports block (lines 1-6):

```tsx
import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import type { Meta, StoryObj } from '@storybook/react'
import { expect, fn, userEvent, within } from 'storybook/test'

import { IconButton } from '@/components/IconButton/IconButton.component'
import MobileNavDrawer from './MobileNavDrawer.component'
```

- [ ] **Step 2: Add `ControlledPhoneMockup` wrapper component**

Insert the wrapper component after the `mockSections` array (after line 78's closing `]`) and before the `Default` story (before line 80's `export const Default`).

```tsx
const ControlledPhoneMockup = (args: React.ComponentProps<typeof MobileNavDrawer>) => {
  const [open, setOpen] = useState(false)

  return (
    <div className="flex items-center justify-center p-8">
      <div className="w-[360px] h-[640px] border-8 border-zinc-800 rounded-[40px] overflow-hidden relative shadow-2xl bg-white flex flex-col shrink-0">
        {/* Notch */}
        <div className="absolute top-2 left-1/2 -translate-x-1/2 w-28 h-4 bg-zinc-800 rounded-full z-50 flex items-center justify-center">
          <div className="w-8 h-1 bg-zinc-600 rounded-full" />
        </div>

        {/* Screen */}
        <div className="flex-1 overflow-y-auto pt-6 bg-zinc-50 flex flex-col">
          {/* Mock Header */}
          <div className="sticky top-0 z-40 flex items-center justify-between border-b border-line bg-white px-4 py-2.5">
            <IconButton
              icon={open ? <X /> : <Menu />}
              label={open ? 'Close mobile navigation' : 'Open mobile navigation'}
              variant="ghost"
              size="md"
              onClick={() => setOpen(!open)}
            />
            <div className="text-base font-extrabold text-brand-blue">MMDC</div>
            <div className="w-[44px]" />
          </div>

          {/* Mock Page Content */}
          <div className="flex-1 space-y-4 p-4">
            <div className="h-40 rounded-xl bg-zinc-200 animate-pulse" />
            <div className="space-y-2">
              <div className="h-4 w-3/4 rounded bg-zinc-200" />
              <div className="h-4 w-1/2 rounded bg-zinc-200" />
            </div>
            <div className="h-20 rounded-xl bg-zinc-200 animate-pulse" />
            <div className="space-y-2">
              <div className="h-4 w-5/6 rounded bg-zinc-200" />
              <div className="h-4 w-2/3 rounded bg-zinc-200" />
              <div className="h-4 w-1/2 rounded bg-zinc-200" />
            </div>
          </div>
        </div>

        {/* Drawer */}
        <MobileNavDrawer {...args} open={open} onClose={() => setOpen(false)} />
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Add `PhoneMockup` story export**

Append after the `WithSelectedLink` story (after line 159's closing `},`):

```tsx
export const PhoneMockup: Story = {
  render: (args) => <ControlledPhoneMockup {...args} />,
  args: {
    ...Default.args,
    open: false,
  },
  parameters: {
    layout: 'fullscreen',
  },
}
```

- [ ] **Step 4: Verify the story renders in Storybook**

Run Storybook dev server and confirm the `PhoneMockup` story appears under Components/MobileNavDrawer:

```bash
npm run storybook
```

Expected: A phone frame (360×640px) with a header, placeholder content, and a hamburger button that toggles the MobileNavDrawer open/closed.

- [ ] **Step 5: Commit**

```bash
git add src/components/MobileNavDrawer/MobileNavDrawer.stories.tsx
git commit -m "feat: add phone mockup story for MobileNavDrawer"
```
