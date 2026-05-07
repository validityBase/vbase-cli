# Agent Memory

## GitHub Actions
- Third-party GitHub Actions are pinned to full commit SHAs.
- vBase-owned shared actions and reusable workflows use reviewed `validityBase/vbase-github-actions` version tags.
- Test dependency setup uses `validityBase/vbase-github-actions/.github/actions/setup-python-deps@v1` with `requirements.txt` followed by `requirements-dev.txt`.
- Documentation publishing delegates to `validityBase/vbase-github-actions/.github/workflows/publish-docs.yml@v1`.
- Docs publishing installs `docs/requirements.txt` before `requirements.txt`, builds Sphinx Markdown into `docs/_build/markdown`, and publishes to the `main` branch of the central docs repository.
- `test.yml` requires `GHCR_PAT` to pull the localhost commitment service image.
