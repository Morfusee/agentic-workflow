# Stand-up Script

Yesterday, I implemented the first half of the article category work: the governed Article Category foundation with the article-categories collection. I raised the pull request against development, and it is currently open and awaiting review.

I also restructured the article tickets based on their content: the original article category ticket had a circular dependency with the article foundation ticket, so I split it into two, moving the archive publishing scope into its own ticket to be tackled after the foundation and the article model are in place, and I corrected the article foundation ticket's dependency so the order is clear. I also informed the team about the complexity of these tickets so the dependency order and the split are understood.

No major blockers right now.

---

# Selected Tasks

- 86d3xhg24: ART-001A - Establish Article Category governance
  - Status: in progress
  - Activity date: 2026-08-06
  - URL: https://app.clickup.com/t/86d3xhg24
  - Reference: `# All Scraped Tasks` -> `## 86d3xhg24: ART-001A - Establish Article Category governance`
  - Stand-up relevance: Implemented the governed category foundation; PR #3 raised against development

- 86d3xhg34: ART-002 - Article foundation and detail shell
  - Status: to do
  - Activity date: 2026-08-06
  - URL: https://app.clickup.com/t/86d3xhg34
  - Reference: `# All Scraped Tasks` -> `## 86d3xhg34: ART-002 - Article foundation and detail shell`
  - Stand-up relevance: Dependency corrected to ART-001A, resolving the circular dependency; team ticket

- 86d3y5m8c: ART-001B - Publish Article Category and Subcategory archives
  - Status: to do
  - Activity date: 2026-08-06
  - URL: https://app.clickup.com/t/86d3y5m8c
  - Reference: `# All Scraped Tasks` -> `## 86d3y5m8c: ART-001B - Publish Article Category and Subcategory archives`
  - Stand-up relevance: Second half of the ART-001 split; queued after ART-002; team ticket

- MANUAL-001: Informed the team of the complexity of the ART tickets
  - Status: Done
  - Activity date: 2026-08-06
  - Reference: `# Manual Tasks` -> `## MANUAL-001: Informed the team of the complexity of the ART tickets`
  - Stand-up relevance: Communicated the ticket complexity, split, and dependency order to the team

---

# Unselected Tasks

No unselected tasks.

---

# Ticket Dump

Generated: 2026-08-06T03:12:25+08:00
Requested range: 2026-08-06 (today)
Dump file date: 2026-08-06

---

# Grouped Summary

2026-08-06

## In Progress
- 86d3xhg24: ART-001A - Establish Article Category governance

## To Do
- 86d3y5m8c: ART-001B - Publish Article Category and Subcategory archives
- 86d3xhg34: ART-002 - Article foundation and detail shell

## Done
- MANUAL-001: Informed the team of the complexity of the ART tickets

---

# Manual Tasks

Entries here are not tracked in ClickUp. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

## MANUAL-001: Informed the team of the complexity of the ART tickets

Status: Done
Activity date: 2026-08-06
My role: dev-owner

### Description
Informed the team about the complexity of the ART tickets (circular dependency between the former ART-001 and ART-002, and the resulting split into ART-001A/ART-001B).

### Activity Notes
Communication: flagged ticket complexity to the team so the dependency order (ART-001A -> ART-002 -> ART-001B) and the split are understood.

---

# All Scraped Tasks

## 86d3xhg24: ART-001A - Establish Article Category governance

Status: in progress
Activity date: 2026-08-06
URL: https://app.clickup.com/t/86d3xhg24
Initial dev assignee: Mark Rolis Valenzuela
Testing actors: None identified
My role for this task: dev-owner

### Why this task was included
Assigned to me; implementation delivered today via GitHub PR #3 and commits (confirmed via gh CLI). Task was split from the former ART-001 to remove a circular dependency with ART-002.

### Description
Create the governed Article Category and Subcategory foundation required by Article authoring. Public archive pages are intentionally delivered after the Article model exists.
Scope
Add the article-categories Payload collection.
Support root Categories and one direct-child Subcategory level.
Add immutable code, public name, unique slug, landing introduction, parent, display order, owner, review dates, draft/published state, and active/archived status.
Define the governed archive-onward-path data shape without introducing raw labels, URLs, images, layouts, or temporary target fields.
Implement hierarchy, immutability, uniqueness, lifecycle, and review-date validation.
Add Admin labels, relationship controls, migration, generated types, fixtures, and automated tests.

