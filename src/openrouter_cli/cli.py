"""CLI entry point for the OpenRouter application."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Annotated

import plotille
import typer
from rich.console import Console
from rich.table import Table

from openrouter_cli.api_client import BalanceInfo, ModelInfo, OpenRouterClient
from openrouter_cli.config import settings
from openrouter_cli.logging_config import setup_logging

app = typer.Typer()
logger = logging.getLogger(__name__)
console = Console()

WEEKLY_GROUPING_THRESHOLD = 14


def _display_balance(balance: BalanceInfo) -> None:
    """Display balance information in a formatted table."""
    table = Table(title="Account Balance")
    table.add_column("Metric", style="cyan")
    table.add_column("Amount", justify="right", style="green")

    table.add_row("Remaining Credits", f"{balance.remaining_credits:.2f}")
    table.add_row("Total Credits (purchased)", f"{balance.total_credits:.2f}")
    table.add_row("Total Usage (lifetime)", f"{balance.usage_total:.2f}")
    if balance.usage_daily > 0:
        table.add_row("Usage Today", f"{balance.usage_daily:.2f}")
        table.add_row("Usage This Week", f"{balance.usage_weekly:.2f}")
        table.add_row("Usage This Month", f"{balance.usage_monthly:.2f}")

    console.print(table)


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
    model_id: Annotated[
        str | None,
        typer.Argument(help="Model ID to show details (e.g., openai/gpt-4o)"),
    ] = None,
    free: Annotated[
        bool,
        typer.Option("--free", help="Filter to show only free models"),
    ] = False,
    images: Annotated[
        bool,
        typer.Option("--images", "-I", help="Filter to show only models that support images"),
    ] = False,
    file: Annotated[
        bool,
        typer.Option("--file", "-F", help="Filter to show only models that support file inputs"),
    ] = False,
    audio: Annotated[
        bool,
        typer.Option("--audio", "-A", help="Filter to show only models that support audio inputs"),
    ] = False,
    provider: Annotated[
        str | None,
        typer.Option("--provider", "-p", help="Filter by provider (e.g., openai, anthropic)"),
    ] = None,
) -> None:
    """List available models from OpenRouter.

    Use --free flag to filter and show only free models.

    Use --images/-I flag to filter and show only models that support image inputs.

    Use --file/-F flag to filter and show only models that support file inputs.

    Use --audio/-A flag to filter and show only models that support audio inputs.

    Use --provider to filter by provider (e.g., openai, anthropic).

    Provide a model ID as argument to show detailed capabilities.
    """
    logger.info(
        "Fetching models (model_id=%s, free=%s, images=%s, file=%s, audio=%s, provider=%s)",
        model_id,
        free,
        images,
        file,
        audio,
        provider,
    )

    async def _run() -> None:
        client = OpenRouterClient(settings)
        try:
            if model_id:
                model = await client.get_model(model_id)
                if not model:
                    console.print(f"[red]Model not found: {model_id}[/red]")
                    return
                _display_model_details(model)
            else:
                all_models = await client.list_models()

                models = all_models
                if provider:
                    provider_prefix = f"{provider}/"
                    models = [m for m in models if m.id.startswith(provider_prefix)]
                if free:
                    models = [m for m in models if m.is_free]
                if images:
                    models = [m for m in models if m.supports_image]
                if file:
                    models = [m for m in models if m.supports_file]
                if audio:
                    models = [m for m in models if m.supports_audio]

                if provider or free or images or file or audio:
                    logger.info("Filtered to %d models", len(models))

                if not models:
                    console.print("[red]No models found[/red]")
                    return

                table = Table(title="OpenRouter Models", show_lines=True)
                table.add_column("ID", style="cyan", max_width=30)
                table.add_column("Name", style="magenta", max_width=40)
                table.add_column("Context", justify="right", style="green")
                table.add_column("Prompt ($/1M)", justify="right", style="yellow")
                table.add_column("Completion ($/1M)", justify="right", style="yellow")
                table.add_column("Free", justify="center", style="bold")
                table.add_column("Capabilities", justify="center", style="bold")

                for model in models:
                    caps = []
                    if model.supports_image:
                        caps.append("📷")
                    if model.supports_file:
                        caps.append("📁")
                    if model.supports_audio:
                        caps.append("🎵")
                    caps_str = " ".join(caps) if caps else "-"

                    table.add_row(
                        model.id,
                        model.name,
                        str(model.context_length),
                        f"{model.prompt_price * 1000000:.4f}",
                        f"{model.completion_price * 1000000:.4f}",
                        "[green]Y[/green]" if model.is_free else "[red]N[/red]",
                        caps_str,
                    )

                console.print(table)
                console.print(f"\n[bold]Total:[/bold] {len(models)} models")
        finally:
            await client.close()

    asyncio.run(_run())


def _display_model_details(model: ModelInfo) -> None:
    """Display detailed model information."""
    console.print(f"\n[bold cyan]{model.name}[/bold cyan]")
    console.print(f"[dim]{model.id}[/dim]\n")

    if model.description:
        console.print("[bold]Description:[/bold]")
        console.print(f"{model.description}\n")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold yellow")
    table.add_column("Value", style="white")

    table.add_row("Canonical Slug", model.canonical_slug)
    table.add_row("Context Length", f"{model.context_length:,} tokens")
    if model.max_completion_tokens:
        table.add_row("Max Completion", f"{model.max_completion_tokens:,} tokens")
    if model.knowledge_cutoff:
        table.add_row("Knowledge Cutoff", model.knowledge_cutoff)

    table.add_row("Prompt Price", f"${model.prompt_price * 1000000:.4f}/1M tokens")
    table.add_row("Completion Price", f"${model.completion_price * 1000000:.4f}/1M tokens")
    table.add_row("Free", "[green]Yes[/green]" if model.is_free else "[red]No[/red]")

    console.print(table)

    console.print("\n[bold]Capabilities:[/bold]")
    cap_table = Table(show_header=False, box=None, padding=(0, 2))
    cap_table.add_column("Key", style="bold yellow")
    cap_table.add_column("Value", style="white")

    if model.modality:
        cap_table.add_row("Modality", model.modality)
    cap_table.add_row("Input Modalities", ", ".join(model.input_modalities) if model.input_modalities else "text")
    cap_table.add_row("Output Modalities", ", ".join(model.output_modalities) if model.output_modalities else "text")
    cap_table.add_row("Image Support", "[green]Yes[/green]" if model.supports_image else "[red]No[/red]")
    cap_table.add_row("File Support", "[green]Yes[/green]" if model.supports_file else "[red]No[/red]")
    cap_table.add_row("Audio Support", "[green]Yes[/green]" if model.supports_audio else "[red]No[/red]")
    cap_table.add_row("Content Moderation", "[green]Yes[/green]" if model.is_moderated else "[red]No[/red]")

    console.print(cap_table)

    if model.supported_parameters:
        console.print("\n[bold]Supported Parameters:[/bold]")
        params = list(model.supported_parameters)
        for i in range(0, len(params), 5):
            chunk = params[i : i + 5]
            console.print("  " + ", ".join(chunk))


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
    chart: Annotated[
        bool,
        typer.Option(
            "--chart",
            "-c",
            help="Show usage as a line chart instead of table",
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
            balance_info = await client.get_balance()

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

            if chart:
                chart_daily_totals: dict[str, float] = {}
                for u in filtered_data:
                    date_clean = u.date.split()[0] if " " in u.date else u.date
                    if date_clean not in chart_daily_totals:
                        chart_daily_totals[date_clean] = 0
                    chart_daily_totals[date_clean] += u.usage

                all_dates = []
                current_date = start_date
                while current_date <= end_date:
                    all_dates.append(current_date.strftime("%Y-%m-%d"))
                    current_date += timedelta(days=1)

                date_labels = []
                for d in all_dates:
                    date_labels.append(datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m"))

                values = [chart_daily_totals.get(d, 0.0) for d in all_dates]

                dates_numeric = list(range(len(all_dates)))

                fig = plotille.Figure()
                fig.width = 70
                fig.height = 15
                fig.x_label = "Date"
                fig.y_label = "Cost"

                def tick_fn(_val: float, idx: float) -> str:
                    idx_int = int(idx)
                    return date_labels[idx_int] if 0 <= idx_int < len(date_labels) else ""

                fig.x_ticks_fkt = tick_fn
                fig.plot(dates_numeric, values, lc="green", label="Daily Cost")

                console.print(f"\n[bold]Credit Usage Chart ({start_str} to {end_str})[/bold]\n")
                print(fig.show())
                console.print(f"\n[bold]Total:[/bold] {sum(values):.2f}")
                console.print()
                _display_balance(balance_info)
                return

            if no_per_day and no_per_model:
                total = sum(u.usage for u in filtered_data)
                total_requests = sum(u.requests for u in filtered_data)
                total_prompt = sum(u.prompt_tokens for u in filtered_data)
                total_completion = sum(u.completion_tokens for u in filtered_data)

                console.print("\n[bold]Total Usage Summary[/bold]")
                console.print(f"  Period: {start_str} to {end_str}")
                console.print(f"  Total Cost: {total:.2f}")
                console.print(f"  Total Requests: {total_requests}")
                console.print(f"  Total Prompt Tokens: {total_prompt:,}")
                console.print(f"  Total Completion Tokens: {total_completion:,}")
                console.print()
                _display_balance(balance_info)
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
                table.add_column("Cost", justify="right", style="green")
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
                        f"{model_totals[model]:.2f}",
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
                    f"[bold]{grand_total:.2f}[/bold]",
                    f"[bold]{grand_requests}[/bold]",
                    f"[bold]{grand_prompt:,}[/bold]",
                    f"[bold]{grand_completion:,}[/bold]",
                    style="bold",
                )

                console.print(table)
                console.print()
                _display_balance(balance_info)
                return

            if no_per_model:
                daily_totals: dict[str, float] = {}
                daily_requests: dict[str, int] = {}
                daily_prompt: dict[str, int] = {}
                daily_completion: dict[str, int] = {}

                for u in filtered_data:
                    date_clean = u.date.split()[0] if " " in u.date else u.date
                    if date_clean not in daily_totals:
                        daily_totals[date_clean] = 0
                        daily_requests[date_clean] = 0
                        daily_prompt[date_clean] = 0
                        daily_completion[date_clean] = 0
                    daily_totals[date_clean] += u.usage
                    daily_requests[date_clean] += u.requests
                    daily_prompt[date_clean] += u.prompt_tokens
                    daily_completion[date_clean] += u.completion_tokens

                all_dates = []
                current_date = start_date
                while current_date <= end_date:
                    all_dates.append(current_date.strftime("%Y-%m-%d"))
                    current_date += timedelta(days=1)

                table = Table(title=f"Daily Credit Usage ({start_str} to {end_str})")
                table.add_column("Date", style="cyan")
                table.add_column("Cost", justify="right", style="green")
                table.add_column("Requests", justify="right", style="yellow")
                table.add_column("Prompt Tokens", justify="right", style="magenta")
                table.add_column("Completion Tokens", justify="right", style="magenta")

                grand_total = 0
                grand_requests = 0
                grand_prompt = 0
                grand_completion = 0

                for date in all_dates:
                    date_display = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m")
                    table.add_row(
                        date_display,
                        f"{daily_totals.get(date, 0.0):.2f}",
                        str(daily_requests.get(date, 0)),
                        f"{daily_prompt.get(date, 0):,}",
                        f"{daily_completion.get(date, 0):,}",
                    )
                    grand_total += daily_totals.get(date, 0.0)
                    grand_requests += daily_requests.get(date, 0)
                    grand_prompt += daily_prompt.get(date, 0)
                    grand_completion += daily_completion.get(date, 0)

                table.add_row(
                    "[bold]Total[/bold]",
                    f"[bold]{grand_total:.2f}[/bold]",
                    f"[bold]{grand_requests}[/bold]",
                    f"[bold]{grand_prompt:,}[/bold]",
                    f"[bold]{grand_completion:,}[/bold]",
                    style="bold",
                )

                console.print(table)
                console.print()
                _display_balance(balance_info)
                return

            daily_models: dict[str, dict[str, float]] = {}
            daily_requests_dm: dict[str, dict[str, int]] = {}
            daily_prompt_dm: dict[str, dict[str, int]] = {}
            daily_completion_dm: dict[str, dict[str, int]] = {}

            for u in filtered_data:
                date_clean = u.date.split()[0] if " " in u.date else u.date
                if date_clean not in daily_models:
                    daily_models[date_clean] = {}
                    daily_requests_dm[date_clean] = {}
                    daily_prompt_dm[date_clean] = {}
                    daily_completion_dm[date_clean] = {}
                if u.model not in daily_models[date_clean]:
                    daily_models[date_clean][u.model] = 0
                    daily_requests_dm[date_clean][u.model] = 0
                    daily_prompt_dm[date_clean][u.model] = 0
                    daily_completion_dm[date_clean][u.model] = 0
                daily_models[date_clean][u.model] += u.usage
                daily_requests_dm[date_clean][u.model] += u.requests
                daily_prompt_dm[date_clean][u.model] += u.prompt_tokens
                daily_completion_dm[date_clean][u.model] += u.completion_tokens

            all_dates = []
            current_date = start_date
            while current_date <= end_date:
                all_dates.append(current_date.strftime("%Y-%m-%d"))
                current_date += timedelta(days=1)

            all_models_sorted = sorted({u.model for u in filtered_data})

            if models:
                all_models_sorted = [m for m in all_models_sorted if m in models]

            if len(all_dates) > WEEKLY_GROUPING_THRESHOLD:
                weeks: dict[str, list[str]] = {}
                current_date = start_date
                while current_date <= end_date:
                    _, iso_week, _ = current_date.isocalendar()
                    week_key = f"W{iso_week}"
                    if week_key not in weeks:
                        weeks[week_key] = []
                    weeks[week_key].append(current_date.strftime("%Y-%m-%d"))
                    current_date += timedelta(days=1)

                weekly_models: dict[str, dict[str, float]] = {}
                for week_key, dates in weeks.items():
                    weekly_models[week_key] = {}
                    for model in all_models_sorted:
                        total = sum(daily_models.get(d, {}).get(model, 0) for d in dates)
                        weekly_models[week_key][model] = total

                table = Table(title=f"Credit Usage: Per Model per Week ({start_str} to {end_str})")
                table.add_column("Model", style="cyan", max_width=25)
                for week_key in sorted(weeks.keys()):
                    table.add_column(week_key, justify="right", style="green", width=8)
                table.add_column("Total", justify="right", style="yellow", width=8)

                grand_total = 0
                week_totals: dict[str, float] = dict.fromkeys(sorted(weeks.keys()), 0.0)

                for model in all_models_sorted:
                    row_data = [model.split("/")[-1][:25]]
                    model_total: float = 0
                    for week_key in sorted(weeks.keys()):
                        value = weekly_models[week_key].get(model, 0)
                        model_total += value
                        week_totals[week_key] += value
                        row_data.append(f"{value:.2f}")
                    row_data.append(f"{model_total:.2f}")
                    table.add_row(*row_data)
                    grand_total += model_total

                summary_row = ["[bold]Total[/bold]"]
                for week_key in sorted(weeks.keys()):
                    summary_row.append(f"[bold]{week_totals[week_key]:.2f}[/bold]")
                summary_row.append(f"[bold]{grand_total:.2f}[/bold]")
                table.add_row(*summary_row, style="bold")

                console.print(table)
                console.print(f"\n[dim]Grouped by week ({len(all_dates)} days)[/dim]")
                console.print()
                _display_balance(balance_info)
            else:
                table = Table(title=f"Credit Usage: Per Model per Day ({start_str} to {end_str})")
                table.add_column("Model", style="cyan", max_width=25)
                for date in all_dates:
                    date_display = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m")
                    table.add_column(date_display, justify="right", style="green", width=6)
                table.add_column("Total", justify="right", style="yellow", width=8)

                grand_total = 0
                date_totals: dict[str, float] = dict.fromkeys(all_dates, 0.0)

                for model in all_models_sorted:
                    row_data = [model.split("/")[-1][:25]]
                    total_per_model: float = 0
                    for date in all_dates:
                        value = daily_models.get(date, {}).get(model, 0)
                        total_per_model += value
                        date_totals[date] += value
                        row_data.append(f"{value:.2f}")
                    row_data.append(f"{total_per_model:.2f}")
                    table.add_row(*row_data)
                    grand_total += total_per_model

                summary_row = ["[bold]Total[/bold]"]
                for date in all_dates:
                    summary_row.append(f"[bold]{date_totals[date]:.2f}[/bold]")
                summary_row.append(f"[bold]{grand_total:.2f}[/bold]")
                table.add_row(*summary_row, style="bold")

                console.print(table)
                console.print()
                _display_balance(balance_info)
        finally:
            await client.close()

    asyncio.run(_run())


@app.command()
def balance() -> None:
    """Get current account balance and usage information."""
    logger.info("Fetching balance")

    async def _run() -> None:
        client = OpenRouterClient(settings)
        try:
            balance_info = await client.get_balance()
            _display_balance(balance_info)
        finally:
            await client.close()

    asyncio.run(_run())


if __name__ == "__main__":
    app()
