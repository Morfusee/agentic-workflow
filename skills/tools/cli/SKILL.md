---
name: cli
description: Route natural-language requests to registered command-line tools. Use when the user invokes /cli, names GitHub CLI (gh) or another registered CLI, or asks to create a reference for a newly installed CLI.
---

# CLI

Route `/cli` requests to registered command-line tools using concise stored references. Normal operation is reference-first: load the stored reference, do not run help routinely, and correct the reference only when verified drift is found.

## Invocation

Support three forms:

```text
/cli gh <request>
/cli <request>
/cli create <CLI name or executable>
```

- Treat an explicitly supplied CLI as authoritative.
- Infer an omitted CLI from `references/registry.md` aliases and intent signals.
- When multiple registered CLIs remain plausible, stop and ask the user which CLI to use before executing anything; never guess or default to one.
- Report that no registered CLI handles the request when no match exists.
- Reserve `create` for first-time CLI reference creation; never route it as an operational request.

## Normal Operation

For `/cli [optional CLI] <request>`:

1. Resolve an explicit CLI or infer one from `references/registry.md`. If inference matches more than one registered CLI, stop and ask the user which to use; do not guess.
2. Load only the selected CLI's reference from `references/`.
3. Select and execute the documented command path under the agent's existing authorization and safety rules.
4. Do not run help routinely before operational commands.
5. If an executed command fails, retry at most once, then report the failure; do not retry in a loop.
6. Classify failures before deciding whether the reference is stale.

### Safety Boundary

This skill grants no additional authority. Destructive, sensitive, or externally visible actions remain governed by the user's request and the agent's normal safeguards. Confirm before commands that delete, modify remotely, or affect other users.

## First-Time Reference Creation

For `/cli create <tool>`:

1. Normalize the requested name and likely executable aliases.
2. Resolve the executable using the platform-aware discovery process below.
3. Validate candidates with non-mutating version or help introspection.
4. Run the CLI's root help interface.
5. Discover commands and subcommands from help output.
6. Recursively inspect every discovered command path through help only.
7. Prevent cycles and duplicate traversal caused by aliases, wrappers, or repeated paths; visit each command path once.
8. Generate `references/<canonical-executable>.md` using the CLI Reference Schema.
9. Add the CLI's aliases, intent signals, and reference path to `references/registry.md`.
10. Compare the generated directory with the discovered tree and account for every unique command path.
11. Report every created or updated file.

Never discover a command tree by executing guessed operational commands. Recursive traversal occurs only during first-time creation, never during normal use or targeted repair.

### Rebuild Rule

If the CLI is already registered and its reference exists, an ordinary `create` request must not overwrite it. Report that it already exists and use targeted self-correction during normal operation. Perform a full regeneration only when the user explicitly requests a rebuild, and preserve unrelated user-authored content.

## Cross-Platform Executable Discovery

Detect the current operating system and shell before resolving an executable. Keep discovery bounded to command-resolution data, configured paths, and common tool locations; do not scan the entire filesystem.

### Windows

Inspect:

- `Get-Command -All <name>` and `where.exe <name>`
- PowerShell aliases, functions, applications, wrappers, and command shims
- Every directory in `PATH`
- Common WinGet, Chocolatey, Scoop, npm, pnpm, Bun, Python, Cargo, and Go binary locations

### Linux and macOS

Use supported resolution mechanisms rather than assuming every shell exposes the same commands:

- `command -v`, `type -a`, `which -a` when available, `whence -a` when supported
- Shell aliases, functions, built-ins, executables, wrappers, and shims
- Every directory in `PATH`
- Common locations including `/usr/local/bin`, `/usr/bin`, `/bin`, `$HOME/.local/bin`, `/opt/homebrew/bin`, and `/opt/local/bin`
- Relevant Homebrew/Linuxbrew, npm, pnpm, Bun, Python, Cargo, Go, Nix, asdf, and mise locations

Account for PowerShell, Bash, Zsh, Fish, and other POSIX-compatible shell differences. Use the CLI's canonical command in references and examples; absolute paths, platform suffixes, and wrappers remain discovery details unless the CLI requires them.

### Absence Handling

If exhaustive local discovery finds no valid executable:

- Report only that the CLI is not present on the current host.
- Do not install it.
- Do not provide installation guidance unless the user separately requests it.
- Do not generate an unverified reference from web documentation.

## Targeted Self-Correction

When normal operation encounters evidence that a documented command path is stale or incomplete:

1. Inspect help only along the affected command path.
2. Compare live help with the stored reference.
3. Update only the verified stale or missing reference entry.
4. Preserve unrelated reference content and user-owned changes.
5. Retry the operation only when doing so is safe and still authorized.
6. Tell the user which reference changed and why.

Do not rewrite an entire reference for a local discrepancy. Do not interpret authentication, authorization, network, remote-service, repository-state, or invalid-input failures as documentation drift.

## Failure Classification

- CLI unavailable: complete platform-specific discovery, then report absence without installation guidance.
- Reference drift: targeted help inspection, surgical correction, disclosure, and a safe retry when appropriate.
- Operational failure: report the actual authentication, authorization, network, repository-state, remote-service, or input problem without modifying references.
- Ambiguous routing: ask the user which registered CLI to use.
- Unmatched routing: report that no registered CLI handles the request.

## CLI Reference Schema

Name each reference after the canonical executable (`gh.md`, `docker.md`). Each reference must contain: canonical executable and detected version; last verified date; supported help syntax; important environment and authentication context; a concise directory of every discovered command and subcommand; a one-line purpose for every command path; CLI-specific caveats; and a maintenance note stating that `/cli create` generated the reference. Do not copy every flag and example from help output; the reference is a navigable command directory, not a frozen replacement for the CLI's complete manual.
