# Desktop Mega Menu Component Design

## Ticket

- ClickUp: `86d36z2nw`
- Title: Implement Navbar desktop mega menu component
- Target branch for implementation: `feat/CU-86d36z2nw_Implement-Navbar-desktop-mega-menu-component`
- Repository worktree: `$HOME\Documents\Programming\worktrees\website-worktree-review`

## Goal

Build a reusable desktop mega-menu component for the Navbar redesign using typed props and mockable data. This ticket should validate the desktop mega-menu in Storybook and avoid production CMS integration.

## Scope

The implementation should live under `src/components`, not under `src/globals/Headers`. All new mega-menu code, types, mock data, and stories belong in the components tree.

In scope:

- Add a desktop mega-menu component under `src/components`.
- Add local component types for top-level items, panels, left brand content, categories, links, view-all links, and CTA content.
- Add local mock data for Storybook validation.
- Add Storybook stories for default, overflow, and simple-link states.
- Support click-only top-level panel opening.
- Support outside click, mouse leave, Escape, and link-selection close behavior.
- Keep links keyboard accessible with visible focus states.
- Validate L1 and L2 overflow with mock data.

Out of scope:

- No changes to `src/globals/Headers`.
- No changes to `MobileNavDrawer.component.tsx`.
- No CMS schema changes.
- No Payload collection/global updates.
- No production Header/Navbar integration.
- No migration of existing `src/globals/Headers/mega-menu.types.ts` or `mega-menu.mock.tsx` in this ticket.

## Current Context

The existing Header and Nav production path lives under `src/globals/Headers` and is CMS-connected through Payload globals and menu records. The repo already contains `mega-menu.types.ts` and `mega-menu.mock.tsx` under `src/globals/Headers`, but the approved design avoids building on that location because it couples the work to CMS/global header code.

The existing mobile drawer remains production code and should not be moved or changed in this ticket. Current user-owned package changes in `package.json` and `pnpm-lock.yaml` must be preserved and not mixed into this work.

## Proposed Component Structure

Create this focused component folder:

```text
src/components/DesktopMegaMenu/
  DesktopMegaMenu.component.tsx
  DesktopMegaMenu.stories.tsx
  DesktopMegaMenu.mock.tsx
  DesktopMegaMenu.types.ts
```

The component must stay fully outside `src/globals/Headers`.

The component owns:

- The desktop trigger row.
- Internal active item state, with an optional `initialOpenIndex` prop only if a pre-open Storybook state is useful.
- The full-width panel layout.
- Close behavior and keyboard handling.
- Rendering of links, category groups, view-all links, and CTA links.

## Data Contract

Define local types equivalent to the needed mega-menu domain model:

- `DesktopMegaMenuData` contains an `items` array.
- `DesktopMegaMenuItem` contains `label`, optional `href`, optional `selected`, and optional `panel`.
- `DesktopMegaMenuPanel` contains `leftPanel` and `categories`.
- `DesktopMegaMenuLeftPanel` contains optional `eyebrow`, `title`, `description`, and optional `cta`.
- `DesktopMegaMenuCategory` contains `title`, optional `icon`, `links`, and optional `viewAll`.
- `MegaMenuLink`, `MegaMenuCTA`, and `MegaMenuViewAllLink` contain label, href, optional `newTab`, and optional descriptive metadata where useful.

The component receives typed props and renders exactly what is passed in. It does not fetch data, map CMS records, or import Payload types.

## Interaction Design

Top-level items are split by capability:

- Items with only `href` render as normal links.
- Items with `panel` render as button triggers and do not redirect.

Opening behavior is click-only:

- Clicking a panel trigger opens its panel.
- Clicking the same trigger again closes it.
- Clicking another trigger swaps to that panel.
- Hover alone does not open a panel.

Close behavior:

- Outside click closes the panel.
- Escape closes the panel.
- Mouse leave from the full menu and panel region closes the panel.
- Selecting a link inside the panel closes the panel.

Keyboard behavior:

- Triggers are reachable by Tab.
- Trigger buttons expose `aria-expanded`.
- Trigger buttons reference the open panel with `aria-controls`.
- Escape should close the panel and return focus to the active trigger if practical.
- Links have visible `focus-visible` states.
- Complex roving tabindex is not required for this ticket.

## Layout Design

The component is desktop-oriented and intended for `xl` and wider viewports. Its root should be hidden below `xl` by default.

The open panel is full-width under the trigger row. It contains:

- A left brand panel with eyebrow, title, description, and optional CTA.
- A right content area with category columns.
- Category blocks with optional icons, headings, links, and optional view-all links.

Overflow handling:

- Top-level item overflow should remain usable in Storybook with many L1 items.
- Panel content should remain usable with many category links.
- Dense panel content may scroll vertically inside a bounded max-height rather than clipping important links.

Styling should follow the existing Tailwind and brand-token conventions in the repo. The component may use the existing reusable `Button` atom where appropriate, but plain `button` and `next/link` are acceptable when they make accessibility and layout simpler.

## Edge Cases

- Empty `items` should return `null`.
- Items with `href` and no `panel` render as links.
- Items with `panel` render as triggers even if `href` is also present.
- Items with neither `href` nor `panel` should be skipped.
- Empty `categories` still allows the left panel to render.
- Empty category `links` should not render blank list chrome.
- `newTab` links must include `target="_blank"` and `rel="noopener noreferrer"`.
- Incomplete mock data should not cause runtime errors.

## Storybook Validation

Add stories that make implementation review possible without touching production Header code:

- Default story using representative mock data.
- Overflow story with many top-level items and dense category links.
- Simple links story with no panels.
- Optional pre-open story if controlled props are included.

Manual validation should confirm:

- Click-only opening works.
- Simple links navigate normally.
- Escape closes the panel.
- Outside click closes the panel.
- Mouse leave closes the panel.
- Link selection closes the panel.
- Focus states are visible for triggers and links.
- Overflow scenarios remain usable.

## Implementation Constraints

- Keep the change additive.
- Do not modify CMS globals, Payload schemas, generated Payload types, or production Header code.
- Do not move `MobileNavDrawer.component.tsx` in this ticket.
- Preserve existing user-owned package changes.
- Use the requested implementation branch: `feat/CU-86d36z2nw_Implement-Navbar-desktop-mega-menu-component`.

## Success Criteria

- A reusable desktop mega-menu exists under `src/components`.
- The component renders from typed props and local mock data.
- Storybook demonstrates default, overflow, and simple-link behavior.
- Links and triggers are keyboard accessible with visible focus states.
- The component supports the requested close behaviors.
- No CMS integration or production Header changes are introduced.
