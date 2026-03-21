"""Tests for configuration module."""

import os

import pytest

from openrouter_cli.config import Settings


def test_settings_default_values() -> None:
    """Test that settings have correct default values."""
    settings = Settings()
    assert settings.openrouter_base_url == "https://openrouter.ai/api/v1"
    assert settings.default_model == "openai/gpt-3.5-turbo"
    assert settings.timeout_seconds == 30


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that settings load from environment variables."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-123")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://custom.api.com")

    settings = Settings()
    assert settings.openrouter_api_key == "test-key-123"
    assert settings.openrouter_base_url == "https://custom.api.com"
