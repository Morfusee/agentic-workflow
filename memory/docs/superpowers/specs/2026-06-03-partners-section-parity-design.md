# Partners Section Parity Design

## Goal

Update the `/partners` page so its partner-category content has page-level sectioning parity with the `Why NGnair` page. The page should keep the existing partner data and logo behavior while making each partner type feel like a distinct section in the page flow.

## Approved Direction

Use the category-as-section approach.

Each partner category becomes its own full-width section with generous vertical spacing, a centered heading and description, and the existing responsive logo grid. This matches the broad rhythm of `Why NGnair` without turning partner logos into cards or implying that they are clickable.

The standalone `Our Partner Network` overview heading should be removed because the hero already introduces the partner ecosystem.

## Page Flow

The route at `src/app/(main)/partners/page.tsx` should continue to render:

1. Shared `HeroSection`
2. `PartnerDirectory`
3. Shared `CTABanner`

Only the body behavior inside `PartnerDirectory` changes. The hero and CTA banner do not need redesigns for this update.

## Section Structure

`src/components/partners/partner-directory.tsx` should render each category from `networkPartnerCategories` as a page-level section:

1. `Banking Partners`
2. `Sponsor Banks`
3. `Technology & Platform Partners`

Each category section should include:

- A full-width `<section>` wrapper.
- Vertical spacing comparable to `Why NGnair`, such as `py-20 md:py-32`.
- A centered heading and short supporting description.
- The existing partner logo grid below the intro.

The current outer `PartnerDirectory` section and its overview heading should be removed so categories are not nested visually inside one large directory block.

## Background Rhythm

Alternate backgrounds to create the same pacing style as `Why NGnair`:

1. Banking Partners: default page background.
2. Sponsor Banks: muted background using `bg-muted/30`.
3. Technology & Platform Partners: default page background.

Use existing site tokens/classes rather than introducing a new visual system. The Sponsor Banks section should use `bg-muted/30` because that directly matches the alternating section treatment on the `Why NGnair` page.

## Data And Component Boundaries

Keep `src/data/network-partners.ts` as the source of truth for:

- Category titles.
- Category descriptions.
- Partner names.
- Logo paths.
- Existing `whiteOnDark` behavior.

Keep the change focused in `PartnerDirectory` unless a very small supporting edit is required elsewhere. The current component is small enough that a focused in-place update is preferable to introducing new abstractions.

## Logo Grid Behavior

Preserve the current logo-grid behavior:

- Mobile: 2 logos per row.
- Tablet: 4 logos per row.
- Desktop: 5 logos per row.
- Logos remain informational only.
- Logos should not be wrapped in links.
- No hover treatment should imply clickability.
- `next/image` usage should remain.
- Current dark-mode handling, including `whiteOnDark`, should remain unchanged.

## Error Handling

The page remains static and does not need runtime error handling.

The implementation should not add or change asset paths. Existing logo omissions and asset confidence are already handled by the current data and missing-logo documentation.

## Verification

Run:

- `pnpm lint`
- `pnpm build`

Browser-check `/partners` at mobile, tablet, and desktop widths:

- The page moves from hero directly into `Banking Partners` without the standalone `Our Partner Network` overview.
- Each partner category reads as a separate page-level section.
- Background alternation is visible and consistent with the `Why NGnair` page rhythm.
- Logo grid column behavior remains unchanged across breakpoints.
- Logos remain legible in light and dark mode.
- Logos do not appear clickable.
- The hero and bottom CTA still render correctly.

## Scope Boundaries

Do not redesign the `/partners` hero, CTA banner, navigation, metadata, sitemap, partner data, or logo assets as part of this update.

Do not refactor unrelated components or change the existing partner application modal behavior.

Preserve all existing user-owned work in the website repository.
