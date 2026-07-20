# GitHub VPS Limited Access Documentation Design

## Goal

Create a standalone infrastructure guide for granting a coding VPS narrowly scoped GitHub access. The guide must preserve the supplied token permissions, authentication commands, destructive-capability warnings, branch-protection advice, and account SSH-key warning.

## Placement

Add the guide at `memory/docs/library/infrastructure/github-vps-limited-access.md` and link it from `memory/docs/library/infrastructure/README.md`. The root library index already routes infrastructure readers to that category and does not need to change.

## Library Metadata

Use the established library frontmatter:

- `date: 2026-07-20`
- `type: howto`
- Tags covering GitHub, VPS, Git, authentication, and security
- Related links to the infrastructure index and server-provisioning guide

## Documentation Structure

Present the material as a numbered, standalone procedure:

1. Create a fine-grained personal access token restricted to the selected repositories.
2. Assign only the required repository permissions, distinguishing optional permissions and the conditional Workflows permission.
3. Store the token in a protected file on the VPS and load it through `GH_TOKEN`.
4. Confirm GitHub CLI authentication.
5. Configure GitHub CLI as Git's credential helper and require HTTPS repository URLs.
6. Test fetching, branching, committing, pushing, and optionally opening a pull request.
7. Explain the boundary between repository administration and destructive Git pushes.
8. Protect the default branch with a GitHub ruleset that restricts deletion, blocks force pushes, and requires pull requests.
9. Summarize the practical least-privilege configuration and warn against adding a normal account SSH key to the VPS.

Use consistent placeholders for the GitHub username, repository, local repository directory, and branch names. Preserve all supplied commands and permission recommendations while improving headings, transitions, and copyability.

## Security Boundaries

State explicitly that omitting Administration write permission prevents repository deletion through the token but does not make write access non-destructive. A token with Contents write access can still delete branches, force-push where rules permit it, or replace code. Explain that GitHub does not provide a permission equivalent to "allow safe pushes only" and that server-side rulesets are the required second control.

Keep the following permissions disabled unless a stated need exists: Administration, Actions, Secrets, Webhooks, Environments, and Deployments. Treat Pull requests and Issues write access as optional. Treat Workflows write access as conditional on editing `.github/workflows/`.

## Index Changes

Add the new guide to the infrastructure index frontmatter's `related` list, the document list, and quick-routing section. Do not alter unrelated index entries.

## Verification

Check the finished Markdown for complete numbered flow, valid fenced code blocks, consistent placeholders, and the presence of every supplied warning and permission. Inspect the final Git diff to confirm that only the new guide and the targeted infrastructure-index lines change during implementation, with all pre-existing user-owned changes preserved.
