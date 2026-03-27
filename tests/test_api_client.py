"""Tests for the API client module."""

from openrouter_cli.api_client import CreditUsage, ModelInfo


def test_model_info_creation() -> None:
    """Test ModelInfo dataclass creation."""
    model = ModelInfo(
        id="openai/gpt-4",
        name="GPT-4",
        canonical_slug="openai/gpt-4",
        prompt_price=0.00003,
        completion_price=0.00006,
        context_length=8192,
        is_free=False,
        supports_image=True,
    )
    assert model.id == "openai/gpt-4"
    assert model.name == "GPT-4"
    assert model.is_free is False
    assert model.supports_image is True


def test_model_info_free_detection() -> None:
    """Test that free models are correctly identified."""
    free_model = ModelInfo(
        id="test/free-model",
        name="Free Model",
        canonical_slug="test/free-model",
        prompt_price=0.0,
        completion_price=0.0,
        context_length=4096,
        is_free=True,
        supports_image=False,
    )
    assert free_model.is_free is True

    paid_model = ModelInfo(
        id="test/paid-model",
        name="Paid Model",
        canonical_slug="test/paid-model",
        prompt_price=0.00001,
        completion_price=0.00002,
        context_length=4096,
        is_free=False,
        supports_image=True,
    )
    assert paid_model.is_free is False


def test_credit_usage_creation() -> None:
    """Test CreditUsage dataclass creation."""
    usage = CreditUsage(
        date="2025-03-21",
        model="openai/gpt-4",
        usage=0.015,
        requests=5,
        prompt_tokens=500,
        completion_tokens=1250,
    )
    assert usage.date == "2025-03-21"
    assert usage.model == "openai/gpt-4"
    assert usage.usage == 0.015
    assert usage.requests == 5
