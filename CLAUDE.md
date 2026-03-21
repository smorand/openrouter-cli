# OpenRouter CLI - AI Documentation

## Overview

CLI tool for interacting with OpenRouter API to list models, filter free models, and track credit usage.

**Tech Stack:** Python 3.13, Typer, httpx (async), pydantic, rich (tables)

## Key Commands

```bash
make sync               # Install dependencies
uv run or-cli           # Run the CLI
uv run or-cli --help    # Show help
make check              # Run all quality checks
make docker-build       # Build Docker image
```

## CLI Commands

- `or-cli models [--free]` - List models, optionally filter free ones
- `or-cli credits [-m model] [-d days] [-npd] [-npm]` - Get credit usage

## Project Structure

- `src/openrouter_cli/cli.py` - CLI entry point (Typer app)
- `src/openrouter_cli/config.py` - Configuration and settings
- `src/openrouter_cli/logging_config.py` - Logging setup with rich
- `src/openrouter_cli/api_client.py` - OpenRouter API client
- `tests/` - Test suite

## Conventions

- Entry point in `src/openrouter_cli/cli.py` contains only CLI wiring
- Business logic in `api_client.py` module
- Use `@dataclass(frozen=True)` for value objects (ModelInfo, CreditUsage)
- All async operations use asyncio patterns
- Logging with `%` formatting
- Rich tables for output formatting

## Documentation Index

- `.agent_docs/python.md` - Python coding standards
- `.agent_docs/makefile.md` - Makefile documentation
- `.agent_docs/opentelemetry.md` - OpenTelemetry setup
- `.agent_docs/openrouter-api.md` - OpenRouter API behavior and limitations

## Processes

### Every Modification Must:
1. Be committed and pushed if remote repo exists
2. Include docs updates (CLAUDE.md + .agent_docs and README.md + docs)
