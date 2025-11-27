"""Version subcommand."""

import sys

import rich_click as click

import qimu

# Context settings to enable -h for help
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--full",
    is_flag=True,
    help='Print full version info including "{programname} {version}" and dependency versions',
)
def version(full: bool):
    """Print the version to STDOUT."""
    if full:
        # Print program name and version
        print(f"qimu {qimu.__version__}")

        # Print versions of required packages
        packages = [
            "numpy",
            "pandas",
            "matplotlib",
            "seaborn",
            "scikit-learn",
            "plotly",
            "pyfastx",
            "python-newick",
            "pysam",
            "pyvcf3",
            "rich",
            "rich-click",
        ]

        for package in packages:
            try:
                if package == "scikit-learn":
                    # scikit-learn is imported as sklearn
                    import sklearn

                    print(f"scikit-learn {sklearn.__version__}")
                elif package == "python-newick":
                    # python-newick is imported as newick
                    import newick

                    print(f"python-newick {newick.__version__}")
                elif package == "pyvcf3":
                    # pyvcf3 is imported as vcf
                    import vcf

                    print(f"pyvcf3 {vcf.__version__}")
                elif package == "rich-click":
                    # rich_click is imported with underscore
                    import rich_click

                    print(f"rich-click {rich_click.__version__}")
                else:
                    # Standard import
                    mod = __import__(package)
                    print(f"{package} {mod.__version__}")
            except (ImportError, AttributeError):
                # If package not found or no __version__, skip it
                print(f"{package} (not available)", file=sys.stderr)
    else:
        # Just print the version number
        print(qimu.__version__)
