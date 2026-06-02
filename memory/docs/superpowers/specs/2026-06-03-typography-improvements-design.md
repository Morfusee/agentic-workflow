# Typography Improvements Design

Date: 2026-06-03
Ticket: ClickUp `86d36xz5f` - Typography Improvements (desktop and mobile)
Target repository: `website`

## Goal

Implement a non-destructive typography foundation that supports fluid type, readable long-form text, controlled hero/display copy, and 200% zoom resilience without globally changing existing production components.

The first implementation should add the foundation and include a temporary Hero verification opt-in. The system should stay inactive globally until future migration work deliberately expands the scope.

## Source Requirements

The ClickUp ticket and the sample typography page align on these requirements:

- Typography scales fluidly across desktop and mobile.
- Long-form body text has a readable floor of at least `16px`.
- Long-form text uses `line-height: 1.5` for comfortable reading rhythm.
- Prose line length stays between `50ch` and `75ch`, with `.text-block` capped at `70ch`.
- Hero/display copy is capped around `30-40` characters, with `.display-copy` capped at `20ch`.
- Text stays left-aligned and is never justified inside the new typography scope.
- Browser zoom is not disabled.
- `overflow-wrap: break-word` is used so 200% zoom does not break layouts.

This ticket does not require a full sitewide migration of every heading, card, nav, calculator, table, CTA, or CMS block to the sample design-system typography page.

## Non-Destructive Constraints

- Do not remap Tailwind's existing `text-*` font-size utilities.
- Do not rewrite existing production blocks.
- Do not change Payload CMS schemas or generated types.
- Do not put `.typography-v2` on `body`, `main`, layout wrappers, or page templates during the initial rollout.
- Preserve existing CMS content and current component variants.
- Preserve any user-owned dirty changes in the active workspace or selected worktree.

## Branch And Worktree Workflow

Implementation must happen in an isolated worktree, not in the current website workspace.

- Base branch: `feat/v3-redesign`
- Feature branch: `feat/86d36xz5f`
- Prefer existing worktrees in this order: `website-worktree-1`, then `website-worktree-2`.
- Inspect `git status` and `git diff` in each candidate worktree before choosing.
- Reuse a dirty worktree only if the existing changes are minimal and do not conflict with the typography ticket.
- Preserve existing dirty changes in the chosen worktree.
- Do not reset, checkout over, stash, or delete dirty changes without explicit approval.
- If dirty changes conflict with the required branch/base setup or typography files, stop and ask.
- If neither existing worktree is safe enough, create a new worktree.

## Architecture

The typography foundation will live in `src/app/(frontend)/styles.css` using Tailwind-compatible CSS layers.

Add these concepts:

- Root typography tokens for fluid body sizing, fluid display sizing, line-height, prose width, and display width.
- `.typography-v2` as the future migration scope.
- `.text-block` for readable prose containers.
- `.display-copy` for hero/display copy.
- Scoped rules for line-height, wrapping, and text alignment.

The system should be designed so rollout can expand over time by moving `.typography-v2` upward:

1. A single component or section.
2. A full page wrapper.
3. `main`.
4. Eventually `body`, if the migrated site is ready.

## Components

### Global Styles

File: `src/app/(frontend)/styles.css`

Responsibilities:

- Define typography v2 tokens.
- Define `.typography-v2`, `.text-block`, and `.display-copy`.
- Enforce left alignment, non-justified text, and wrapping only inside the new scope or new utilities.
- Keep existing global styles and Tailwind utilities intact.

### Hero Verification Sample

File: `src/blocks/Hero/Hero.component.tsx`

Responsibilities:

- Add a temporary opt-in to prove `.typography-v2` and `.display-copy` work in a real production component.
- Keep the edit small and reversible.
- Do not rewrite Hero variants, CMS fields, image behavior, or layout structure.

The expected implementation is limited to class additions on the Hero wrapper and/or title/subtitle nodes.

### RichText

File: `src/blocks/RichText/RichText.renderer.tsx`

RichText remains unchanged in the first implementation. The approved first rollout is foundation plus Hero verification only.

## Data Flow

- CMS content continues through the existing block renderers.
- Existing Tailwind classes continue to render as they do today.
- Typography v2 rules apply only when `.typography-v2`, `.text-block`, or `.display-copy` is present.
- Future migration expands by applying `.typography-v2` to larger wrappers.

## Error Handling And Safety

The main risk is visual regression. Runtime risk is low because the work is CSS and class additions.

Safety measures:

- Avoid Tailwind token remapping.
- Avoid schema changes.
- Avoid global activation.
- Keep the Hero opt-in clearly removable.
- Verify no viewport metadata disables zoom.
- Use scoped `overflow-wrap: break-word` to handle long words and 200% zoom.
- Scope left alignment so intentionally centered legacy content is not broadly changed.

## Verification

Implementation should verify:

- `git status` and `git diff` before and after edits in the selected worktree.
- The selected branch is `feat/86d36xz5f` and is based on `feat/v3-redesign`.
- `pnpm lint` passes if dependencies are available.
- A build or local dev check runs if feasible.
- No viewport metadata disables zoom.
- Tailwind's existing `text-*` utilities are not remapped.
- The Hero sample uses the new typography classes.
- At 200% browser zoom, the Hero sample avoids horizontal overflow and long display text wraps.
- Surfaces without `.typography-v2`, `.text-block`, or `.display-copy` retain existing behavior.

## Removal Note For Temporary Hero Sample

To remove the temporary verification opt-in after testing, remove only the added typography classes from `src/blocks/Hero/Hero.component.tsx`:

- Remove `.typography-v2` from the Hero sample wrapper or scoped node.
- Remove `.display-copy` from the Hero title/subtitle nodes where it was added.

Do not remove the global typography foundation from `styles.css` unless the team no longer wants the future migration system. Once the Hero classes are removed, the foundation remains available but inactive except where future code explicitly opts in.

## Future Migration Path

After the Hero sample is validated, future tickets can progressively apply the system:

1. Add `.text-block` to known long-form prose containers.
2. Add `.display-copy` to other hero/display surfaces.
3. Wrap selected pages with `.typography-v2`.
4. Move `.typography-v2` to broader layout scopes only after visual QA confirms component compatibility.

Each migration step should remain reversible and avoid rewriting CMS schemas or shared component APIs unless a later ticket explicitly requires it.
