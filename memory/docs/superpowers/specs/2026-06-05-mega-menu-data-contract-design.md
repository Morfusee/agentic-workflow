# Mega Menu Data Contract Design

Date: 2026-06-05

Source ticket: ClickUp `86d36z2p9` - Define mega menu component data contract

Target repo: `$HOME\Documents\Programming\website`

## Goal

Define a source-of-truth TypeScript data contract for future desktop mega-menu and mobile grouped navigation consumers. The contract should guide the next developer who wires mega-menu components or Storybook examples without being driven by the current `Nav.component.tsx`, `MobileNavDrawer.component.tsx`, Payload `Menu` collection, or Header global schema.

The contract must support the `website3.0-prototype` navbar structure while staying additive and CMS-independent.

## Scope

Implementation should add contract and mock-data files only:

- Add `src/globals/Headers/mega-menu.types.ts` for exported TypeScript contracts.
- Add `src/globals/Headers/mega-menu.mock.tsx` if mock icons use JSX.
- Export Storybook-friendly named mock examples from the mock file.
- Keep existing production navigation behavior unchanged.

Implementation must not change:

- `src/collections/Menu.ts`
- `src/globals/Headers/Header.global.ts`
- Payload Header/Menu relationships
- Existing production render logic in `Nav.component.tsx`, `MobileNavDrawer.component.tsx`, or `Submenu.component.tsx`

## Design Approach

Use colocated header-domain files under `src/globals/Headers`. This follows the existing project convention of keeping header/nav concerns near the header implementation without introducing a premature global `src/types` layer.

Use a hybrid contract shape:

- Shared primitives for links, CTAs, and reusable content pieces.
- Separate top-level contracts for desktop mega-menu data and mobile grouped navigation data.

This avoids a single over-abstract navigation model while keeping repeated concepts consistent across desktop and mobile consumers.

## Type Contract

The contract should define these shared primitives:

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
```

Icons should use `ReactNode` because existing component-level APIs in the website repo use renderable React icons for component props, such as `Button`, `CardMolecule`, and `FloatingButton`. CMS/block data may still use strings or uploads elsewhere, but this contract is component-facing and CMS-independent.

### Desktop Contract

The desktop contract should support both direct navigation links and mega-menu triggers:

```ts
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

This covers the prototype details:

- Direct links such as Home, FAQ, and About Us.
- Mega-menu triggers such as College Programs, Certification Program, Admission, and News & Events.
- A desktop left panel with eyebrow, title, description, and CTA.
- Category columns with icons, L2 links, and category-level view-all links.

### Mobile Contract

The mobile contract should model grouped navigation data separately from desktop flyout behavior:

```ts
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

This covers the prototype details:

- Search copy such as placeholder and button label.
- Optional popular search suggestions as data only.
- Quick links card.
- Multiple mobile section/card treatments represented semantically by `tone`, not by raw Tailwind classes.
- Bottom drawer CTA.

The contract should not model search callback functions, click handlers, hover handlers, animations, reduced-motion behavior, or raw styling classes. Those remain component responsibilities.

## Mock Data

The mock data should optimize for developer clarity rather than exact production content or CMS mapping.

The mock file should export Storybook-friendly named examples:

- `desktopMegaMenuMock`
- `mobileGroupedNavMock`
- `megaMenuMockData` as `{ desktop, mobile }` for combined consumers

Mock data should use MMDC/prototype-inspired labels and routes so examples feel realistic, while making clear that the data is sample component data rather than CMS schema or production content.

The desktop mock should demonstrate:

- At least one direct top-level link.
- Multiple mega-menu triggers.
- A fully populated left panel with eyebrow, title, description, and CTA.
- Category icons using JSX/lucide components.
- Category links and view-all links.

The mobile mock should demonstrate:

- Search placeholder and button label.
- Quick links.
- Multiple section tones such as `highlight`, `brand`, `dark`, `danger`, `muted`, and `default`.
- Plain link sections for simple pages.
- Bottom CTA data.

If JSX icons are used, the mock file should use a `.tsx` extension. The type contract file should remain `.ts` and import only `ReactNode` as a type.

## Boundaries

The contract is intentionally independent from Payload and existing render logic:

- Do not import `Menu` from `@/payload-types` into the contract.
- Do not update Payload collections or globals.
- Do not map current CMS menu data into the new contract in this ticket.
- Do not refactor current navigation components to consume the new contract in this ticket.
- Do not encode prototype Tailwind classes into data.

Future CMS integration can map Payload/Header/Menu data into this contract later, but that mapping is outside this ticket.

## Verification

Because this is contract-only work, verification should focus on type safety and non-regression:

- Run the closest available TypeScript validation command for the repo.
- Run lint if the repo command is available and not blocked by unrelated project issues.
- Confirm no changes were made to CMS schema files, Header global relationships, or production render logic.
- Confirm `.tsx` mock exports compile if JSX icons are used.
- Confirm the website working tree only contains the intended additive contract/mock files after implementation.

No browser QA, Storybook story creation, CMS migration testing, or visual regression testing is required for this ticket unless implementation later expands beyond the approved scope.

## Acceptance Criteria

- The website repo contains a colocated mega-menu type contract under `src/globals/Headers`.
- The contract models desktop mega-menu data and mobile grouped navigation data using shared primitives and separate top-level shapes.
- The contract supports the prototype's direct links, mega-menu triggers, left panel content, category groups, L2 links, view-all links, optional icons, CTA data, mobile quick links, mobile search copy, and mobile section tones.
- Mock data exports are named and Storybook-friendly.
- The implementation is additive and does not modify CMS schemas, Header global relationships, or production navigation behavior.
