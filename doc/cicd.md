
## Research

#### Docker

Cons:
- 140MB extra disk space for the base with python:3.12-slim-bookworm
- 1.86GB total image size (includes python modules, playwright, chromium)
  - Although most of that needs to be in the VM anyways, using docker requires it to be in a container registry as well, for which we have a limit of 500MB

#### Docker Registry

- **GCP** → Google Container Registry (GCR) or Artifact Registry (modern replacement).
  - URLs look like: `gcr.io/<project>/<image>` or `us-docker.pkg.dev/<project>/<repo>/<image>`.
  - Free storage limit: 500 MB 
- **GitHub Actions / GitHub Packages** → GitHub Container Registry (GHCR).
  - URLs look like: `ghcr.io/<owner>/<image>`.
  - Unlimited storage for public repositories
  - Free storage limit: 500 MB for private repositories
