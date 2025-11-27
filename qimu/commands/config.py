"""Config subcommand."""

import rich_click as click
from rich.console import Console
from rich.table import Table

# Console for stderr output (messages)
console = Console(stderr=True)

# Context settings to enable -h for help
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--set",
    "set_value",
    nargs=2,
    type=str,
    metavar="PARAM VALUE",
    help="Set a configuration value (use section.param or just param for [qimu] section)",
)
@click.pass_context
def config(ctx, set_value):
    """Manage configuration settings.

    Without options, prints the current configuration.
    Use --set to modify configuration values.
    """
    config_handler = ctx.obj.config

    if set_value:
        # Set a configuration value
        param, value = set_value
        section, key = config_handler.parse_param(param)

        config_handler.set(key, value, section)
        console.print(f"[green]✓[/green] Set [bold]{section}.{key}[/bold] = [cyan]{value}[/cyan]")
        console.print(f"Configuration saved to: {config_handler.config_path}")
    else:
        # Display current configuration
        all_config = config_handler.get_all()

        if not all_config or not any(all_config.values()):
            console.print("[yellow]No configuration found.[/yellow]")
            console.print(f"Default config location: {config_handler.config_path}")
            console.print("Use [bold]--set PARAM VALUE[/bold] to add configuration.")
            return

        # Create a nice table for display
        table = Table(title="qimu Configuration", show_header=True, header_style="bold magenta")
        table.add_column("Section", style="cyan")
        table.add_column("Parameter", style="green")
        table.add_column("Value", style="yellow")

        for section, values in all_config.items():
            for key, value in values.items():
                table.add_row(section, key, value)

        console.print(table)
        console.print(f"\nConfig file: {config_handler.config_path}")
