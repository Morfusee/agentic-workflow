---
date: 2026-07-20
type: howto
tags: [github, vps, git, authentication, security]
related:
  - memory/docs/library/infrastructure/README.md
  - memory/docs/library/infrastructure/server-provisioning.md
---

# Limited GitHub Access for a Coding VPS

Use this guide to give a coding VPS access to only the GitHub repositories it needs. The setup uses a fine-grained personal access token over HTTPS, without granting repository-administration access or attaching a normal account SSH key to the VPS.

The protection has two layers:

1. A fine-grained token limits which repositories and GitHub operations the VPS can access.
2. A GitHub ruleset protects important branches from deletion and force pushes.

## 1. Create a limited fine-grained token

On GitHub, open:

```text
Profile picture
→ Settings
→ Developer settings
→ Personal access tokens
→ Fine-grained tokens
→ Generate new token
```

Use settings similar to:

```text
Token name:       Coding VPS
Expiration:       30–90 days
Resource owner:   Your GitHub account
Repository access: Only select repositories
```

Select only the repositories you will code on from the VPS. Fine-grained tokens can be restricted to specific selected repositories instead of every repository your account can access.

### Repository permissions

Set these permissions:

```text
Contents:       Read and write
Metadata:       Read-only
Pull requests:  Read and write  # Optional
Issues:         Read and write  # Optional
```

Leave everything else at **No access**. In particular, leave these permissions disabled:

```text
Administration
Actions
Secrets
Webhooks
Environments
Deployments
```

If you later need to edit files inside `.github/workflows/`, you may also need:

```text
Workflows: Read and write
```

Do not enable Workflows access unless you actually need it.

Generate the token and copy it immediately. GitHub will not show the complete token again.

### Repositories belonging to different owners

A fine-grained token can target repositories belonging to only one resource owner.

For example:

- Personal repositories may require one token.
- Organization A repositories may require another token.
- Organization B repositories may require another token.

Authenticate each corresponding GitHub account or token separately, and use `gh auth switch` where applicable.

## 2. Authenticate GitHub CLI

Create a temporary token file:

```bash
mkdir -p ~/.config/gh
chmod 700 ~/.config/gh

nano ~/.config/gh/vps-token
chmod 600 ~/.config/gh/vps-token
```

Paste only the fine-grained personal access token into the file.

Make sure no environment token is overriding GitHub CLI:

```bash
unset GH_TOKEN GITHUB_TOKEN
```

Import the token into GitHub CLI:

```bash
gh auth login \
  --hostname github.com \
  --git-protocol https \
  --with-token < ~/.config/gh/vps-token
```

Verify the authenticated account:

```bash
gh auth status
gh api user --jq '.login'
```

Configure Git to use GitHub CLI as its HTTPS credential helper:

```bash
gh auth setup-git
```

After confirming that authentication works, delete the temporary token file:

```bash
rm ~/.config/gh/vps-token
```

GitHub CLI retains the authentication after the terminal closes, the SSH connection ends, or the VPS reboots. Authentication stops only when the token expires, is revoked, is deleted through `gh auth logout`, or otherwise becomes invalid.

### Fine-grained PAT caveat

GitHub CLI officially documents `--with-token` primarily for classic PATs and warns that fine-grained PAT resource restrictions can cause confusing behavior in some `gh` commands. It recommends `GH_TOKEN` for fine-grained PAT usage. However, globally exporting `GH_TOKEN` prevents account switching, so storing the token through `gh auth login` is the more practical tradeoff for your multi-account interactive VPS.

Some commands failing outside the selected repositories is expected—it demonstrates that the token is properly restricted.

## 3. Switch between GitHub accounts

List all accounts stored by GitHub CLI:

```bash
gh auth status
```

Switch interactively:

```bash
gh auth switch --hostname github.com
```

Or select a specific account:

```bash
gh auth switch \
  --hostname github.com \
  --user YOUR_GITHUB_USERNAME
```

Verify which account is active:

