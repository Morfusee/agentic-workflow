# Block Extraction Document

## 1. Block Summary
- **Name/purpose:** `form` block; a three-layer composable form system built on react-hook-form that provides field-level composition via a compound component pattern, progressively wiring from raw context-aware field primitives up to fully automated form-level wrappers.
- **What it enables:** Render typed, validated, accessible forms with minimal boilerplate by auto-wiring `control`, `isSubmitting`, `isSubmitSuccessful`, and submit-reset behavior while allowing drop-down to lower layers for custom layouts.
- **High-level flow:** `FormContext` creates a `useForm` instance and wraps children in `FormProvider` -> child `Form*` components pull `control` and form state from context -> they render `FieldController*` composites -> which render `FieldController.Root` (Controller provider) -> which renders raw `Field*` components consuming the controller context.

## 2. File and Component Map
- `src/components/blocks/form/form-context.tsx`
  - **Responsibility:** Top-level consumer layer. Provides `FormContext` (wires `useForm`, `FormProvider`, `Form` element, `FieldGroup` wrapper), plus auto-wired consumer components (`FormInput`, `FormRadioGroup`, `FormImageDropzone`, `FormSubmitButton`, `FormRootError`, `FormReset`).
  - **Inputs:** `defaultValues`, optional `resolver`, enhanced `onSubmit` (receives `setError`/`reset`), `submitReset` flag.
  - **Outputs/actions:** Form submission with integrated error-setting and reset. Disables all inputs and submit during `isSubmitting` and `isSubmitSuccessful`.
  - **Relationships:** Consumes `FieldControllerInput`, `FieldControllerRadioGroup`, `FieldControllerImageDropzone` from `field-input.tsx`. Uses UI primitives (`Field`, `FieldGroup`, `FieldError`, `Button`, `Spinner`).

- `src/components/blocks/form/field-input.tsx`
  - **Responsibility:** Mid-level composite layer (Layer 2) and raw field components (Layer 0). Exports composites (`FieldControllerInput`, `FieldControllerRadioGroup`, `FieldControllerImageDropzone`) that compose `FieldController.Root` + `FieldController.Label` + raw field + `FieldController.Description` + `FieldController.Error`. Also exports raw context-consuming field components (`FieldInput`, `FieldRadioGroup`, `FieldImageDropzone`).
  - **Inputs:** For composites: `FieldControllerRootProps` + field-specific props. For raw fields: consumed via `useFieldController()` context.
  - **Outputs/actions:** Field value changes propagated through react-hook-form `field.onChange`. `FieldInput` adds clearable inputs, password toggle visibility, dynamic right-section rendering with padding adjustment.
  - **Relationships:** Imports `FieldController` namespace and `useFieldController` from `field-controller.tsx`. Composes UI primitives (`Input`, `RadioGroup`, `Dropzone`, `Button`). Uses lucide-react icons (`Eye`, `EyeOff`, `X`).

- `src/components/blocks/form/field-controller.tsx`
  - **Responsibility:** Primitive layer (Layer 1). Provides the `FieldController` compound component namespace (`Root`, `Label`, `Input`, `Error`, `Description`), the `FieldControllerContext` context, and the `useFieldController` hook. Wraps react-hook-form's `Controller` render prop with a context provider.
  - **Inputs:** `FieldControllerRootProps` (extends `ControllerProps` minus `render`, adds `className`, `label`, `description`, `children`).
  - **Outputs/actions:** Exposes `{ name, field, fieldState, formState, label, description, id }` through context to descendant components.
  - **Relationships:** Depends on react-hook-form's `Controller`. Consumes UI primitives (`Field`, `FieldError`, `FieldLabel`, `FieldDescription`, `Input`). Has `"use client"` directive.

## 3. Design Principles
- **Layout structure**
  - Form root uses `FieldGroup` wrapper for consistent vertical stacking.
  - Default composite layout: Label -> Input -> Description -> Error, vertically stacked with `gap-1`.
  - Custom layouts available by dropping to `FieldController.Root` + manual child composition.
