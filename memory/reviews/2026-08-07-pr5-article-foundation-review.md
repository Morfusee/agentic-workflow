# Review: PR #5 article foundation and detail shell

- **Date:** 2026-08-07
- **Repo:** mmdc-tech/mmdc-v3
- **Subject:** PR #5 "feat: add article foundation and detail shell" (`feature/articles-art-002-article-foundation` -> `development`, head `5823e71`, 2 commits: `d2c15b0` feat + `5823e71` fix of prior ART-002 review findings)
- **PR URL:** https://github.com/mmdc-tech/mmdc-v3/pull/5
- **overall_status:** FAIL (ticket-AC cross-check appended 2026-08-07 via ClickUp MCP; failures are process/DoD and one documented deferral, not code defects)

## Review scope

- Diff `origin/development...5823e71`: 50 files, +10470/-92. Article foundation vertical slice: Articles/People/Organizations collections, Media governance extension, Article lifecycle hooks, validation/eligibility/queries/SEO utilities, permanent slug-change redirects, `/articles/[articleSlug]` detail shell, sitemap/robots, migration, fixtures/tests, authoring runbook.
- Reviewed against `docs/specs/06-technical-foundation.md` (§7.1, §7.3, §7.4, §24, §27), `docs/specs/data-model.md`, `docs/specs/information-architecture-and-pages.md`, `docs/specs/05-blocks-components-and-design-system.md`, `AGENTS.md`, and the PR description. Prior review comment (FAIL at `d2c15b0`) used as regression checklist.
- Worktree read at `$HOME/AppData/Local/Temp/opencode/pr5-art-002-wt` (head `5823e71`). Verification executed at head: lint, tsc --noEmit, prettier --check, `pnpm build`, 120/120 unit tests, 23/23 integration tests (live local Postgres).
- **Ticket:** ClickUp ART-002 "Article foundation and detail shell" (`86d3xhg34`, assignee MITCH CABRERA, status in progress, depends on ART-001A). Ticket acceptance criteria checked directly against the head via ClickUp MCP on 2026-08-07; delta checks below.

## Reviewers

- requirements-reviewer (PASS overall, 2 PARTIAL checks)
- thermos (PARTIAL overall; thermo-nuclear-review + thermo-nuclear-code-quality-review internally)
- react-quality-review (PASS overall, 2 PARTIAL checks)
- orchestrator ticket-AC cross-check (ClickUp ART-002 `86d3xhg34`, direct inspection at head)

## Aggregated checks