Deliverable
Editors can create a root Category without a parent.
Editors can create a Subcategory with exactly one root parent.
Self-parenting, cycles, and third-level nesting are rejected.
Code is unique and immutable.
Slug is unique and follows the governed redirect process when changed.
Landing introduction is limited to 240 Unicode characters.
Draft Categories may retain incomplete archive-governance fields.
Category or parent changes never store or mutate an Article URL.
No public archive route, Article preview, eligible-Article count, pagination, navigation link, or sitemap entry is introduced by this ticket.
A reversible migration, generated Payload types, Admin behavior, fixtures, and tests are included.

### Comments
No comments found.

### Activity Timeline
- 2026-08-04T15:00:26+08:00 created: ART-001A task created in the Sprint list
- 2026-08-05T21:11:57+08:00 moved status: Task set to in progress and assigned to Mark Rolis Valenzuela
- 2026-08-06T01:59:17+08:00 committed: Commit 6d0d9c4 "feat: add article category governance" (GitHub, branch feature/art-001a-category-governance)
- 2026-08-06T02:33:53+08:00 PR opened: Pull request #3 "feat: add article category governance" opened targeting development (GitHub)
- 2026-08-06T02:58:04+08:00 committed: Commit 80c192d "style: format article-categories persistence import" (GitHub, pushed after PR opening)

### In-Range Day Mapping
- 2026-08-06: commit 6d0d9c4 at 01:59:17; PR #3 opened at 02:33:53; commit 80c192d at 02:58:04 (all GitHub evidence via gh CLI)

### Activity Notes
Implemented the governed Article Category foundation per the ticket deliverable: article-categories Payload collection with root Category + one direct-child Subcategory level, immutable code, unique slug, landing introduction, parent, display order, owner, review dates, draft/published and active/archived lifecycle; hierarchy/immutability/uniqueness/lifecycle/review-date validation; slug and category-status shared fields; persistence hooks; routing, validation, and archive-onward-path utilities; reversible migration 20260805_000000_article_category_governance; regenerated Payload types; fixtures; unit and integration tests. PR #3 targets development and is still open (no reviews yet). No public archive routes or navigation were introduced, per the ticket's exclusion.

---

## 86d3y5m8c: ART-001B - Publish Article Category and Subcategory archives

Status: to do
Activity date: 2026-08-06
URL: https://app.clickup.com/t/86d3y5m8c
Initial dev assignee: Not available
Testing actors: None identified
My role for this task: contributor

### Why this task was included
Ticket maintenance by me in range: created as the second half of the ART-001 split (task updated on 2026-08-06 per API). Team ticket - not my implementation todo.

### Description
Description
Publish qualified Category and Subcategory archive pages after the Article Category and Article foundations are available.
Scope
Implement the shared ArticlePreview component.
Implement the article-archive-v1 query service.
Add:
Root Category archive routes
Subcategory archive routes
Derived breadcrumbs
Qualified child navigation
Crawlable pagination
Add derived archive qualification and eligible-Article counts.
Add Category SEO:
Overrides
Defaults
Canonical behavior
Robots behavior
Breadcrumb structured data
Sitemap inclusion
Render one governed onward path after page-one pagination.
Add:
Lifecycle invalidation
Fixtures
Responsive verification
Automated tests
Deliverables
Routes
Root Category archives use:
/articles/category/[category-slug]
Subcategory archives use:
/articles/category/[category-slug]/[subcategory-slug]
Archive Content
Root Category archives aggregate:
Articles assigned directly to the root Category
Articles assigned to direct-child Subcategories
Subcategory archives include direct Article assignments only.
Article Previews
Each Article preview displays:
Complete title
Concise summary
Publication date
Approved byline
Optional eligible featured Media
Missing or ineligible Media collapses without displaying a placeholder.
Ordering and Pagination
Eligible Articles are ordered by publishedAt in descending order.
Immutable Article code is used as the deterministic tie-breaker.
Each crawlable page contains 12 unique records.
Page Layout
Page one renders:
Full archive identity
Qualified child navigation
Article listing
Pagination
One governed onward path
Later pages render:
Compact archive identity
Article listing
Pagination
Archive Qualification
An archive qualifies for publication only when it has:
At least three eligible Articles
A unique, visible introduction
Current owner and review metadata
At least one valid onward path
Non-qualifying Categories:
Remain assignable to Articles
Do not produce a public route
Do not appear in public navigation
Do not appear in the sitemap
Exclusions
Do not introduce:
Hero images
Filters
Client-only sorting
Infinite scrolling
Offering shelves
Repeated CTA breakers
Testing and Verification
The following must be tested:
Query bounds
Lifecycle changes
Qualification loss
Optional-region suppression
SEO behavior
Accessibility
Compact layouts
Wide layouts
No-JavaScript output

