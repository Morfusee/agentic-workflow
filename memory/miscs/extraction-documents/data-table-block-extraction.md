# Block Extraction Document

## 1. Block Summary
- **Name/purpose:** `data-table` block; a composable, URL-driven data listing system with optional search, tab filtering, sorting, row-limit selection, pagination, responsive mobile rendering, and reusable table-cell primitives.
- **What it enables:** Render tabular datasets with server-controlled state (via query params), while keeping a consistent UI/state framework across multiple product areas.
- **High-level flow:** Parent page parses URL params -> fetches data -> injects `state/actions/meta` into `DataTable.Provider` -> child table controls mutate URL/query state -> page re-fetches and re-renders with updated data.

## 2. File and Component Map
- `src/components/blocks/data-table/data-table.tsx`
  - **Responsibility:** Core presentational pieces (`DataTableContent`, `DataTableTabFilter`, `DataTableSearch`, `DataTableRowsSelector`, `DataTablePagination`) + built-in empty/loading/error fallbacks.
  - **Inputs:** column defs, row data, pagination/sort state, callbacks, responsive flag, fallback overrides, style/class overrides.
  - **Outputs/actions:** calls `onSort`, `onSelect`, `onSearchChange`, `onSearchSubmit`, `onPageClick`, `onPrevClick`, `onNextClick`.
  - **Relationships:** Rendering layer used directly or through context wrappers.

- `src/components/blocks/data-table/data-table-context.tsx`
  - **Responsibility:** Context provider + connected wrappers (`DataTable.Table`, `.TabFilter`, `.Search`, `.RowsSelector`, `.Pagination`) that map provider state/actions/meta into presentational components.
  - **Inputs:** `state`, `actions`, `meta` from parent integrator.
  - **Outputs/actions:** propagates user interactions to parent handlers; enforces provider usage.
  - **Relationships:** Public block entry point (`DataTable.Provider` and subcomponents).

- `src/components/blocks/data-table/use-data-table.tsx`
  - **Responsibility:** URL query-state adapters for tab filter, search, pagination, row limit, and sorting.
  - **Inputs:** config (tabs, sort columns/defaults, page limits, totalPages) and optional React transition starter.
  - **Outputs/actions:** `{ state, actions, meta }` slices consumed by `DataTable.Provider`.
  - **Relationships:** Primary state engine used by feature pages.

- `src/components/blocks/data-table/data-table-query-state.ts`
  - **Responsibility:** Canonical query param keys/parsers/loaders.
  - **Inputs:** URL search params.
  - **Outputs:** parsed values (`tab`, `search`, `page`, `limit`, `sortBy`, `sortDirection`) and server loaders.
  - **Relationships:** Shared contract between server data loaders and client hooks.

- `src/components/blocks/data-table/types.ts`
  - **Responsibility:** TS contracts for all table state/actions/meta and component props.
  - **Inputs/outputs:** type-only glue for strict integration.

- `src/components/blocks/data-table/data-column-meta.ts`
  - **Responsibility:** Extends table-column metadata contract.
  - **Key metadata:** `mobile.align`, `mobile.hidden`, `sort.enabled`, `sort.key`.
  - **Relationships:** Used by `DataTableContent` for responsive rendering and sortable header behavior.

- `src/components/blocks/data-table/data-cell.tsx`
  - **Responsibility:** Reusable cell atoms (`Text`, `Stacked`, `Avatar`, `Image`, `MenuAction`).
  - **Inputs:** content strings/media/menu items and style overrides.
  - **Outputs/actions:** menu item click/link navigation callbacks.
  - **Relationships:** Consumed by feature-specific column definitions.

- `src/components/blocks/data-table/data-table-skeleton.tsx`
  - **Responsibility:** Skeleton versions for rows/cards/search/tabs/selector/pagination.
  - **Relationships:** Optional loading UIs used by consumers/fallback overrides.

- Related dependency: `src/components/data-state.tsx`
  - **Responsibility:** tri-state renderer with strict priority `loading -> error -> empty -> data`.
  - **Relationships:** used by `DataTableContent` to switch body state.

## 3. Design Principles
- **Layout structure**
  - Desktop: bordered, rounded table container; fixed table layout with explicit column widths.
  - Mobile (when `responsive`): each row collapses into a two-column card-like grid inside a single table cell; no visible header row.
