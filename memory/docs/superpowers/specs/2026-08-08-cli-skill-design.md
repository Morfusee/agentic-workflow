# CLI Skill Design

## Objective

Create a user-invocable `cli` skill that routes natural-language requests to registered command-line tools, beginning with GitHub CLI (`gh`). Keep normal operation fast by using concise stored references, while allowing references to be created exhaustively and corrected when verified command drift is encountered.

## Invocation

Support three forms:

```text
/cli gh <request>
/cli <request>
/cli create <CLI name or executable>
```

- Treat an explicitly supplied CLI as authoritative.
- Infer an omitted CLI from the registry's aliases and intent signals.
- Ask the user when multiple registered CLIs remain plausible.
- Report that no registered CLI handles the request when no match exists.
- Reserve `create` for first-time CLI reference creation; never route it as an operational request.

The first release registers only `gh`. The structure must support later CLIs without adding a separate skill for each one.

## Skill Structure

Create the skill at:

```text
skills/tools/cli/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── registry.md
    └── gh.md
```

Do not add a scripts directory. The installed CLI's help interface already provides the required introspection, and agents can perform the discovery directly.

`SKILL.md` owns argument parsing, routing, normal execution, reference creation, and targeted repair rules. `registry.md` owns CLI aliases and routing signals. Each CLI reference owns its concise command directory and CLI-specific context.

## Registry Schema

Keep `registry.md` compact. Record for each supported CLI:

- Canonical executable
- Human-friendly names and aliases
- Intent signals for automatic routing
- Reference-file path

Initial example:

```markdown
| CLI | Names and aliases | Intent signals | Reference |
|---|---|---|---|
| `gh` | GitHub CLI, GitHub | pull requests, issues, releases, repositories, Actions | `gh.md` |
```

Avoid duplicating the command directory in the registry.

## CLI Reference Schema

Name each reference after the canonical executable when practical, such as `gh.md`, `docker.md`, or `clickup.md`.

Each reference must contain:

- Canonical executable and detected version
- Last verified date
- Supported help syntax
- Important environment and authentication context
- A concise directory of every discovered command and subcommand
- A one-line purpose for every command path
- CLI-specific caveats that materially affect safe or correct use
- A maintenance note stating that `/cli create` generated the reference

Do not copy every flag and example from help output. The reference is a navigable command directory, not a frozen replacement for the CLI's complete manual.

## Normal Operation

For `/cli [optional CLI] <request>`:

1. Resolve an explicit CLI or infer one from `registry.md`.
2. Load only the selected CLI's reference.
3. Select and execute the documented command path under the agent's existing authorization and safety rules.
4. Do not run help routinely before operational commands.
5. Classify failures before deciding whether the reference is stale.

Normal operation must not gain additional authority from this skill. Destructive, sensitive, or externally visible actions remain governed by the user's request and the agent's normal safeguards.

## First-Time Reference Creation

For `/cli create <tool>`, use an exhaustive help-only documentation process:

1. Normalize the requested name and likely executable aliases.
2. Resolve the executable using the platform-aware discovery process.
3. Validate candidates with non-mutating version or help introspection.
4. Run the CLI's root help interface.
5. Discover commands and subcommands from help output.
6. Recursively inspect every discovered command path through help only.
7. Prevent cycles and duplicate traversal caused by aliases, wrappers, or repeated paths.
8. Generate `references/<canonical-executable>.md` using the reference schema.
9. Add the CLI's aliases, intent signals, and reference path to `registry.md`.
10. Compare the generated directory with the discovered tree and account for every unique command path.
11. Report every created or updated file.

Never discover a command tree by executing guessed operational commands. Recursive traversal occurs only during first-time creation, not normal use or targeted repair.

If the CLI is already registered and its reference exists, do not overwrite it through an ordinary `create` request. Report that it already exists and use targeted self-correction during normal operation. Perform a full regeneration only when the user explicitly requests a rebuild, and preserve unrelated user-authored content.

