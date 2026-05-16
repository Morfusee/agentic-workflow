---
name: opencode-plugin
description: Create, install, and manage opencode plugins. Use when asked to add a plugin, create a plugin, extend opencode with hooks, subscribe to opencode events, or configure npm/local plugins.
---

## Overview

Opencode plugins are JavaScript/TypeScript modules that hook into events to customize behavior. They live in `.opencode/plugins/` (project) or `~/.config/opencode/plugins/` (global).

## Plugin Structure

A plugin is an exported async function receiving `{ project, client, $, directory, worktree }` and returning a hooks object:

```js
export const MyPlugin = async ({ project, client, $, directory, worktree }) => {
  return {
    // hook implementations
  }
}
```

Context:
- `project` — current project info
- `directory` — current working directory
- `worktree` — git worktree path
- `client` — opencode SDK client
- `$` — Bun shell API

## Install a Plugin

### From local file

Place `.js` or `.ts` files in:
- `.opencode/plugins/` — project-level
- `~/.config/opencode/plugins/` — global

Files are auto-loaded at startup.

### From npm

Add package names to `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-helicone-session", "@my-org/custom-plugin"]
}
```

Packages are cached in `~/.cache/opencode/node_modules/`.

## Create a Plugin

1. Create a `.js` or `.ts` file in the plugin directory
2. Export a named plugin function
3. Return hooks as key-value pairs

### TypeScript

```ts
import type { Plugin } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return { /* hooks */ }
}
```

### External Dependencies

Add a `package.json` to `.opencode/` or `~/.config/opencode/`:

```json
{
  "dependencies": {
    "shescape": "^2.1.0"
  }
}
```

Opencode runs `bun install` at startup. Plugins can then `import` from those packages.

## Available Events

| Category | Events |
|---|---|
| Command | `command.executed` |
| File | `file.edited`, `file.watcher.updated` |
| Installation | `installation.updated` |
| LSP | `lsp.client.diagnostics`, `lsp.updated` |
| Message | `message.part.removed`, `message.part.updated`, `message.removed`, `message.updated` |
| Permission | `permission.asked`, `permission.replied` |
| Server | `server.connected` |
| Session | `session.created`, `session.compacted`, `session.deleted`, `session.diff`, `session.error`, `session.idle`, `session.status`, `session.updated` |
| Todo | `todo.updated` |
| Shell | `shell.env` |
| Tool | `tool.execute.after`, `tool.execute.before` |
| TUI | `tui.prompt.append`, `tui.command.execute`, `tui.toast.show` |

## Common Patterns

### Generic event listener

```js
export const MyPlugin = async () => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.idle") {
        // handle
      }
    }
  }
}
```

### Tool interceptor

```js
export const EnvProtection = async () => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "read" && output.args.filePath.includes(".env")) {
        throw new Error("Do not read .env files")
      }
    }
  }
}
```

### Shell environment injection

```js
export const InjectEnvPlugin = async () => {
  return {
    "shell.env": async (input, output) => {
      output.env.MY_API_KEY = "secret"
    }
  }
}
```

### Custom tools

```ts
import { type Plugin, tool } from "@opencode-ai/plugin"

export const CustomToolsPlugin: Plugin = async () => {
  return {
    tool: {
      mytool: tool({
        description: "This is a custom tool",
        args: { foo: tool.schema.string() },
        async execute(args, context) {
          return `Hello ${args.foo} from ${context.directory}`
        }
      })
    }
  }
}
```

### Structured logging

```ts
export const MyPlugin = async ({ client }) => {
  await client.app.log({
    body: {
      service: "my-plugin",
      level: "info",
      message: "Plugin initialized",
      extra: { foo: "bar" }
    }
  })
}
```

### Compaction hooks

```ts
import type { Plugin } from "@opencode-ai/plugin"

export const CompactionPlugin: Plugin = async () => {
  return {
    "experimental.session.compacting": async (input, output) => {
      output.context.push(`## Custom Context
Add domain-specific state here.`)
      // Or replace entirely:
      // output.prompt = "Your custom compaction prompt"
    }
  }
}
```

## Load Order

1. Global config (`~/.config/opencode/opencode.json`)
2. Project config (`opencode.json`)
3. Global plugin directory
4. Project plugin directory

Duplicate npm packages (same name + version) load once. Local + npm plugins with the same name both load.
