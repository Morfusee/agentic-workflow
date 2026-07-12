# EnrollMate Form Definition Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Replace the permissive EnrollMate scrape shape with a strict, versioned, editor-aware form-definition contract that preserves the data required for profile creation and Playwright automation.

**Architecture:** The checked-in JSON becomes the canonical camelCase source document and declares $schema plus schemaVersion. Strict Zod source schemas parse and cross-validate it, then normalize reusable and dynamic options into the existing EnrollmateDefinition/validator API. A checked-in JSON Schema exposes the same document vocabulary to editors; focused unit tests protect runtime behavior and rejection paths.

**Tech Stack:** TypeScript, Zod 4, JSON Schema Draft 2020-12, Vitest, pnpm/Just.

---

## Starting constraints

- The working tree already contains intentional uncommitted updates to the EnrollMate JSON, form-definition.schema.ts, form-data.schema.ts, and types.ts. Build on those changes; do not reset or remove their added conditional fields.
- The nested conditional_fields collection contains schoolNotFound and lastschOther, with a boolean condition. Promote both fields to their section normal list and preserve the boolean rule.
- Preserve getEnrollmateFlowDefinition, getEnrollmateValidator, and getEnrollmateDefinitionHash.

## File structure

- Modify: packages/enrollmate-contract/src/definitions/enrollmate-form-fields.json — versioned camelCase source document.
- Create: packages/enrollmate-contract/src/definitions/enrollmate-form-definition.schema.json — editor-facing JSON Schema.
- Modify: packages/enrollmate-contract/src/form-definition.schema.ts — strict source schemas, cross-reference checks, normalization.
- Modify: packages/enrollmate-contract/src/form-data.schema.ts — boolean and string condition evaluation.
- Modify: packages/enrollmate-contract/src/types.ts — explicit consumer-visible source/runtime metadata.
- Modify: packages/enrollmate-contract/src/index.ts — public source parser/type exports.
- Modify: nextjs/__tests__/unit/lib/enrollmate-contract.test.ts — form-contract regression tests.

### Task 1: Write failing contract tests

**Files:**

- Modify: nextjs/__tests__/unit/lib/enrollmate-contract.test.ts

- [ ] **Step 1: Add source parsing and strictness coverage**

Import the source JSON and an exported parseEnrollmateDefinitionSource. Assert the real document declares version 1, retains a section prefix/note, and includes the former nested lastschOther field. Clone the source and prove that an undocumented field property, invalid reusable-option reference, and unknown condition parent each throw.

~~~ts
import source from "../../../../packages/enrollmate-contract/src/definitions/enrollmate-form-fields.json";
import {
  parseEnrollmateDefinition,
  parseEnrollmateDefinitionSource,
} from "@mihc/enrollmate-contract";

it("rejects undocumented form-definition properties", () => {
  const invalid = structuredClone(source);
  invalid.flows.bachelors.steps[0]!.sections[0]!.fields[0]!.unknown = true;

  expect(() => parseEnrollmateDefinitionSource(invalid)).toThrow();
});
~~~

- [ ] **Step 2: Add behavioral regression coverage**

Use actual fields to test a select-controlled required field, the boolean-controlled schoolNotFound to lastschOther rule, a hidden conditional value, dependent options, and the DR upload extension/size rules. Supply a complete valid bachelor fixture rather than weakening unrelated required fields.

~~~ts
expect(getEnrollmateValidator("bachelors").safeParse({
  ...validBachelorData,
  schoolNotFound: true,
}).success).toBe(false);

expect(getEnrollmateValidator("bachelors").safeParse({
  ...validBachelorData,
  schoolNotFound: true,
  lastschOther: "Example Academy",
}).success).toBe(true);
~~~

- [ ] **Step 3: Verify the new tests fail**

Run:

~~~powershell
pnpm --dir nextjs test -- __tests__/unit/lib/enrollmate-contract.test.ts
~~~

Expected: FAIL because the source parser/export and normalized document do not yet exist.

- [ ] **Step 4: Commit the test-first checkpoint**

~~~powershell
git add nextjs/__tests__/unit/lib/enrollmate-contract.test.ts
git commit -m "test: cover enrollmate form definition contract"
~~~

### Task 2: Implement strict source and runtime types

**Files:**

