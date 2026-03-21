# OpenRouter CLI Documentation

## Overview

OpenRouter CLI is a command-line interface for interacting with the OpenRouter API, which provides unified access to various large language models.

## Installation

### Prerequisites

- Python 3.13 or later
- uv package manager
- OpenRouter API key

### Quick Install

```bash
# Clone the repository
git clone <repository-url>
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
DEFAULT_MODEL=openai/gpt-3.5-turbo
TIMEOUT_SECONDS=30
```

## Usage

### Basic Commands

```bash
# Show help
openrouter-cli --help

# List available models
openrouter-cli models

# List models with custom limit
openrouter-cli models --limit 20

# Generate a completion
openrouter-cli complete "What is the capital of France?"

# Use a specific model
openrouter-cli complete "Explain quantum computing" --model anthropic/claude-3-opus
```

### Command Options

#### models

List available models from OpenRouter.

```bash
openrouter-cli models [OPTIONS]

Options:
  -l, --limit INTEGER  Maximum number of models to display (default: 10)
  --help               Show this message and exit
```

#### complete

Generate a completion using OpenRouter.

```bash
openrouter-cli complete [OPTIONS] PROMPT

Arguments:
  PROMPT  The prompt to send

Options:
  -m, --model TEXT  Model to use for completion (default: openai/gpt-3.5-turbo)
  --help            Show this message and exit
```

### Global Options

```bash
-v, --verbose  Enable debug logging
-q, --quiet    Only show warnings and errors
--help         Show this message and exit
```

## Development

### Running During Development

```bash
# Run with uv (auto-syncs dependencies)
make run

# Run with arguments
make run ARGS='models --limit 5'

# Run entry point directly (faster for development)
make run-dev ARGS='complete "Hello"'
```

### Testing

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Run specific tests
make test ARGS='-k test_cli_complete'
```

### Code Quality

```bash
# Run all checks
make check

# Format code
make format

# Lint code
make lint

# Type checking
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make check` to ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
