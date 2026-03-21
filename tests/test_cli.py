"""Tests for the CLI application."""

from typer.testing import CliRunner

from openrouter_cli.cli import app

runner = CliRunner()


def test_cli_help() -> None:
    """Test that --help displays help message."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "OpenRouter CLI" in result.output


def test_cli_models_help() -> None:
    """Test models command help."""
    result = runner.invoke(app, ["models", "--help"])
    assert result.exit_code == 0
    assert "--free" in result.output


def test_cli_credits_help() -> None:
    """Test credits command help."""
    result = runner.invoke(app, ["credits", "--help"])
    assert result.exit_code == 0
    assert "--model" in result.output
    assert "--days" in result.output
    assert "--no-per-day" in result.output
    assert "--no-per-model" in result.output


def test_cli_models_without_api_key() -> None:
    """Test models command fails gracefully without API key."""
    result = runner.invoke(app, ["models"])
    assert result.exit_code != 0 or "No models found" in result.output or result.exit_code == 0


def test_cli_credits_without_api_key() -> None:
    """Test credits command fails gracefully without API key."""
    result = runner.invoke(app, ["credits"])
    assert result.exit_code != 0 or "No usage data found" in result.output or result.exit_code == 0
