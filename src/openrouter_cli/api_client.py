"""OpenRouter API client service."""

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from openrouter_cli.config import Settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ModelInfo:
    """Model information from OpenRouter API."""

    id: str
    name: str
    canonical_slug: str
    prompt_price: float
    completion_price: float
    context_length: int
    is_free: bool


@dataclass(frozen=True)
class CreditUsage:
    """Credit usage information."""

    date: str
    model: str
    usage: float
    requests: int
    prompt_tokens: int
    completion_tokens: int


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the OpenRouter client.

        Args:
            settings: Application settings with API key
        """
        self.settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.openrouter_base_url,
            headers={
                "Authorization": f"Bearer {settings.openrouter_mgt_key}",
                "HTTP-Referer": "https://github.com/smorand/openrouter-cli",
                "X-Title": "OpenRouter CLI",
            },
            timeout=settings.timeout_seconds,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def list_models(self, category: str | None = None) -> list[ModelInfo]:
        """List all available models.

        Args:
            category: Optional category filter

        Returns:
            List of ModelInfo objects
        """
        params = {}
        if category:
            params["category"] = category

        logger.info("Fetching models from OpenRouter API")
        response = await self._client.get("/models", params=params)
        response.raise_for_status()
        data = response.json()

        models = []
        for item in data.get("data", []):
            pricing = item.get("pricing", {})
            prompt_price = float(pricing.get("prompt", 0))
            completion_price = float(pricing.get("completion", 0))
            is_free = prompt_price == 0 and completion_price == 0

            models.append(
                ModelInfo(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    canonical_slug=item.get("canonical_slug", ""),
                    prompt_price=prompt_price,
                    completion_price=completion_price,
                    context_length=item.get("context_length", 0),
                    is_free=is_free,
                )
            )

        logger.info("Fetched %d models", len(models))
        return models

    async def get_credit_usage(
        self,
        start_date: str,
        end_date: str,
    ) -> list[CreditUsage]:
        """Get credit usage for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of CreditUsage objects
        """
        logger.info(
            "Fetching credit usage from %s to %s",
            start_date,
            end_date,
        )

        response = await self._client.get(
            "/activity",
            params={
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        response.raise_for_status()
        data = response.json()

        usage_list = []
        for item in data.get("data", []):
            usage_list.append(
                CreditUsage(
                    date=item.get("date", ""),
                    model=item.get("model", ""),
                    usage=float(item.get("usage", 0)),
                    requests=int(item.get("requests", 0)),
                    prompt_tokens=int(item.get("prompt_tokens", 0)),
                    completion_tokens=int(item.get("completion_tokens", 0)),
                )
            )

        logger.info("Fetched %d credit usage records", len(usage_list))
        return usage_list

    async def get_current_key_usage(self) -> dict[str, Any]:
        """Get current API key usage information.

        Returns:
            Dictionary with usage information
        """
        logger.info("Fetching current API key usage")
        response = await self._client.get("/auth/key")
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]
