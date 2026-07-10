# EnrollMate Reusable Option Sets API Design

**Status:** Approved design; implementation pending user review of this spec

## Goal

Expose every reusable EnrollMate option set through the shared contract package so both Next.js and Playwright consume the same typed source without reading the JSON file directly or using an HTTP route.

## Current context

The canonical definition already validates `reusableOptionSets` as a dynamic record and resolves individual sets onto fields returned by `getEnrollmateFlowDefinition`. Next.js already depends on `@mihc/enrollmate-contract`; Playwright currently does not declare the package as a dependency.

## Design

Add a registry getter:

```ts
getEnrollmateReusableOptionSets(): Readonly<
  Record<string, readonly EnrollmateOption[]>
>
```

The getter will read the canonical source document and return every named option set. It will create a fresh record, option array, and option object for each call so consumers cannot mutate the registry’s in-memory source. Dynamic set names remain supported without TypeScript changes.

Re-export the getter and its public return type from `@mihc/enrollmate-contract`. Add `@mihc/enrollmate-contract` as a local file dependency of the Playwright project; Next.js keeps its existing dependency and `transpilePackages` configuration. Server-only Playwright validation belongs under `playwright/__tests__/unit/server/` and runs with Node's test runner, not `playwright test`.

No HTTP route, database lookup, duplicate option catalog, or change to per-field option resolution is included.

## Data flow

```text
enrollmate-form-fields.json
        ↓ strict source parsing
shared registry getter
        ├─ Next.js import
        └─ Playwright import
```

The getter exposes the validated reusable sets as a read-only TypeScript view. Consumers can use a set by name for profile forms, test fixtures, or option lookup while the source remains owned by the contract package.

## Testing and verification

- Add a contract test that asserts the getter exposes the canonical set names and option values.
- Assert returned data is detached from the registry by mutating a returned option and verifying a subsequent getter call is unchanged.
- Run the focused and full Next.js test suites, Next.js typecheck and lint, and Playwright typecheck.
- Run `git diff --check` and confirm only the option-set API, Playwright dependency wiring, and related tests changed.

## Alternatives considered

- Getter only without Playwright dependency: smallest code change, but Playwright would need a brittle relative import or an undeclared package resolution.
- HTTP endpoint: useful for independently deployed browser clients, but unnecessary because both consumers are repository projects and would add route/auth/cache concerns.
- Duplicated option data per consumer: rejected because it would allow drift from the canonical definition.

## Scope boundary

This change exposes the existing reusable option data. It does not create profile CRUD, form rendering, submission APIs, or a public network endpoint.