### Comments
No comments found.

### Activity Timeline
- 2026-08-05T19:01:43+08:00 created: ART-001B task created as part of the ART-001 split (content-based ticket restructure)
- 2026-08-06T03:06:30+08:00 updated: Task updated in range (relationship/status maintenance during the ART ticket restructure)

### In-Range Day Mapping
- 2026-08-06: task updated at 03:06:30 (per API date_updated); no comments

### Activity Notes
Second half of the ART-001 split: the original ART-001 had a circular dependency with ART-002, so the first half (category governance) became ART-001A to unblock ART-002, and the archive publishing scope moved to ART-001B to be tackled after ART-001A and ART-002 land. Team ticket - my involvement today was the split and relationship maintenance, not implementation.

---

## 86d3xhg34: ART-002 - Article foundation and detail shell

Status: to do
Activity date: 2026-08-06
URL: https://app.clickup.com/t/86d3xhg34
Initial dev assignee: Not available
Testing actors: None identified
My role for this task: contributor

### Why this task was included
Relationship fixed by me based on ticket content: ART-002 now explicitly depends on ART-001A instead of the circular former ART-001 (task updated in range on 2026-08-06 per API). Team ticket - not my implementation todo.

### Description
Repository source: docs/epics/article-publishing-v1.md
Type: Task
Suggested labels: articles, payload, frontend, content-model, seo
Dependencies: ART-001A
Outcome
Editors can create governed guide and news Article records, and visitors can open a stable, server-rendered Article detail route with the required identity, metadata, dates, Media, and body outlet.
Scope
Add the canonical articles collection.
Add the minimum canonical Person and Organization fields needed for Article authorship when those shared collections do not already exist.
Implement:
Article lifecycle
Category assignment
Dates
Featured Media
Source notes
SEO
Routes
Eligibility
Bounded query projections
Base detail shell
Provide extension points for the component tickets without adding unfinished public regions.
Content Model
Immutable, unique code.
Unique public slug.
Required title.
Required concise summary or standfirst.
editorialMode of guide or news.
One to four ordered, distinct Person or Organization author credits using stable edge keys.
Required publishedAt.
Optional materiallyUpdatedAt.
Optional short updateNote.
Exactly one active primary Article Category.
Selecting a Subcategory derives its root Category.
Optional, currently eligible editorial featuredMedia.
Controlled body field whose available nodes are delivered by:
ART-003
ART-004
ART-005
ART-006
ART-008
ART-009
Governed source relationships and notes for:
Claims
Quotations
Downloads
Images
Video
Required owner.
Guide review metadata.
Payload draft/published state.
Operational active/archived status.
Optional SEO title, description, and social Media overrides.
SEO Behavior
Meta title defaults to the Article title.
Meta description defaults to the concise summary.
Social Media defaults to:
Eligible featured Media
The site default
Canonical URL is derived from the Article slug and is not editor-authored.
Robots and sitemap eligibility derive from:
Publication eligibility
Operational eligibility
Author eligibility
Category eligibility
Route eligibility
Guide-review eligibility
Article structured data derives from visible canonical content.
Editors cannot enter raw JSON-LD.
Acceptance Criteria
Article Authoring and Lifecycle
Editors can create guide and news Articles with the defined:
Identity
Lifecycle
Authors
Dates
Category
Media
Sources
Body
SEO groups
A guide cannot publish without:
reviewedAt
A future reviewDueAt
A news Article does not require guide review metadata unless it is materially maintained beyond the original report.
publishedAt is required.
A visible material-update date and note are supported without treating typo-only changes as material revisions.
Authors
Articles contain one to four ordered, distinct author credits.
Author credits reference canonical, active People or Organizations.
Person targets require Article-author eligibility.
No author name, role, biography, image, or profile URL is copied onto the Article.
Categories and Routes
Every publishable Article has exactly one active Category or Subcategory.
Selecting a Subcategory derives the root Category and prevents a separate override.
Article Category changes do not change /articles/[article-slug].
Media and Sources
Featured Media is optional.
Featured Media is selectable only when:
Approved for editorial use
Rights are current
Accessibility data is present
Missing optional Media or sources remove their complete regions without placeholders or empty headings.
Article Detail Page
The base detail shell renders:
Breadcrumbs or Category
H1
Summary
Ordered byline names
Publication date
Material-update date, when applicable
Optional featured Media
Body outlet
Sources or update context
Qualified archive return
Eligibility
The eligible-Article predicate requires:
Published status
Active operational status
A canonical route
At least one valid author credit
One active primary Category
Current review metadata for guides
Query Projections
Hub and archive projections retrieve preview fields only.
Hub and archive projections do not populate:
Article bodies
Full relationship graphs
Detail projections are bounded to the root fields and summaries required by the enabled components.
SEO and Server Rendering
SEO defaults and overrides are implemented and tested.
Canonical URL behavior is implemented and tested.
Redirect behavior is implemented and tested.
Robots behavior is implemented and tested.
Sitemap behavior is implemented and tested.
Initial Article structured data is implemented and tested.
Core metadata, headings, links, and body are present in server-rendered HTML without client-side data fetching.
Supporting Work
Required indexes are included.
A reversible migration is included.
Payload types are regenerated.
Admin help text is included.
Fixtures are included.
Automated tests are included.
Exclusions
The following are delivered by their own tickets:
Key Takeaways
Share Bar
Generated table of contents
Expanded author profiles
Topics
A5-A7
A9
A10
Additionally:
No related Offering field is created.
No A8 editor control is created.
Common Definition of Done
Branch and Pull Request
Work branches from the current development branch.
Branch names use one of the following formats:
feature/articles-art-###-short-name
fix/articles-art-###-short-name
The pull request:
Targets development
Links its ART ticket
Identifies the specification sections implemented
Schema and Types
Schema work includes a reversible production migration.
Payload TypeScript types are regenerated.
Testing
The following cases are tested:
Positive cases
Boundary cases
Rejection cases
Lifecycle cases
Optional-suppression cases
UI work includes:
Compact-width verification
Wide-width verification
Keyboard-accessibility evidence
Server Rendering and Content Safety
Core public content and navigation are present in server-rendered HTML.
Test content is synthetic or explicitly:
Sanitized
Rights-cleared
The following must not be committed:
Secrets
Raw production data
Copied canonical relationship content
Temporary raw URL fields
Required Checks
The following commands must pass:
pnpm format
pnpm check
pnpm build
The production Docker image build must also pass.
Verification and Documentation
Relevant local and development routes pass smoke tests before merge.
Documentation is updated when any of the following change:
Authoring
Validation
Fixtures
Contributor workflow
CI and required review pass before merge.

### Comments
No comments found.

### Activity Timeline
- 2026-08-04T15:00:29+08:00 created: ART-002 task created in the Sprint list
- 2026-08-06T02:53:41+08:00 updated: Dependency relationship fixed to ART-001A (removed circular dependency on the former ART-001)

### In-Range Day Mapping
- 2026-08-06: task updated at 02:53:41 (per API date_updated); no comments

### Activity Notes
ART-002's dependency was corrected from the former ART-001 to ART-001A as part of the content-based relationship fix, resolving the circular dependency so ART-001A can be tackled first, then ART-002, then ART-001B. Team ticket - my involvement today was the dependency/relationship fix, not implementation.

---