- **Visual hierarchy**
  - Label first (descriptive), input second (actionable), description third (supplementary), error last (reactive).
  - Submit button wrapped in a standalone `Field` wrapper with inline-start spinner icon during loading.
  - Root-level errors rendered at form level, not per-field.
- **Spacing/alignment**
  - Default composites use `gap-1` between elements.
  - Input right-section dynamically adjusts padding: `pr-12` for single icon, `pr-20` for multiple icons.
  - Right-section icons sized at `size-4` with `size-7` touch targets.
- **Typography intent**
  - Labels and descriptions delegated to `FieldLabel`/`FieldDescription` UI primitives.
  - Error messages use `FieldError` which expects an errors array.
- **Color/status usage**
  - `data-invalid` attribute set on `Field` wrapper when field is invalid.
  - `aria-invalid` set on inputs.
  - Right-section buttons toggle between `muted-foreground` (idle) and `foreground` (hover), inheriting `ring-ring` focus styles.
- **Responsiveness**
  - No explicit responsive breakpoints in the block itself; inherits from consuming pages and UI primitives.
  - Image dropzone preview uses `aspect-video` container for consistent sizing.
- **Accessibility considerations**
  - Labels linked to inputs via `htmlFor={name}`.
  - `aria-invalid` on all input fields.
  - Password toggle button has contextual `aria-label` ("Show password" / "Hide password").
  - Clear button has `aria-label="Clear value"`.
  - Submit button is `type="submit"`.
  - `autocomplete="off"` on all inputs.
  - Right-section buttons use `focus-visible` rings.
- **Reusable patterns**
  - Three-layer architecture enables consumers to pick the right abstraction level.
  - Compound component pattern (`FieldController.*`) enables flexible sub-component composition.
  - React 19 `use()` for context reading (enables conditional/optional context consumption).
  - Auto-disabling during submission prevents double-submit.

## 4. Functional Contract
- **User interactions**
  - Standard text/number/email/etc. input with optional clear button for supported types.
  - Password fields: toggle visibility button toggles between `text` and `password` type.
  - Radio groups: selection changes propagate via `onValueChange` hooked to `field.onChange`.
  - Image dropzone: file drop or selection sets field value to `File` object; preview renders with remove button; clicking remove sets value to `undefined`.
  - Form submit: triggers enhanced `onSubmit` handler; submit button disabled during submission.
- **State transitions**
  - Default behavior: on successful submit, form resets (controlled by `submitReset` prop, defaults to `true`).
  - During `isSubmitting`: all `Form*` inputs, submit button, and dropzone become disabled.
  - During `isSubmitSuccessful`: all inputs remain disabled (prevents post-submit editing).
  - `FormReset` component provides an alternative reset-on-success mechanism for custom layouts.
- **Validation/guard rules**
  - react-hook-form `resolver` prop supports any resolver (zod, yup, joi, etc.).
  - `rules` prop on `FieldController.Root` supports inline validation rules.
  - Root-level errors rendered via `FormRootError` component.
  - `defaultValue` falls back to empty string `""` if not provided (prevents uncontrolled-to-controlled warnings).
- **Conditional rendering**
  - `FieldController.Label`: hidden when no `label` prop and no `children`.
  - `FieldController.Description`: hidden when no `description` prop and no `children`.
  - `FieldController.Error`: hidden when `fieldState` is not invalid or has no error.
  - `FormRootError`: hidden when `errors.root` is falsy.
  - Image dropzone: shows preview with remove button when value exists, shows dropzone otherwise.
  - Input right section: hidden when no icons/buttons to render.
  - Clear button: shown only when `clearable=true`, type is clearable, input has value, and input is not disabled/readOnly.
