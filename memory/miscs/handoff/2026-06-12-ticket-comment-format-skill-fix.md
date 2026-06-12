# Handoff: Ticket Comment Format Skill Fix

## Next Session Focus

Fix the skill workflow so provider-facing implementation comments reliably use the exact template in `skills/ticket-implementation-flow/references/ticket-comment-format.md`.

The immediate problem: during the HAT-19 implementation flow, the Linear comment was first posted in the older/stale format, then rewritten in a custom heading-heavy format, and only corrected after the user pointed to the current reference file. The skill setup paths appear correct; the gap is that the workflow does not force a fresh template read and exact-format self-check immediately before publishing.

## Current Repository State

- Repo: `C:\Users\mrqvp\Documents\Programming\agentic-workflow`
- Canonical memory root: `C:\Users\mrqvp\Documents\Programming\agentic-workflow\memory`
- Existing uncommitted change before this handoff: `skills/ticket-implementation-flow/references/ticket-comment-format.md`
- That existing change updates the provider-facing comment template labels to use bold branch label and `###` section headings.
- This handoff file is the only new file intentionally added for this request.

Do not overwrite or revert the existing uncommitted template change. Treat it as user-owned context unless the user explicitly asks otherwise.

## Relevant References

- Active template to enforce: `skills/ticket-implementation-flow/references/ticket-comment-format.md`
- Skill to revise: `skills/ticket-implementation-flow/SKILL.md`
- Likely related orchestrator reference: `skills/workflow-orchestrator/references/providers/linear.md`
- Workflow entrypoint skill: `skills/workflow-orchestrator/SKILL.md`
- Prior Linear ticket involved: HAT-19, `https://linear.app/hatudoggy/issue/HAT-19/define-dndgame-sqlite-schema-and-migration-contract`
- Prior DnDGame implementation branch: `docs/hat-19` in `C:\Users\mrqvp\Documents\Programming\DnDGame`
- Prior DnDGame commit: latest commit on that branch when completed was `docs(db): define sqlite schema contract for HAT-19`

## What Happened

- HAT-19 was implemented in the separate `DnDGame` repo and committed.
- A Linear implementation comment was posted using the ticket implementation notification flow.
- The user later asked to redo the Linear comment based on the new format.
- The comment was rewritten, but not exactly according to `skills/ticket-implementation-flow/references/ticket-comment-format.md`.
- The user asked whether that exact file was used and pasted the current template.
- The comment was then corrected in place to match the current template.
- Follow-up discussion concluded this is best categorized as a skill workflow robustness issue, not a symlink/setup issue.

## Diagnosis

The OpenCode skill symlink appears correct:

- `C:\Users\mrqvp\.config\opencode\skills\ticket-implementation-flow` resolves to `C:\Users\mrqvp\Documents\Programming\agentic-workflow\skills\ticket-implementation-flow`.

The likely root cause is procedural:

- The skill says to use the exact structure but does not require re-reading the template immediately before publishing.
- The workflow allows stale loaded context or memory to stand in for the current file.
- There is no pre-publish checklist that verifies the section labels and branch line against the template.
- Provider references delegate notification publishing but do not explicitly require template freshness or exact-format validation.

## Suggested Fix Direction

Update the skills minimally so future agents cannot repeat this failure:

- In `skills/ticket-implementation-flow/SKILL.md`, strengthen Notification Rules to require a fresh read of `references/ticket-comment-format.md` immediately before creating or updating any provider-facing implementation notification.
- Add an exact-format self-check before publishing: first sentence, branch line, section headings, notes behavior, required action section, and no developer names/commit hashes/emojis.
- Consider adding a short rule to `skills/workflow-orchestrator/references/providers/linear.md` under implementation-flow publishing: when publishing ticket-implementation-flow comments, use the comment body produced after the template freshness check and do not reformat it.
- Avoid broad rewrites of unrelated workflow sections.

## Suggested Skills

- `$config-symlink-maintainer`: Use only if investigating skill source/symlink drift or sync behavior.
- `$refactor`: Useful for surgical skill wording updates without changing behavior outside the notification path.
- `$git-commit`: Use if the user asks to commit the skill fix; follow repo Conventional Commit rules.

## Safety Notes

- No secrets or credentials are included here.
- Do not touch the separate `DnDGame` repo unless the next user request explicitly asks for follow-up there.
- Preserve the existing uncommitted change to `skills/ticket-implementation-flow/references/ticket-comment-format.md`.
- Before editing, run `git status` and `git diff` in `agentic-workflow` and confirm the current uncommitted template change is still present.
