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
    supports_image: bool
    supports_file: bool
    supports_audio: bool
    description: str | None = None
    input_modalities: tuple[str, ...] = ()
    output_modalities: tuple[str, ...] = ()
    modality: str | None = None
    knowledge_cutoff: str | None = None
    supported_parameters: tuple[str, ...] = ()
    max_completion_tokens: int | None = None
    is_moderated: bool = False


@dataclass(frozen=True)
class CreditUsage:
    """Credit usage information."""

    date: str
    model: str
    usage: float
    requests: int
    prompt_tokens: int
    completion_tokens: int


@dataclass(frozen=True)
class BalanceInfo:
    """Account balance information."""

    total_credits: float
    usage_total: float
    usage_daily: float
    usage_weekly: float
    usage_monthly: float

    @property
    def remaining_credits(self) -> float:
        """Calculate remaining credits."""
        return self.total_credits - self.usage_total


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
            models.append(self._parse_model(item))

        logger.info("Fetched %d models", len(models))
        return models

    async def get_model(self, model_id: str) -> ModelInfo | None:
        """Get a single model by ID.

        Args:
            model_id: Model ID (e.g., "openai/gpt-4o")

        Returns:
            ModelInfo object if found, None otherwise
        """
        logger.info("Fetching model %s", model_id)
        response = await self._client.get("/models")
        response.raise_for_status()
        data = response.json()

        for item in data.get("data", []):
            if item.get("id") == model_id or item.get("canonical_slug") == model_id:
                return self._parse_model(item)

        return None

    def _parse_model(self, item: dict[str, Any]) -> ModelInfo:
        """Parse model data from API response.

        Args:
            item: Model data from API

        Returns:
            ModelInfo object
        """
        pricing = item.get("pricing", {})
        prompt_price = float(pricing.get("prompt", 0))
        completion_price = float(pricing.get("completion", 0))
        is_free = prompt_price == 0 and completion_price == 0

        architecture = item.get("architecture", {})
        input_modalities = tuple(architecture.get("input_modalities", []))
        output_modalities = tuple(architecture.get("output_modalities", []))
        supports_image = "image" in input_modalities
        supports_file = "file" in input_modalities
        supports_audio = "audio" in input_modalities

        top_provider = item.get("top_provider") or {}
        per_request_limits = item.get("per_request_limits") or {}

        return ModelInfo(
            id=item.get("id", ""),
            name=item.get("name", ""),
            canonical_slug=item.get("canonical_slug", ""),
            prompt_price=prompt_price,
            completion_price=completion_price,
            context_length=item.get("context_length", 0),
            is_free=is_free,
            supports_image=supports_image,
            supports_file=supports_file,
            supports_audio=supports_audio,
            description=item.get("description"),
            input_modalities=input_modalities,
            output_modalities=output_modalities,
            modality=architecture.get("modality"),
            knowledge_cutoff=item.get("knowledge_cutoff"),
            supported_parameters=tuple(item.get("supported_parameters", [])),
            max_completion_tokens=per_request_limits.get("completion_tokens"),
            is_moderated=top_provider.get("is_moderated", False),
        )

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

    async def get_balance(self) -> BalanceInfo:
        """Get account balance and usage information.

        Returns:
            BalanceInfo object with balance details
        """
        logger.info("Fetching account balance")

        response = await self._client.get("/credits")
        response.raise_for_status()
        data = response.json()
        credits_data = data.get("data", {})

        key_data = await self.get_current_key_usage()
        usage_data = key_data.get("data", {})

        return BalanceInfo(
            total_credits=float(credits_data.get("total_credits", 0)),
            usage_total=float(credits_data.get("total_usage", 0)),
            usage_daily=float(usage_data.get("usage_daily", 0)),
            usage_weekly=float(usage_data.get("usage_weekly", 0)),
            usage_monthly=float(usage_data.get("usage_monthly", 0)),
        )
