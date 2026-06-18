---
date: 2026-05-21
type: research
tags: [clickup, epics, task-analysis, mmdc-web, performance, cms]
related: []
---

# ClickUp Epics Board — Unassigned Task Analysis

**Source list:** Epics board (`list_id: 901613629699`)
**Context:** mmdc-web codebase (`$HOME\Documents\Programming\website`)
**Stack:** Next.js 16 (App Router), Payload CMS 3.75, Tailwind CSS 3, MongoDB, React 19

Of 9 tickets in the Epics board, 4 are unassigned. Ranked by implementation effort (fastest first):

---

## 1. `86d32m54w` — LLMs.txt

**Status:** to do
**URL:** https://app.clickup.com/t/86d32m54w
**Estimate:** ~30 min
**Files:** 3 new, 1 edit. All additive.

**Description:** Add CMS-managed LLMs.txt content served at `/llms.txt`, similar to `robots.ts`.

### Implementation Plan

| Step | File | What |
|------|------|------|
| Create | `src/globals/LLMs/LLMs.global.ts` | Global singleton with a `code` field for Markdown content + `afterChange` revalidation hook |
| Create | `src/globals/LLMs/hooks/revalidateLLMs.ts` | Calls `revalidateTag('global_llms')` |
| Create | `src/app/llms.txt/route.ts` | `GET` route handler — fetches global via `payload.findGlobal`, returns `text/plain` |
| Edit | `src/payload.config.ts` | Import `LLMs` + add to `globals` array |
| Auto | `src/payload-types.ts` | Regenerate via `payload generate:types` |

### Existing Patterns to Follow
- `robots.ts` — text-file route serving pattern
- `SiteSettings.ts` — simple global singleton with `access: { read: () => true }`
- `my-route/route.ts` — raw Route Handler with `getPayload`
- `revalidateNotificationBanner.ts` — `afterChange` hook pattern
- `getGlobals.ts` — `getCachedGlobal()` with `global_<slug>` cache tags

---

## 2. `86d32mfe8` — Recreate College Program Mockup

**Status:** to do
**URL:** https://app.clickup.com/t/86d32mfe8
**Estimate:** 0-8 dev hours (80-90% is CMS content configuration)

**Description:** Recreate the mockup at https://mmdc-programs-page.fenunez.com/ using existing blocks in the CMS. Identify gaps for new blocks.

### Existing Blocks Sufficient For
- **Hero** (`program` variant) — program banner with title, CTA, image, badges
- **BSITShowcase** — auto-displays all BSIT specializations grouped by focus
- **Grid + IconCard/BasicCard** — key benefits, stats cards
- **Accordion** — curriculum details, FAQ
- **Carousel + ProfileCard** — testimonials
- **LeadForm** — apply/lead capture form
- **MapuaBanner + BrandPartners** — accreditation, partner logos
- **Video** — video showcase
- **Tabs** — tabbed content (e.g., different specializations)
- **RichText** — program overview, admissions info
- **List** — admissions steps
- **Container** — section wrapping with background colors

### New Blocks Possibly Needed
- **StatsGrid** — large-number statistics display (salary ranges, employment rate)
- **Timeline** — semester-by-semester roadmap visualization
- **StickyCTA** — floating "Apply Now" button
- **ProgramDetail** — block that references a specific bachelor program by relationship

### What a Developer Would Do
1. Recreate the page in CMS using existing blocks (no code, content editor task)
2. Identify which sections truly can't be replicated
3. Build 1-2 new blocks at `src/blocks/<Name>/` following the 3-file convention (`.block.ts`, `.component.tsx`, `.renderer.tsx`)
4. Register new blocks in `src/collections/Pages.ts` `LayoutBlocks` array

---

## 3. `86d32m987` — Optimize Render-Blocking CSS

**Status:** to do
**URL:** https://app.clickup.com/t/86d32m987
**Estimate:** 1-3 hours

**Description:** Two CSS files render-blocking — 11.3KB/160ms and 1KB/400ms. Investigate CSS delivery.

### Root Causes Found (Direct from Code Analysis)

| # | Cause | Evidence |
|---|-------|----------|
| **1** | **~942 force-safelisted Tailwind classes** | `tailwind.config.js` generates Cartesian product: 5 breakpoints × 5 properties × 35 spacing values = 875 classes, plus ~67 regex-pattern-matched classes |
| **2** | **All default Tailwind colors retained** | `colors: { ...colors }` spreads all 22 default colors × 11 shades into bundle |
| **3** | **Content scan too broad** | `'./src/**/*.{ts,tsx}'` scans 257 files including admin-only components |
| **4** | **No CSS optimization** | Missing `experimental.optimizeCss` in Next.js, no `cssnano` in PostCSS |
| **5** | **No CDN in CMS mode** | 400ms for 1KB suggests server TTFB — CSS served from Node.js directly |

### Fixes (Priority Order)

