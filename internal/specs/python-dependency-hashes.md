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

To update lock-generation tooling, update its pins in `requirements-lock.in`,
then regenerate `requirements-lock.txt`.

## Security updates to transitive dependencies

Existing lock files preserve resolved versions during ordinary compilation.
For a vulnerable transitive dependency, use `--upgrade-package 'package==version'`
with the regeneration command for every lock containing that dependency. Keep
the normal flags above, including `--generate-hashes` and, for dev/tooling,
`--allow-unsafe`. Do not add a runtime dependency solely to refresh a lock.

Update runtime dependencies consistently in `requirements.txt`,
`requirements-dev.txt`, and `docs/requirements.txt`. Update installer/build
dependencies in both `requirements-lock.txt` and `requirements-dev.txt`; install
the regenerated tooling lock before compiling the remaining locks.

After the targeted update, rerun the normal regeneration commands without
`--upgrade-package` and verify that they reproduce the locks. Install with
`--require-hashes`, run `pip check`, the CLI tests, and the documentation build.
Confirm that Dependabot closes the alerts after the fix reaches `main`.