- **Loading/empty/error**
  - Loading state: submit button shows `Spinner` icon; all inputs disabled.
  - Error state: per-field errors shown inline below input; root errors shown via `FormRootError` or accessible via the enhanced `onSubmit` payload's `setError`.
  - Empty/initial state: form renders with `defaultValues` applied; no special empty-state UI.
- **Success state**
  - No explicit success banner; success is implicit: form resets to `defaultValues`, inputs re-enabled.
  - `isSubmitSuccessful` flag disables inputs until reset occurs.
- **Navigation/routing**
  - Block has no built-in navigation/routing behavior.
- **API/data dependencies**
  - Form block is purely presentational/stateful; data fetching and API calls happen in `onSubmit`, which receives a payload enhanced with `setError` and `reset`.
- **Side effects**
  - `FormContext` effect: resets form on `isSubmitSuccessful` when `submitReset` is `true`.
  - `FormReset` effect: standalone reset trigger on `isSubmitSuccessful`.
  - File inputs: `URL.createObjectURL` used for preview; no cleanup of blob URLs (consumer must handle).

## 5. Data and State Model
- **Required inputs**
  - `FormContext`: `defaultValues` (required), `onSubmit` (required). Optionally `resolver`, `submitReset`.
  - `FieldController*` composites: `control` (unless consuming from `FormContext`), `name`.
  - Raw `Field*` components: must be rendered within a `FieldController.Root` ancestor.
- **Derived values**
  - `currentValue` in `FieldInput`: `String(field.value ?? "")`.
  - `isPasswordVisible` toggles the actual input `type` between `text` and `password`.
  - `hasValue`, `isClearableType`, `showClearButton`, `showPasswordToggle` derived from field state and props.
  - Right-section content resolved from `rightSection` prop (function receives default sections; union with custom content).
- **Local state**
  - `FieldInput`: `isPasswordVisible` (boolean).
- **Shared/global state**
  - react-hook-form's `FormProvider` carries `control`, form methods, and form state.
  - `FieldControllerContext` carries per-field state (`name`, `field`, `fieldState`, `formState`, `label`, `description`, `id`).
- **Server/API state**
  - None; form is client-only. API integration happens in `onSubmit`.
- **Mutations/submitted payloads**
  - `onSubmit` receives: `{ data: T, setError, reset, formState, ...FormSubmitHandler params }`.
  - `setError` allows setting field-level or root-level errors from server responses.
- **Transformations**
  - `defaultValue` coalesced to `""` if undefined.
  - Password field type toggled between `text` and `password` based on visibility state.
  - File value rendered as string URL (existing) or blob URL (new File).

## 6. Interaction Flow
1. **Initial render**
   - `FormContext` initializes `useForm` with `defaultValues` and optional `resolver`. Wraps children in `FormProvider` and `Form`.
2. **User action**
   - User types in input, selects radio, or drops a file.
3. **State/data change**
   - react-hook-form's `field.onChange` is called, updating form state internally.
   - For `FieldInput`, a passthrough `onChange?(event)` is also called for consumer callbacks.
4. **UI response**
   - Validation runs (if rules/resolver configured); errors appear inline.
   - Right-section icons appear/disappear based on input value and type.
   - Password visibility toggles the rendered input type.
5. **Form submission**
   - User clicks submit button or presses Enter.
   - `isSubmitting` becomes `true`; all inputs and submit button disable; spinner appears.
   - Enhanced `onSubmit` payload fires (with `setError` and `reset` available).
   - On success: `isSubmitSuccessful` becomes `true`; if `submitReset=true`, form resets to `defaultValues`.
6. **Final state**
   - Form is reset to initial `defaultValues`; inputs re-enabled; ready for another submission.

## 7. 1:1 Parity Requirements
- **Visual parity**
   - Stacked label-input-description-error layout in default composites.
   - `FieldGroup` wrapper for overall form structure.
   - Right-section icons positioned absolutely with appropriate padding adjustment.
   - Image preview with `aspect-video` ratio and destructive remove button.
   - Spinner icon on submit button during loading.
