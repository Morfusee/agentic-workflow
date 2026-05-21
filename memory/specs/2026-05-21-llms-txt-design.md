# LLMs.txt CMS-Managed Publishing Design

Date: 2026-05-21
Ticket: https://app.clickup.com/t/86d32m54w
Project: MMDC Website (`website`)

## 1) Goal

Provide a CMS-managed `llms.txt` document that is publicly available at `https://mmdc.mcl.edu.ph/llms.txt`, similar to `robots.txt`, while following existing Payload and Next.js patterns in this codebase.

## 2) Confirmed Decisions

- Content source is a **Payload collection** (not a global).
- Public output is **manual CMS-managed content**, not auto-generated from other entities.
- Publishing follows existing flow: save/publish in CMS, then normal sync/deploy.
- If no eligible content exists, `GET /llms.txt` returns `200 OK` with an empty body.
- Content is stored in **rich text** and rendered to plain text for response output.
- Exactly one entry should be active at a time; activating one entry auto-deactivates others.
- Public route reads **published documents only**.
- If multiple active published entries exist unexpectedly, newest `updatedAt` wins.

## 3) Scope

### In Scope

- Add `llms-txt` Payload collection for editor-managed entries.
- Add `/llms.txt` App Router route handler returning `text/plain`.
- Add active-entry enforcement in collection lifecycle logic.
- Add rich text to plain text serialization utility with deterministic formatting rules.
- Add tests for collection behavior, route behavior, and serialization logic.

### Out of Scope

- AI-generated `llms.txt` content.
- Multi-language `llms.txt` variants.
- Dedicated one-click publish action separate from CMS publish/sync flow.
- Changes to robots/sitemap strategy outside this route.

## 4) Architecture

### 4.1 Payload Collection

Create `src/collections/LLMsTxt.ts` with:

- `slug: 'llms-txt'`
- `admin.useAsTitle: 'title'`
- Fields:
  - `title: text` (required)
  - `content: richText` (required for authoring quality; route still handles missing defensively)
  - `isActive: checkbox` (default false)
- `versions.drafts` enabled to align with existing editorial workflow.

Register the collection in `src/payload.config.ts` collections list.

### 4.2 Public Route

Create `src/app/llms.txt/route.ts`:

- `GET` handler fetches from Payload using runtime config (`getPayload({ config: configPromise })`).
- Query only published entries.
- Resolve candidate in order:
  1. Exactly one active published entry -> use it.
  2. Multiple active published entries -> sort by `updatedAt` descending and use first.
  3. No active published entries -> return empty body.
- Serialize rich text to plain text with utility function.
- Respond with `text/plain; charset=utf-8`, status `200` unless hard server failure.

## 5) Component Boundaries

### `src/collections/LLMsTxt.ts`

- Owns schema, editorial metadata, and activation lifecycle behavior.
- Does not own formatting logic or response rendering.

### `src/utilities/llmsTextSerializer.ts`

- Pure conversion logic from Payload lexical/rich text JSON to plain text.
- Deterministic, side-effect-free, independently unit-testable.

### `src/app/llms.txt/route.ts`

- Owns HTTP concerns: data retrieval, candidate selection, headers, status codes.
- Calls serializer; does not embed serialization rules inline.

## 6) Data Flow

1. Editor creates or updates an `llms-txt` entry in Payload.
2. Editor publishes the chosen entry and marks `isActive = true`.
3. Collection hook deactivates any other entries currently active.
4. Public request hits `GET /llms.txt`.
5. Route fetches published entries, chooses effective source using active/fallback rules.
6. Route serializes rich text into plain text.
7. Route returns `200` plain text response.

## 7) Rich Text to Plain Text Rules

Serializer rules:

- Headings -> plain line text (no markdown prefixes required).
- Paragraphs -> plain line text.
- Bulleted items -> `- {item text}` one per line.
- Links -> `{label}: {url}`.
- Preserve intentional line breaks between logical blocks.
- Unknown/unsupported node types are ignored safely; known textual children are retained when possible.

This keeps output readable and stable while avoiding fragile markup assumptions.

## 8) Error Handling and Resilience

- No published/active content: return `200` with empty body.
- Missing/null content in selected doc: treat as empty output, still `200`.
- Multiple active published docs: deterministic fallback to newest `updatedAt`.
- Serializer sees unknown node shape: skip unsupported formatting, avoid throw.
- Payload/runtime failure: return `500` with minimal plain-text body and log error.

## 9) Testing Strategy

### Unit Tests

- Serializer:
  - heading/paragraph conversion
  - bullet list conversion
  - link conversion (`Label: URL`)
  - graceful handling of unknown nodes

### Integration Tests (or focused collection tests)

- Activating one entry deactivates all other active entries.
- Draft-only changes are not exposed publicly.

### Route Tests

- Normal case: active published entry returns serialized text.
- No published entries: returns `200` empty body.
- Multiple active published entries: newest `updatedAt` is selected.
- Response content type is `text/plain; charset=utf-8`.

### Manual Smoke

- Verify `/llms.txt` is reachable locally/UAT and serves plain text.
- Publish a newer active entry and verify output switches after deploy/sync.

## 10) Acceptance Criteria

- Editors can manage `llms.txt` content via Payload collection entries.
- Exactly one active entry is maintained automatically at publish-time.
- Public `GET /llms.txt` serves published active content as plain text.
- Empty state returns `200` with empty body.
- Multiple-active anomaly does not break output; newest `updatedAt` is used.
- Tests cover core behavior and serialization mapping.

## 11) Risks and Mitigations

- Risk: Rich text schema changes could affect serializer.
  - Mitigation: keep serializer isolated with tests and defensive node handling.
- Risk: Race conditions during concurrent publishes.
  - Mitigation: deterministic route fallback + hook-based deactivation logic.
- Risk: Editors expect immediate prod visibility without deploy/sync.
  - Mitigation: document expected publish + sync behavior in admin field description.

## 12) Implementation Notes (For Planning Step)

- Follow established patterns from `src/app/robots.ts` and existing collection hook style.
- Keep route and serializer separate for small, testable units.
- Avoid unrelated refactors; this ticket is additive.
