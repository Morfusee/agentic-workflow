# AGENTS.md

Repository policy for Codex agents in `agentic-workflow`.

This file adopts Skill Creator conventions 1:1, with one enforced override:
all skill authoring and updates must be written in this repository.

## Non-Negotiable Path Override

- Treat `$HOME\Documents\Programming\agentic-workflow\skills` as canonical.
- Force all new skill creation into a categorized folder under `skills/<category>/<skill-name>/` in this repo.
- Force all edits to existing project skills to remain in this repo.
- Do not default to `$CODEX_HOME/skills` or `~/.codex/skills`.
- If asked for no location, still write to this repo.
- If asked for a different location, confirm intent before writing outside this repo.

## Approved Generated Artifact Locations

Use these canonical subpaths under `${HOME}/Documents/Programming/agentic-workflow/memory`:

- `memory/tickets/linear/YYYY-W##/` for Linear ticket dumps and weekly Linear ticket artifacts.
- `memory/tickets/clickup/YYYY-W##/` for ClickUp ticket dumps and weekly ClickUp ticket artifacts.
- `memory/presentations/[presentation-name]/` for slideshow generator output.

Before creating a new directory or file in one of these locations, check whether an existing implementation already exists in the target location and reuse it if present.

## Path Privacy

- When writing docs, handoffs, plans, tickets, memory artifacts, config examples, or generated skill output, use `$HOME` for paths under the current user's home directory.
- Do not write expanded user-specific home paths such as `C:\Users\<name>` or `/Users/<name>` into repository files.
- If a tool returns an expanded home path, rewrite the home prefix to `$HOME` before saving or reporting it.

## Worktree Directory

- Canonical worktree root: `~/Documents/Programming/worktrees`.
- The `using-git-worktrees` skill resolves this preference automatically when `AGENTS.md` declares it.

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

Each skill must live under a category folder:

`skills/<category>/<skill-name>/`

The provider-facing sync target remains flat as `<skill-name>/`; category folders are for repo navigation only.

Inside each skill folder:

- Required file: `SKILL.md`
- Recommended file: `agents/openai.yaml`
- Optional folders: `scripts/`, `references/`, `assets/`

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

## Commit Convention

All commits in this repository must follow [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) as defined in [`CONTRIBUTING.md`](CONTRIBUTING.md). Before committing, read `CONTRIBUTING.md` and apply its rules: valid types (`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`), optional scope in parentheses, imperative mood, lowercase description, no trailing period, and under 72 characters.

- Never batch unrelated changes into a single commit. Each logical change gets its own commit.
- Stage and commit one concern at a time. Do not combine feature work, refactors, migrations, or doc updates into the same commit.

## Skill Visibility Control

Place an empty `.codex-hidden` file inside any skill folder to prevent it from being symlinked into Codex's skills directory. The skill will still sync to OpenCode when `SYNC_OPENCODE=true`.

Use this for skills that are opencode-specific or should not be exposed to other LLM agents.

Place an empty `.opencode-hidden` file inside any skill folder to prevent it from being symlinked into OpenCode's skills directory. The skill will still sync to Codex.

Use this for skills that are Codex-specific or should not be exposed to OpenCode agents.
