# Reusable Block Audit From MMDC Certifications Mockup

Audit date: 2026-05-27
Mockup checked: https://mmdc-certifications-page.fenunez.com/
Browser artifact: `memory/audits/website/mmdc-certifications-block-audit.png`

## Scope

This audit uses the MMDC certifications mockup as a reference page, but the recommended blocks below are intentionally generic. The goal is not to create one-off certification components. The goal is to identify reusable Payload CMS blocks that can support landing pages, program pages, product pages, admissions pages, campaign pages, and future certification pages with the same system.

## Codebase Conventions Observed

- Blocks live under `src/blocks/<BlockName>/` and usually split into `*.block.ts`, `*.component.tsx`, optional `*.renderer.tsx`, and optional Storybook stories.
- Payload layout blocks are registered in `src/collections/Pages.ts` in the `LayoutBlocks` array.
- Public rendering is dynamic through `src/utilities/RenderBlocks.tsx`, which imports `@/blocks/${blockType}/${blockType}.renderer.tsx` first and falls back to `*.component.tsx`.
- Nested CMS composition is already common. `Container`, `Grid`, `Tabs`, `Carousel`, `Flex`, and `Accordion` accept nested blocks and delegate rendering through renderers or children.
- Styling is CMS-controlled through `StyleField` and rendered by `useStyling`, with responsive spacing and max-width classes.
- The design language is Tailwind-driven, using `primary` `#1E3A8A`, `secondary` `#C02C36`, white, muted gray, and `background` `#F5F5F5`.
- Components favor compact cards, `rounded-xl`/`rounded-lg`, light shadows, thin borders, responsive grids, and restrained CTAs.

## Reusable Block Principles

- Name blocks after layout/content patterns, not page subjects. Prefer `SplitHero` over `CertificationHero`, `MetricStrip` over `ProgramFactStrip`, and `ProofSection` over `PartnerProof`.
- Keep data structured when editors repeat items. Arrays of cards, facts, logos, modules, plans, and quotes should be first-class fields instead of rich-text formatting.
- Use variants sparingly. A good block can support a few layout variants, but should not become a catch-all page builder inside a page builder.
- Preserve current system conventions: `StyleField`, `ButtonField`, upload relations to `images`, optional renderers only for nested Payload blocks, and Storybook stories for each visual block.
- Reuse existing generic blocks where composition stays editor-friendly. Add a block when the current composition would force editors to manage fragile spacing, nested rich text, or repeated visual semantics manually.

## Mockup Section Inventory

| Mockup section | Current coverage | Generic recommendation |
| --- | --- | --- |
| Sticky header and footer | Existing globals | Use existing `Header` and `Footer`; no page block required. |
| Hero with badge, rating, CTAs, and image | Partial: existing `Hero` is image-background/overlay oriented | Add generic `SplitHero`. |
| Quick facts strip | Partial: can be forced with `Grid` + `IconCard` | Add generic `MetricStrip`. |
| Logos plus quote cards | Partial: `BrandPartners` handles global marquee logos only | Add generic `ProofSection`. |
| Benefit/stat cards | Mostly covered by `Grid` + `IconCard` | Reuse existing blocks unless exact card semantics are needed. |
| Learning/module cards | Partial: `Grid` + `List` can approximate, but nested lists are awkward | Add generic `StructuredCardGroup`. |
| Pricing/payment cards | Not covered | Add generic `PlanCards`. |
| Lead form with intro and card shell | Partial: `LeadForm` exists, but field support and section shell are limited | Add generic `FormSection` and form field enhancements. |
| Accreditation/recognition logo row | Partial: possible with `Image` in `Grid`, but awkward | Add generic `LogoStrip`. |
| Learner/testimonial cards | Partial: `Carousel` + `ProfileCard` can approximate | Add generic `QuoteCarousel` or extend `Carousel` with quote-card slides. |
| FAQ accordion | Existing `Accordion` | Use existing block. |
| Blue conversion CTA | Existing `Container` + `RichText` + `Button` | Reuse existing blocks. |
| Resource/article cards | Partial: `ArticleCategory` is category-driven and dark-primary | Add generic `ContentCards`. |

## Recommended Generic Blocks and Components

### 1. `SplitHero`

Component files needed:
- `src/blocks/SplitHero/SplitHero.block.ts`
- `src/blocks/SplitHero/SplitHero.component.tsx`
- `src/blocks/SplitHero/SplitHero.stories.tsx`

Short description:
A reusable two-column hero for landing, product, program, admissions, and campaign pages. It supports an eyebrow/badge, headline, body copy, optional proof metadata, one or two CTAs, and an image or media panel. In the mockup, this maps to the top section with the IBM badge, title, rating, CTAs, and student image.

Suggested Payload fields:
- `eyebrow`
- `title`
- `body`
- `proofItems` array with `icon`, `label`, optional `value`
- `media` upload relation to `images`
- `mediaPosition`: `left` or `right`
- `primaryButton` via existing `ButtonField`
- `secondaryButton` via existing `ButtonField`
- `variant`: `default`, `light`, `brand`, `minimal`
- `StyleField`

