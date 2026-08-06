# Aggregated Review — PR #10: OAuth DCR slice 1

- **Date:** 2026-08-06
- **Repo:** markdown2share
- **PR:** #10 `feat(mcp): OAuth DCR slice 1 — client registration, consent, and resource-bound tokens` (https://github.com/Morfusee/markdown2share/pull/10)
- **Branch:** `feat/mcp-01-oauth-dcr` vs `main` (2 commits: db316fa docs, e9c55e7 feature; 21 files, +3544/−30)
- **Requirements source:** `docs/plans/2026-08-04-mcp-01-oauth-dcr-implementation-plan.md` (Tasks 1–5 + acceptance criteria) + PR body
- **overall_status: PARTIAL**

> **Status update (2026-08-06):** PR #10 merged into `main` (merge commit `670a080`). Review findings were addressed before merge: `scope` guard + regression tests (`3e18135`), plan-doc revert (`433b614`), dead re-export removal (`5e89629`), consent polish — metadata/h1/aria-busy/deny copy (`d605389`), HTTPS config tests (`718638a`), Conditional alignment (`670a080`). Plan doc restored locally as untracked. Next: slice 2 — Notion ticket "MCP Delegated Identity".

## Reviewers

| Reviewer | Status | Confidence |
|---|---|---|
| requirements-reviewer | PARTIAL | high |
| thermos | PARTIAL | high |
| react-quality-review | PARTIAL | high |

Aggregate rationale: all implementation checks and acceptance criteria are satisfied with file-backed evidence; integration suites were executed 9/9 pass (thermos). PARTIAL because two low-severity defects (consent-page 500 on missing `scope`; dead re-export) and several test-coverage/a11y/copy gaps are real findings.

## Blocking / required fixes

None. Finding #1 (consent-page `scope` guard) was **fixed and pushed** after this review: commit `3e18135` `fix(consent): render the missing-client state when scope params are absent` (guard at `page.tsx:18` + new regression tests `__tests__/unit/components/consent-page.test.tsx`, 2/2 pass; lint 0 errors, typecheck clean).

## Key findings (consolidated)

1. **FAIL (low) — Consent page 500 on missing `scope` param** — `nextjs/app/(public)/consent/page.tsx:18` runs `scope.split(" ")` before any guard; `/consent` or `/consent?client_id=x` throws TypeError → 500 instead of the intended "Missing client information" state. Fix: `scope?.split(" ") ?? []`. The authorize redirect always includes `scope`, so the happy path is unaffected. (thermos FAIL + react-quality-review PARTIAL, independently)
2. **FAIL (trivial) — Dead re-export** — `nextjs/features/mcp/config/mcp.config.ts:6` re-exports `MCP_SCOPE_DESCRIPTIONS`, but the sole consumer (`oauth-consent-form.tsx:6`) imports from `mcp-scope-descriptions.ts` directly. (thermos; also flagged by react-quality-review)
3. **PARTIAL — No unit test for the production HTTPS check** in `app-url.config.ts:9-11` (fail-fast throw untested).
4. **PARTIAL — `page.tsx` `getData` untested** (missing-client fallback, "this application" fallback, fetch-failure path; no server-component test).
5. **PARTIAL — A11y/copy nits:** consent page has no `h1`/document outline (only page in the app without one); no `aria-busy`/loading announcement during pending; deny-failure copy reads "…while approving access…" (wrong verb for deny path); unknown-scope raw-string fallback (`?? scope`) untested.
6. **Notes:** provider-advertised `scopes_supported` includes OIDC scopes (openid/profile/email) that DCR clients cannot register — metadata inconsistency, fails closed. Resource-side JWT verification at `/api/mcp` is intentionally slice-2. Tokens carry no `jti` (refresh-family revocation only). No `client_name` length cap and no CAPTCHA on unauthenticated DCR — acceptable per RFC 7591, worth an ops note.

## Reviewer check details

### requirements-reviewer (PARTIAL, high)

All implementation checks PASS — including T1 URL/TTL/scope contract (4/4 unit tests executed), T2 DCR/JWT/PKCE/audience config (`lib/auth/index.ts:108-131`), T2.8 JWT claims asserted not token text, T3 well-known routes (thin handlers, nodejs runtime, RFC 8414 layout), T4 consent flow (query-driven, plain-language descriptions, `authClient.oauth2.consent({accept, scope})`, no secrets rendered), T5 refresh gating/rotation/wrong-resource rejection/redaction tests present, all 5 acceptance criteria PASS including negative check "no /api/mcp endpoint added" and the documented migration-0001 deviation (jwkss, additive, assessed deliberate).

