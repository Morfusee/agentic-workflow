# Markdown Error Serializer Boundary Design

## Context

The Markdown feature now keeps `MarkdownError` as a domain exception while
converting caught failures into plain transport payloads at server-action and
route boundaries. The conversion code currently lives beside the domain error
class, which mixes domain errors with transport serialization concerns.

## Approved design

Keep `MarkdownErrorCode` and `MarkdownError` in:

```text
nextjs/features/markdown/errors/markdown.error.ts
```

Move the transport-specific message table, payload types, operation-type union,
and `mapMarkdownErrorToPayload()` into:

```text
nextjs/features/markdown/serializers/markdown-error.serializer.ts
```

The serializer imports `MarkdownError` and `MarkdownErrorCode` from the errors
module. The errors module does not import the serializer, so the dependency
direction remains one-way.

Update all existing action and API imports, and move the mapper tests beside
the serializer. Preserve the mapper name and every payload, message,
authentication, permission, database, cache-revalidation, and frontend
behavior exactly.

## Non-goals

- Do not return `MarkdownError` instances through server actions or JSON routes.
- Do not change error codes, operation names, message precedence, or payload
  shape.
- Do not modify services, permissions, business rules, or unrelated dirty
  worktree files.

## Validation

- Run `pnpm lint` from `nextjs/`.
- Run the focused serializer and action payload tests.
- Run `pnpm test` from `nextjs/`.
- Run `git diff --check` and verify only serializer imports/tests changed.
