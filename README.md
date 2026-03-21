# OpenRouter CLI

A command-line interface for interacting with the OpenRouter API.

## Features

- List available models with pricing information
- Filter free models
- Track credit usage per day and per model
- Detailed usage reports with token counts

## Requirements

- Python 3.13 or later
- uv (package manager)
- OpenRouter API key

## Quick Start

```bash
# Install dependencies
make sync

# Run the CLI
uv run or-cli --help

# List all models
uv run or-cli models

# List only free models
uv run or-cli models --free

# Get credit usage for last 7 days
uv run or-cli credits

# Get credit usage for specific models over last 30 days
uv run or-cli credits -m openai/gpt-4 -m anthropic/claude-3 -d 30
```

## Configuration

Set your OpenRouter management key via environment variable:

```bash
export OPENROUTER_MGT_KEY=your_key_here
```

Or create a `.env` file:

```
OPENROUTER_MGT_KEY=your_key_here
```

## Commands

### models

List available models from OpenRouter with pricing and context length information.

```bash
# List all models
uv run or-cli models

# List only free models
uv run or-cli models --free
```

Output includes:
- Model ID and name
- Context length
- Prompt and completion pricing (per 1k tokens)
- Free/paid indicator

### credits

Get credit usage filtered by model and days with detailed breakdown.

```bash
# Default: per-day per-model breakdown for last 7 days
uv run or-cli credits

# Filter by specific models
uv run or-cli credits -m openai/gpt-4 -m anthropic/claude-3

# Custom date range (last 30 days)
uv run or-cli credits -d 30

# Show only totals per model (no per-day breakdown)
uv run or-cli credits -npd

# Show only daily totals (no per-model breakdown)
uv run or-cli credits -npm

# Show grand total only
uv run or-cli credits -npd -npm
```

Options:
- `-m, --model`: Filter by model slug (can be specified multiple times)
- `-d, --days`: Number of days to look back (default: 7, max: 90)
- `-npd, --no-per-day`: Show total for period instead of per-day breakdown
- `-npm, --no-per-model`: Show total across all models instead of per-model breakdown

## Available Make Commands

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
├── src/openrouter_cli/
│   ├── cli.py             # CLI entry point
│   ├── config.py          # Configuration
│   ├── logging_config.py  # Logging setup
│   └── api_client.py      # OpenRouter API client
├── tests/                 # Test suite
├── pyproject.toml         # Project configuration
├── Makefile               # Build automation
├── Dockerfile             # Container build
└── README.md              # This file
```