- **Functional parity**
   - Three-layer architecture with consistent prop contracts across layers.
   - `Form*` consumer components auto-wire `control` from `FormProvider`.
   - `FieldController.*` compound component pattern with context-based sub-components.
   - `FieldController.Root` wraps react-hook-form `Controller` render prop.
   - `FieldController.Input` is a bare input (not the same as `FieldInput` which adds clear/password UX).
   - Auto-disabling during `isSubmitting` and `isSubmitSuccessful`.
   - Submit-reset behavior (configurable via `submitReset`).
   - Enhanced `onSubmit` payload with `setError` and `reset`.
   - Root-level error rendering via `FormRootError`.
- **Responsive parity**
   - No explicit responsive behavior in the block; full-width inputs default.
   - Image dropzone container uses `aspect-video` for consistent ratio.
- **Accessibility parity**
   - Label `htmlFor` linked to input `id` (both use `name`).
   - `aria-invalid` on all inputs.
   - `aria-label` on clear and password-toggle buttons.
   - `autocomplete="off"` on all inputs.
   - `focus-visible` ring styles on interactive right-section buttons.
   - `type="submit"` on submit button.
- **Data/API parity**
   - Same react-hook-form API surface (`useForm`, `FormProvider`, `Controller`, `useFormContext`, `useFormState`).
   - Same `onSubmit` enhancement contract (`setError`, `reset` available).
   - Same `defaultValue` fallback to `""`.

## 8. Replaceable vs Essential Details
**Essential**
- Three-layer architecture (consumer -> composite -> primitive) with context-based sub-component composition.
- `FieldControllerContext` and `useFieldController` hook using React 19 `use()` for conditional consumption.
- `FieldController` compound component namespace pattern (`Root`, `Label`, `Input`, `Error`, `Description`).
- react-hook-form as the underlying form state manager (or equivalent with same Controller pattern).
- Enhanced `onSubmit` payload that includes `setError` and `reset`.
- Auto-disabling pattern during `isSubmitting` / `isSubmitSuccessful`.
- Submit-reset behavior (`submitReset` prop and `FormReset` component).
- Clearable inputs (type-constrained list), password toggle, and right-section composition with dynamic padding.
- Image dropzone preview with remove button and hybrid string/File value handling.
- Root-level error rendering via `FormRootError`.

**Replaceable**
- UI component library (`Field`, `FieldError`, `FieldLabel`, `FieldDescription`, `FieldGroup`, `Input`, `Button`, `RadioGroup`, `Dropzone`, `Spinner`).
- Icon library (lucide-react `Eye`, `EyeOff`, `X`) — any icon set works.
- CSS utility library (`cn` / tailwind-merge + clsx).
- File/module names and folder organization.
- Exact CSS class names and styling approach (Tailwind vs others).
- `"use client"` directive placement (only if framework requires client-component markers for hooks).
- `use()` vs `useContext()` — React 19 `use()` is preferred but `useContext` works if conditional consumption not needed.

## 9. Migration Guidance for Another Agent
- **Recommended approach**
  - Recreate the architecture in layers: (1) context + compound component primitives, (2) raw field components + composite wrappers, (3) form-level consumer wrappers.
- **Build order**
  1. Implement `FieldControllerContext` context and `useFieldController` hook with `use()`.
  2. Build `FieldController` compound components (`Root`, `Label`, `Input`, `Error`, `Description`).
  3. Implement raw field components (`FieldInput` with clear/password/right-section, `FieldRadioGroup`, `FieldImageDropzone`) that consume `useFieldController()`.
  4. Build composite wrappers (`FieldControllerInput`, `FieldControllerRadioGroup`, `FieldControllerImageDropzone`) that compose `FieldController.Root` + Label + raw field + Description + Error.
  5. Implement form-level consumer layer (`FormContext`, `FormInput`, `FormRadioGroup`, `FormImageDropzone`, `FormSubmitButton`, `FormRootError`, `FormReset`).
