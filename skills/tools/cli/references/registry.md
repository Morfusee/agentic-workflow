# CLI Registry

Maps `/cli` routing to registered CLIs. One row per CLI; reference files live in this directory.

| CLI | Names and aliases | Intent signals | Reference |
|---|---|---|---|
| `gh` | GitHub CLI, GitHub | pull requests, issues, releases, repositories, Actions, codespaces, gists, workflows, auth | `gh.md` |

## Maintenance

- `/cli create` adds rows and reference files.
- An ordinary `create` request never overwrites an existing reference; full regeneration requires an explicit rebuild request.
- Each registered CLI maps to its own reference file; rows sharing a reference are authoring errors, not aliases.
