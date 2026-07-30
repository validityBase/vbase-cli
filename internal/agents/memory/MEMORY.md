# Agent Memory

## GitHub Actions
- Third-party GitHub Actions are pinned to full commit SHAs.
- vBase-owned shared actions and reusable workflows use reviewed `validityBase/vbase-github-actions` version tags.
- Test dependency setup uses `validityBase/vbase-github-actions/.github/actions/setup-python-deps@v1` with `requirements-dev.txt` and `require-hashes: "true"`.
- Documentation publishing delegates to `validityBase/vbase-github-actions/.github/workflows/publish-docs.yml@v1`.
- Docs publishing installs `docs/requirements.txt` with `require-hashes: true`, builds Sphinx Markdown into `docs/_build/markdown`, and publishes to the `main` branch of the central docs repository.
- `test.yml` requires `GHCR_PAT` to pull the localhost commitment service image.

## Dependency Locks
- Dependency layout, lock policy, and package metadata rules are canonical in
  `internal/specs/python-dependency-hashes.md`; keep that as the only detailed
  copy.
