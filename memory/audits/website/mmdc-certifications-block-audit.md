# MMDC Certifications Page Block Audit

Audit date: 2026-05-27
Mockup checked: https://mmdc-certifications-page.fenunez.com/
Browser artifact: `audit-mmdc-certifications-full.png`

## Scope

This audit compares the certification landing page mockup against the current Payload CMS block/component system in this repository. The goal is to identify the missing blocks and component work needed to recreate the mockup in a maintainable, CMS-editable way.

## Codebase Conventions Observed

- Blocks live under `src/blocks/<BlockName>/` and usually split into `*.block.ts`, `*.component.tsx`, optional `*.renderer.tsx`, and optional Storybook stories.
- Payload layout blocks are registered in `src/collections/Pages.ts` in the `LayoutBlocks` array.
- Public rendering is dynamic through `src/utilities/RenderBlocks.tsx`, which imports `@/blocks/${blockType}/${blockType}.renderer.tsx` first and falls back to `*.component.tsx`.
- Nested CMS composition is already common. `Container`, `Grid`, `Tabs`, `Carousel`, `Flex`, and `Accordion` accept nested blocks and delegate rendering through renderers or children.
- Styling is CMS-controlled through `StyleField` and rendered by `useStyling`, with responsive spacing and max-width classes.
- The design language is Tailwind-driven, using `primary` `#1E3A8A`, `secondary` `#C02C36`, white, muted gray, and `background` `#F5F5F5`.
- Components favor compact cards, `rounded-xl`/`rounded-lg`, light shadows, thin borders, responsive grids, and restrained CTAs.

## Mockup Section Inventory

| Mockup section | Current coverage | Recommendation |
| --- | --- | --- |
| Sticky header and footer | Existing globals | Use existing `Header` and `Footer`; no page block required. |
| Certification hero with badge, rating, CTAs, and image | Partial: `Hero` cannot model this layout cleanly | Add `CertificationHero`. |
| Quick facts strip: length, cost, start date | Partial: could be forced with `Grid` + `IconCard` | Add `ProgramFactStrip` for repeatable facts. |
| Trusted by Industry Leaders logos plus quote cards | Partial: `BrandPartners` only handles global marquee logos | Add `PartnerProof`. |
| Why Choose MMDC stats/cards | Mostly covered by `Grid` + `IconCard` | No new block required unless exact icon/stat styling is required. |
| What You'll Learn module cards | Partial: `Grid` + `List` can approximate, but module grouping is awkward | Add `CurriculumModules`. |
| Pricing and payment cards | Not covered | Add `PricingPlans`. |
| Start Learning Now lead form | Partial: `LeadForm` exists; form fields are missing radio/textarea and mockup shell | Add form field support and a `LeadFormSection` wrapper or extend `LeadForm`. |
| Accredited and Recognized logo row | Partial: can use `Image` in `Grid`, but repeated logo-strip editing is awkward | Add `LogoStrip` or extend `BrandPartners` with manual source mode. |
| Learner testimonials image carousel | Partial: `Carousel` + `ProfileCard` can approximate | Add `TestimonialCarousel` variant if social-card screenshot layout must be exact. |
| FAQ accordion | Existing `Accordion` | Use existing block. |
| Blue conversion CTA | Existing `Container` + `RichText` + `Button` | No new block required. |
| Learning Resources cards | Partial: `ArticleCategory` is category-driven and dark-primary, not manual cards | Add `ResourceCards` or extend `ArticleCategory`. |

## Missing Blocks and Components

### 1. `CertificationHero`

Component files needed:
- `src/blocks/CertificationHero/CertificationHero.block.ts`
- `src/blocks/CertificationHero/CertificationHero.component.tsx`
- `src/blocks/CertificationHero/CertificationHero.stories.tsx`

Short description:
CMS-editable hero for certification landing pages. It should render a small program badge, headline, supporting copy, rating/social proof, primary and secondary CTAs, and a right-side image. The mockup layout is not a full-bleed image hero; it is a two-column editorial hero with a light blue-to-white background and a contained image card.

Suggested Payload fields:
- `badgeText`
- `title`
- `body`
- `ratingLabel`
- `reviewLabel`
- `image`
- `imageAlt`
- `primaryButton` via existing `ButtonField`
- `secondaryButton` via existing `ButtonField`
- `StyleField`

