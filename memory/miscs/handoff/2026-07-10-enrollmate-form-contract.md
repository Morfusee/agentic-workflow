# EnrollMate Form Contract Handoff

## Requested continuation

Complete and review the EnrollMate form-definition normalization work in `$HOME/Documents/Programming/mihc`. The user requested this handoff to a new Codex task and prefers the 5.6 Luna max model if that surface supports model selection.

## Current state

- The workspace is intentionally dirty. Preserve all existing user-owned changes; do not reset or overwrite unrelated Next.js, database, E2E, Docker, or Playwright work.
- The EnrollMate JSON has been converted from a permissive scrape shape to a versioned, camelCase source contract with a local `$schema` reference.
- The source lives at `packages/enrollmate-contract/src/definitions/enrollmate-form-fields.json`.
- The editor schema lives at `packages/enrollmate-contract/src/definitions/enrollmate-form-definition.schema.json` and is currently untracked.
- `form-definition.schema.ts` has strict Zod schemas, source parsing, normalization, dynamic reusable option-set support, and cross-reference validation.
- `form-data.schema.ts` has been refactored into switch-based field schemas and helper-based conditional/dependent-option validation.
- `nextjs/lib/drizzle/seed/seed-profiles.ts` was updated to use `conditionalOn.equalsAny` for string and boolean conditions.
- Contract tests now cover strict unknown-property rejection, preserved section metadata, promoted boolean conditional fields, and dynamically declared reusable option sets.

## Key design decisions

- Reusable option sets are a dynamic record of non-empty option arrays. New set names require no TypeScript schema change.
- `addressFieldsPattern` is not an option set; it moved under the root `templates` object so reusable option sets remain homogeneous.
- Choice fields use explicit `optionSource` variants: `inline`, `reusable`, `dependent`, `cascade`, or `external`.
- The former nested `conditional_fields` source data was promoted into the containing section field list. In particular, `schoolNotFound` controls `lastschOther` through a boolean `visibleWhen.equalsAny: [true]` rule.
- Existing public APIs remain: `getEnrollmateFlowDefinition`, `getEnrollmateValidator`, and `getEnrollmateDefinitionHash`.
- There is not yet an explicit public getter/HTTP route for all reusable option sets. The flow definition already exposes resolved options per field. If frontend profile creation needs all sets independently, add a deliberate getter such as `getEnrollmateReusableOptionSets()` and expose it through a Next.js route as appropriate.

## Review feedback already addressed

- Replaced fixed reusable-option-set key enum with dynamic typed keys.
- Replaced option-source and field-type conditional chains with switches.
- Extracted nested conditional validation into helpers.
- Extracted field-reference and dependent-option validation helpers.
- Added a regression test for dynamically declared option sets and missing references.

## Verification completed

- `npx --yes pnpm@10.29.2 --dir nextjs test -- __tests__/unit/lib/enrollmate-contract.test.ts` — passed: 10 test files, 52 tests.
- `npx --yes pnpm@10.29.2 --dir nextjs exec tsc --noEmit --types vitest/globals` — passed.
- `npx --yes pnpm@10.29.2 --dir nextjs lint` — 0 errors; 18 existing warnings outside this work.
- `git diff --check` — passed.

The default installed `pnpm` is 11.4.0 while this project requires 10.29.2; use the `npx --yes pnpm@10.29.2` prefix above for verification.

## References

- Design: `$HOME/Documents/Programming/agentic-workflow/memory/docs/superpowers/specs/2026-07-10-enrollmate-form-definition-contract-design.md`
- Implementation plan: `$HOME/Documents/Programming/agentic-workflow/memory/docs/superpowers/plans/2026-07-10-enrollmate-form-definition-contract.md`
- Repository plan: `$HOME/Documents/Programming/mihc/docs/plans/2026-07-10-enrollmate-jsonb-profile-model.md`

## Suggested skills

- `requirements-reviewer` to check the implementation against the design/plan before declaring it complete.
- `refactor` only if further review identifies a specific maintainability issue.
- `git-commit` if the user asks to commit the intended changes.
