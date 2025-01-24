import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from typing import Optional
from .probe import APIProbe, ProbeResult

app = typer.Typer()
console = Console()

def format_result_table(result: ProbeResult) -> Table:
    """Format the probe results into a rich table."""
    table = Table(title="OpenAI API Compatibility Report")
    
    # Add columns
    table.add_column("Model", style="cyan", no_wrap=True)
    table.add_column("Chat", style="green")
    table.add_column("Functions", style="green")
    table.add_column("JSON Mode", style="green")
    table.add_column("Vision", style="green")
    table.add_column("Embeddings", style="green")
    table.add_column("Details", style="yellow", width=50)

    # Add rows for each model
    for model_id, capabilities in result.model_capabilities.items():
        table.add_row(
            model_id,
            "✓" if capabilities.supports_chat else "✗",
            "✓" if capabilities.supports_function_calling else "✗",
            "✓" if capabilities.supports_json_mode else "✗",
            "✓" if capabilities.supports_vision else "✗",
            "✓" if capabilities.supports_embeddings else "✗",
            capabilities.details or ""
        )
    
    return table

def run_probe(api_key: Optional[str], api_base: Optional[str], json_output: bool):
    """Run the probe and display results."""
    with console.status("[bold green]Probing API endpoint..."):
        probe = APIProbe(api_key=api_key, api_base=api_base)
        
        try:
            # Run the probe
            result = asyncio.run(probe.run())
            
            if result.error_message:
                rprint(f"[red]Error: {result.error_message}[/red]")
                raise typer.Exit(1)
            
            if json_output:
                # Output as JSON
                rprint(result.model_dump_json(indent=2))
            else:
                # Output as table
                table = format_result_table(result)
                console.print(table)
                
                # Print summary
                rprint(f"\n[green]Found {len(result.available_models)} models[/green]")
                
                # Print any global API issues
                if result.error_message:
                    rprint(f"\n[yellow]Note: {result.error_message}[/yellow]")
                
        except Exception as e:
            rprint(f"[red]Error: {str(e)}[/red]")
            raise typer.Exit(1)

@app.command()
def main(
    api_key: Optional[str] = typer.Option(
        None, "--api-key", "-k", 
        help="OpenAI API key. Will use OPENAI_API_KEY environment variable if not provided."
    ),
    api_base: Optional[str] = typer.Option(
        None, "--api-base", "-b",
        help="API base URL. Will use OPENAI_API_BASE environment variable if not provided."
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j",
        help="Output results in JSON format instead of table"
    )
) -> None:
    """
    Probe an OpenAI-compatible API endpoint to discover available models and their capabilities.
    """
    run_probe(api_key, api_base, json_output)

if __name__ == "__main__":
    app() 