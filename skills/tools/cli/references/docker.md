# Docker CLI Reference

| | |
|---|---|
| Canonical executable | `docker` (`C:\Program Files\Docker\Docker\resources\bin\docker.exe` on this host) |
| Version | 28.3.3 (build 980b856), Docker Desktop on Windows |
| Last verified | 2026-08-08 |
| Help syntax | `docker COMMAND --help`; `docker COMMAND SUBCOMMAND --help` |

## Environment and auth

- Daemon runs via Docker Desktop; context `docker-desktop` is default. `DOCKER_HOST` overrides; `-c/--context` selects another context.
- Client config in `$HOME/.docker` (config.json holds registry auth/creds).
- Registry auth: `docker login` / `docker logout`; credentials stored via Desktop credential helper.
- Plugins ship with Docker Desktop: `ai`, `buildx`, `cloud`, `compose`, `debug`, `desktop`, `extension`, `init`, `mcp`, `model`, `sbom`, `scout`. They are real binaries/plugins — `docker <plugin> --help` works, but some need network/daemon to function.

## Command directory

### Top-level commands

| Command | Purpose |
|---|---|
| `run` | Create and run a new container from an image (alias of `container run`) |
| `exec` | Execute a command in a running container |
| `ps` | List containers (alias of `container ls`) |
| `build` | Build an image from a Dockerfile (alias of `image build`) |
| `bake` | Build from a file (buildx bake) |
| `pull` | Download an image from a registry |
| `push` | Upload an image to a registry |
| `images` | List images (alias of `image ls`) |
| `login` | Authenticate to a registry |
| `logout` | Log out from a registry |
| `search` | Search Docker Hub for images |
| `version` | Show Docker version information |
| `info` | Display system-wide information |
| `attach` | Attach streams to a running container |
| `commit` | Create a new image from a container's changes |
| `cp` | Copy files/folders between a container and the local filesystem |
| `create` | Create a new container |
| `diff` | Inspect changes on a container's filesystem |
| `events` | Get real-time events from the server |
| `export` | Export a container's filesystem as a tar archive |
| `history` | Show the history of an image |
| `import` | Import from a tarball to create a filesystem image |
| `inspect` | Return low-level information on Docker objects |
| `kill` | Kill one or more running containers |
| `load` | Load an image from a tar archive or STDIN |
| `logs` | Fetch the logs of a container |
| `pause` / `unpause` | Pause / unpause container processes |
| `port` | List port mappings for a container |
| `rename` | Rename a container |
| `restart` | Restart one or more containers |
| `rm` | Remove one or more containers |
| `rmi` | Remove one or more images |
| `save` | Save images to a tar archive |
| `start` / `stop` | Start / stop containers |
| `stats` | Live stream of container resource usage |
| `tag` | Tag an image |
| `top` | Display running processes of a container |
| `update` | Update container configuration |
| `wait` | Block until containers stop, print exit codes |

### Management commands

| Command | Purpose |
|---|---|
| `container` | Manage containers — `attach`, `commit`, `cp`, `create`, `diff`, `exec`, `export`, `inspect`, `kill`, `logs`, `ls`, `pause`, `port`, `prune`, `rename`, `restart`, `rm`, `run`, `start`, `stats`, `stop`, `top`, `unpause`, `update`, `wait` |
| `image` | Manage images — `build`, `history`, `import`, `inspect`, `load`, `ls`, `prune`, `pull`, `push`, `rm`, `save`, `tag` |
| `network` | Manage networks — `connect`, `create`, `disconnect`, `inspect`, `ls`, `prune`, `rm` |
| `volume` | Manage volumes — `create`, `inspect`, `ls`, `prune`, `rm` |
| `system` | Manage Docker — `df` (disk usage), `events`, `info`, `prune` |
| `context` | Manage contexts — `create`, `export`, `import`, `inspect`, `ls`, `rm`, `show`, `update`, `use` |
| `trust` | Manage image trust — `inspect` (keys/signatures), `revoke`, `sign` |
| `manifest` | Manage image manifests and manifest lists — `annotate`, `create`, `inspect`, `push`, `rm` |
| `builder` | Manage builds (buildx) — `bake`, `build`, `create`, `dial-stdio`, `du`, `inspect`, `ls`, `prune`, `rm`, `stop`, `use`, `version` |
| `buildx` | Docker Buildx (same subcommands as `builder`) |
| `plugin` | Manage plugins — `create`, `disable`, `enable`, `inspect`, `install`, `ls`, `push`, `rm`, `set`, `upgrade` |
| `swarm` | Manage Swarm — `init`, `join` only in this build |

### Plugin commands

| Command | Purpose |
|---|---|
| `compose` | Docker Compose — `attach`, `build`, `commit`, `config`, `cp`, `create`, `down`, `events`, `exec`, `export`, `images`, `kill`, `logs`, `ls`, `pause`, `port`, `ps`, `publish`, `pull`, `push`, `restart`, `rm`, `run`, `scale`, `start`, `stats`, `stop`, `top`, `unpause`, `up`, `version`, `volumes`, `wait`, `watch` |
| `buildx` / `builder` | Buildx — build, bake, create/inspect/ls/use/rm builder instances, `du`, `prune`, `stop`, `dial-stdio`, `version` |
| `scout` | Docker Scout — image analysis; cves, compare, enroll, environments, integration, policy, quickview, recommendations, repo, sbom, stack, watch, version |
| `sbom` | Software Bill of Materials for images (only `version` subcommand in this build) |
| `debug` | Get a shell into any image or container — all, attach, checks, config, core-dump, debug, open, profiles, run, top, trace |
| `desktop` | Docker Desktop — `logs`, `restart`, `start`, `status`, `stop`, `update`, `version` |
| `extension` | Docker extensions — `init`, `install`, `ls`, `rm`, `share`, `update`, `validate`, `version` |
| `ai` | Docker AI Agent (Ask Gordon) — natural-language conversation, `feedback`, `version` |
| `model` | Docker Model Runner (EXPERIMENTAL) — `df`, `inspect`, `install-runner`, `list`, `logs`, `package`, `ps`, `pull`, `push`, `rm`, `run`, `status`, `tag`, `unload`, `version` |
| `cloud` | Docker Cloud — `accounts`, `diagnose`, `start`, `status`, `stop`, `version` |
| `mcp` | Docker MCP Toolkit — `catalog`, `client`, `config`, `feature`, `gateway`, `policy`, `secret` |
| `init` | Create Docker starter files for a project (`--version` only) |

## Caveats

- `docker ps`, `images`, `rm`, `rmi`, `run`, `build`, `start`, `stop`, `restart`, `exec`, `logs` etc. are top-level aliases for the `container`/`image` management groups; behavior is identical.
- `docker swarm init --help` is shadowed by the `docker-init` plugin in this build and prints the plugin's help instead. `docker swarm join` help works. Swarm exposes only `init`/`join` here (legacy swarm commands trimmed from this Docker Desktop build).
- `docker model` is EXPERIMENTAL and requires the Model Runner (`model install-runner`).
- Plugin availability varies by Docker Desktop version; `docker <plugin> --help` fails if the plugin is missing.
- Commands with `--help` never touch the daemon; everything else needs the Docker Desktop engine running (check with `docker info`).

## Maintenance

Generated by `/cli create` on 2026-08-08. Reference is a navigable command directory, not a full manual; for flags and examples run `docker <path> --help`. Update only verified drift, and only along the affected command path.
