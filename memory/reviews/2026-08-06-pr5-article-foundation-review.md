# Review: PR #5 — feat: add article foundation and detail shell

- **Date:** 2026-08-06
- **Repo:** mmdc-tech/mmdc-v3
- **PR:** #5 `feature/articles-art-002-article-foundation` → `development` (head d2c15b0, stacked on ART-001A)
- **Scope:** 45 files, +10177/-9. New Articles/People/Organizations collections, Media governance, Article lifecycle/validation/eligibility/queries/SEO, slug-change redirects, `/articles/[articleSlug]` detail shell, sitemap/robots, migration, tests, runbook.
- **Reviewers:** requirements-reviewer, thermo-nuclear-review, thermo-nuclear-code-quality-review, react-quality-review (aggregated by review-orchestrator)

## overall_status: FAIL

## Checks

- **Functional: publication-time dependency resolution returns clean validation errors**
  status: FAIL
  expected: Missing/draft-only author or media surfaces the intended eligibility ValidationError (like the Category NotFound handling).
  actual: `src/hooks/articles/index.ts:120-126` (author loop) and `:147-152` (media) call `req.payload.findByID({ draft: false })` with no try/catch; `authorCredits` has no filterOptions (`src/collections/Articles.ts:77-101`), so a draft-only Person is selectable and publishing throws a raw NotFound. Category path (`hooks/articles/index.ts:72-98`) handles it correctly. Source: thermo-nuclear-review (verified).

- **Spec: structured data emits each ordered author as its own Person or Organization object; no invented image URL**
  status: FAIL
  expected: data-model.md:1109 — each ordered author its own Person/Organization object; missing featured image produces no invented image URL.
  actual: `src/utilities/articles/articles.seo.ts:53` types every byline `@type: 'Person'` (Organization credits mis-typed; `authorNames` drops relationTo at `articles.queries.ts:314`); `:58` always emits image via `resolveArticleSocialImage` fallback to socialMediaRecord/siteDefault. Source: requirements-reviewer (verified against data-model.md:1109).

- **Correctness: review-currency policy agrees between publish gate and public gate**
  status: FAIL
  expected: Both gates enforce "guide OR materially-maintained news requires current review".
  actual: Validation requires review dates for materially-maintained news (`src/utilities/articles/articles.validation.ts:360-366`), but `isCurrentGuideReview` (`src/utilities/articles/articles.eligibility.ts:25-40`) returns true for every non-guide article — a maintained news article whose reviewDueAt lapses stays publicly eligible indefinitely. Presence/order/future checks also duplicated between the two modules. Source: thermo-nuclear-code-quality-review (verified).

- **Public copy: no em dashes**
  status: FAIL
  expected: AGENTS.md — sentence case, no em dashes in public copy.
  actual: `src/app/(frontend)/articles/[articleSlug]/page.tsx:126` uses `' — '` as the figcaption credit separator. Source: react-quality-review (verified).

- **Maintainability: canonical validation primitives shared, not re-implemented with drift**
  status: FAIL
  expected: App-wide primitives (trim, relationshipSchema, relationshipID, validDate, ValidationIssue) live once in src/utilities/ (precedent: article-categories.validation.ts exports RelationshipID).
  actual: relationshipID re-implemented 4x (`articles.validation.ts:146`, `hooks/articles/index.ts:50`, `articles.queries.ts:135`, `articles.persistence.ts:26`); relationshipSchema/trimRequired/ValidationIssue 4x; review-date refinement copy-pasted with divergent rules (people vs organizations archived exemption: `people.validation.ts:135` vs `organizations.validation.ts:109`). One shared governance-helpers module would delete ~1/3 of ~2500 new lines. Source: thermo-nuclear-code-quality-review (partially verified).

- **Maintainability: redirect staging machinery not duplicated from article-categories**
  status: FAIL
  expected: One shared redirects module (query-by-source-path, destination normalization, apply-work) for the app-wide Redirects collection.
  actual: `src/hooks/articles/articles.persistence.ts:57,81` structurally mirrors `src/hooks/article-categories/article-categories.persistence.ts:116,148`; third redirect query with hand-rolled destination shape in `src/utilities/articles/articles.queries.ts:322-362`; destination-ID normalization written 3 ways. Source: thermo-nuclear-code-quality-review.