Why it is missing:
Existing `Hero` variants are image-background/overlay oriented. The mockup needs text-first certification messaging, review metadata, two CTAs, and a contained image.

### 2. `ProgramFactStrip`

Component files needed:
- `src/blocks/ProgramFactStrip/ProgramFactStrip.block.ts`
- `src/blocks/ProgramFactStrip/ProgramFactStrip.component.tsx`
- `src/blocks/ProgramFactStrip/ProgramFactStrip.stories.tsx`

Short description:
A compact responsive row of program facts such as `Program Length`, `Cost Per Month`, and `Next Start Date`. Each fact has an icon, label, value, and helper text.

Suggested Payload fields:
- `items` array with `icon`, `label`, `value`, `description`
- `columns` select or number, default `3`
- `StyleField`

Why it is missing:
`Grid` + `IconCard` can mimic the cards, but the fact strip is a recurring certification-page pattern with consistent icon/value/description semantics.

### 3. `PartnerProof`

Component files needed:
- `src/blocks/PartnerProof/PartnerProof.block.ts`
- `src/blocks/PartnerProof/PartnerProof.component.tsx`
- `src/blocks/PartnerProof/PartnerProof.stories.tsx`

Short description:
A social-proof block that combines a logo row with one or more quote cards. The mockup has a heading, subheading, partner logos, and testimonial quotes from company representatives.

Suggested Payload fields:
- `title`
- `subtitle`
- `logos` array with `image`, `name`
- `quotes` array with `quote`, `name`, `role`, `company`, optional `avatar`
- `StyleField`

Why it is missing:
`BrandPartners` reads global partner data and renders marquee logo rows only. It does not support page-specific logos, quotes, attribution cards, or the static row layout shown in the mockup.

### 4. `CurriculumModules`

Component files needed:
- `src/blocks/CurriculumModules/CurriculumModules.block.ts`
- `src/blocks/CurriculumModules/CurriculumModules.component.tsx`
- `src/blocks/CurriculumModules/CurriculumModules.stories.tsx`

Short description:
Structured curriculum cards for modules. Each module has a pill label, title, and checklist of lessons or outcomes.

Suggested Payload fields:
- `title`
- `subtitle`
- `modules` array with `eyebrow`, `title`, `items` array
- `StyleField`

Why it is missing:
Existing `List` and `BasicCard` can display text, but they do not model nested modules with lesson lists cleanly. A dedicated block keeps the CMS editing experience simple and prevents fragile rich-text formatting.

### 5. `PricingPlans`

Component files needed:
- `src/blocks/PricingPlans/PricingPlans.block.ts`
- `src/blocks/PricingPlans/PricingPlans.component.tsx`
- `src/blocks/PricingPlans/PricingPlans.stories.tsx`

Short description:
Two or more pricing cards with optional `Popular` ribbon, plan type, price, billing note, feature checklist, and CTA. It should support individual and team/company pricing.

Suggested Payload fields:
- `title`
- `subtitle`
- `plans` array with `name`, `summary`, `price`, `pricePrefix`, `priceSuffix`, `badge`, `highlighted`, `features`, `button`
- `StyleField`

Why it is missing:
`BasicCard` has title/body/image/button, but it does not provide pricing semantics, highlighted plan styling, feature checklist rows, or a ribbon/badge.

### 6. Form Enhancements and `LeadFormSection`

Component files needed:
- `src/blocks/LeadFormSection/LeadFormSection.block.ts`
- `src/blocks/LeadFormSection/LeadFormSection.component.tsx`
- optional `src/blocks/LeadFormSection/LeadFormSection.renderer.tsx`
- `src/components/Form/fields/RadioFormField.tsx`
- `src/components/Form/fields/TextareaFormField.tsx`

Short description:
A landing-page form section that wraps the existing Payload form with a heading, subheading, light gradient/background section, and centered card layout. The form itself needs radio-group and textarea field rendering to match the mockup's learner-type selector and message field.

Suggested Payload fields for the wrapper:
- `title`
- `subtitle`
- `form` relationship to `forms`
- `StyleField`

Required form-builder work:
- Enable or add a `radio` field block.
- Enable or add a `textarea` field block.
- Register both in `FormFieldComponents` in `src/components/Form/fields/FormFields.tsx`.

Why it is missing:
`LeadForm` currently renders the existing `Form` directly. The mockup has a purpose-built section shell and fields that are not currently rendered by the local form system.

