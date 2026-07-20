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

## 2. Store the token securely on the VPS

Create the GitHub CLI configuration directory and restrict access to your account:

```bash
mkdir -p ~/.config/gh
chmod 700 ~/.config/gh
```

Create a token file:

```bash
nano ~/.config/gh/vps-token
```

Paste only the token into the file, save it, and then restrict the file permissions:

```bash
chmod 600 ~/.config/gh/vps-token
```

Load the token automatically through `GH_TOKEN`:

```bash
echo 'export GH_TOKEN="$(cat "$HOME/.config/gh/vps-token")"' >> ~/.profile
source ~/.profile
```

Confirm that GitHub CLI recognizes the token:

```bash
gh auth status
```

Because this is a fine-grained token, GitHub CLI recommends supplying it through the `GH_TOKEN` environment variable.

## 3. Make Git use HTTPS through GitHub CLI

Configure GitHub CLI as Git's credential helper:

```bash
gh auth setup-git
```

This configures Git to use the credentials available to GitHub CLI.

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

## 4. Test normal development access

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

## 5. Understand what the VPS can still destroy

There is an important distinction between deleting a repository and destructively changing its Git content.

### It cannot delete the GitHub repository

This command should fail:

```bash
gh repo delete YOUR_USERNAME/YOUR_REPOSITORY
```

The token lacks `Administration: Read and write`, which is required to delete a repository.

### It can delete code and branches

Any credential capable of pushing code can potentially run commands such as:

```bash
git push origin --delete some-branch
git push --force
```

GitHub has no permission equivalent to "allow code pushes but never allow destructive changes." A token with `Contents: Read and write` can change repository content and can delete or rewrite branches wherever repository rules allow it.

## 6. Protect important branches with a ruleset

On each selected repository, open:

```text
Repository
→ Settings
→ Rules
→ Rulesets
→ New branch ruleset
```

Target `main`, then enable:

```text
Restrict deletions
Block force pushes
Require a pull request before merging
```

The ruleset supplies protections that token permissions cannot express. Confirm that the ruleset is active and applies to every user or role that should not bypass it.

## 7. Final least-privilege configuration

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