- **Visual hierarchy**
  - Header uses muted background; sortable headers show iconography (inactive/asc/desc).
  - Body rows use hover tint and optional selected data-state styling.
  - Empty/error states are centered, icon-led informational panels.
- **Spacing/alignment**
  - Consistent cell padding (`px-6 py-4`), row-level compact density.
  - Mobile alignment derives from per-column metadata (`left` or right-aligned stack).
- **Typography intent**
  - Primary row content medium weight; secondary metadata muted, smaller.
  - Action affordances are icon-forward with optional text buttons.
- **Color/status usage**
  - Neutral muted surfaces for structure; destructive color reserved for error icons and destructive menu actions.
- **Responsiveness**
  - Breakpoint from `useIsMobile` (`<768px`).
  - Columns may be hidden on mobile via metadata while still present on desktop.
- **Accessibility considerations**
  - Menu trigger includes screen-reader label.
  - Search supports Enter submission; clear action explicit.
  - Pagination disables prev/next at boundaries.
  - Consumers can add row-level links/ARIA labels in cell renderers.
- **Reusable patterns**
  - Context-based composition with independently placeable controls.
  - Controlled/uncontrolled hybrid inputs with URL as canonical remote state.
  - Metadata-driven responsive and sort behavior at column level.

## 4. Functional Contract
- **User interactions**
  - Sortable headers toggle state: new column -> asc; same column toggles asc/desc.
  - Tab selection updates tab filter and resets page to 1.
  - Search input:
    - updates local input state on typing,
    - Enter submits,
    - optional search button submits,
    - clear button empties input and submits empty query,
    - optional debounced submit triggers automatically while typing.
  - Rows-per-page selector updates `limit`.
  - Pagination supports prev/next/page-number/last-page jumps.
- **State transitions**
  - Data rendering precedence: loading first, then error, then empty, else rows.
  - Query-state updates can trigger route-level re-fetch (`shallow: false`).
- **Validation/guard rules**
  - Pagination is clamped to `[1, totalPages]`.
  - Sort rejects columns not in `sortableColumns`.
  - Tab deselect falls back to first tab value.
- **Conditional rendering**
  - Mobile layout only when `responsive && isMobile`.
  - Sort UI only when `sortable && onSort && resolved sort key`.
  - Search controls section changes based on `showFilter` / `searchButtonLabel` presence.
- **Loading/empty/error**
  - Built-in desktop + mobile defaults; all overrideable via fallback props.
- **Success state**
  - No explicit success banner; success is implicit rendered dataset update.
- **Navigation/routing**
  - Block itself does not navigate except through optional menu links.
  - Query params are primary persistence mechanism for control state.
- **API/data dependencies**
  - Block expects parent to provide already paginated/sorted/filtered data (manual table mode).
  - Server loaders (`load*SearchParams`) are the intended counterpart contract.
- **Side effects**
  - `DataTable.Pagination` wrapper calls `onReset` on unmount (clears pagination query state).
  - Tab/search submissions reset page to 1.

## 5. Data and State Model
- **Required inputs**
  - `table.columns`, `table.data`.
  - For full controls: pagination state/actions, limit state/actions, optional tab/search/sort state/actions.
- **Derived values**
  - `pageIndex = currentPage - 1` for table internals.
  - Mobile row left/right cell groups from column metadata.
  - Sort key derived from `meta.sort.key` else accessor key (unless `meta.sort.enabled === false`).
- **Local state**
  - Search hook keeps `inputValue` local.
- **Shared/global state**
  - Provider context carries all table slices.
- **Server/API state**
  - URL query params parse/load on server; fetch layer uses parsed values to request data.
- **Mutations/submitted payloads**
  - Query param mutations (`tab`, `search`, `page`, `limit`, `sortBy`, `sortDirection`) are primary submitted state.
- **Transformations**
  - Pagination numbers are windowed with custom slice logic plus forced last-page rendering.
  - Mobile rendering filters out columns with `mobile.hidden`.

## 6. Interaction Flow
1. **Initial render**
   - Parent parses query params, fetches dataset, builds hook slices, passes into `DataTable.Provider`.
