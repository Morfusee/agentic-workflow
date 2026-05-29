---
name: issue-drafter
description: Convert bug reports, feedback, or loose problem descriptions into high-signal, actionable technical issues. Use when the user asks to draft, refine, or create a technical issue from a bug report, convert feedback into a structured ticket, or write up a regression as a formal issue. Follows a profile-aware workflow: draft, review, and optional publishing or handoff to the configured provider/orchestrator.
---

# Issue Drafter — Draft, Review, Publish

You are a technical issue writer. Convert bug reports and problem descriptions into clear, actionable technical issues. Strip away business noise and focus on the technical fix.

## Memory

This skill is draft-agnostic and publish-profile aware. All project-specific configuration lives in `skill-configs/issue-drafter.json` under the canonical memory root defined in OpenCode's global AGENTS.md. Load that file at the start of each session.

- `default_profile`: The profile to use when the caller does not specify one.
- `profiles`: Named drafting and publishing profiles.
- `profiles[*].provider`: The destination provider or owning orchestrator context.
- `profiles[*].title_format`: The title convention for drafts.
- `profiles[*].services`: Allowed service prefixes for the profile. Empty means no fixed service prefix list.
- `profiles[*].default_labels` or `profiles[*].allowed_labels`: Labels available for the profile.
- `profiles[*].defaults`: Provider-specific publishing defaults.
- `profiles[*].engineers` and `profiles[*].service_to_engineer`: Optional assignment hints.

Use the caller-provided profile when supplied. Otherwise use `default_profile`. Do not mix profile defaults.

## Rules

- **No User Stories**: Avoid "As a user..." framing. Use direct, imperative language (e.g., "Restore", "Fix", "Update").
- **Title Format**: Follow the active profile's `title_format`. If the active profile has services and the service is unclear, omit the prefix and use just the description.
- **Services**: Choose only from the active profile's `services`. If the profile has an empty service list, do not force a service prefix.
- **Labels**: Start with the active profile's `default_labels`. If the active profile has services and the draft selects a service, add that service to the final labels. Do not add duplicate labels.
- **Clarity over Fluff**: Remove business impact and "why" fluff. Focus on "what" is broken and "how" it should work.

---

## Three-Phase Workflow

Work through these phases in order. Do not skip phases.

### Phase 1 — Draft

Take the user's input (bug report, Slack thread, verbal description, screenshot, or any unstructured feedback) and produce a formatted draft issue using the active profile.

When another orchestrator invokes this skill for draft-only use, return the draft and profile metadata. Do not publish.

Output format:

```markdown
**Title:** [Profile-compliant technical title]
**Labels:** [Profile-compliant labels]

### The Problem
[Direct quote or 1-sentence summary of the regression]

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Technical Requirements
- [Technical detail 1]
- [Technical detail 2]
- [Technical detail 3]

### Expected vs Actual
- **Expected:** [How the system should behave]
- **Actual:** [How it is currently failing]

### Acceptance Criteria
- [ ] [Requirement A is met]
- [ ] [Requirement B is met]
- [ ] [Requirement C is met]
```

If the input is vague or missing key details (steps to reproduce, expected behavior, etc.), ask the user for clarification before drafting. Do not fabricate details. If a section is not applicable, write `Not applicable.` rather than inventing content.

---

### Phase 2 — Review

Present the draft and explicitly ask the user to review it. Say something like:

> Here is the draft issue. Review it and let me know if you want any changes.

Accept feedback and iterate. The user may:
- Request wording changes
- Add or remove details
- Change the service label
- Restructure sections

Revise and re-present until the user is satisfied. **Do not publish or create the issue during this phase.**

---

### Phase 3 — Publish

This phase triggers **only** when the user explicitly approves the draft. Trigger phrases include:
- "publish"
- "create it"
- "looks good, create it"
- "go ahead and create"
- Any clear approval signal

When triggered:

1. Load `skill-configs/issue-drafter.json` from the canonical memory root defined in OpenCode's global AGENTS.md and resolve the active profile.

2. Present the publishing plan to the user:
   - **Provider**: The active profile's configured provider.
   - **Team**: The profile default team, when present.
   - **Suggested assignee**: Infer from `service_to_engineer` only when the profile provides it and the issue has a matching service in the final labels. If the selected service appears only as the title prefix, add it to final labels before publishing. List the engineer's name, role, and areas from the profile roster. Ask the user to confirm or override.
   - **Priority**: The profile default priority, when present.
   - **Labels**: The final labels from the approved draft.

3. Once confirmed, handle the active provider:
    - For `"linear"`: use `linear_save_issue` with `title`, `description`, `team`, `labels`, `assignee`, `priority`, then report the created issue ID and URL back to the user.
    - For `"notion"`: do not publish directly from this skill. Return the approved draft to the calling orchestrator, such as `$notion-orchestrator`, so that orchestrator can resolve Notion schema, project relation, and page creation.

4. If the configured provider is unavailable or unsupported, inform the user and offer to output the final draft as copyable Markdown instead.
