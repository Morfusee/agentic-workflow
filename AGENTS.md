# AGENTS.md

Repository policy for Codex agents in `agentic-workflow`.

This file adopts Skill Creator conventions 1:1, with one enforced override:
all skill authoring and updates must be written in this repository.

## Non-Negotiable Path Override

- Treat `C:\Users\mrqvp\Documents\Programming\agentic-workflow\skills` as canonical.
- Force all new skill creation into `skills/<skill-name>/` in this repo.
- Force all edits to existing project skills to remain in this repo.
- Do not default to `$CODEX_HOME/skills` or `~/.codex/skills`.
- If asked for no location, still write to this repo.
- If asked for a different location, confirm intent before writing outside this repo.

## Skill Creation Standard

Follow the Skill Creator process in order:

1. Understand the skill with concrete trigger examples.
2. Plan reusable contents (`scripts/`, `references/`, `assets/`) only if needed.
3. Initialize the skill structure.
4. Implement and edit `SKILL.md` plus any required resources.
5. Validate structure and metadata.
6. Iterate using real usage feedback and forward-testing when appropriate.

## Naming Rules

- Use lowercase letters, digits, and hyphens only.
- Keep skill name under 64 characters.
- Prefer short action-oriented names.
- Name the folder exactly as the skill name.

## Required Skill Structure

Each skill must live under:

`skills/<skill-name>/`

Required file:

- `skills/<skill-name>/SKILL.md`

Recommended file:

- `skills/<skill-name>/agents/openai.yaml`

Optional folders:

- `skills/<skill-name>/scripts/`
- `skills/<skill-name>/references/`
- `skills/<skill-name>/assets/`

Do not create auxiliary docs like `README.md`, `CHANGELOG.md`, or install guides inside skill folders unless explicitly requested.

## SKILL.md Rules

`SKILL.md` must contain:

1. YAML frontmatter with only:
- `name`
- `description`
2. Markdown body with operational instructions.

Frontmatter requirements:

- Keep `description` as the main trigger signal.
- Include what the skill does and when to use it in `description`.
- Do not add extra frontmatter fields.

Body requirements:

- Write instructions in imperative/infinitive style.
- Keep core instructions concise.
- Keep variant-heavy details in `references/` and link from `SKILL.md`.
- Avoid duplicating the same details across files.

## agents/openai.yaml Rules

When present, keep strings quoted and keys unquoted.

Include:

- `interface.display_name`
- `interface.short_description`
- `interface.default_prompt`

`interface.default_prompt` must explicitly reference the skill as `$skill-name`.

Add optional icon/color fields only when explicitly provided or available.

## Progressive Disclosure Standard

- Keep `SKILL.md` lean and focused on workflow.
- Store deep reference material in `references/`.
- Store deterministic repeatable logic in `scripts/`.
- Store output templates/resources in `assets/`.
- Link reference files directly from `SKILL.md` when needed.

## Validation Standard

- Run Skill Creator validation scripts when runtime is available.
- Validate frontmatter shape, naming, and required files.
- If validation cannot run (tooling missing), report that limitation explicitly.

## Editing and Update Policy

- Preserve user-authored intent when revising a skill.
- Make minimal, targeted changes when updating existing skills.
- Keep skills standalone unless explicit coupling is requested.
- Never move skill source-of-truth outside this repository by default.

## Symlink Intent

This repository is symlinked for skill usage. Treat local repo files as source of truth for all skill work.
