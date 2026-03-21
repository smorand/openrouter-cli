# OpenRouter CLI

A command-line interface for interacting with the OpenRouter API.

## Features

- List available models
- Generate completions
- Track usage and costs
- Configure API settings

## Requirements

- Python 3.13 or later
- uv (package manager)
- OpenRouter API key

## Quick Start

```bash
# Install dependencies
make sync

# Run the CLI
make run

# Show available commands
make run ARGS='--help'
```

## Configuration

Set your OpenRouter API key via environment variable:

```bash
export OPENROUTER_API_KEY=your_api_key_here
```

Or create a `.env` file:

```
OPENROUTER_API_KEY=your_api_key_here
```

## Available Commands

| Command | Description |
|---------|-------------|
| `make sync` | Install dependencies |
| `make run` | Run the CLI |
| `make run ARGS='...'` | Run with arguments |
| `make test` | Run tests |
| `make test-cov` | Run tests with coverage |
| `make check` | Run all quality checks |
| `make format` | Format code |
| `make docker-build` | Build Docker image |
| `make run-up` | Start with Docker Compose |
| `make clean` | Remove build artifacts |
| `make help` | Show all commands |

## Project Structure

```
openrouter-cli/
├── src/
│   ├── cli.py             # CLI entry point
│   ├── config.py          # Configuration
│   └── logging_config.py  # Logging setup
├── tests/                 # Test suite
├── pyproject.toml         # Project configuration
├── Makefile               # Build automation
├── Dockerfile             # Container build
└── README.md              # This file
```
