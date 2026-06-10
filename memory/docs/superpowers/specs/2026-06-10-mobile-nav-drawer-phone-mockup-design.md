# MobileNavDrawer Phone Mockup Story

**Date:** 2026-06-10
**Status:** approved

## Goal

Add a Storybook story variant for `MobileNavDrawer` that renders inside a polished smartphone device frame with a hamburger toggle button, providing an interactive phone-shaped preview.

## Scope

- One new phone-mockup story variant in `MobileNavDrawer.stories.tsx`
- Inline phone frame (no new components, no new dependencies)
- Stateful toggle via `useState`
- Existing stories remain untouched

## Phone Frame

Follows the Kitchen Sink pattern from `website3.0-prototype`:

- Outer shell: `w-[360px] h-[640px] border-8 border-zinc-800 rounded-[40px] overflow-hidden shadow-2xl bg-white`
- Notch: absolute centered at top, `w-28 h-4 bg-zinc-800 rounded-full` with inner camera dot `w-8 h-1 bg-zinc-600 rounded-full`
- Screen area: `flex-1 overflow-y-auto pt-6 bg-zinc-50` (pt-6 clears the notch)

## Mock Page Content

Inside the phone screen, above the drawer:

- A mock header bar with a hamburger button and a placeholder logo
- The hamburger uses the existing `IconButton` component with `<Menu />` icon when drawer is closed, `<X />` when open (following the project's `HamburgerTrigger` pattern)
- Below the header, simple placeholder content (a few lines of text or colored blocks) to represent a real page

## State Management

A `ControlledPhoneMockup` wrapper component inside the stories file:

```tsx
const ControlledPhoneMockup: React.FC<MobileNavDrawerProps> = (args) => {
  const [open, setOpen] = useState(false)
  return (
    <PhoneFrame>
      <MockHeader onToggle={() => setOpen(!open)} isOpen={open} />
      <MockContent />
      <MobileNavDrawer {...args} open={open} onClose={() => setOpen(false)} />
    </PhoneFrame>
  )
}
```

Follows the existing controlled-state story pattern from `GlobalSearch.stories.tsx`.

## Story Definition

```tsx
export const PhoneMockup: Story = {
  render: (args) => <ControlledPhoneMockup {...args} />,
  args: {
    ...Default.args,
    open: false,
  },
}
```

`open: false` in args so the drawer starts closed in the phone preview.

## Non-Goals

- No changes to the `MobileNavDrawer` component itself
- No new npm dependencies
- No new component files — everything lives in the stories file
- No modification of existing stories
- No dedicated PhoneFrame component exported from the project (it's story-only)
