# OpenRouter CLI - AI Documentation

## Overview

CLI tool for interacting with OpenRouter API to manage models, generate completions, and track usage.

**Tech Stack:** Python 3.13, Typer, httpx, pydantic, OpenTelemetry

## Key Commands

```bash
make sync               # Install dependencies
make run                # Run the CLI
make run ARGS='--help'  # Show help
make check              # Run all quality checks
make docker-build       # Build Docker image
```

## Project Structure

- `src/cli.py` - CLI entry point (Typer app)
- `src/config.py` - Configuration and settings
- `src/logging_config.py` - Logging setup with rich
- `tests/` - Test suite

## Conventions

- Entry point in `src/cli.py` contains only CLI wiring
- Business logic in separate modules within `src/`
- Use `@dataclass(frozen=True)` for value objects
- All async operations use asyncio patterns
- Logging with `%` formatting
- OpenTelemetry tracing mandatory

## Documentation Index

- `.agent_docs/python.md` - Python coding standards
- `.agent_docs/makefile.md` - Makefile documentation
- `.agent_docs/opentelemetry.md` - OpenTelemetry setup

## Processes

### Every Modification Must:
1. Be committed and pushed if remote repo exists
2. Include docs updates (CLAUDE.md + .agent_docs and README.md + docs)
