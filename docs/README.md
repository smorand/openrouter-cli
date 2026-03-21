# OpenRouter CLI Documentation

## Overview

OpenRouter CLI is a command-line interface for interacting with the OpenRouter API, providing:
- Model listing with pricing information
- Free model filtering
- Credit usage tracking with detailed breakdowns

## Installation

### Prerequisites

- Python 3.13 or later
- uv package manager
- OpenRouter API key

### Quick Install

```bash
# Clone the repository
git clone git@github.com:smorand/openrouter-cli.git
cd openrouter-cli

# Install dependencies
make sync

# Install as a system-wide CLI tool
make install
```

## Configuration

### Environment Variables

Set your API key via environment variable:

```bash
export OPENROUTER_API_KEY=your_api_key_here
```

### Using .env File

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
TIMEOUT_SECONDS=30
```

## Usage

### Models Command

List available models from OpenRouter with pricing and context information.

```bash
# List all models
uv run or-cli models

# List only free models
uv run or-cli models --free
```

**Output columns:**
- ID: Model identifier (e.g., `openai/gpt-4`)
- Name: Display name
- Context: Maximum context length in tokens
- Prompt ($/1k): Cost per 1,000 prompt tokens
- Completion ($/1k): Cost per 1,000 completion tokens
- Free: Indicator showing if model is free (✓) or paid (✗)

### Credits Command

Get detailed credit usage information with flexible filtering and display options.

```bash
# Default: per-day per-model breakdown for last 7 days
uv run or-cli credits

# Filter by specific models (can use multiple -m)
uv run or-cli credits -m openai/gpt-4 -m anthropic/claude-3

# Custom date range (last 30 days)
uv run or-cli credits -d 30

# Show only totals per model (no per-day breakdown)
uv run or-cli credits -npd

# Show only daily totals (no per-model breakdown)
uv run or-cli credits -npm

# Show grand total only (no per-day, no per-model)
uv run or-cli credits -npd -npm
```

**Options:**
- `-m, --model TEXT`: Filter by model slug (can be specified multiple times)
- `-d, --days INTEGER`: Number of days to look back (default: 7, max: 90)
- `-npd, --no-per-day`: Show total for period instead of per-day breakdown
- `-npm, --no-per-model`: Show total across all models instead of per-model breakdown

**Display modes:**

1. **Default (per-day per-model):** Shows a table with dates as rows and models as columns, with day totals and model totals

2. **No per-day (`-npd`):** Shows totals aggregated by model with request counts and token usage

3. **No per-model (`-npm`):** Shows daily totals with request counts and token usage

4. **Both flags (`-npd -npm`):** Shows a simple summary with grand totals only

### Global Options

```bash
-v, --verbose  Enable debug logging
-q, --quiet    Only show warnings and errors
--help         Show this message and exit
```

## Development

### Running During Development

```bash
# Sync dependencies and run
make sync
uv run or-cli models

# Run with verbose logging
uv run or-cli models -v
```

### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific tests
make test ARGS='-k test_cli_models'
```

### Code Quality

```bash
# Run all checks (lint, format, typecheck, test)
make check

# Format code only
make format

# Lint code only
make lint

# Type checking only
make typecheck
```

## Docker

### Build and Run

```bash
# Build Docker image
make docker-build

# Build with custom tag
DOCKER_TAG=v1.0.0 make docker-build

# Build and push to registry
MAKE_DOCKER_PREFIX=gcr.io/my-project/ DOCKER_TAG=v1.0.0 make docker

# Start with Docker Compose
make run-up

# Stop Docker Compose
make run-down
```

## Troubleshooting

### Common Issues

#### API Key Not Found

Ensure `OPENROUTER_API_KEY` is set:

```bash
echo $OPENROUTER_API_KEY
```

The API key must be a management key (not a regular API key) to access credit usage data.

#### No Models Found

Check your internet connection and verify the OpenRouter API is accessible.

#### No Usage Data Found

- Verify your API key has usage data
- Try a larger date range with `-d 30`
- Ensure the API key has management permissions

#### Dependency Issues

Reinstall dependencies:

```bash
make clean-all
make sync
```

#### Permission Errors

If installing globally fails:

```bash
# Ensure ~/.local/bin is in PATH
export PATH="$HOME/.local/bin:$PATH"
```

## API Reference

The CLI uses the following OpenRouter API endpoints:

- `GET /models` - List all available models
- `GET /activity` - Get usage activity for date range
- `GET /auth/key` - Get current API key information

See [OpenRouter API Documentation](https://openrouter.ai/docs) for more details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make check` to ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
