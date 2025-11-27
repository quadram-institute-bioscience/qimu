# qimu: a Python CLI toolset

qimu is a modern python toolkit that works as

```
qimu [general_args] [subcommand] [subcommand_args]
```

General requirements of the project:

* Must be "pip installable"
* Must offer a nice CLI using rich, rich-click
* Must support a nice logging coherently in the application (default level: WARNING)
* The program version should only be written in one file (typically __init__.py and then 'dynamic = ["version"]' in pyproject.toml)
* All messages will be nicely formatted with rich and print to STDERR, only the "real" program output (if any) is to stdout
* Must be easily maintainable with a directory structure that might resemble

--/qimu --- /utils/       (for files containing classes or methods used by subcommands)
         |
         +- /commands/    (each subcommand has it's companion subcommand.py)


* This is meant to add new subcommands easily. Some subcommands will use routines from "utils" previoulsy added
* Automatic tests should be available (pytest or other as suggested)

Package requirements:

* Write code in modern Python avoid deprecations, but target a relatively widely available python version like 3.10 to allow compatibility with other packages in the same environment
* As requirements use 'numpy', 'pandas', 'matplotlib', 'seaborn', 'scikit-learn', 'plotly' for all the data analysis package
* As requirements use 'pyfastx', 'python-newick', 'pysam', 'pyvcf' for common bionformatics tasks

## General args

* -c, --config FILE	Specify a config file to override default (see below)
* --debug               Enable debug printing (logging level: DEFAULT)
* --verbose             Enable verbose (logging level: INFO)
* --log FILE            Save the log to FILE **in addition to** printing to STDERR

## Other general requirements

* Support a configuration file in INI format. Default location will be ~/.config/qimu.ini. Configuration should be available 

### Config file format

```
[qimu]
; generic parameters
value = args...

[subcommand]
; 'subcommand' specific parameters
value = args...
```

## A minimal viable example

* add the subcommand 'version' that will print the version to STDOUT
	with `--full` will print: "{programname} {version}" and then the version of the required modules (pandas, etc) one per line"

* add the subcommand 'config':
	will print the configuration
	with --set PARAM VALUE will set 


