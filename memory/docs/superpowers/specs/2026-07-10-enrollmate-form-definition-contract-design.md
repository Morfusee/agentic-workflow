# EnrollMate Form Definition Contract Design

## Goal

Turn `packages/enrollmate-contract/src/definitions/enrollmate-form-fields.json` into a strict, versioned form-definition contract. It must be safe to consume for profile creation, submission validation, UI rendering, and Playwright test generation without silently accepting or discarding data.

## Current problem

The source JSON mixes application semantics, presentation hints, scraped notes, option data, and automation examples. `rawFieldSchema` currently uses `.passthrough()`, so misspelled or undocumented field properties are accepted. Section objects only declare `section`, `title`, and `fields`; their other properties are stripped while parsing. Consequently, the parsed contract is not a faithful, typed representation of the source file.

## Chosen approach

Adopt one explicit source format, validated strictly by Zod, and expose an editor-facing JSON Schema from the same contract vocabulary. The source format is versioned and uses consistent camelCase names. The existing parser converts it directly to the exported form definition; it must not rely on a permissive raw-scrape layer.

This is deliberately not a broad UI implementation. It establishes the shared, durable definition needed by future profile creation and Playwright work.

## Source model

The root document contains:

- `schemaVersion`: an integer, initially `1`.
- `metadata`: descriptive source metadata currently represented by `_metadata`.
- `applicationTypes`: the bachelor and microcredential labels and submission endpoints.
- `reusableOptionSets`: named, typed option collections.
- `flows`: the `bachelors` and `microcredentials` flows.

Each flow contains ordered steps; each step contains ordered sections; each section contains a typed, ordered collection of fields. IDs and names remain stable so existing integrations and selectors keep working.

Sections explicitly support the current meaningful metadata: identifier/title, description, notes, prefix, type, required indicator, and fields. No unknown section property is permitted.

## Field model

Every field has explicit common properties: `id`, `name`, `label`, `type`, `required`, optional description, placeholder, placeholder value, default value, and optional visibility/conditional requirement rules.

Fields are a discriminated union by `type`:

- Text-like fields (`text`, `textarea`, `email`, `tel`, and `date`) may use common presentation and default-value properties.
- Choice fields (`select` and `combobox`) declare one of: inline options, a reusable option-set reference, dependent options, or an explicit externally populated/cascading option source. Option-source behavior is never inferred from free-form prose.
- Checkbox fields are boolean answer fields.
- File fields declare their accepted file extensions and maximum size in bytes in a typed upload configuration.

Conditional visibility uses one consistent `visibleWhen` object. A separately named boolean expresses whether the field becomes required when the condition is satisfied. This replaces the current mix of `conditional_on` and `required_when_condition_met`.

Address cascade behavior is represented by an explicit typed relation (`parent`, `dependsOn`, and `triggers`) rather than unrelated `cascade_*` keys.

Existing examples that support test data, such as municipality or barangay option examples, are retained in a documented `automation` object. Pure explanatory scrape prose is retained as `sourceNotes` only when it helps future maintenance; it does not control runtime behavior.

## Validation and compatibility

All document, flow, step, section, field, option, condition, option-source, cascade, upload, and automation objects use strict validation. Unknown keys fail parsing. The validator also verifies cross-references: reusable option-set names, conditional parent field names, cascade field names, and dependent option references must point to valid declared targets.

The public normalized `EnrollmateDefinition` preserves all information needed by present consumers, including section metadata and field behavior. Existing `getEnrollmateFlowDefinition` and `getEnrollmateValidator` remain the consumer entry points. Existing conditional fields and reusable option references already added to the working tree are preserved and converted to the new vocabulary.

## Developer experience

The JSON includes a `$schema` reference to a checked-in JSON Schema. Editors can therefore provide autocomplete and flag invalid form definitions before tests run. Zod remains the runtime authority; contract tests ensure the checked-in schema accepts the real document and rejects representative malformed documents.

## Verification

Tests will prove that:

- the checked-in JSON source parses to both flows;
- undocumented section and field properties are rejected;
- each supported field category validates its allowed properties and rejects incompatible ones;
- option-set, conditional, and cascade references are checked;
- current validator behavior for required, conditional, dependent-option, and file answers remains intact;
- the Next.js and package typechecks remain green.

## Scope boundaries

This change does not build a form renderer, modify profile persistence, or build Playwright generation. It provides the structured contract those future implementations can safely rely on.