- **Scale: sitemap generation bounded**
  status: PARTIAL
  expected: Sitemap covers eligible articles with bounded work per request.
  actual: `src/utilities/articles/articles.queries.ts:375-407` re-resolves full eligible detail (body-bearing select, category + up to 4 authors + 2 media ≈ 8 calls/article) per entry of a `limit: 1000` `pagination: false` query — silent truncation past 1000 and ~8k payload calls per force-dynamic render. Not urgent at current volume. Source: both thermo reviews.

- **Correctness: public read path revalidates dependency `_status` truthfully**
  status: PARTIAL
  expected: §27.3 — public rendering cannot leak drafts/archived relationships; §17.52 dependency revalidation.
  actual: Resolved dependencies get `_status` overwritten to 'published' post-fetch (`src/utilities/articles/articles.queries.ts:178-182, 203-207, 276`), making `_status` checks inside isArticleEligible/isPersonArticleAuthorEligible/isOrganizationArticleAuthorEligible vacuous on the read path; safety rests entirely on Payload `draft: false` findByID semantics (codified in `articles.queries.test.ts:139-176`). Publication-time gating is sound. Source: requirements-reviewer.

- **Spec: ArticleBody governed to A1–A10 node union (§7.4)**
  status: PARTIAL
  expected: body outlet restricted to A1–A10; unknown nodes fail closed.
  actual: body is unrestricted Lexical richText (`src/collections/Articles.ts:157-164`); regenerated importMap registers default features outside A1-A10 (checklist, align, indent, upload, relationship, sup/sub). Deferral is documented (runbook, `Articles.ts:162-163`) but §7.4 is an active slice requirement. Source: requirements-reviewer.

- **Type cleanliness: query layer typed; casts auditable**
  status: PARTIAL
  expected: Canonical queries return typed projections; casts isolated and auditable.
  actual: `findArticlePreviewRoots`/`findArticleDetailRootBySlug` return `Promise<unknown>`; ~30 `as never` casts across queries/hooks/page (`page.tsx:135`, `articles.queries.ts:75-385`); post-fetch `_status` patches on already-published records. Source: thermo-nuclear-code-quality-review + react-quality-review.

## Passed dimensions (notable)

- No draft/archived/future leaks found: DB predicate + draft:false + full eligibility predicate on every public path (detail, redirect resolution, sitemap); page 404s/noindexes otherwise.
- No XSS: JSON-LD escapes `<` (`page.tsx:66-77`); no dangerouslySetInnerHTML; body via Lexical React renderer with no raw HTML.
- No open redirect / redirect loops: typed destinations (Redirects relationTo limited), single-hop resolution re-checking destination eligibility, path-conflict guards in beforeChange.
- Scope gate §24 respected: only `/articles/[articleSlug]` route added; no unauthorized archives; no internal terms in copy.
- Migration reversible, registered (`migrations/index.ts`), unique code/slug indexes; types + importMap regenerated.
- Layer boundaries respected; zero client components on the route; no client fetching; design tokens honored in page.module.css (one 48rem breakpoint outside DESIGN.md 7.1 guidance, minor).
- Test coverage genuinely good (validation/eligibility/hooks/queries/integration with real PostgreSQL). Tests not re-run locally (read-only review; author reports 138/138 + build + Docker + migration pass).

## Notes

- PR discussion has zero comments/reviews; nothing from BugBot to incorporate.
- `vitest.config.mts` sets `fileParallelism: false` (shared-DB integration) — full-suite runtime cost.
- Person archiving blocked when reviewDueAt lapsed (`people.validation.ts:135`) while Organizations exempt archived — low-severity inconsistency.
- aria-current="page" placed on the category crumb rather than the article (`page.tsx:89-95`); category name announced twice. Minor.
- No route-level not-found boundary: the noindex metadata branch in generateMetadata (`page.tsx:43`) may not be consumed by default 404 handling.

## Confidence

high (aggregate; all FAIL findings verified against worktree files and spec text)