| Status | Check | Expected | Actual |
| --- | --- | --- | --- |
| PASS | Published-only public reads with bounded projections | No draft/archived/future leaks; explicit select; depth 0/1 | `buildEligibleArticleWhere` (`articles.queries.ts:55-61`) + `draft:false` + JS eligibility re-check (`articles.eligibility.ts:37-56`); bounded `ARTICLE_PREVIEW_SELECT`/`ARTICLE_DETAIL_SELECT` (`articles.queries.ts:16-52`); unit tests reject draft/archived/future cases |
| PASS | Publication-time dependency checks surface ValidationError | Missing/unpublished Category/author/Media at publish -> field-level ValidationError, never raw NotFound | `src/hooks/articles/index.ts:76-91` (Category), `123-130` (author), `159-166` (Media); covered by unit + integration tests |
| PASS | JSON-LD correctness | Organization bylines typed Organization; no invented image URL; real dates; safe escaping | `articles.seo.ts:42-62` types from resolved `relationTo`; image spread only when URL exists; `<` escaped `\u003c` (`page.tsx:66-76`); tests at `articles.seo.test.ts:68-98` |
| PASS | Review-currency policy consistent publish gate vs public eligibility | Same current-review predicate governs both paths | `isCurrentReview` single canonical predicate (`governance.ts:44-81`), shared by `articles.validation.ts:305-309` and `articles.eligibility.ts:27-29`; author/media eligibility predicates identical on both paths |
| PASS | Redirect behavior: permanent, no loops, typed destinations | 301 permanent; only eligible article destinations; conflicts blocked at publish | `redirects.persistence.ts:62-82` (permanent), destination `relationTo==='articles'` + re-validation (`articles.queries.ts:329-369`), publish-time path-conflict guards (`hooks/articles/index.ts:199-244`); integration tests assert permanent + typed destination |
| PASS | Immutable code, unique slugs, slug-change redirects | code immutable post-create; unique index; redirect on slug change | Zod superRefine (`articles.validation.ts:159-165`); migration unique indexes; `Articles.integration.test.ts:163-265` |
| PASS | Author eligibility (People AND Organizations) | Person: published+active+eligible+role+bio+owner+current review; Organization: published+active+owner+current review | `people.validation.ts:116-120`, `organizations.validation.ts:80-86`, applied in publish hook (`hooks/articles/index.ts:131-142`) and `isArticleEligible`; `filterOptions` restrict pickers |
| PASS | Category eligibility and root derivation | Exactly one active Category; root derived from parent-or-self; not editor-overridable | beforeChange derivation (`hooks/articles/index.ts:66-91`), publish gate (`102-108`), hidden/readOnly field (`Articles.ts:165-172`); unit test at `hooks/articles/index.test.ts:66-98` |
| PASS | Guide/news publication rules | guide requires current reviewedAt/reviewDueAt; original news does not; updateNote paired with materiallyUpdatedAt; no future publishedAt | `articles.validation.ts:225-309`; branch tests `articles.validation.test.ts:55-144`, integration `125-161` |
| PASS | Media governance extension | alt/credit/rights fields required; approval evidence; runtime expiry | `media.validation.ts:73-175`; featured/social media re-validated at publish and in detail resolution; 7 unit + integration tests |
| PASS | Canonical metadata, robots, sitemap, structured data from visible content | Derived canonical URL; noindex for missing articles; eligible-only sitemap | `articles.seo.ts:12-62`, `page.tsx:43` (noindex fallback), `not-found.tsx:6-9`, `robots.ts`, `sitemap.ts` force-dynamic + paginated eligible entries; robots/SEO/query tests pass |
| PASS | §24 scope gate | Only `/articles/[articleSlug]` added; no excluded routes | Only `articles/[articleSlug]/page.tsx` + not-found added; build route table = `/articles/[articleSlug]`, `/sitemap.xml`, `/robots.txt` |
| PASS | Duplication consolidation (prior finding) | Shared relationship/trim/review/redirect primitives | `governance.ts` centralizes `relationshipSchema`/`relationshipID`/`trimRequired`/`isCurrentReview`; `redirects.persistence.ts` shared by articles + article-categories hooks (fix commit removed 496 lines) |
| PASS | Sitemap scales (prior finding) | Paginated, bounded dependency batches | `articles.queries.ts:377-525`: 100 roots/page, batched category/people/organization resolution, no body fields |
| PASS | `_status` not overwritten post-fetch (prior finding) | Fetched publication status used as-is | Hard-coded `_status: 'published'` assignments removed at `5823e71`; selects include `_status`; test rejects results omitting status (`articles.queries.test.ts:139-176`) |
| PASS | Migration reversible + artifacts committed | Symmetric down(); registered; types/importMap regenerated | `down()` drops tables/types/columns/indexes in reverse (`20260806_090804_art_002_article_foundation.ts:355-428`); registered in `migrations/index.ts`; `payload-types.ts` + importMap committed |
| PASS | Security: no XSS, no open redirect, no secrets | No raw HTML; no secrets in diff | JSON-LD escaped, RichText server-rendered; no secrets; only server-side env vars; unit + integration suites green |
| PASS | No em dash in public copy (prior finding) | Em-dash-free public copy | Grep-verified: none in article frontend/utilities; sentence-case, no prohibited terms/CTAs |
| PASS | Test coverage + quality gates | Unit/integration tests for lifecycle, eligibility, redirects, queries, SEO, validation; lint/typecheck/format/build clean | 120/120 unit + 23/23 integration pass at head; lint, tsc, prettier, build all pass (also verified by CI `validate` SUCCESS) |
| PARTIAL | ArticleBody node governance (§7.4) | Server-side A1-A10 node validation per `06-technical-foundation.md` §7.4 | Body is a bounded Lexical feature set (`Articles.ts:185-207`) but A5-A10 nodes + server-side body-node validation deferred to node tickets; deferral documented (runbook `article-authoring.md:25`, collection description). Same classification as prior review |
| PARTIAL | Query-layer typing hygiene | No `unknown`/`as never` escapes in read contract | Remaining `as unknown as` projection casts (`articles.queries.ts:98,181,208,254,284,342,361,401`), `as never` for RichText (`page.tsx:137`) and relationTo arrays. Cosmetic; covered by tests; consistent with pre-existing pattern |
| PARTIAL | Residual duplication and layering | No repeated helpers; shared helpers not in collection modules | `validDate` private ×3 (`governance.ts:37`, `articles.validation.ts:141`, `media.validation.ts:66`); `countUnicodeCharacters` imported cross-collection; thin passthrough wrappers around `redirects.persistence.ts`. Minor; no file exceeds 600 lines |
| PARTIAL | Non-atomic redirect application / draft-field UX | Redirect work atomic; draft lifecycle matches runbook | `applyPermanentRedirectWork` deletes-then-creates sequentially (`redirects.persistence.ts:57-82`); mid-loop failure leaves partial alias state (admin-only compensating flow); `publishedAt`/`body` field-level required (`Articles.ts:131-136,185-207`) conflicts with create-a-draft runbook step |
| PARTIAL | Route-level rendering tests | `page.tsx`/`not-found.tsx` rendering + noindex path covered | No route-render tests exist repo-wide (no `*page*.test` files); robots/SEO/query utilities covered. Known project gap, not a PR regression |
| PASS | Ticket AC: no author data copied onto Article | No name/role/bio/image/profile URL stored on Article | Author credits reference People/Organizations relations only; no copied fields in `Articles.ts` (grep verified) |
| PASS | Ticket AC: admin help text | Admin help text included on new collections | `admin:` descriptions present: Articles 26, People 10, Organizations 6, Media 10 entries |
| PASS | Ticket AC: missing Media/sources suppress regions | No placeholders or empty headings | Conditional region rendering verified (`page.tsx`), sources filtered to note-bearing entries with stable keys |
| PASS | Ticket AC: Category changes do not change URL | Route keyed by slug only | `/articles/[articleSlug]` route; category not part of path |
| PASS | Ticket AC: preview projections bounded | Hub/archive projections exclude body and full relationship graphs | `ARTICLE_PREVIEW_SELECT` excludes body/sources (`articles.queries.ts:16-34`) |
| PARTIAL | Ticket AC: qualified archive return in detail shell | Base detail shell renders a qualified archive return link | Not implemented; explicitly deferred to ART-001B in PR body (archive routes do not exist yet). Documented extension point, but AC unmet at head |
| FAIL | Ticket DoD: PR links its ART ticket | PR description links the ART ticket | PR body contains no ticket reference (no ClickUp ID/URL anywhere in description) |
| FAIL | Ticket DoD: PR identifies specification sections implemented | PR description lists the spec sections implemented | PR body has no reference to `06-technical-foundation.md`/`data-model.md`/section numbers; only a feature bullet list |