## Cross-Platform Executable Discovery

Detect the current operating system and shell before resolving an executable.

### Windows

Inspect:

- `Get-Command -All`
- `where.exe`
- PowerShell aliases, functions, applications, wrappers, and command shims
- Every directory in `PATH`
- Common WinGet, Chocolatey, Scoop, npm, pnpm, Bun, Python, Cargo, and Go binary locations

### Linux and macOS

Use supported resolution mechanisms rather than assuming every shell exposes the same commands:

- `command -v`
- `type -a`
- `which -a` when available
- `whence -a` when supported
- Shell aliases, functions, built-ins, executables, wrappers, and shims
- Every directory in `PATH`
- Common locations including `/usr/local/bin`, `/usr/bin`, `/bin`, `$HOME/.local/bin`, `/opt/homebrew/bin`, and `/opt/local/bin`
- Relevant Homebrew/Linuxbrew, npm, pnpm, Bun, Python, Cargo, Go, Nix, asdf, and mise locations

Account for PowerShell, Bash, Zsh, Fish, and other POSIX-compatible shell differences. After discovery, use the CLI's canonical command in references and examples; absolute paths, platform suffixes, and wrappers remain discovery details unless the CLI requires them.

Keep discovery bounded to command-resolution data, configured paths, and common tool locations. Do not scan the entire filesystem indiscriminately.

If exhaustive local discovery finds no valid executable:

- Report only that the CLI is not present on the current host.
- Do not install it.
- Do not provide installation guidance unless the user separately requests it.
- Do not generate an unverified reference from web documentation.

## Targeted Self-Correction

Treat the skill as self-correcting rather than freely self-modifying.

When normal operation encounters evidence that a documented command path is stale or incomplete:

1. Inspect help only along the affected command path.
2. Compare live help with the stored reference.
3. Update only the verified stale or missing reference entry.
4. Preserve unrelated reference content and user-owned changes.
5. Retry the operation only when doing so is safe and still authorized.
6. Tell the user which reference changed and why.

Do not rewrite an entire reference for a local discrepancy. Do not interpret authentication, authorization, network, remote-service, repository-state, or invalid-input failures as documentation drift.

## Failure Classification

- **CLI unavailable:** complete platform-specific discovery, then report absence without installation guidance.
- **Reference drift:** perform targeted help inspection, surgical correction, disclosure, and a safe retry when appropriate.
- **Operational failure:** report the actual authentication, authorization, network, repository-state, remote-service, or input problem without modifying references.
- **Ambiguous routing:** ask the user which registered CLI to use.
- **Unmatched routing:** report that no registered CLI handles the request.

## Validation

Validate the implementation through:

- Skill metadata, naming, required-file, and `agents/openai.yaml` checks
- Explicit routing with `/cli gh <request>`
- Inferred routing from a GitHub-related request without `gh`
- `/cli create gh` using recursive help-only discovery
- Complete correspondence between the discovered `gh` tree and `gh.md`
- Alias-cycle and duplicate-path protection
- Unavailable-command handling without installation or web-generated reference fallback
- A deliberately stale command entry that triggers targeted repair
- Preservation and disclosure of self-correcting reference changes
- Confirmation that normal operational routing does not routinely invoke help

Test the current host directly. Treat the documented Windows, Linux, and macOS discovery branches as required behavior; validate additional operating systems when an appropriate host is available.

## Success Criteria

The design is successfully implemented when:

- `/cli` provides one durable entry point for registered CLI tools.
- `gh` can be selected explicitly or inferred from a request.
- `gh.md` contains a concise, complete command and subcommand directory derived from the installed CLI's help tree.
- `/cli create` can add future locally installed CLIs without another skill.
- First-time creation uses exhaustive recursive help traversal without operational probing.
- Normal use remains reference-first and does not run help routinely.
- Verified drift produces a surgical, user-disclosed reference correction.
- Missing CLIs are exhaustively checked, reported, and neither installed nor documented from unverified sources.
