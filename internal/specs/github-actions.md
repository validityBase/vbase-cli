# GitHub Actions

## Policy
- Third-party actions are pinned by full commit SHA for reproducibility.
- Shared vBase-owned actions and reusable workflows use `validityBase/vbase-github-actions` with reviewed release tags such as `@v1`.
- Workflow permissions are declared explicitly and kept minimal.
- Secrets must come from GitHub Secrets or deployment configuration, never from committed files or logs.

## Workflows

### `.github/workflows/test.yml`
- Runs on pull requests and pushes to `main` and `dev`.
- Checks out the repository with the pinned `actions/checkout` action.
- Logs in to GHCR with `GHCR_PAT`, then runs `ghcr.io/validitybase/commitment-service-localhost:latest`.
- Installs `requirements.txt` followed by `requirements-dev.txt` with Python 3.11 through `validityBase/vbase-github-actions/.github/actions/setup-python-deps@v1`.
- Runs `python3 -m unittest discover -s tests`.
- Removes the commitment service container with `if: always()`.

### `.github/workflows/update-main-docs.yml`
- Runs on pushes to `main` and manual dispatch.
- Delegates to `validityBase/vbase-github-actions/.github/workflows/publish-docs.yml@v1`.
- Installs `docs/requirements.txt` before `requirements.txt` with Python 3.11.
- Builds Sphinx Markdown docs into `docs/_build/markdown`.
- Publishes `docs/_build/markdown` to the `main` branch of the central docs repository.
- Uses `DOCS_REPO_ACCESS_TOKEN` for the central docs repository.
