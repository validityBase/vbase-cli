# CLAUDE.md

## Core Standards
- Keep changes scoped and minimal.
- Follow the existing Python style and formatting conventions.
- Use `black` for formatting and `pylint` for linting when relevant.
- Do not commit secrets, private tokens, webhook URLs, or generated `.env` payloads.
- Public documentation belongs in `docs/`; internal specs, guides, and agent memory belong in `internal/`.

## Internal Documentation
- GitHub Actions spec: [internal/specs/github-actions.md](internal/specs/github-actions.md)
- Persistent agent memory: [internal/agents/memory/MEMORY.md](internal/agents/memory/MEMORY.md)

## Validation
- Run relevant tests or list the exact commands that could not be run.
- For CI/test changes, keep [internal/specs/github-actions.md](internal/specs/github-actions.md) in sync.