Why this should be generic:
The same layout can serve degree pages, scholarship pages, event campaigns, article landing pages, and lead-generation pages. Nothing in the component should know about certifications.

### 2. `MetricStrip`

Component files needed:
- `src/blocks/MetricStrip/MetricStrip.block.ts`
- `src/blocks/MetricStrip/MetricStrip.component.tsx`
- `src/blocks/MetricStrip/MetricStrip.stories.tsx`

Short description:
A responsive strip of compact facts, stats, or highlights. Each item has optional icon, label, value, and supporting text. In the mockup, this maps to program length, cost, and next start date.

Suggested Payload fields:
- `items` array with `icon`, `label`, `value`, `description`
- `columns` select or number, default `3`
- `alignment`: `left` or `center`
- `variant`: `cards`, `inline`, `bordered`
- `StyleField`

Why this should be generic:
The same block can show program facts, application deadlines, scholarship amounts, event details, campus stats, performance metrics, or partner counts.

### 3. `ProofSection`

Component files needed:
- `src/blocks/ProofSection/ProofSection.block.ts`
- `src/blocks/ProofSection/ProofSection.component.tsx`
- `src/blocks/ProofSection/ProofSection.stories.tsx`

Short description:
A trust/social-proof section that combines section copy, logos, and optional quote cards. In the mockup, this maps to the industry leader logo row and company representative quotes.

Suggested Payload fields:
- `title`
- `subtitle`
- `logos` array with `image`, `name`, optional `url`
- `quotes` array with `quote`, `name`, `role`, `organization`, optional `avatar`
- `logoDisplay`: `static`, `marquee`, `grid`
- `quoteDisplay`: `cards`, `carousel`, `hidden`
- `StyleField`

Why this should be generic:
This pattern covers partners, employers, accreditors, press mentions, outcomes proof, client logos, and alumni/company testimonials.

### 4. `StructuredCardGroup`

Component files needed:
- `src/blocks/StructuredCardGroup/StructuredCardGroup.block.ts`
- `src/blocks/StructuredCardGroup/StructuredCardGroup.component.tsx`
- `src/blocks/StructuredCardGroup/StructuredCardGroup.stories.tsx`

Short description:
A grid or carousel of structured cards where each card can include eyebrow text, title, body, icon/image, checklist items, and optional CTA. In the mockup, this maps to the module cards in the `What You'll Learn` section, but it can also cover benefits, steps, requirements, learning paths, or feature comparisons.

Suggested Payload fields:
- `title`
- `subtitle`
- `cards` array with `eyebrow`, `title`, `body`, `image`, `icon`, `items`, optional `button`
- `cardLayout`: `default`, `checklist`, `numbered`, `media`
- `columns`
- `carouselOnMobile`
- `StyleField`

Why this should be generic:
This avoids creating narrow blocks like `CurriculumModules`, `AdmissionsSteps`, or `BenefitCards` when the underlying pattern is a repeated structured card.

### 5. `PlanCards`

Component files needed:
- `src/blocks/PlanCards/PlanCards.block.ts`
- `src/blocks/PlanCards/PlanCards.component.tsx`
- `src/blocks/PlanCards/PlanCards.stories.tsx`

Short description:
A reusable plan/package/card comparison block with highlighted cards, pricing or non-pricing labels, feature lists, and CTAs. In the mockup, this maps to the individual and team pricing cards.

Suggested Payload fields:
- `title`
- `subtitle`
- `plans` array with `name`, `summary`, `price`, `pricePrefix`, `priceSuffix`, `badge`, `highlighted`, `features`, `button`
- `comparisonMode`: `pricing`, `package`, `option`
- `columns`
- `StyleField`

Why this should be generic:
The same component can present tuition plans, payment options, scholarship packages, enrollment tracks, service tiers, event passes, or downloadable bundles.

### 6. `FormSection` and Form Field Enhancements

Component files needed:
- `src/blocks/FormSection/FormSection.block.ts`
- `src/blocks/FormSection/FormSection.component.tsx`
- optional `src/blocks/FormSection/FormSection.renderer.tsx`
- `src/components/Form/fields/RadioFormField.tsx`
- `src/components/Form/fields/TextareaFormField.tsx`

Short description:
A generic section wrapper for any Payload form. It provides title, subtitle, optional supporting content, background treatment, and form-card presentation while continuing to use the existing `forms` collection. In the mockup, this maps to the `Start Learning Now` form.

Suggested Payload fields for the wrapper:
- `title`
- `subtitle`
- `body` via `RichTextField`
- `form` relationship to `forms`
- `layout`: `centered`, `split`, `card`
- `StyleField`

Required form-builder work:
- Enable or add a `radio` field block.
- Enable or add a `textarea` field block.
- Register both in `FormFieldComponents` in `src/components/Form/fields/FormFields.tsx`.

Why this should be generic:
The existing `LeadForm` name is narrow. A generic `FormSection` can support inquiry forms, event registration, brochure downloads, applications, newsletter signups, contact forms, and campaign funnels.

### 7. `LogoStrip`

Component files needed:
- `src/blocks/LogoStrip/LogoStrip.block.ts`
- `src/blocks/LogoStrip/LogoStrip.component.tsx`
- `src/blocks/LogoStrip/LogoStrip.stories.tsx`

