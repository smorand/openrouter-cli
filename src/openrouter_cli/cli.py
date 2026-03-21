"""CLI entry point for the OpenRouter application."""

import logging
from typing import Annotated

import typer

from openrouter_cli.logging_config import setup_logging

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.callback()
def main(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable debug logging"),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Only show warnings and errors"),
    ] = False,
) -> None:
    """OpenRouter CLI - Interact with OpenRouter API."""
    setup_logging(verbose=verbose, quiet=quiet)


@app.command()
def models(
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="Maximum number of models to display"),
    ] = 10,
) -> None:
    """List available models from OpenRouter."""
    logger.info("Fetching models (limit: %d)", limit)
    typer.echo(f"Listing up to {limit} models...")


@app.command()
def complete(
    prompt: Annotated[str, typer.Argument(help="The prompt to send")],
    model: Annotated[
        str,
        typer.Option("--model", "-m", help="Model to use for completion"),
    ] = "openai/gpt-3.5-turbo",
) -> None:
    """Generate a completion using OpenRouter."""
    logger.info("Generating completion with model: %s", model)
    typer.echo(f"Prompt: {prompt}")
    typer.echo(f"Model: {model}")


if __name__ == "__main__":
    app()
