[![PyPI Downloads](https://static.pepy.tech/badge/repod-cli)](https://pepy.tech/projects/repod-cli)
# repod
REPOsitory Dumper:  
A command-line tool to generate a Markdown document containing the entire contents of a repository, including directory structure and file contents.

## Motivation
This tool was created to make it easier for LLMs to read the contents of an entire repository by converting an entire repository into a single markdown file.

## Features

- Directory tree visualization
- Markdown-formatted output
- Customizable file ignoring patterns

## Installation

Requires Python 3.10 or later.

```bash
pip install repod-cli
```

## Usage

Basic usage:
```bash
repod # default to current dir
```
or,
```bash
repod /path/to/repository
```

This will create a `repod.md` file containing the repository contents.

### Options

```bash
Usage: repod [OPTIONS] [REPO_PATH]

  Repod: Dump repository contents to single markdown file.

Options:
  -o, --output FILE       Output file path (default: repod.md)
  -i, --ignore-file FILE  Path to ignore file (default: .rpdignore)
  -p, --preamble FILE     Path to preamble file
  --no-tree               Disable tree structure in output
  --encoding TEXT         File encoding (default: utf-8)
  --help                  Show this message and exit.
```

### Ignore File

Default ignore patterns:  
```gitignore
--- Project-specific files ---
.rpdignore
repod.md

--- Git-related files ---
.git/*
.gitignore

--- OS-specific metadata ---
.DS_Store
Thumbs.db
Desktop.ini

--- IDE/editor settings ---
.idea/*
.vscode/*
.project
.classpath
.settings/*

--- Python-related caches/build artifacts ---
.tox/*
*.pyc
__pycache__/*
.mypy_cache/*
.ruff_cache/*
*.whl
.env*
.venv/*

--- Archives ---
*.tar
*.tar.gz

--- Media files (images) ---
*.png
*.jpeg
*.jpg

--- Log files, binaries, lock files ---
*.log
*bin/*
*.lock

--- Node.js dependencies ---
*/node_modules/*

```


You can specify files and directories to additionally ignore using a `.rpdignore` file. The file uses glob patterns, similar to `.gitignore`:

```gitignore
# Example .rpdignore
node_modules/*
```

### Example Output

The generated markdown file from this repo: [repod.md](https://github.com/yutaka-shoji/repod/blob/main/repod.md) 

## Requirements

- Python >=3.10
- click >=8.1.8
- rich >=13.9.4
- treelib >=1.7.0

## License

MIT License