Short description:
A static or lightly responsive row/grid of logos with optional title and copy. In the mockup, this maps to accreditation and recognition logos.

Suggested Payload fields:
- `title`
- `body` via `RichTextField`
- `logos` array with `image`, `name`, optional `url`
- `display`: `row`, `grid`, `wrapped`
- `StyleField`

Why this should be generic:
This covers accreditations, partner marks, press logos, platform logos, award badges, school affiliations, and employer logos without depending on the global `Partners` data model.

### 8. `QuoteCarousel`

Component files needed:
- `src/blocks/QuoteCarousel/QuoteCarousel.block.ts`
- `src/blocks/QuoteCarousel/QuoteCarousel.component.tsx`
- `src/blocks/QuoteCarousel/QuoteCarousel.stories.tsx`

Short description:
A carousel or grid for quotes, testimonial cards, social proof screenshots, or image-first endorsements. In the mockup, this maps to the learner testimonial cards.

Suggested Payload fields:
- `title`
- `subtitle`
- `items` array with `image`, `quote`, `name`, `role`, `organization`
- `displayMode`: `quote-card`, `image-card`, `mixed`
- `autoplay`
- `showIndicators`
- `StyleField`

Why this should be generic:
The same block can render learner stories, alumni quotes, employer feedback, event testimonials, partner endorsements, or press pull quotes.

### 9. `ContentCards`

Component files needed:
- `src/blocks/ContentCards/ContentCards.block.ts`
- `src/blocks/ContentCards/ContentCards.component.tsx`
- `src/blocks/ContentCards/ContentCards.stories.tsx`

Short description:
A generic card grid for related content. Cards may be manually entered or pulled from the `articles` collection. In the mockup, this maps to learning resources and insights.

Suggested Payload fields:
- `title`
- `subtitle`
- `source`: `manual` or `articles`
- `manualItems` array with `image`, `badge`, `title`, `excerpt`, `link`, `newTab`
- `articles` relationship array to `articles`
- `button` via `ButtonField`
- `columns`
- `StyleField`

Why this should be generic:
This can power resource sections, related articles, next steps, guides, downloads, webinars, news previews, and campaign follow-up content. It should not be tied to a category page layout.

## Existing Blocks to Reuse

- `Accordion`: use for FAQ and expandable informational sections.
- `Container`: use as a section wrapper for CTA, background, rounded, and spacing control.
- `Grid`: use for simple repeated item layouts where cards do not need special semantics.
- `IconCard`: use for small icon/stat/benefit cards where no nested checklist or price logic is needed.
- `BasicCard`: use for simple image/title/body/button cards.
- `Carousel`: reuse internally for generic carousel behavior, or compose it inside `QuoteCarousel`/`StructuredCardGroup`.
- `Button`: use for all CTAs through `ButtonField` so links, new-tab behavior, and colors remain consistent.
- `RichText`: use for section intro copy and body copy.
- `Image`: use for uploaded media and logos.

## Payload Integration Checklist

For every new block:

1. Add the block definition file under `src/blocks/<BlockName>/<BlockName>.block.ts`.
2. Add the React component under `src/blocks/<BlockName>/<BlockName>.component.tsx`.
3. Add a renderer only if the block renders nested Payload blocks.
4. Export the component from `src/blocks/components.ts` if it will be consumed by other blocks.
5. Import and register the block in `LayoutBlocks` in `src/collections/Pages.ts`.
6. Use `StyleField` for section spacing/background control unless the block is intentionally presentational only.
7. Prefer arrays/groups over rich-text-only content when editors need structured repeated items.
8. Add a focused Storybook story for visual regression and editor-intent documentation.

## Recommended Build Order

1. `SplitHero`, `MetricStrip`, and `PlanCards`: highest-impact reusable landing-page blocks.
2. `FormSection` plus radio/textarea field support: needed for conversion workflows across multiple page types.
3. `StructuredCardGroup`, `ProofSection`, and `LogoStrip`: reusable trust, feature, and information-density sections.
4. `QuoteCarousel` and `ContentCards`: useful for social proof and related content, with lower implementation risk.

## Notes and Risks

- The current `BrandPartnersBlock` has only `StyleField`; its component expects `brands` from global data. If it is used directly in page layout without a renderer injecting global partners, it may not have the data it needs.
- The existing form plugin disables `message` fields and the local renderer has no radio or textarea component. The mockup form cannot be faithfully recreated until those fields are supported.
- Existing `Hero` could receive a new split variant, but a generic `SplitHero` is cleaner because it avoids overloading an image-overlay hero with a different content model.
- `LeadForm` can remain for backward compatibility, but new work should prefer `FormSection` as the generic wrapper name.
- The current color palette can support most of the mockup, but repeated light-blue surfaces may justify a named design token only if they are used across several pages.
- Some sections can be assembled from generic blocks today, but doing so would shift too much layout responsibility to CMS editors. Dedicated structured blocks are better when the content has repeated semantics: plans, metrics, proof, structured cards, forms, logos, quotes, and related content.