- Modify: packages/enrollmate-contract/src/types.ts
- Modify: packages/enrollmate-contract/src/form-definition.schema.ts
- Modify: packages/enrollmate-contract/src/index.ts

- [ ] **Step 1: Define strict source objects and discriminated field schemas**

Replace the snake_case raw schemas and passthrough call with strict document, metadata, application type, flow, step, section, option, visibility-condition, cascade, automation, and upload schemas. Define fields as a discriminated union. Choice fields must declare exactly one option source: inline, reusable, dependent, or cascade. Only file fields may define upload settings.

~~~ts
const conditionValueSchema = z.union([z.string(), z.boolean()]);

const visibleWhenSchema = z.object({
  field: z.string().min(1),
  equalsAny: z.array(conditionValueSchema).min(1),
}).strict();

const cascadeSchema = z.object({
  dependsOn: z.string().min(1).optional(),
  triggers: z.array(z.string().min(1)).min(1).optional(),
}).strict().refine((value) => value.dependsOn || value.triggers);
~~~

- [ ] **Step 2: Extend public types without escape hatches**

Add only metadata future profile and Playwright consumers need: section description/notes/prefix/group requirement; field placeholder/default; visibility/conditional requirement; option-source; cascade; upload; and automation examples. Do not use an index signature, passthrough object, or untyped record for form structure.

~~~ts
export type EnrollmateConditionalRule = {
  field: string;
  equalsAny: Array<string | boolean>;
};

export type EnrollmateSection = {
  label: string;
  description?: string;
  notes?: string;
  prefix?: string;
  type?: "checkboxGroup";
  required?: boolean;
  fields: EnrollmateField[];
};
~~~

- [ ] **Step 3: Parse, normalize, and cross-validate**

Export parseEnrollmateDefinitionSource(input), then make parseEnrollmateDefinition(input) normalize that parsed source. Resolve option sources to the existing runtime options and optionsByDependency values while retaining typed metadata. Collect field names and reject unknown/self visibility or cascade references; check that dependent-options keys belong to their declared parent captured options.

~~~ts
for (const field of fields) {
  const references = [
    field.visibleWhen?.field,
    field.cascade?.dependsOn,
    ...(field.cascade?.triggers ?? []),
  ].filter((name): name is string => Boolean(name));

  for (const name of references) {
    if (!fieldNames.has(name) || name === field.name) {
      throw new z.ZodError([{ code: "custom", path: ["fields", field.name], message: "Invalid field reference: " + name }]);
    }
  }
}
~~~

- [ ] **Step 4: Typecheck the parser checkpoint**

Run:

~~~powershell
just typecheck
~~~

Expected: PASS for TypeScript. The new parser tests remain red until Task 3 migrates the JSON.

- [ ] **Step 5: Commit strict parser work**

~~~powershell
git add packages/enrollmate-contract/src/types.ts packages/enrollmate-contract/src/form-definition.schema.ts packages/enrollmate-contract/src/index.ts
git commit -m "feat: define strict enrollmate form contract"
~~~

### Task 3: Add JSON Schema and migrate the definition

**Files:**

- Create: packages/enrollmate-contract/src/definitions/enrollmate-form-definition.schema.json
- Modify: packages/enrollmate-contract/src/definitions/enrollmate-form-fields.json

- [ ] **Step 1: Create the editor-facing JSON Schema**

Write a Draft 2020-12 schema with strict additionalProperties false objects and reusable $defs for options, conditions, cascades, automation, upload, sections, option sources, and field types. Use a choice-field oneOf discriminated by optionSource.kind. Keep relational checks in Zod to avoid duplicating runtime logic.

~~~json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "./enrollmate-form-definition.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["$schema", "schemaVersion", "metadata", "applicationTypes", "reusableOptionSets", "flows"],
  "properties": {
    "$schema": { "const": "./enrollmate-form-definition.schema.json" },
    "schemaVersion": { "const": 1 }
  }
}
~~~

- [ ] **Step 2: Normalize root and section vocabulary**

Convert _metadata, application_types, reusable_option_sets, and top-level flow names into metadata, applicationTypes, reusableOptionSets, and flows. Add the local $schema reference and schemaVersion 1. Convert sections to label, description, notes, prefix, type, and required; change checkbox_group to checkboxGroup.

- [ ] **Step 3: Normalize every field without loss**

