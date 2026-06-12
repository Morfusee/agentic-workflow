# Common Ticket Workflows

Use this reference for provider-neutral ticket, dump, stand-up, review-comment, weekly-slideshow, and publishing rules.

## Helper Skill Routing

- Use `$ticket-drafter` for technical ticket drafts covering defects, regressions, production problems, features, enhancements, refactors, and other implementation work.
- Use `$ticket-implementation-flow` for provider-backed or prompt-backed implementation work that needs requirements analysis, confidence scoring, branch/worktree setup, implementation, commit, and optional ticket notification.
- Use `$ticket-review-comment-drafter` for code review findings, implementation review notes, QA results, pass/fail checks, or test observations intended for provider comments.
- Use `$ticket-dump-creator` after provider facts are collected and normalized.
- Use `$standup-generator` after selected dump/manual items have been normalized into source-agnostic evidence.
- Use `$weekly-ticket-slideshow-generator` only when the selected provider reference supports weekly slideshow prep.

Do not let helper skills publish directly unless the selected provider reference explicitly allows it. Provider tools remain the source of truth for provider writes.

## Draft-First Publishing

- Draft ambiguous or multi-field ticket requests first.
- Present drafts for review before provider creation.
- Publish only after a clear approval signal such as `create it`, `add it`, `publish`, `looks good`, or equivalent.
- Map approved handoff metadata into provider fields using provider tools.
- Ask one focused clarification before publishing when a required provider field is missing.

## Dump Creation Contract

Provider references own retrieval. After retrieval, normalize qualifying items for `$ticket-dump-creator` with these concepts:

- provider identifier and display name
- item terminology and collection heading
- canonical memory subpath
- requested range and dump file date
- generated timestamp
- stable item identifiers, titles, URLs, statuses, dates, chronology, role, ownership, and evidence

Provider-specific filtering must happen before normalization. Include only items with explicit qualifying user activity in the requested range unless the user asks for a broader provider-specific review.

## Stand-Up Contract

Stand-up generation reads an existing dump unless the active branch is a full-flow branch that just created one.

- Prefer the latest compatible ISO week folder and latest `YYYY-MM-DD-ticket-dump.md`.
- Present selectable scraped, manual, and carry-over items.
- Accept `all`, numeric indexes, item IDs, and clear natural-language selections.
- Parse manual items from `Manual: [task title] -- [Done / In Progress / To Do] [optional description]`.
- Parse explicit next-day plans from `Plan: [what you intend to work on next]`.
- Pass only selected items and explicit next-day plans to `$standup-generator`.
- Treat existing `# Stand-up Script` prose as output-only, never evidence.
- Preserve historical scraped item sections unchanged.
- Keep unselected items available for future stand-ups until selected.

Do not infer next-day plans from open, remaining, or unselected work.

## Full-Flow and Range Contract

For each date branch:

1. Run dump creation for that exact date.
2. If successful, run stand-up selection or stand-up generation against the produced dump according to the provider reference.
3. Pass through explicit stand-up selection intent when provided.
4. On dump failure for a date, stop that date branch and continue other dates.

At the end, report each date with status, output path when available, and concise failure reason when failed.

## Evidence and Attribution Rules

- Do not fabricate task details, ticket details, ownership, chronology, or outcomes.
- Do not infer implementation authorship from testing comments, QA-only updates, watching, following, or subscription activity.
- Mark tester-only activity when in-range user activity is only testing, verification, or QA evidence.
- Mark contributor activity only with explicit user development evidence when the user is not the initial dev owner.
- Mark dev-owner activity only with explicit evidence that the user is the initial dev assignee or owner.
- Preserve provider-specific assignment and watching semantics from the provider reference.

## Review Comments

For review or QA comment drafting:

1. Pass provider context and any provider item ID or URL to `$ticket-review-comment-drafter`.
2. Let the drafter create the comment body and determine whether it can publish directly.
3. If the drafter returns a provider-ready body but cannot publish, use the selected provider reference's comment publishing rules.

## Implementation Flow

For `/workflow-orchestrator implement [ticket-or-task]` or provider-specific implementation intent:

1. Resolve the ticket/task/page when a provider ID or URL is supplied.
2. Normalize provider facts: provider name, item ID, title, URL, status, body/description, acceptance criteria, comments needed for requirements, and comment target.
3. Pass normalized context to `$ticket-implementation-flow`.
4. Let `$ticket-implementation-flow` own analysis, confidence scoring, branching, worktree setup, implementation, commit, and notification decisions.
5. Use the selected provider reference's comment publishing rules only when `$ticket-implementation-flow` reaches the ticket notification stage.

## Weekly Slideshows

Route weekly slideshow prep to `$weekly-ticket-slideshow-generator` only when the selected provider reference lists `weekly-slideshow` as a supported branch. Do not infer cross-provider weekly slideshow support.
