"""CLI entry point for the OpenRouter application."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from openrouter_cli.api_client import OpenRouterClient
from openrouter_cli.config import settings
from openrouter_cli.logging_config import setup_logging

app = typer.Typer()
logger = logging.getLogger(__name__)
console = Console()


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
    free: Annotated[
        bool,
        typer.Option("--free", help="Filter to show only free models"),
    ] = False,
) -> None:
    """List available models from OpenRouter.

    Use --free flag to filter and show only free models.
    """
    logger.info("Fetching models (free=%s)", free)

    async def _run() -> None:
        client = OpenRouterClient(settings)
        try:
            all_models = await client.list_models()

            if free:
                models = [m for m in all_models if m.is_free]
                logger.info("Filtered to %d free models", len(models))
            else:
                models = all_models

            if not models:
                console.print("[red]No models found[/red]")
                return

            table = Table(title="OpenRouter Models")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="magenta")
            table.add_column("Context", justify="right", style="green")
            table.add_column("Prompt ($/1k)", justify="right", style="yellow")
            table.add_column("Completion ($/1k)", justify="right", style="yellow")
            table.add_column("Free", justify="center", style="bold")

            for model in models:
                table.add_row(
                    model.id,
                    model.name,
                    str(model.context_length),
                    f"{model.prompt_price * 1000:.6f}",
                    f"{model.completion_price * 1000:.6f}",
                    "[green]✓[/green]" if model.is_free else "[red]✗[/red]",
                )

            console.print(table)
            console.print(f"\n[bold]Total:[/bold] {len(models)} models")
        finally:
            await client.close()

    asyncio.run(_run())


@app.command()
def credits(
    models: Annotated[
        list[str],
        typer.Option(
            "--model",
            "-m",
            help="Filter by model slug (can be specified multiple times)",
        ),
    ]
    | None = None,
    days: Annotated[
        int,
        typer.Option(
            "--days",
            "-d",
            help="Number of days to look back (default: 7)",
            min=1,
            max=90,
        ),
    ] = 7,
    no_per_day: Annotated[
        bool,
        typer.Option(
            "--no-per-day",
            "-npd",
            help="Show total for period instead of per-day breakdown",
        ),
    ] = False,
    no_per_model: Annotated[
        bool,
        typer.Option(
            "--no-per-model",
            "-npm",
            help="Show total across all models instead of per-model breakdown",
        ),
    ] = False,
) -> None:
    """Get credit usage filtered by model and days.

    By default shows a table with per-day (rows) and per-model (columns) breakdown.

    Use -m/--model to filter by specific models (can be used multiple times).

    Use -d/--days to specify the number of days to look back (default: 7, max: 90).

    Use -npd to show only the total for the period (no per-day breakdown).

    Use -npm to show only the total across all models (no per-model breakdown).
    """
    logger.info(
        "Fetching credits (models=%s, days=%d, no_per_day=%s, no_per_model=%s)",
        models,
        days,
        no_per_day,
        no_per_model,
    )

    async def _run() -> None:
        client = OpenRouterClient(settings)
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days - 1)

            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")

            usage_data = await client.get_credit_usage(start_str, end_str)

            if not usage_data:
                console.print("[yellow]No usage data found for the specified period[/yellow]")
                return

            filtered_data = usage_data
            if models:
                filtered_data = [u for u in usage_data if u.model in models]
                if not filtered_data:
                    console.print(f"[red]No data found for specified model(s): {', '.join(models)}[/red]")
                    return

            if no_per_day and no_per_model:
                total = sum(u.usage for u in filtered_data)
                total_requests = sum(u.requests for u in filtered_data)
                total_prompt = sum(u.prompt_tokens for u in filtered_data)
                total_completion = sum(u.completion_tokens for u in filtered_data)

                console.print("\n[bold]Total Usage Summary[/bold]")
                console.print(f"  Period: {start_str} to {end_str}")
                console.print(f"  Total Cost: ${total:.4f}")
                console.print(f"  Total Requests: {total_requests}")
                console.print(f"  Total Prompt Tokens: {total_prompt:,}")
                console.print(f"  Total Completion Tokens: {total_completion:,}")
                return

            if no_per_day:
                model_totals: dict[str, float] = {}
                model_requests: dict[str, int] = {}
                model_prompt: dict[str, int] = {}
                model_completion: dict[str, int] = {}

                for u in filtered_data:
                    if u.model not in model_totals:
                        model_totals[u.model] = 0
                        model_requests[u.model] = 0
                        model_prompt[u.model] = 0
                        model_completion[u.model] = 0
                    model_totals[u.model] += u.usage
                    model_requests[u.model] += u.requests
                    model_prompt[u.model] += u.prompt_tokens
                    model_completion[u.model] += u.completion_tokens

                table = Table(title=f"Credit Usage by Model ({start_str} to {end_str})")
                table.add_column("Model", style="cyan")
                table.add_column("Cost ($)", justify="right", style="green")
                table.add_column("Requests", justify="right", style="yellow")
                table.add_column("Prompt Tokens", justify="right", style="magenta")
                table.add_column("Completion Tokens", justify="right", style="magenta")

                grand_total: float = 0
                grand_requests: int = 0
                grand_prompt: int = 0
                grand_completion: int = 0

                for model in sorted(model_totals.keys()):
                    table.add_row(
                        model,
                        f"${model_totals[model]:.4f}",
                        str(model_requests[model]),
                        f"{model_prompt[model]:,}",
                        f"{model_completion[model]:,}",
                    )
                    grand_total += model_totals[model]
                    grand_requests += model_requests[model]
                    grand_prompt += model_prompt[model]
                    grand_completion += model_completion[model]

                table.add_row(
                    "[bold]Total[/bold]",
                    f"[bold]${grand_total:.4f}[/bold]",
                    f"[bold]{grand_requests}[/bold]",
                    f"[bold]{grand_prompt:,}[/bold]",
                    f"[bold]{grand_completion:,}[/bold]",
                    style="bold",
                )

                console.print(table)
                return

            if no_per_model:
                daily_totals: dict[str, float] = {}
                daily_requests: dict[str, int] = {}
                daily_prompt: dict[str, int] = {}
                daily_completion: dict[str, int] = {}

                for u in filtered_data:
                    if u.date not in daily_totals:
                        daily_totals[u.date] = 0
                        daily_requests[u.date] = 0
                        daily_prompt[u.date] = 0
                        daily_completion[u.date] = 0
                    daily_totals[u.date] += u.usage
                    daily_requests[u.date] += u.requests
                    daily_prompt[u.date] += u.prompt_tokens
                    daily_completion[u.date] += u.completion_tokens

                table = Table(title=f"Daily Credit Usage ({start_str} to {end_str})")
                table.add_column("Date", style="cyan")
                table.add_column("Cost ($)", justify="right", style="green")
                table.add_column("Requests", justify="right", style="yellow")
                table.add_column("Prompt Tokens", justify="right", style="magenta")
                table.add_column("Completion Tokens", justify="right", style="magenta")

                grand_total = 0
                grand_requests = 0
                grand_prompt = 0
                grand_completion = 0

                for date in sorted(daily_totals.keys()):
                    table.add_row(
                        date,
                        f"${daily_totals[date]:.4f}",
                        str(daily_requests[date]),
                        f"{daily_prompt[date]:,}",
                        f"{daily_completion[date]:,}",
                    )
                    grand_total += daily_totals[date]
                    grand_requests += daily_requests[date]
                    grand_prompt += daily_prompt[date]
                    grand_completion += daily_completion[date]

                table.add_row(
                    "[bold]Total[/bold]",
                    f"[bold]${grand_total:.4f}[/bold]",
                    f"[bold]{grand_requests}[/bold]",
                    f"[bold]{grand_prompt:,}[/bold]",
                    f"[bold]{grand_completion:,}[/bold]",
                    style="bold",
                )

                console.print(table)
                return

            daily_models: dict[str, dict[str, float]] = {}
            daily_requests_dm: dict[str, dict[str, int]] = {}
            daily_prompt_dm: dict[str, dict[str, int]] = {}
            daily_completion_dm: dict[str, dict[str, int]] = {}

            for u in filtered_data:
                if u.date not in daily_models:
                    daily_models[u.date] = {}
                    daily_requests_dm[u.date] = {}
                    daily_prompt_dm[u.date] = {}
                    daily_completion_dm[u.date] = {}
                if u.model not in daily_models[u.date]:
                    daily_models[u.date][u.model] = 0
                    daily_requests_dm[u.date][u.model] = 0
                    daily_prompt_dm[u.date][u.model] = 0
                    daily_completion_dm[u.date][u.model] = 0
                daily_models[u.date][u.model] += u.usage
                daily_requests_dm[u.date][u.model] += u.requests
                daily_prompt_dm[u.date][u.model] += u.prompt_tokens
                daily_completion_dm[u.date][u.model] += u.completion_tokens

            all_dates = sorted(daily_models.keys())
            all_models_sorted = sorted({u.model for u in filtered_data})

            if models:
                all_models_sorted = [m for m in all_models_sorted if m in models]

            table = Table(title=f"Credit Usage: Per Day per Model ({start_str} to {end_str})")
            table.add_column("Date", style="cyan")
            for model in all_models_sorted:
                table.add_column(
                    model.split("/")[-1][:20],
                    justify="right",
                    style="green",
                )
            table.add_column("Day Total", justify="right", style="yellow")

            grand_total = 0
            for date in all_dates:
                row_data = [date]
                day_total: float = 0
                for model in all_models_sorted:
                    value = daily_models[date].get(model, 0)
                    day_total += value
                    row_data.append(f"${value:.4f}")
                row_data.append(f"${day_total:.4f}")
                table.add_row(*row_data)
                grand_total += day_total

            summary_row = ["[bold]Total[/bold]"]
            model_totals_sum: dict[str, float] = {m: 0.0 for m in all_models_sorted}  # noqa: C420
            for date in all_dates:
                for model in all_models_sorted:
                    model_totals_sum[model] += daily_models[date].get(model, 0)

            for model in all_models_sorted:
                summary_row.append(f"${model_totals_sum[model]:.4f}")
            summary_row.append(f"[bold]${grand_total:.4f}[/bold]")
            table.add_row(*summary_row, style="bold")

            console.print(table)
        finally:
            await client.close()

    asyncio.run(_run())


if __name__ == "__main__":
    app()
