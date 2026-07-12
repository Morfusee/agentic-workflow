# GHCR Next.js Docker Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a GitHub Actions workflow that builds `nextjs/Dockerfile` and pushes the image to GHCR on `main` and version tag pushes.

**Architecture:** A single GitHub Actions workflow owns CI image publishing. It uses official Docker actions for authentication, metadata, and BuildKit build/push behavior, with GitHub Actions cache enabled.

**Tech Stack:** GitHub Actions, Docker Buildx, GitHub Container Registry, Next.js Dockerfile.

---

## File Structure

- Create `.github/workflows/build-nextjs.yml`: workflow trigger, permissions, Docker metadata, Buildx build, GHCR push.

### Task 1: Create GHCR Workflow

**Files:**
- Create: `.github/workflows/build-nextjs.yml`

- [ ] **Step 1: Create the workflow file**

Create `.github/workflows/build-nextjs.yml` with:

```yaml
name: Build Next.js Docker image

on:
  push:
    branches:
      - main
    tags:
      - "v*.*.*"

permissions:
  contents: read
  packages: write

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: mihc-nextjs

jobs:
  build:
    name: Build and push image
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Normalize image name
        id: image
        run: echo "name=${GITHUB_REPOSITORY_OWNER,,}/${IMAGE_NAME}" >> "$GITHUB_OUTPUT"

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ steps.image.outputs.name }}
          tags: |
            type=ref,event=branch
            type=raw,value=latest,enable={{is_default_branch}}
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix=sha-

      - name: Build and push Next.js image
        uses: docker/build-push-action@v6
        with:
          context: ./nextjs
          file: ./nextjs/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          build-args: |
            NEXT_PUBLIC_APP_URL=${{ vars.NEXT_PUBLIC_APP_URL }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

- [ ] **Step 2: Validate YAML syntax**

Run:

```bash
python -c "import pathlib, yaml; yaml.safe_load(pathlib.Path('.github/workflows/build-nextjs.yml').read_text())"
```

Expected: command exits successfully with no output.

- [ ] **Step 3: Review diff**

Run:

```bash
git diff -- .github/workflows/build-nextjs.yml
```

Expected: diff contains only the new workflow file.

## Self-Review

- Spec coverage: the workflow creates the requested GHCR image publishing path for `main` and version tags, passing only public `NEXT_PUBLIC_APP_URL` from a repository variable as a build arg.
- Placeholder scan: no placeholders remain.
- Scope check: the implementation is one file and does not change app, Dockerfile, or Compose behavior.
