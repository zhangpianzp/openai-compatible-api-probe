import asyncio
from typing import List, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from openai_compatible_api_probe.config import load_env_vars

from .probe import APIProbe, ProbeResult


def version_callback(value: bool) -> None:
    if value:
        typer.echo("OpenAI API Probe v0.1.0")
        raise typer.Exit()


app = typer.Typer(
    add_completion=False,
    help="Probe OpenAI-compatible APIs for model capabilities",
)
console = Console()


def format_result_table(result: ProbeResult) -> Table:
    """Format the probe results into a rich table."""
    table = Table(
        title=f"OpenAI API Compatibility Report - {result.model_id}\nAPI URL: {result.api_base}",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,  # This adds horizontal separators
    )

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
#        table.add_row(
#            "Structured Output",
#            "✓" if capabilities.supports_structured_output else "✗",
#            next(
#                (
#                    d
#                    for d in capabilities.details.split("\n")
#                    if "Structured Output:" in d
#                ),
#                "",
#            ),
#        )
#        table.add_row(
#            "Vision",
#            "✓" if capabilities.supports_vision else "✗",
#            next((d for d in capabilities.details.split("\n") if "Vision:" in d), ""),
#        )

    return table


def filter_models(models: List[str], pattern: str) -> List[str]:
    """Filter models based on a pattern."""
    pattern = pattern.lower()
    return [m for m in models if pattern in m.lower()]


async def probe_models_async(
    probe: APIProbe, models: List[str], json_output: bool
) -> None:
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


async def probe_all_models(probe: APIProbe, json_output: bool) -> None:
    """Probe all available models."""
    models = await probe.list_models()
    await probe_models_async(probe, models, json_output)


@app.command()
def probe_models(
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
    """Probe all available models."""
    load_env_vars()  # Load environment variables
    probe = APIProbe(api_key=api_key, api_base=api_base)
    try:
        asyncio.run(probe_all_models(probe, json_output))
    except Exception as e:
        rprint(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


async def probe_pattern_async(probe: APIProbe, pattern: str, json_output: bool) -> None:
    """Probe models matching a pattern."""
    models = await probe.list_models()
    matching_models = filter_models(models, pattern)
    if matching_models:
        rprint(f"\nFound {len(matching_models)} matching models:")
        for model in matching_models:
            rprint(f"  • {model}")
        await probe_models_async(probe, matching_models, json_output)
    else:
        rprint("[red]No models found matching that pattern[/red]")
        raise typer.Exit(1)


@app.command()
def probe_pattern(
    pattern: str,
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
    """Probe models matching a pattern."""
    load_env_vars()  # Load environment variables
    probe = APIProbe(api_key=api_key, api_base=api_base)
    try:
        asyncio.run(probe_pattern_async(probe, pattern, json_output))
    except Exception as e:
        rprint(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


class InteractiveMenu:
    def __init__(self, probe: APIProbe, json_output: bool):
        self.probe = probe
        self.json_output = json_output
        self.models: List[str] = []

    async def initialize(self) -> None:
        """Initialize the menu by fetching available models."""
        self.models = await self.probe.list_models()

    def display_menu(self) -> None:
        """Display the main menu options."""
        rprint("\n[bold]Main Menu[/bold]")
        rprint("1. 列出所有模型")
        rprint("2. 指定模型名称进行验证")
#        rprint("3. Probe models matching a pattern")
#        rprint("4. Probe all models")
#        rprint("5. Exit")

    def list_models(self) -> None:
        """Display all available models."""
        rprint("\n[bold]Available models:[/bold]")
        for model in sorted(self.models):
            rprint(f"  • {model}")

    async def probe_specific_model(self) -> None:
        """Handle probing a specific model."""
        model_id = Prompt.ask("\nEnter the model ID to probe")
        if model_id in self.models:
            await probe_models_async(self.probe, [model_id], self.json_output)
        else:
            rprint(f"[red]Model {model_id} not found[/red]")

    async def probe_matching_models(self) -> None:
        """Handle probing models matching a pattern."""
        pattern = Prompt.ask("\nEnter pattern to match model IDs")
        matching_models = filter_models(self.models, pattern)
        if matching_models:
            rprint(f"\nFound {len(matching_models)} matching models:")
            for model in matching_models:
                rprint(f"  • {model}")
            if Confirm.ask("\nProbe these models?"):
                await probe_models_async(self.probe, matching_models, self.json_output)
        else:
            rprint("[red]No models found matching that pattern[/red]")

    async def probe_all_models(self) -> None:
        """Handle probing all available models."""
        msg = f"\nThis will probe all {len(self.models)} models. Continue?"
        if Confirm.ask(msg):
            await probe_models_async(self.probe, self.models, self.json_output)


async def interactive_menu_async(probe: APIProbe, json_output: bool) -> None:
    """Run the interactive menu for model selection."""
    menu = InteractiveMenu(probe, json_output)
    await menu.initialize()

    actions = {
        "1": menu.list_models,
        "2": menu.probe_specific_model,
        "3": menu.probe_matching_models,
        "4": menu.probe_all_models,
    }

    while True:
        menu.display_menu()
        choice = Prompt.ask(
            "\n请选择", choices=["1", "2"]
        )

        if choice == "5":
            break

        action = actions[choice]
        if asyncio.iscoroutinefunction(action):
            await action()
        else:
            action()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="OpenAI API key. Uses OPENAI_API_KEY from .env if not set.",
    ),
    api_base: Optional[str] = typer.Option(
        None,
        "--api-base",
        "-b",
        help="API base URL. Uses OPENAI_API_BASE from .env if not set.",
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output results in JSON format instead of table"
    ),
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
    Probe OpenAI-compatible APIs for model capabilities.
    By default, starts in interactive mode.
    """
    if ctx.invoked_subcommand is None:
        # Load environment variables first
        load_env_vars()

        # Create probe instance
        probe = APIProbe(api_key=api_key, api_base=api_base)

        try:
            asyncio.run(interactive_menu_async(probe, json_output))
        except Exception as e:
            rprint(f"[red]Error: {str(e)}[/red]")
            raise typer.Exit(1)
