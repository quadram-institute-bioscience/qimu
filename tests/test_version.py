"""Tests for version command."""

from click.testing import CliRunner

import qimu
from qimu.cli import cli


def test_version_simple():
    """Test version command without --full flag."""
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])

    assert result.exit_code == 0
    assert qimu.__version__ in result.output


def test_version_full():
    """Test version command with --full flag."""
    runner = CliRunner()
    result = runner.invoke(cli, ["version", "--full"])

    assert result.exit_code == 0
    assert f"qimu {qimu.__version__}" in result.output
    # Check that at least some packages are listed
    assert "numpy" in result.output or "pandas" in result.output


def test_help_shorthand_main():
    """Test that -h works as an alias for --help on main command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["-h"])

    assert result.exit_code == 0
    assert "qimu: A modern Python CLI toolset for bioinformatics" in result.output
    assert "Options" in result.output


def test_help_shorthand_subcommand():
    """Test that -h works as an alias for --help on subcommands."""
    runner = CliRunner()
    result = runner.invoke(cli, ["version", "-h"])

    assert result.exit_code == 0
    assert "Print the version to STDOUT" in result.output
    assert "Options" in result.output