```bash
gh api user --jq '.login'
```

Do not permanently export `GH_TOKEN` or `GITHUB_TOKEN`. Environment tokens override the account selected through `gh auth switch`.

If a fine-grained token must be used directly for one specific command, scope it to that command only:

```bash
GH_TOKEN="$(cat /secure/path/to/token)" \
  gh repo view OWNER/REPOSITORY
```

## 4. Configure per-repository commit identity

Authentication determines **who can push**. It does not automatically change the name and email written into commits.

Because this VPS has multiple GitHub users, add this inside each repository:

```bash
cd ~/repository/YOUR_REPOSITORY

git config user.name "YOUR NAME"
git config user.email "ACCOUNT_EMAIL_OR_NOREPLY_EMAIL"
```

Verify it:

```bash
git config user.name
git config user.email
git config --show-origin --get-regexp '^user\.'
```

Git uses `user.name` and `user.email` for commit authorship, and repository-local configuration overrides global configuration.

You could also prevent accidental commits with an inherited identity:

```bash
git config --global user.useConfigOnly true
```

Then configure `user.name` and `user.email` in each repository.

## 5. Make Git use HTTPS through GitHub CLI

After running `gh auth setup-git` in section 2, Git uses GitHub CLI as its credential helper for HTTPS remotes.

Clone repositories with an HTTPS URL:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

For an existing repository, replace its `origin` URL:

```bash
cd ~/repository/YOUR_REPOSITORY

git remote set-url origin \
  https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Confirm the remote before pushing:

```bash
git remote -v
```

## 6. Test normal development access

Fetch from the selected repository:

```bash
git fetch origin
```

Create a temporary branch, commit a test file, and push the branch:

```bash
git switch -c test/vps-access
echo "VPS access test" >> vps-test.txt
git add vps-test.txt
git commit -m "Test limited VPS GitHub access"
git push -u origin test/vps-access
```

Optionally create a pull request:

```bash
gh pr create --fill
```

Creating the pull request requires `Pull requests: Read and write`. Without that optional permission, the Git push can still succeed while PR creation fails.

## 7. Understand what the VPS can still destroy

There is an important distinction between deleting a repository and destructively changing its Git content.

### It cannot delete the GitHub repository

Because the token does not have repository-administration permission, it cannot delete the repository or change administrative repository settings.

The token can only perform actions available to its owner and further allowed by the token's selected permissions.

### It can delete code and branches

Any credential capable of pushing code can potentially run commands such as:

```bash
git push origin --delete some-branch
git push --force
```

GitHub has no permission equivalent to "allow code pushes but never allow destructive changes." A token with `Contents: Read and write` can change repository content and can delete or rewrite branches wherever repository rules allow it.

## 8. Protect important branches with a ruleset

On each selected repository, open:

```text
Repository
→ Settings
→ Rules
→ Rulesets
→ New branch ruleset
```

Use:

```text
Enforcement status: Active

Target branches:
    main
    master, if used
    release/*, if used

Rules:
    Restrict deletions
    Block force pushes
    Require a pull request before merging
    Require at least one approval, where practical

Bypass:
    Do not include the VPS account
```

Ensure that the VPS account is not included in the ruleset bypass list. A ruleset does not protect the branch from an actor that has been explicitly allowed to bypass it.

The ruleset supplies protections that token permissions cannot express. Confirm that the ruleset is active and applies to every user or role that should not bypass it.

## 9. Final least-privilege configuration

The practical setup is:

```text
Fine-grained token:
    Selected repositories only
    Contents read/write
    Metadata read-only
    No administration
    Optional pull request or issue access only when needed
    Workflow access only when editing .github/workflows/

GitHub ruleset:
    Protect main from deletion
    Block force pushes to main
    Require pull requests before merging to main
```

Do not add a normal SSH key from this VPS to your main GitHub account. A regular account SSH key acts as your account and inherits its repository access; it is not naturally restricted to a selected list of repositories.
