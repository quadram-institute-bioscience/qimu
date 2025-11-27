"""Reads-table subcommand."""

import sys
from pathlib import Path

import rich_click as click
from rich.console import Console

from qimu.utils.reads_paths import build_sequenced_run

# Console for stderr output (messages)
console = Console(stderr=True)

# Context settings to enable -h for help
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command("reads-table", context_settings=CONTEXT_SETTINGS)
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True, path_type=Path))
@click.option(
    "-e",
    "--extensions",
    multiple=True,
    default=[".fastq", ".fastq.gz"],
    help="File extensions to include (can be specified multiple times)",
)
@click.option(
    "-1",
    "--tag-for",
    multiple=True,
    default=["_R1_", "_1."],
    help="Tags indicating forward reads (can be specified multiple times)",
)
@click.option(
    "-2",
    "--tag-rev",
    multiple=True,
    default=["_R2_", "_2."],
    help="Tags indicating reverse reads (can be specified multiple times)",
)
@click.option(
    "-s",
    "--separators",
    multiple=True,
    default=["_"],
    help="Characters used to split sample names (can be specified multiple times)",
)
@click.option(
    "--strip",
    multiple=True,
    default=[],
    help="Strings to remove from sample IDs (can be specified multiple times)",
)
@click.option(
    "--single-end",
    is_flag=True,
    help="Force loading reads as single-end (default: autodetect)",
)
@click.option(
    "-f",
    "--format",
    type=str,
    default=None,
    help="Predefined output format (e.g., manifest, ampliseq, mag)",
)
@click.option(
    "--tab-sep",
    type=str,
    default="\t",
    help="Column separator (default: tab)",
)
@click.option(
    "--col-id",
    type=str,
    default="SampleId",
    help="Column name for sample ID",
)
@click.option(
    "--col-for",
    type=str,
    default="reads_R1",
    help="Column name for forward reads",
)
@click.option(
    "--col-rev",
    type=str,
    default="reads_R2",
    help="Column name for reverse reads",
)
@click.option(
    "--abs",
    is_flag=True,
    help="Print absolute paths (default: relative)",
)
@click.pass_context
def reads_table(
    ctx,
    paths,
    extensions,
    tag_for,
    tag_rev,
    separators,
    strip,
    single_end,
    format,
    tab_sep,
    col_id,
    col_for,
    col_rev,
    abs,
):
    """Generate a table of sequencing reads from directories.

    Scans the specified PATH(s) for sequencing read files and generates
    a table mapping sample IDs to read file paths.

    Examples:

        # Basic usage with paired-end reads
        qimu reads-table /path/to/reads/

        # Multiple directories with custom tags
        qimu reads-table dir1/ dir2/ -1 _R1 -2 _R2

        # Force single-end mode
        qimu reads-table /path/to/reads/ --single-end

        # Generate manifest with absolute paths
        qimu reads-table /path/to/reads/ --abs
    """
    logger = ctx.obj.logger

    try:
        # Convert paths to Path objects
        path_list = [Path(p) for p in paths]

        # Log parameters in debug mode
        logger.debug(f"Scanning directories: {path_list}")
        logger.debug(f"Extensions: {extensions}")
        logger.debug(f"Forward tags: {tag_for}")
        logger.debug(f"Reverse tags: {tag_rev}")
        logger.debug(f"Separators: {separators}")
        logger.debug(f"Strip strings: {strip}")

        # Build the sequenced run
        run = build_sequenced_run(
            paths=path_list,
            extensions=list(extensions),
            forward_tags=list(tag_for),
            reverse_tags=list(tag_rev),
            separators=list(separators),
            strip_strings=list(strip),
            force_single_end=single_end,
        )

        if len(run) == 0:
            console.print("[yellow]Warning:[/yellow] No read files found")
            sys.exit(0)

        logger.info(f"Found {len(run)} samples")
        logger.info(
            f"Read type: {'Paired-end' if run.is_paired_end() else 'Single-end'}"
        )

        # Apply format presets if specified
        if format:
            output = apply_format_preset(run, format, abs)
        else:
            # Generate table with custom options
            output = run.to_table(
                separator=tab_sep,
                col_id=col_id,
                col_for=col_for,
                col_rev=col_rev,
                absolute=abs,
            )

        # Print to stdout
        print(output)

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Unexpected error in reads-table")
        sys.exit(1)


def apply_format_preset(run, format_name: str, use_absolute: bool) -> str:
    """Apply predefined format presets.

    Args:
        run: SequencedRun object
        format_name: Name of format preset
        use_absolute: Whether to use absolute paths

    Returns:
        Formatted output string

    Raises:
        ValueError: If format is not recognized
    """
    format_name = format_name.lower()

    if format_name == "manifest":
        # Simple manifest format: sample-id,forward,reverse
        return run.to_table(
            separator=",",
            col_id="sample-id",
            col_for="forward-absolute-filepath",
            col_rev="reverse-absolute-filepath",
            absolute=True,  # Manifest always uses absolute paths
        )
    elif format_name == "ampliseq":
        # QIIME2 ampliseq format
        return run.to_table(
            separator="\t",
            col_id="sample-id",
            col_for="forward-absolute-filepath",
            col_rev="reverse-absolute-filepath",
            absolute=True,
        )
    elif format_name == "mag":
        # MAG pipeline format
        return run.to_table(
            separator=",",
            col_id="sample",
            col_for="R1",
            col_rev="R2",
            absolute=True,
        )
    else:
        raise ValueError(
            f"Unknown format: {format_name}. "
            f"Available formats: manifest, ampliseq, mag"
        )