- **Test after migration**
  - Form submission with default values, validation errors, server errors via `setError`.
  - Submit-reset behavior: form resets after successful submit, inputs re-enabled.
  - Disabled state during submission: all inputs and submit button disabled, spinner visible.
  - Clearable input: clear button visible only for supported types when value exists and not disabled.
  - Password toggle: visibility toggles, aria-label updates.
  - Right-section single vs multiple icon padding.
  - Custom right-section renderer receives default sections; custom content merges correctly.
  - Image dropzone: file selection, preview, removal.
  - Radio group: selection propagates.
  - Field-level errors appear; root-level errors via `FormRootError`.
  - Compound component throws when used outside `FieldController.Root`.
- **Common mistakes**
  - Forgetting to wire `control` from `useFormContext()` at the `Form*` layer.
  - Not disabling inputs during `isSubmitSuccessful` (can lead to post-submit edits before reset).
  - Missing `defaultValue` fallback to `""` (causes uncontrolled-to-controlled React warning).
  - Using `useContext` instead of `use()` (if using React 19 pattern).
  - Not handling `rightSection` renderer function vs ReactNode union correctly.
  - Forgetting `type="button"` on clear and password-toggle buttons (prevents form submission).
  - Not cleaning up `URL.createObjectURL` for file previews.
- **Edge cases to preserve**
  - `rightSection` prop can be a function that receives default sections array; function must not mutate default array.
  - `rightSection` can return `null`/`undefined` to suppress default sections.
  - Clear button only for `text|search|email|tel|url|password` types; never for `number`, `date`, etc.
  - Password toggle not shown when input is `disabled`.
  - Image dropzone `maxSize` defaults to 5MB; `maxFiles` defaults to 1; accept set to `image/*`.
  - File value can be a string (existing URL) or File object (new upload) — preview must handle both.
  - `FieldController.Label` and `FieldController.Description` render nothing when both label/description prop and children are absent.
  - `FormReset` renders nothing visually (`<></>`) — it's a side-effect-only component.
  - `FieldController.Input` (primitive) is NOT the same as `FieldInput` (raw field); the former is a bare `<Input>`, the latter adds clear/password UX.
  - `submitReset` controls behavior in `FormContext`; `FormReset` provides the same effect independently.

## 10. Parity Checklist
- [ ] Three-layer architecture preserved: consumer (`Form*`) -> composite (`FieldController*`) -> primitive (`FieldController.*`).
- [ ] `FieldController.Root` wraps react-hook-form `Controller` render prop with context provider.
- [ ] `useFieldController` uses `use()` (React 19) and throws when outside `FieldController.Root`.
- [ ] `FieldController` compound components (`Label`, `Input`, `Error`, `Description`) consume context correctly.
- [ ] `FieldInput` supports clearable (type-constrained), password toggle, custom right-section, dynamic padding.
- [ ] `FormContext` wires `useForm`, `FormProvider`, `Form` element, and enhanced `onSubmit` with `setError`/`reset`.
- [ ] `Form*` consumer components auto-wire `control` from `useFormContext()`.
- [ ] Disabled states: `isSubmitting` and `isSubmitSuccessful` disable all inputs and submit button.
- [ ] Submit button shows `Spinner` icon during loading states.
- [ ] Submit-reset behavior: `submitReset` prop on `FormContext`; standalone `FormReset` component.
- [ ] `FormRootError` renders `errors.root` when present.
- [ ] `defaultValue` falls back to `""` to prevent uncontrolled-to-controlled warnings.
- [ ] Image dropzone: file drop sets `field.onChange(files[0])`; preview handles string and File values; remove button clears value.
- [ ] All inputs have `aria-invalid`, `id={name}`, `autocomplete="off"`.
- [ ] Labels use `htmlFor={name}`; password toggle has dynamic `aria-label`.
- [ ] Right-section clear/password buttons have `type="button"` to prevent form submission.
