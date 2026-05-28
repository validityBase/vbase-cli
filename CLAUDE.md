# CLAUDE.md

## Core Standards
- Keep changes scoped and minimal.
- Follow the existing Python style and formatting conventions.
- Use `black` for formatting and `pylint` for linting when relevant.
- Do not commit secrets, private tokens, webhook URLs, or generated `.env` payloads.
- Public documentation belongs in `docs/`; internal specs, guides, and agent memory belong in `internal/`.

## Dependency Locks
- Human-edited dependency inputs are `requirements.in`, `requirements-dev.in`,
  `requirements-lock.in`, and `docs/requirements.in`.
- Generated lock files are `requirements.txt`, `requirements-dev.txt`,
  `requirements-lock.txt`, and `docs/requirements.txt`; install them with
  `--require-hashes`.
- Runtime package metadata is sourced from `requirements.in` via `setup.py`.
- See [internal/specs/python-dependency-hashes.md](internal/specs/python-dependency-hashes.md).

## Internal Documentation
- GitHub Actions spec: [internal/specs/github-actions.md](internal/specs/github-actions.md)
- Dependency hashes: [internal/specs/python-dependency-hashes.md](internal/specs/python-dependency-hashes.md)
- Persistent agent memory: [internal/agents/memory/MEMORY.md](internal/agents/memory/MEMORY.md)

## Validation
- Run relevant tests or list the exact commands that could not be run.
- For CI/test changes, keep [internal/specs/github-actions.md](internal/specs/github-actions.md) in sync.