2. **User action**
   - User types/searches, changes tab, clicks sort, changes page/limit.
3. **State/data change**
   - Hook action writes query-state (and sometimes local input state), often clamped/validated.
4. **UI response**
   - Control reflects new state; loading fallback may show while route transition/fetch occurs.
5. **API call or side effect**
   - Page-level loader/service re-runs with updated query params.
6. **Final state**
   - New data renders; if no rows -> empty fallback; if failure -> error fallback.

## 7. 1:1 Parity Requirements
- **Visual parity**
  - Bordered rounded table shell, muted header, row hover, icon-based sorting cues, consistent cell density.
  - Mobile card-row split into left/right stacks with metadata-driven alignment/hiding.
- **Functional parity**
  - URL-driven tab/search/sort/page/limit behavior.
  - Search clear + Enter submit + optional debounced submit + optional explicit search button.
  - Page reset to 1 on tab change and search submit.
  - Manual/server-style pagination contract.
- **Responsive parity**
  - Breakpoint behavior equivalent to `<768px`.
  - No desktop header in mobile mode; rows rendered as paired stacks.
- **Accessibility parity**
  - Keyboard-enter search submit, disabled pagination controls at bounds, menu trigger SR label.
- **Data/API parity**
  - Same query key semantics/defaults: `tab=all`, `search=''`, `page=1`, optional `limit`, sort constrained to allowed literals.
  - Same loading/error/empty precedence.

## 8. Replaceable vs Essential Details
**Essential**
- Context contract shape (`state/actions/meta`) and subcomponent collaboration.
- URL as canonical control state, including reset behaviors.
- Manual data mode (parent owns fetching/filtering/pagination/sorting).
- Column metadata semantics for mobile and sort mapping.
- Exact tri-state rendering order and fallback override capability.

**Replaceable**
- UI component library, icon set, CSS utility syntax, and exact class names.
- TanStack Table specifically (if replacement preserves column/cell/header behavior).
- File/module names and folder organization.
- Specific hook library for query parsing (`nuqs`) if equivalent typed URL-state behavior is kept.

## 9. Migration Guidance for Another Agent
- **Recommended approach**
  - Recreate the architecture in layers: (1) query-state contract, (2) provider/context contract, (3) presentational table + controls, (4) optional cell primitives/skeletons.
- **Build order**
  1. Implement query param parser/mutators with same defaults and clamping.
  2. Implement provider and connected wrappers.
  3. Implement core table rendering + mobile metadata behavior.
  4. Add controls (search/tab/limit/pagination/sort) and state-reset rules.
  5. Add default fallback states and override hooks.
- **Test after migration**
  - Sort toggle logic, tab/search page reset, pagination bounds, mobile column hide/align, fallback precedence.
  - URL deep-link reload parity (query -> data fetch -> UI).
- **Common mistakes**
  - Treating table as client-side paginated/sorted (this block is manual/server-driven).
  - Forgetting page reset on search/tab changes.
  - Not honoring `meta.sort.key` override.
  - Rendering desktop headers in mobile mode.
  - Breaking unmount pagination reset side effect.
- **Edge cases to preserve**
  - Empty search clears query immediately.
  - Invalid sort column ignored.
  - `totalPages=1` still renders last-page link behavior.
  - Deselecting active tab falls back to first tab.
  - Fallback components accept `columnCount`.

## 10. Parity Checklist
- [ ] Provider accepts and propagates `state/actions/meta` slices exactly.
- [ ] Query keys/defaults match (`tab`, `search`, `page`, `limit`, `sortBy`, `sortDirection`).
- [ ] Search supports typing, Enter submit, clear submit, optional debounced submit.
- [ ] Tab and search submit both force page to 1.
- [ ] Pagination clamps within bounds; prev/next disabled correctly.
- [ ] Sort headers only activate when sortable and key-resolvable; icon state matches active/inactive/dir.
- [ ] Mobile mode uses metadata-driven hide + left/right alignment and card-like row structure.
- [ ] Data state priority is `loading > error > empty > rows`.
- [ ] Default and override fallback UIs work for desktop and mobile.
- [ ] Manual/server data responsibility preserved (no implicit client-side filtering/pagination/sorting unless consumer does it intentionally).
