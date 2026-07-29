# Markdown Parity Follow-up Review

overall_status: FAIL

## Review scope

- Repository: `markdown2share`
- Commit range: `eea1296..1dd9d8f`
- Requirements:
  - `docs/brainstorm/2026-07-29-editor-published-markdown-parity-follow-up.md`
  - `docs/plans/2026-07-29-editor-published-markdown-parity-follow-up.md`
  - User-reported excessive breakline and wrapping spacing
- Changed files:
  - `nextjs/features/markdown/markdown-element-styles.ts`
  - `nextjs/features/markdown/components/published/render/published-plate-elements.tsx`
  - `nextjs/__tests__/unit/features/markdown/components/published-markdown.test.tsx`
  - `nextjs/__tests__/e2e/markdown-documents.spec.ts`
- Reviewers:
  - `requirements-reviewer`
  - `thermos`
  - `react-quality-review`

## Checks

### 1. Editor/published line-break spacing

- status: FAIL
- expected: Each authored Markdown break renders exactly once with the same vertical rhythm as the interactive Plate editor.
- actual: `MARKDOWN_CONTENT_CLASS_NAME` adds inherited `whitespace-pre-wrap` at `nextjs/features/markdown/markdown-element-styles.ts:3-4`. The supplied document uses production-shaped hard breaks containing carriage return, backslash, and line feed. Published static output contains two visible newline characters for each break. The metadata paragraph renders at 196px with a 28px line height instead of the editor-equivalent 112px.
- reviewers: `requirements-reviewer`, `thermos`, `react-quality-review`

### 2. Plate remains the presentation source of truth

- status: PARTIAL
- expected: Plate determines Markdown structure and break semantics; the shared style contract presents those elements without reinterpreting raw newline counts.
- actual: The published path still deserializes through Plate and renders through `PlateStatic`, but root-level `pre-wrap` makes raw text-node whitespace determine layout across every descendant. This duplicates hard-break presentation and also preserves repeated spaces and tabs in headings, lists, tables, and prose.
- reviewers: `requirements-reviewer`, `thermos`, `react-quality-review`

### 3. Break regression coverage

- status: FAIL
- expected: Tests cover ordinary LF soft breaks, production-shaped CR/backslash/LF hard breaks, and assert one rendered line advance per authored break.
- actual: `nextjs/__tests__/unit/features/markdown/components/published-markdown.test.tsx:54-72` and `nextjs/__tests__/e2e/markdown-documents.spec.ts:276-291` assert the `whitespace-pre-wrap` implementation and newline-containing `textContent`. They do not exercise the supplied hard-break shape, compare editor and published output, or measure rendered line geometry.
- reviewers: `requirements-reviewer`, `thermos`, `react-quality-review`

### 4. Publishing E2E remains executable

- status: FAIL
- expected: The focused publishing scenario passes and reaches all new parity assertions.
- actual: The focused Playwright run fails at `nextjs/__tests__/e2e/markdown-documents.spec.ts:304`. `getByText("Plate task item")` matches both the checked item and `"Pending Plate task item"`, causing a strict-mode violation.
- reviewers: `requirements-reviewer`, `thermos`, `react-quality-review`

### 5. Published task marker is server-only and non-interactive

- status: PASS
- expected: Published task markers contain no hydrated checkbox, input, button, focus target, checkbox role, or interaction handler.
- actual: `PublishedTodoMarker` at `nextjs/features/markdown/components/published/render/published-plate-elements.tsx:262-295` renders an `aria-hidden` span and static SVG without a client dependency or interactive semantics.
- reviewers: `requirements-reviewer`, `thermos`, `react-quality-review`

### 6. Published task marker has editor visual parity

- status: PARTIAL
- expected: Checked and unchecked markers share the canonical editor checkbox presentation so the two surfaces cannot drift.
- actual: The published marker reproduces the main editor checkbox dimensions, radius, colors, border, and icon size. It remains a separate hand-built SVG and class set rather than a visual primitive shared with the editor checkbox; automated checks prove class presence but not exact visual parity.
- reviewers: `requirements-reviewer`, `thermos`, `react-quality-review`

### 7. Scope and static quality checks

- status: PASS
- expected: The implementation stays within the approved files, introduces no parser or persistence changes, typechecks, and adds no lint errors.
- actual: The commit range changes exactly the four approved files. `pnpm typecheck` passes. `pnpm lint` exits successfully with 30 pre-existing warnings and no errors. `git diff --check eea1296..HEAD` passes.
- reviewers: `requirements-reviewer`, `thermos`, `react-quality-review`

## Verification evidence

- Focused Vitest file: PASS, 20 tests.
- Focused Playwright publishing test: FAIL at `markdown-documents.spec.ts:304` due ambiguous locator.
- TypeScript: PASS.
- ESLint: PASS with 0 errors and 30 warnings.
- Live published document:
  - root white space: `pre-wrap`
  - paragraph line height: 28px
  - metadata paragraph height: 196px
  - text sequence contains two newline characters between metadata lines

## Notes

- The excessive spacing is not primarily caused by `leading-7`. Reducing line height would mask the defect while still rendering every hard break twice.
- The correction should remove whitespace recovery from the shared content root and handle soft and hard breaks at Plate's static text, leaf, paragraph, or AST normalization boundary.
- Tests should assert user-visible break behavior rather than require `whitespace-pre-wrap`, so a cleaner Plate-aligned implementation is allowed.
- The task-marker work is not responsible for the spacing regression and should be preserved unless a shared server-safe visual primitive is deliberately introduced.
