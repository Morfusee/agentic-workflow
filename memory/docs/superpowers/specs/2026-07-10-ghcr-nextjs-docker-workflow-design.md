# GHCR Next.js Docker Workflow Design

## Context

ClickUp task `86d3keu0y` asks for a GitHub Actions workflow that builds the Next.js Docker image and pushes it to a container registry when `main` or version tags are pushed.

The approved registry is GitHub Container Registry.

## Approved Approach

Use the industry-standard GitHub Actions Docker flow directly against `nextjs/Dockerfile`:

- `docker/login-action` authenticates to `ghcr.io` with `GITHUB_TOKEN`.
- `docker/metadata-action` generates image tags and OCI labels.
- `docker/build-push-action` builds and pushes the image.
- BuildKit GitHub Actions cache is enabled with `cache-from: type=gha` and `cache-to: type=gha,mode=max`.

This intentionally does not use `docker/compose.build.yml`, even though the original ClickUp scope mentioned it. The user explicitly approved the direct Docker build action approach because it is cleaner and more standard for GHCR image publishing.

## Workflow Behavior

- Trigger on pushes to `main`.
- Trigger on pushed version tags matching `v*.*.*`.
- Publish image `ghcr.io/${{ github.repository_owner }}/mihc-nextjs`.
- Use `./nextjs` as the build context.
- Use `./nextjs/Dockerfile` as the Dockerfile.
- Pass only the public `NEXT_PUBLIC_APP_URL` build arg from a GitHub Actions repository variable, because the Better Auth browser client reads it through the Next.js public env path.
- Keep private runtime configuration out of workflow build args. Runtime values such as database URLs, auth secrets, and Inngest keys belong in the deployment environment.

## Boundaries

- Do not change application code.
- Do not change Dockerfiles or Compose files.
- Do not introduce registry secrets beyond the built-in `GITHUB_TOKEN`.
- Do not bake runtime secrets or service-network URLs into the image through GitHub Actions build args.
