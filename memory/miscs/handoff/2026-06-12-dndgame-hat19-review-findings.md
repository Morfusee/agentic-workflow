# Handoff: DnDGame HAT-19 Review Findings

## Next Session Focus

Address the implementation-review findings from the HAT-19 DnDGame documentation branch review. The prior review initially looked at the `agentic-workflow` skill changes by mistake; the user clarified that the review should be for DnDGame. The current handoff is for a fresh agent to continue from the DnDGame HAT-19 findings, not the ticket-comment workflow skill review.

## Scope

- Target repo: `<dndgame-repo>`
- Branch reviewed: `docs/hat-19`
- Base branch used for review: `master`
- Linear ticket: `https://linear.app/hatudoggy/issue/HAT-19/define-dndgame-sqlite-schema-and-migration-contract`
- HAT-19 commit on the branch: `docs(db): define sqlite schema contract for HAT-19`

Do not duplicate the ticket body, full branch diff, or schema document in the next response. Inspect the source files directly.

## Files To Inspect

- `<dndgame-repo>/docs/plans/hat19-sqlite-schema.md`
- `<dndgame-repo>/docs/architecture/ARCHITECTURE.md`
- `<dndgame-repo>/docs/specifications/game-design/dice-rolling.md`
- Linear HAT-19 issue linked above, if provider context is needed

## Review Findings To Address

1. `campaigns.current_location_id` and `campaigns.current_event_id` are documented without explicit foreign-key or integrity guidance, even though campaign resume depends on those pointers. Review `docs/plans/hat19-sqlite-schema.md` around the `campaigns` table and the common read paths.

2. `dice_rolls.visibility` allows `dm_hidden`, but the active dice-rolling game-design spec says dice results are never hidden from the player. Decide whether HAT-19 should remove hidden dice visibility or whether the design spec needs an explicit exception, then update the docs consistently.

3. `docs/architecture/ARCHITECTURE.md` points to the HAT-19 schema contract but still includes stale concrete schema examples that do not match the HAT-19 table set. Decide whether to update those examples, make them explicitly illustrative/legacy, or replace them with a short reference to the HAT-19 contract.

## Current Agentic-Workflow State

This handoff was created from the `agentic-workflow` repo. Before writing this file, `git status --short` and `git diff` were clean. This file is the only intended new artifact for this request.

Separate handoff artifacts already exist for the ticket-comment workflow review and skill fix. Do not mix those with the DnDGame HAT-19 review unless the user explicitly asks.

## Suggested Skills

- `$workflow-orchestrator`: Use if the next session needs Linear HAT-19 context or wants to publish a review/fix comment back to the ticket.
- `$ticket-implementation-flow`: Use if the next session will implement the HAT-19 documentation fixes in DnDGame and potentially commit/comment on the ticket.
- `$refactor`: Use for minimal, targeted documentation cleanups if the fixes are wording-only and should avoid broad rewrites.
- `$git-commit`: Use only if the user asks to commit the finalized DnDGame changes.

## Safety Notes

- No secrets, API keys, tokens, or passwords are included here.
- Personal local paths are redacted to placeholders.
- Preserve any existing uncommitted work in both `agentic-workflow` and DnDGame. Run `git status` and `git diff` before editing.
