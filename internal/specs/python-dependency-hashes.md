# Python Dependency Hashes

Python dependencies are installed from generated lock files with hashes.

## Files

- `requirements.in` is the human-edited runtime dependency input.
- `requirements.txt` is the generated runtime lock.
- `requirements-dev.in` is the human-edited development dependency input.
- `requirements-dev.txt` is the generated development lock.
- `docs/requirements.in` is the human-edited documentation dependency input.
- `docs/requirements.txt` is the generated documentation lock.
- `requirements-lock.in` pins the lock-generation tooling.
- `requirements-lock.txt` is the generated lock-tooling lock.

Do not edit generated `.txt` lock files by hand.

## Runtime Metadata

`setup.py` reads runtime dependencies from `requirements.in`. This keeps package
metadata free of `--hash` syntax while making `requirements.in` the source of
truth for top-level runtime dependencies.

## Regeneration

Use the pinned lock tooling first:

```bash
python -m pip install --require-hashes -r requirements-lock.txt
```

Regenerate lock files with Python 3.11:

```bash
python -m piptools compile --strip-extras --no-annotate --generate-hashes -o requirements.txt requirements.in
python -m piptools compile --strip-extras --no-annotate --allow-unsafe --generate-hashes -o requirements-dev.txt requirements-dev.in
python -m piptools compile --strip-extras --no-annotate --generate-hashes -o docs/requirements.txt docs/requirements.in
python -m piptools compile --strip-extras --no-annotate --allow-unsafe --generate-hashes -o requirements-lock.txt requirements-lock.in
```

To change dependencies:

1. Edit the matching `.in` file.
2. Regenerate the matching `.txt` lock.
3. Review the full dependency diff in the PR.
4. Install with `python -m pip install --require-hashes -r <lock-file>`.

To update lock-generation tooling, update the `pip-tools==...` pin in
`requirements-lock.in`, then regenerate `requirements-lock.txt`.
