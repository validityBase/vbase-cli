# Agent Memory

## GitHub Actions
- Third-party GitHub Actions are pinned to full commit SHAs.
- vBase-owned shared actions and reusable workflows use reviewed `validityBase/vbase-github-actions` version tags.
- Test dependency setup uses `validityBase/vbase-github-actions/.github/actions/setup-python-deps@v1` with `requirements-dev.txt` and `require-hashes: "true"`.
- Documentation publishing delegates to `validityBase/vbase-github-actions/.github/workflows/publish-docs.yml@v1`.
- Docs publishing installs `docs/requirements.txt` with `require-hashes: "true"`, builds Sphinx Markdown into `docs/_build/markdown`, and publishes to the `main` branch of the central docs repository.
- `test.yml` requires `GHCR_PAT` to pull the localhost commitment service image.

## Dependency Locks
- Runtime, development, documentation, and lock-tooling dependency inputs live in `requirements.in`, `requirements-dev.in`, `docs/requirements.in`, and `requirements-lock.in`.
- Generated lock files are `requirements.txt`, `requirements-dev.txt`, `docs/requirements.txt`, and `requirements-lock.txt`.
- `setup.py` reads runtime package metadata from `requirements.in`, not from generated hash-locked files.