Rename common keys to camelCase. Convert options, options_ref, and options_by_dependency to the typed option-source union; countryOptions and similar names must be an enum, not prose. Convert conditional_on to visibleWhen.equalsAny and required_when_condition_met to requiredWhenVisible. Convert upload formats and size strings to upload.acceptedFormats and integer upload.maxSizeBytes.

~~~json
{
  "type": "select",
  "optionSource": {
    "kind": "dependent",
    "field": "programFocus",
    "optionsByValue": { "BS Information Technology": [] }
  },
  "visibleWhen": {
    "field": "programFocus",
    "equalsAny": ["BS Information Technology", "BS Business Administration"]
  }
}
~~~

Convert address cascade properties into cascade.dependsOn/cascade.triggers. Preserve municipality/barangay examples in automation.exampleOptionsByParent, keyed by actual parent values. Preserve explanatory scrape content in metadata.sourceNotes or typed field/section notes; do not leave prose as hidden behavioral input. Promote every item in conditional_fields into the containing section fields with its equivalent boolean visibility condition.

- [ ] **Step 4: Run source and contract tests**

Run:

~~~powershell
pnpm --dir nextjs test -- __tests__/unit/lib/enrollmate-contract.test.ts
~~~

Expected: PASS. The source loads, strict malformed copies fail, section/automation data survives parsing, and existing hash-format assertion still passes.

- [ ] **Step 5: Commit source migration**

~~~powershell
git add packages/enrollmate-contract/src/definitions/enrollmate-form-fields.json packages/enrollmate-contract/src/definitions/enrollmate-form-definition.schema.json
git commit -m "refactor: normalize enrollmate form definition"
~~~

### Task 4: Validate typed conditions at submission time

**Files:**

- Modify: packages/enrollmate-contract/src/form-data.schema.ts
- Modify: nextjs/__tests__/unit/lib/enrollmate-contract.test.ts

- [ ] **Step 1: Replace string-only conditional matching**

Use one helper for both visible/required and hidden-value checks. It supports strings and booleans; other parent values do not satisfy a condition. Resolve dependent options from the field declared option-source parent rather than hard-coding programFocus.

~~~ts
function conditionMatches(value: unknown, rule: EnrollmateConditionalRule) {
  return (typeof value === "string" || typeof value === "boolean")
    && rule.equalsAny.includes(value);
}
~~~

- [ ] **Step 2: Run focused regression tests**

Run:

~~~powershell
pnpm --dir nextjs test -- __tests__/unit/lib/enrollmate-contract.test.ts
~~~

Expected: PASS for select and checkbox conditions, hidden-value rejection, dependent options, and upload rules.

- [ ] **Step 3: Commit compatibility work**

~~~powershell
git add packages/enrollmate-contract/src/form-data.schema.ts nextjs/__tests__/unit/lib/enrollmate-contract.test.ts
git commit -m "fix: validate enrollmate boolean conditions"
~~~

### Task 5: Verify and preserve existing work

**Files:**

- Verify only the task files above change for this work.

- [ ] **Step 1: Run complete relevant verification**

Run:

~~~powershell
pnpm --dir nextjs test -- __tests__/unit/lib/enrollmate-contract.test.ts
just typecheck
just test-all
~~~

Expected: PASS. If a broad command fails in a pre-existing unrelated area, report it with the focused contract test evidence.

- [ ] **Step 2: Audit the diff and status**

Run:

~~~powershell
git diff --check
git diff -- packages/enrollmate-contract/src/definitions/enrollmate-form-fields.json packages/enrollmate-contract/src/definitions/enrollmate-form-definition.schema.json packages/enrollmate-contract/src/form-definition.schema.ts packages/enrollmate-contract/src/form-data.schema.ts packages/enrollmate-contract/src/types.ts packages/enrollmate-contract/src/index.ts nextjs/__tests__/unit/lib/enrollmate-contract.test.ts
git status --short
~~~

Confirm every former section/field key has a typed purpose, all existing essential data remains represented, and unrelated Docker, database, E2E, and Playwright changes are untouched.

- [ ] **Step 3: Commit any final contract-only correction**

~~~powershell
git add packages/enrollmate-contract/src nextjs/__tests__/unit/lib/enrollmate-contract.test.ts
git commit -m "test: verify enrollmate form contract"
~~~

Do not stage unrelated modified or untracked files.