1. **Drop/reduce the safelist** — remove the 875-class Cartesian product. Tailwind JIT already scans source files. Keep only specific patterns actually used in dynamic CMS Lexical content.
2. **Restrict colors** — remove `...colors` spread, keep only colors actually used by frontend components.
3. **Tighten content path** — scan `./src/app/(frontend)/**`, `./src/components/**`, `./src/blocks/**` instead of `./src/**/*`.
4. **Enable CSS optimization** — add `experimental: { optimizeCss: true }` to `next.config.mjs` or `cssnano` to PostCSS.
5. **Cache static CSS** — add aggressive `Cache-Control: public, max-age=31536000, immutable` for `.next/static/css/*` in CMS deployment.

### Key Files
- `tailwind.config.js` — safelist (lines 8-14), content paths (line 18), colors (line 33)
- `next.config.mjs` — missing CSS optimization
- `postcss.config.js` — minimal (tailwindcss, autoprefixer only)
- `src/app/(frontend)/styles.css` — sole frontend CSS entry point (63 lines, imports Tailwind directives)
- `src/app/(frontend)/layout.tsx` — imports `./styles.css`
- `Dockerfile` — no CDN for CMS-deployed static assets

---

## 4. `86d32mckh` — Reduce JavaScript Execution Time

**Status:** to do
**URL:** https://app.clickup.com/t/86d32mckh
**Estimate:** 4-8+ hours (investigation + implementation)

**Description:** First-party scripts execute at 1.6s. Investigate and reduce via chunking and aggressive dynamic imports.

### Root Causes Found

| # | Cause | Evidence |
|---|-------|----------|
| **1** | **`React.lazy()` double-loads blocks** | `RenderBlocks.tsx` uses `React.lazy()` which can't SSR — blocks fall through to `.catch()` on server, re-import on client. Every block loads twice. |
| **2** | **`embla-carousel-react` statically imported** | ~30KB gzipped, shipped to all pages via `components.ts` barrel file (even pages without carousels) |
| **3** | **`Image.component.tsx` is `'use client'` unnecessarily** | Zero hooks, zero events — just renders `<picture>` + `<img>`. Imported by 20+ files. |
| **4** | **Heavy initial hydration** | LayoutProvider (4 context states), Query.tsx (sessionStorage + history API), Nav (resize listener + body class), Grid (ResizeObserver on mount) |
| **5** | **Barrel file pulls in transitive deps** | `src/blocks/components.ts` re-exports 20 components — bundlers may tree-shake poorly with dynamic imports |

### Fixes (Priority Order)

| Priority | File | Change | Impact |
|----------|------|--------|--------|
| **P1** | `src/utilities/RenderBlocks.tsx` | Replace `React.lazy()` with `next/dynamic()` for proper SSR + per-block code splitting | **HIGH** — eliminates double-loading, enables chunking |
| **P2** | `src/blocks/Image/Image.component.tsx` | Remove `'use client'`, make server component | **HIGH** — removes Image from client bundle entirely |
| **P3** | `src/components/ui/carousel.tsx` + `Carousel.component.tsx` | Wrap embla imports with `next/dynamic` | **MEDIUM** — removes 30KB from non-carousel pages |
| **P4** | `src/utilities/Query.tsx` | Defer `window.history.replaceState` with `requestIdleCallback` | **MEDIUM** — reduces blocking hydration work |
| **P5** | `src/blocks/Grid/Grid.component.tsx` | Debounce ResizeObserver or use CSS container queries | **LOW** — reduces layout thrashing |

### Large Dependencies & Import Status

| Package | Size | Status |
|---------|------|--------|
| `pdfjs-dist` | Very Large (~3MB+) | Already dynamically imported |
| `react-pageflip` | Large | Already `next/dynamic` with `ssr: false` |
| `embla-carousel-react` | Medium | **Statically imported** — needs wrapping |
| `@payloadcms/richtext-lexical` | Very Large | Statically imported in 20+ files |
| `lucide-react` | Medium (tree-shakeable) | 17 files, tree-shakeable via path imports |
| `lodash/*` | Medium (tree-shakeable) | 27 imports, individual path imports used |

### Key Files
- `src/utilities/RenderBlocks.tsx` — core block loading with `React.lazy()` + TODO comment on line 9
- `src/blocks/components.ts` — barrel file re-exporting 20 components
- `src/blocks/Image/Image.component.tsx` — unnecessarily marked `'use client'`
- `src/components/ui/carousel.tsx` — statically imports embla
- `src/utilities/Query.tsx` — runs `replaceState` on every page load
- `src/app/(frontend)/layout.tsx` — LayoutProvider, GA4/GTM scripts, Query component
- `src/blocks/Grid/Grid.component.tsx` — ResizeObserver on mount
- `src/globals/Headers/Nav/Nav.component.tsx` — resize listener + body class manipulation

---

## Summary Ranking

| Rank | Task ID | Ticket | Effort | Risk |
|------|---------|--------|--------|------|
| 1 | 86d32m54w | LLMs.txt | ~30 min | None — additive only |
| 2 | 86d32m987 | Render-Blocking CSS | 1-3 hrs | Low — config changes mostly |
| 3 | 86d32mfe8 | Mockup Recreation | 0-8 hrs | None — mostly CMS work |
| 4 | 86d32mckh | JS Execution Time | 4-8+ hrs | Medium — touches rendering core |
