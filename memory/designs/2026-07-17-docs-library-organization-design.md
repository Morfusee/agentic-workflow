# Documentation Library Organization Design

## Goal

Make `$HOME/Documents/Programming/agentic-workflow/memory/docs/` understandable at a glance while keeping agent-generated specifications and plans separate from curated documentation.

## Approved Direction

Use a topic-first curated library beside the existing `superpowers/` directory. Preserve `superpowers/` exactly as it is because it contains agent working artifacts rather than user-facing reference documentation.

## Target Structure

```text
memory/docs/
├── README.md
├── library/
│   ├── README.md
│   ├── infrastructure/
│   │   ├── README.md
│   │   ├── current-services.md
│   │   ├── dokploy-service-deployment.md
│   │   ├── proxmox-opnsense-network-design.md
│   │   └── server-provisioning.md
│   └── developer-tools/
│       ├── README.md
│       ├── git-worktree-guide.md
│       └── lazygit-lazyvim-cheatsheet.md
└── superpowers/
    ├── plans/
    └── specs/
```

## Navigation

`memory/docs/README.md` acts as a short directory map. It explains that:

- `library/` contains curated documentation intended for direct use.
- `superpowers/` contains agent-generated design specifications and implementation plans.

`memory/docs/library/README.md` is the main documentation entry point. It routes readers by intent rather than presenting an undifferentiated filename list.

Each topic directory contains a concise `README.md` that describes every document in plain language and tells the reader when to open it.

## File Placement

Move the existing documents without changing their contents:

- Move infrastructure documents into `library/infrastructure/`.
- Move Git, worktree, LazyGit, and LazyVim documents into `library/developer-tools/`.
- Move `proxmox-opnsense-network-design.md` into `library/infrastructure/`.

Do not rename, move, edit, or index anything under `superpowers/`.

## Scope Boundaries

- Do not rewrite existing document content.
- Do not introduce metadata or tags into existing documents.
- Do not add generated indexing scripts.
- Do not reorganize agent plans or specifications.
- Do not create additional topic categories without current documents to justify them.

## Verification

- Confirm all six curated documents exist under their intended topic directories.
- Confirm their contents remain unchanged after relocation.
- Confirm every Markdown link in the three new navigation files resolves locally.
- Confirm no file under `memory/docs/superpowers/` changes.
- Confirm the old loose-document locations no longer exist.
- Confirm the final Git diff contains only the approved documentation organization work.
