"""Main CLI entry point for qimu."""

import sys
from pathlib import Path

import rich_click as click
from rich.console import Console

from qimu.utils.config_handler import ConfigHandler
from qimu.utils.logger import setup_logging

# Configure rich-click
click.rich_click.TEXT_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True

# Console for stderr output
console = Console(stderr=True)

# Context settings to enable -h for help
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


class Context:
    """Shared context for CLI commands."""

    def __init__(self):
        self.config: ConfigHandler | None = None
        self.logger = None


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-c",
    "--config",
    "config_file",
    type=click.Path(path_type=Path),
    help="Specify a config file to override default",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug printing (logging level: DEBUG)",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output (logging level: INFO)",
)
@click.option(
    "--log",
    "log_file",
    type=click.Path(path_type=Path),
    help="Save the log to FILE in addition to printing to STDERR",
)
@click.pass_context
def cli(ctx, config_file: Path | None, debug: bool, verbose: bool, log_file: Path | None):
    """qimu: A modern Python CLI toolset for bioinformatics.

    Use [bold]qimu [SUBCOMMAND] --help[/bold] for help on specific subcommands.
    """
    # Initialize shared context
    ctx.obj = Context()

    # Set up logging
    ctx.obj.logger = setup_logging(verbose=verbose, debug=debug, log_file=log_file)

    # Initialize config handler
    ctx.obj.config = ConfigHandler(config_file)

    ctx.obj.logger.debug(f"Using config file: {ctx.obj.config.config_path}")


# Import and register subcommands at module level
from qimu.commands import config as config_cmd
from qimu.commands import reads_table as reads_table_cmd
from qimu.commands import version as version_cmd

cli.add_command(version_cmd.version)
cli.add_command(config_cmd.config)
cli.add_command(reads_table_cmd.reads_table)


def main():
    """Main entry point."""
    try:
        cli()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