### 7. `LogoStrip`

Component files needed:
- `src/blocks/LogoStrip/LogoStrip.block.ts`
- `src/blocks/LogoStrip/LogoStrip.component.tsx`
- `src/blocks/LogoStrip/LogoStrip.stories.tsx`

Short description:
A static row/grid of accreditation or recognition logos with title and body copy. This differs from partner marquees because the order and display are content-specific and should be manually curated per page.

Suggested Payload fields:
- `title`
- `body` via `RichTextField`
- `logos` array with `image`, `name`, optional `url`
- `StyleField`

Why it is missing:
The current `BrandPartners` block is global and animated. The mockup requires a static trust/accreditation strip with page-specific copy and logos.

### 8. `TestimonialCarousel`

Component files needed:
- `src/blocks/TestimonialCarousel/TestimonialCarousel.block.ts`
- `src/blocks/TestimonialCarousel/TestimonialCarousel.component.tsx`
- `src/blocks/TestimonialCarousel/TestimonialCarousel.stories.tsx`

Short description:
Carousel/grid for learner testimonials. It should support image-only testimonial cards, quote cards, or mixed cards depending on assets.

Suggested Payload fields:
- `title`
- `subtitle`
- `items` array with `image`, `quote`, `name`, `role`
- `displayMode`: `image-card`, `quote-card`, `mixed`
- `autoplay`
- `StyleField`

Why it is missing:
Existing `Carousel` and `ProfileCard` can approximate this, but the mockup shows social-style testimonial image cards. A dedicated block keeps those assets and captions editable without overloading `ProfileCard`.

### 9. `ResourceCards`

Component files needed:
- `src/blocks/ResourceCards/ResourceCards.block.ts`
- `src/blocks/ResourceCards/ResourceCards.component.tsx`
- `src/blocks/ResourceCards/ResourceCards.stories.tsx`

Short description:
Manual or relationship-backed article/resource cards with image, category badge, title, excerpt, link text, and a section-level CTA.

Suggested Payload fields:
- `title`
- `subtitle`
- `source`: `manual` or `articles`
- `manualItems` array with `image`, `badge`, `title`, `excerpt`, `link`, `newTab`
- `articles` relationship array to `articles`
- `button` via `ButtonField`
- `StyleField`

Why it is missing:
`ArticleCategory` is useful for category pages, but it assumes category-driven content and a dark-primary section. The mockup needs a light gray landing-page resource grid with hand-picked cards and a `View All Resources` CTA.

## Existing Blocks to Reuse

- `Accordion`: use for the FAQ section with the current `default` or `topic` variants.
- `Container`: use as a section wrapper for CTA and general background/spacing control.
- `Grid`: use for the `Why Choose MMDC?` metric cards and other simple card layouts.
- `IconCard`: use for small icon/stat cards where no nested checklist or price logic is needed.
- `Button`: use for all CTAs through `ButtonField` so links, new-tab behavior, and colors remain consistent.
- `RichText`: use for section intro copy and body copy.
- `Image`: use for uploaded certification imagery and logos.

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

1. `CertificationHero`, `ProgramFactStrip`, and `PricingPlans`: these are the highest-impact missing above-the-fold and conversion blocks.
2. Form enhancements and `LeadFormSection`: needed for the page's main conversion workflow.
3. `CurriculumModules`, `PartnerProof`, and `LogoStrip`: needed for page-specific trust and learning-details sections.
4. `TestimonialCarousel` and `ResourceCards`: important for visual parity, but less structurally risky than form and pricing.

## Notes and Risks

- The current `BrandPartnersBlock` has only `StyleField`; its component expects `brands` from global data. If it is used directly in page layout without a renderer injecting global partners, it may not have the data it needs.
- The existing form plugin disables `message` fields and the local renderer has no radio or textarea component. The mockup form cannot be faithfully recreated until those fields are supported.
- `Hero` could be extended with a new `certification` variant instead of adding `CertificationHero`, but a dedicated block is cleaner because the mockup's fields are certification-specific.
- The current color palette can support the mockup, but the mockup uses light blue surfaces and gray section bands not fully represented in `tailwind.config.js`. Consider adding a named light-blue token only if repeated across multiple certification pages.
- Some sections can be assembled from generic blocks today, but doing so would shift too much layout responsibility to CMS editors. Dedicated structured blocks are better for pricing, curriculum, proof, and form conversion sections.
