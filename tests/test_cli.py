"""Tests for the CLI application."""

import pytest
from typer.testing import CliRunner

from openrouter_cli.cli import app

runner = CliRunner()


def test_cli_help() -> None:
    """Test that --help displays help message."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "OpenRouter CLI" in result.output


def test_cli_models() -> None:
    """Test the models command."""
    result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert "Listing" in result.output


def test_cli_complete() -> None:
    """Test the complete command."""
    result = runner.invoke(app, ["complete", "Test prompt"])
    assert result.exit_code == 0
    assert "Prompt: Test prompt" in result.output


@pytest.mark.parametrize(
    "limit,expected_text",
    [
        (5, "Listing up to 5 models"),
        (20, "Listing up to 20 models"),
    ],
)
def test_cli_models_with_limit(limit: int, expected_text: str) -> None:
    """Test models command with different limits."""
    result = runner.invoke(app, ["models", "--limit", str(limit)])
    assert result.exit_code == 0
    assert expected_text in result.output
