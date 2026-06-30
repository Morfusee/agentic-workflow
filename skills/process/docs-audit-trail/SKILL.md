---
name: docs-audit-trail
description: Docs audit trail for bootstrappable repos. Use when a repo needs AGENTS.md to force brainstorms, plans, agreements, and project references under docs/, or when another bootstrap skill needs to create docs/brainstorm and docs/plans idempotently.
---

# Docs Audit Trail

Use this skill to make project knowledge auditable inside the target repository.

## Steps

1. Identify the target repository root.
   - Use the user-provided path when present.
   - Otherwise use the current working directory.
   - Complete when the repository root is known.

2. Protect existing work.
   - Run `git status` and `git diff` in the target repository before edits.
   - Identify modified files and user-owned changes.
   - Preserve existing `AGENTS.md` content unless it directly conflicts with the docs audit trail directive.
   - Complete when the existing-change summary is known.

3. Create the docs directories.
   - Ensure `docs/`, `docs/brainstorm/`, and `docs/plans/` exist.
   - Do not create placeholder files unless the user asks for them.
   - Complete when all three directories exist.

4. Update or create `AGENTS.md`.
   - Add the docs audit trail directive below as a single source of truth.
   - If an equivalent directive already exists, leave it unchanged unless the directive needs the updated wording below.
   - If another instruction says brainstorms or plans belong outside the repo, this directive must explicitly override it.
   - Complete when `AGENTS.md` contains the directive exactly once.

5. Verify and report.
   - Re-run `git diff`.
   - Confirm the docs directories exist and `AGENTS.md` contains one docs audit trail directive.
   - Report created directories and whether `AGENTS.md` was created, updated, or already compliant.

## AGENTS.md Directive

```md
## Docs Audit Trail

Agents must treat `docs/` as the repository source of truth for project references, brainstorms, plans, agreements, and other durable working notes.

Agents must check relevant files under `docs/` before planning or implementing changes.

Brainstorms must be saved under `docs/brainstorm/`. Capture the full useful conversation trail, including context, options considered, decisions, rejected paths, and open questions. Do not rely on chat history as the only audit trail.

Plans must be saved under `docs/plans/`. Each plan must distill the concrete implementation path from the related brainstorm or agreement, including scope, steps, validation, risks, and unresolved questions.

If the user and agent reach a concrete agreement, the agent must ask whether to write it as a Markdown file under `docs/`. When the agreement is a brainstorm, use `docs/brainstorm/`; when it is an execution plan, use `docs/plans/`; otherwise use the most relevant `docs/` subfolder.

This repository-local directive overrides any global or parent `AGENTS.md` instruction that would place brainstorms, plans, or durable project notes outside this repository.
```