## Notes

- All three reviewers agree: no security or correctness FAIL at head. The fix commit `5823e71` resolved all six prior FAIL findings (NotFound->ValidationError, JSON-LD byline/image, review-currency divergence, em dash, duplication consolidation, sitemap truncation) and both prior PARTIALs with code fixes (`_status` overwrite, sitemap scaling).
- Ticket-AC cross-check (ClickUp `86d3xhg34`) confirms the codebase satisfies the substantive acceptance criteria; the three new non-PASS items are: qualified archive return (deferred to ART-001B), and two Definition-of-Done process items (PR does not link its ART ticket, does not identify spec sections). No ticket AC exposes a code defect.
- The ArticleBody "controlled body field" PARTIAL is consistent with the ticket: the ticket itself excludes A5-A7/A9/A10 and assigns node delivery to ART-003..ART-009; only server-side body-node validation remains deferred.
- Overall downgraded PARTIAL -> FAIL solely on the DoD process items + deferred archive-return AC; if those are accepted as tracked follow-ups, the implementation itself stands at PASS-level quality.
- Minor nits (not elevated to checks): `SITE_DEFAULT_SOCIAL_IMAGE` read at `page.tsx:47` but missing from `.env.example`; "Article" capitalized mid-sentence in not-found copy (borderline vs sentence-case rule); base layout title template "%s | MMDC Design Foundation" leaks into article titles (base-owned, outside diff); `aria-label="Authors"` on meta list is redundant but harmless.
- Preview projection consumers (future hub/archive, ART-001B) do not yet resolve featuredMedia eligibility; no current consumer renders the preview, so no leak today.
- Reviewer disagreement: none material. The `_status` re-check was confirmed genuine (draft:false + SQL predicate + JS dependency re-verification), not vacuous.

## Verification evidence

- `pnpm check` (format, lint, typecheck, 120/120 unit tests) and 23/23 integration tests pass at `5823e71` in the PR worktree.
- `pnpm build` passes; CI `validate` check SUCCESS on the PR.
- Migration up/down/reapply verified reversible on isolated PostgreSQL (per PR verification notes).
