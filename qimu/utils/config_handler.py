"""Configuration file handler for qimu."""

import configparser
from pathlib import Path


class ConfigHandler:
    """Handle configuration file reading and writing."""

    DEFAULT_CONFIG_PATH = Path.home() / ".config" / "qimu.ini"

    def __init__(self, config_path: Path | None = None):
        """Initialize config handler.

        Args:
            config_path: Optional custom config file path
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = configparser.ConfigParser()
        self._load_defaults()
        self._load_from_file()

    def _load_defaults(self):
        """Load internal default configuration."""
        self.config["qimu"] = {}
        # Add default values here as needed

    def _load_from_file(self):
        """Load configuration from file if it exists."""
        if self.config_path.exists():
            self.config.read(self.config_path)

    def get(self, key: str, section: str = "qimu", fallback: str | None = None) -> str | None:
        """Get a configuration value.

        Args:
            key: Configuration key
            section: Configuration section (default: qimu)
            fallback: Default value if key not found

        Returns:
            Configuration value or fallback
        """
        return self.config.get(section, key, fallback=fallback)

    def set(self, key: str, value: str, section: str = "qimu"):
        """Set a configuration value and save to file.

        Args:
            key: Configuration key
            value: Configuration value
            section: Configuration section (default: qimu)
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._save_to_file()

    def _save_to_file(self):
        """Save configuration to file."""
        # Create parent directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            self.config.write(f)

    def get_all(self) -> dict:
        """Get all configuration as a dictionary.

        Returns:
            Dictionary with all sections and their values
        """
        return {section: dict(self.config[section]) for section in self.config.sections()}

    def parse_param(self, param: str) -> tuple[str, str]:
        """Parse parameter in format 'section.key' or 'key'.

        Args:
            param: Parameter string

        Returns:
            Tuple of (section, key)
        """
        if "." in param:
            section, key = param.split(".", 1)
            return section, key
        return "qimu", param
