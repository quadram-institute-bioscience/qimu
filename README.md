# qimu

Quadram institute miscellaneous utilities

## Installation

### Development Installation

```bash
# Clone the repository
cd qimu

pip install qimu
# or Install in development mode with dev dependencies
pip install -e ".[dev]"
```
 
## Usage

```bash
qimu [OPTIONS] COMMAND [ARGS]...
```

### General Options

- `-c, --config FILE` - Specify a config file to override default (~/.config/qimu.ini)
- `--debug` - Enable debug logging (DEBUG level)
- `--verbose` - Enable verbose logging (INFO level)
- `--log FILE` - Save log to FILE in addition to printing to STDERR

### Commands

#### version

Print the version information.

```bash
# Print version number only
qimu version

# Print full version info including all dependencies
qimu version --full
```

#### config

Manage configuration settings.

```bash
# Display current configuration
qimu config

# Set a parameter in the default [qimu] section
qimu config --set mykey myvalue

# Set a parameter in a specific section
qimu config --set mysection.mykey myvalue
```

## Configuration

qimu uses an INI-format configuration file. The default location is `~/.config/qimu.ini`.

Example configuration:

```ini
[qimu]
# Generic parameters
value = args...

[subcommand]
# Subcommand-specific parameters
value = args...
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black qimu tests

# Lint code
ruff check qimu tests

# Fix linting issues automatically
ruff check --fix qimu tests
```


## License

MIT