Execution-verified by this reviewer: `pnpm lint` 0 errors (23 pre-existing warnings, none in changed files), `pnpm typecheck` clean, 10/10 new unit tests pass.

3 checks BLOCKED on integration-test execution (T2.9, T3.7, integration evidence) — reviewer could not run them due to the interactive `DATABASE_RESET_CONFIRM` guard; **resolved by thermos, which ran all 9 OAuth integration tests against the test DB: 9/9 pass** (see thermos checks).

Additional notes from this reviewer:
- PR body claim "PR #9 review-hardening plan doc was left uncommitted" is **inaccurate**: `docs/plans/2026-08-05-pr9-review-hardening-plan.md` IS committed on this branch (db316fa) and will land in PR #10. Docs-only, but the claim should be corrected.
- Plan path deviation `features/mcp/mcp.config.ts` vs `features/mcp/config/mcp.config.ts` — cosmetic, matches PR body and code-style.md §14.
- Login→consent round-trip (T4.6) relies on plugin-internal signed `oAuthState` cookie; source-verified, no test walks the login-first path.

### thermos (PARTIAL, high)

- PASS — DCR abuse/DoS surface: provider-enforced (unauthenticated → `token_endpoint_auth_method=none`, no `client_credentials`, no `skip_consent`, `require_pkce=false` rejected, scope capped, default rate limit 5/min/IP). Residual: no CAPTCHA, no client_name length cap, http:// redirect_uris accepted (standard for public clients).
- PASS — Scope enforcement chain (registration ⊆ allowed → authorize ⊆ registered → consent ⊆ signed query → token from consumed verification value).
- PASS — offline_access gating + refresh rotation (atomic prior-token revocation).
- PASS — PKCE enforcement (S256 at authorize and token exchange).
- PASS — JWT/JWKS: EdDSA (Ed25519), private keys encrypted at rest with auth secret, jwkss migration matches plugin adapter schema exactly, aud/iss/TTL verified, `checkResource` rejects outside `validAudiences`.
- PASS — Consent integrity: signed query with constant-time verify, tamper → 400, redirect_uri exact-match, session + CSRF on consent POST, React-escaped rendering.
- PASS — Secret/token leakage: no client_secret for public clients, generic error copy, console-spy redaction test asserts no tokens/codes/verifier/client_id in output.
- PASS — Well-known routes: correct RFC 8414 path-based form, no user input, no header-injection surface.
- PASS — HTTPS enforcement: fail-fast at import/build time; test env exempt. (Gap: untested.)
- **FAIL** — consent-page `scope.split(" ")` crash (see Key findings #1).
- **FAIL** — dead `MCP_SCOPE_DESCRIPTIONS` re-export (see Key findings #2).
- PASS — Test quality: full register→authorize→consent→token→refresh flow vs real Postgres, exact claim/TTL/rotation/error assertions; **9/9 integration tests ran and passed**.
- PASS — Tooling: typecheck clean, lint 0 errors, unit 273/273.

### react-quality-review (PARTIAL, high)

- PASS — §14 cached `getData` pattern matches spec verbatim.
- PARTIAL — Query robustness: `scope` unguarded (same crash as thermos); type declares `scope: string` while Next 16 searchParams are `string | undefined`.
- PASS — Loading/error/empty states: static error copy, `role="alert"`, no raw messages, buttons disabled while pending, retry resets error.
- PASS — Effect Usage Policy: zero effects, `"use client"` first line, sibling imports follow §6.
- PARTIAL — A11y: no `h1`/document outline, no `aria-busy` during pending, no JS-disabled fallback.
- PASS — Unit tests 6/6: exact consent payloads `{accept, scope:"documents:read"}`, `location.assign` URL, disabled buttons under held promise, error-copy + absence of raw detail. Gaps: page getData untested, deny-redirect/unknown-scope fallback untested, "Publish and unpublish" description unasserted.
- PASS — Consumed APIs verified against installed `@better-auth/oauth-provider` types (`oauth2.consent`, `getOAuthClientPublic`, `{redirect, url}` shape).
- PASS — typecheck clean, lint 0 errors, `vi.hoisted` mock pattern correct.

## Review scope

Branch changes only (`git diff main...HEAD`, 21 files). Excluded: unrelated repo code, `docs/plans/2026-08-05-pr9-review-hardening-plan.md` content (docs-only; noted only for the inaccurate PR claim), and the bundled migration snapshot (verified consistent with schema). Reviewers were read-only; no code modified.

## Notes for follow-up

- Correct the PR body "left uncommitted" claim or drop db316fa from the branch.
- Recommend the one-line `scope?.split(" ") ?? []` fix + a test before merge; everything else is nit-level.
- Resource-side token verification lands in slice 2 per the roadmap — keep the `/api/mcp` route metadata-only until then.
