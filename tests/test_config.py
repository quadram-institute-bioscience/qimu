"""Tests for config command."""

from click.testing import CliRunner

from qimu.cli import cli


def test_config_display_empty():
    """Test config command with no configuration."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--config", "test_config.ini", "config"])

        assert result.exit_code == 0
        assert "No configuration found" in result.stderr or "qimu Configuration" in result.stderr


def test_config_set_simple_param():
    """Test setting a simple parameter (default section)."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Set a value
        result = runner.invoke(
            cli, ["--config", "test_config.ini", "config", "--set", "test_key", "test_value"]
        )

        assert result.exit_code == 0
        assert "test_key" in result.stderr
        assert "test_value" in result.stderr

        # Verify it was saved by reading config
        result = runner.invoke(cli, ["--config", "test_config.ini", "config"])
        assert result.exit_code == 0


def test_config_set_with_section():
    """Test setting a parameter with section.param notation."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Set a value with section
        result = runner.invoke(
            cli,
            ["--config", "test_config.ini", "config", "--set", "mysection.mykey", "myvalue"],
        )

        assert result.exit_code == 0
        assert "mysection" in result.stderr
        assert "mykey" in result.stderr
        assert "myvalue" in result.stderr

        # Verify it was saved
        result = runner.invoke(cli, ["--config", "test_config.ini", "config"])
        assert result.exit_code == 0
        assert "mysection" in result.stderr
