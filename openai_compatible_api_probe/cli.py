import asyncio
from typing import List, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .probe import APIProbe, ProbeResult


def version_callback(value: bool) -> None:
    if value:
        typer.echo("OpenAI API Probe v0.1.0")
        raise typer.Exit()


app = typer.Typer(
    add_completion=False,
    help="Probe OpenAI-compatible APIs for model capabilities",
    invoke_without_command=True,
)
console = Console()


def format_result_table(result: ProbeResult) -> Table:
    """Format the probe results into a rich table."""
    table = Table(title=f"OpenAI API Compatibility Report - {result.model_id}")

    # Add columns
    table.add_column("Feature", style="cyan")
    table.add_column("Supported", style="green")
    table.add_column("Details", style="yellow", width=50)

    # Add rows for capabilities
    capabilities = result.capabilities
    table.add_row(
        "Chat",
        "✓" if capabilities.supports_chat else "✗",
        capabilities.details.split("\n")[0] if capabilities.details else "",
    )
    if capabilities.supports_chat:
        table.add_row(
            "Functions",
            "✓" if capabilities.supports_function_calling else "✗",
            next(
                (d for d in capabilities.details.split("\n") if "Functions:" in d), ""
            ),
        )
        table.add_row(
            "JSON Mode",
            "✓" if capabilities.supports_json_mode else "✗",
            next(
                (d for d in capabilities.details.split("\n") if "JSON Mode:" in d), ""
            ),
        )
        table.add_row(
            "Vision",
            "✓" if capabilities.supports_vision else "✗",
            next((d for d in capabilities.details.split("\n") if "Vision:" in d), ""),
        )

    return table


def filter_models(models: List[str], pattern: str) -> List[str]:
    """Filter models based on a pattern."""
    pattern = pattern.lower()
    return [m for m in models if pattern in m.lower()]


async def probe_models(probe: APIProbe, models: List[str], json_output: bool) -> None:
    """Probe a list of models and display results."""
    for model_id in models:
        with console.status(f"[bold green]Probing model {model_id}..."):
            try:
                result = await probe.probe_model(model_id)
                if json_output:
                    rprint(result.model_dump_json(indent=2))
                else:
                    table = format_result_table(result)
                    console.print(table)
                    console.print("")  # Add spacing between tables
            except Exception as e:
                rprint(f"[red]Error probing {model_id}: {str(e)}[/red]")


def handle_model_probe(
    probe: APIProbe, models: List[str], model_id: str, json_output: bool
) -> None:
    """Handle probing a specific model."""
    if model_id in models:
        asyncio.run(probe_models(probe, [model_id], json_output))
    else:
        rprint(f"[red]Model {model_id} not found[/red]")


def handle_pattern_probe(
    probe: APIProbe, models: List[str], pattern: str, json_output: bool
) -> None:
    """Handle probing models matching a pattern."""
    matching_models = filter_models(models, pattern)
    if matching_models:
        rprint(f"\nFound {len(matching_models)} matching models:")
        for model in matching_models:
            rprint(f"  • {model}")
        if Confirm.ask("\nProbe these models?"):
            asyncio.run(probe_models(probe, matching_models, json_output))
    else:
        rprint("[red]No models found matching that pattern[/red]")


def interactive_menu(probe: APIProbe, json_output: bool) -> None:
    """Run the interactive menu for model selection."""
    try:
        # Get available models
        with console.status("[bold green]Fetching available models..."):
            models = asyncio.run(probe.list_models())

        while True:
            rprint("\n[bold]Available actions:[/bold]")
            rprint("1. List all available models")
            rprint("2. Probe a specific model")
            rprint("3. Probe models matching a pattern")
            rprint("4. Probe all models")
            rprint("5. Exit")

            choice = Prompt.ask(
                "\nWhat would you like to do?", choices=["1", "2", "3", "4", "5"]
            )

            if choice == "1":
                rprint("\n[bold]Available models:[/bold]")
                for model in sorted(models):
                    rprint(f"  • {model}")

            elif choice == "2":
                model_id = Prompt.ask("\nEnter the model ID to probe")
                handle_model_probe(probe, models, model_id, json_output)

            elif choice == "3":
                pattern = Prompt.ask("\nEnter pattern to match model IDs")
                handle_pattern_probe(probe, models, pattern, json_output)

            elif choice == "4":
                msg = f"\nThis will probe all {len(models)} models. Continue?"
                if Confirm.ask(msg):
                    asyncio.run(probe_models(probe, models, json_output))

            else:  # choice == "5"
                break

    except Exception as e:
        rprint(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """
    Probe an OpenAI-compatible API endpoint to discover available models and capabilities.

    This tool provides an interactive interface to:
    - List all available models
    - Probe specific models
    - Test models matching a pattern
    - Test all available models

    Results show support for: chat completions, function calling, JSON mode, and vision.
    """
    if ctx.invoked_subcommand is None:
        if not version:
            ctx.info_name = ""
            typer.echo(ctx.get_help())
            raise typer.Exit()


@app.command()
def probe(
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="OpenAI API key. Uses OPENAI_API_KEY environment variable if not set.",
    ),
    api_base: Optional[str] = typer.Option(
        None,
        "--api-base",
        "-b",
        help="API base URL. Uses OPENAI_API_BASE environment variable if not set.",
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output results in JSON format instead of table"
    ),
) -> None:
    """Start the interactive probe interface."""
    probe = APIProbe(api_key=api_key, api_base=api_base)
    interactive_menu(probe, json_output)


if __name__ == "__main__":
    app()
