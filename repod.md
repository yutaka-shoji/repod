# Repository Content Dump

    This document contains a dump of a repository's contents. The structure is as follows:

    1. Repository Structure (tree format)
    2. File Contents (each file with its path and content)

## Repository Structure

```

├── .git/
├── .python-version
├── .venv/
├── README.md
├── pyproject.toml
└── src/
    └── repod/
        ├── __init__.py
        ├── __pycache__/
        ├── cli.py
        ├── core.py
        └── py.typed

```


## File Contents

### pyproject.toml

```
[project]
name = "repod"
version = "0.0.1"
description = "REPOsitory Dumper"
readme = "README.md"
authors = [
    { name = "Shoji, Yutaka", email = "ytk.shoji@gmail.com" }
]
requires-python = ">=3.10"
dependencies = [
    "click>=8.1.8",
    "rich>=13.9.4",
    "treelib>=1.7.0",
]

[project.scripts]
repod = "repod.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

```

### README.md

```markdown
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
pip install repod
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
  --help                  Show this message and exit.
```

### Ignore File

Default ignore patterns:  
```gitignore
.rpdignore
repod.md
.git/*
.gitignore
.github/*
.tox/*
*.pyc
__pycache__/*
.mypy_cache/*
.ruff_cache/*
*.whl
*.tar
*.tar.gz
*.env*
*.png
*.jpeg
*.jpg
*bin/*
*.lock
.venv/*
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

```

### .python-version

```
3.10

```

### src/repod/__init__.py

```python
def hello() -> str:
    return "Hello from repod!"

```

### src/repod/core.py

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, TextIO
import fnmatch
import logging
from rich.console import Console
from rich.progress import Progress
from treelib import Tree

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class DumperConfig:
    """Config dataclass."""

    repo_path: Path
    output_path: Path
    ignore_file: Optional[Path] = None
    preamble_file: Optional[Path] = None
    include_tree: bool = True
    default_preamble: str = """
    # Repository Content Dump

    This document contains a dump of a repository's contents. The structure is as follows:

    1. Repository Structure (tree format)
    2. File Contents (each file with its path and content)
    """.strip()


class RepositoryDumper:
    """Class to dump repository contents to a markdown file."""

    EXT_TO_LANG: Dict[str, str] = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".rs": "rust",
        ".go": "go",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".md": "markdown",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".json": "json",
        ".xml": "xml",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".sql": "sql",
        ".sh": "bash",
        ".bat": "batch",
        ".ps1": "powershell",
    }

    # default ignore patterns
    DEFAULT_IGNORE_PATTERNS = [
        ".rpdignore",
        "repod.md",
        ".git/*",
        ".gitignore",
        ".github/*",
        ".tox/*",
        "*.pyc",
        "__pycache__/*",
        ".mypy_cache/*",
        ".ruff_cache/*",
        "*.whl",
        "*.tar",
        "*.tar.gz",
        "*.env*",
        "*.png",
        "*.jpeg",
        "*.jpg",
        "*bin/*",
        "*.lock",
        ".venv/*",
    ]

    def __init__(self, config: DumperConfig):
        self.config = config
        self.ignore_patterns = (
            self.DEFAULT_IGNORE_PATTERNS + self._load_ignore_patterns()
        )

    def _get_file_language(self, file_path: Path) -> str:
        """Get the language for a given file based on its extension."""
        return self.EXT_TO_LANG.get(file_path.suffix.lower(), "")

    def _load_ignore_patterns(self) -> List[str]:
        """Load ignore patterns from the ignore file."""
        if not self.config.ignore_file:
            return []

        try:
            with open(self.config.ignore_file, "r") as f:
                return [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        except FileNotFoundError:
            logger.warning(f"Ignore file not found: {self.config.ignore_file}")
            return []
        except Exception as e:
            logger.error(f"Error reading ignore file: {e}")
            return []

    def _should_ignore(self, file_path: str) -> bool:
        """Check if a file should be ignored based on the ignore patterns."""
        return any(
            fnmatch.fnmatch(file_path, pattern) for pattern in self.ignore_patterns
        )

    def _generate_tree(self) -> str:
        """Generate a tree structure of the repository."""
        tree = Tree()
        root_name = self.config.repo_path.name
        tree.create_node(root_name, root_name)

        def add_to_tree(parent_path: Path, parent_id: str) -> None:
            items = sorted(
                [
                    x
                    for x in parent_path.iterdir()
                    if not self._should_ignore(
                        str(x.relative_to(self.config.repo_path))
                    )
                ],
                key=lambda x: (x.is_file(), x.name.lower()),
            )

            for item in items:
                name = f"{item.name}/" if item.is_dir() else item.name
                item_id = str(item.relative_to(self.config.repo_path))
                tree.create_node(name, item_id, parent=parent_id)

                if item.is_dir():
                    add_to_tree(item, item_id)

        add_to_tree(self.config.repo_path, root_name)
        tree_str = tree.show(stdout=False)
        assert isinstance(tree_str, str)
        return f"```\n{tree_str}\n```\n"

    def _write_preamble(self, output_file: TextIO) -> None:
        """Write preamble and tree structure to output file."""
        preamble = self.config.default_preamble
        if self.config.preamble_file:
            try:
                with open(self.config.preamble_file, "r") as pf:
                    preamble = pf.read().strip()
            except Exception as e:
                logger.error(f"Error reading preamble file: {e}")

        output_file.write(f"{preamble}\n\n")

        if self.config.include_tree:
            output_file.write("## Repository Structure\n\n")
            output_file.write(self._generate_tree())
            output_file.write("\n\n## File Contents\n\n")

    def _process_file(
        self, file_path: Path, repo_root: Path, output_file: TextIO
    ) -> None:
        """Process a single file and write its contents to the output file."""
        try:
            relative_path = file_path.relative_to(repo_root)
            if self._should_ignore(str(relative_path)):
                return

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()
                lang = self._get_file_language(file_path)
                output_file.write(f"### {relative_path}\n\n")
                output_file.write(
                    f"```{lang}\n{content}\n```\n\n"
                    if lang
                    else f"```\n{content}\n```\n\n"
                )

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

    def dump(self) -> None:
        """Dump the repository contents to the output file."""
        try:
            files = [f for f in self.config.repo_path.rglob("*") if f.is_file()]
            total_files = len(files)

            with open(self.config.output_path, "w", encoding="utf-8") as output_file:
                self._write_preamble(output_file)

                with Progress() as progress:
                    task = progress.add_task(
                        "[cyan]Processing files...", total=total_files
                    )

                    for file_path in files:
                        self._process_file(
                            file_path, self.config.repo_path, output_file
                        )
                        progress.update(task, advance=1)

            console.print(
                f"\n[green]Repository contents written to {self.config.output_path}[/green]"
            )

        except Exception as e:
            logger.error(f"Error during dump process: {e}")
            raise

```

### src/repod/cli.py

```python
import click
from pathlib import Path
from .core import DumperConfig, RepositoryDumper
from rich.console import Console

console = Console()


@click.command()
@click.argument(
    "repo_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=".",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    default="repod.md",
    help="Output file path (default: repod.md)",
)
@click.option(
    "-i",
    "--ignore-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=".rpdignore",
    help="Path to ignore file (default: .rpdignore)",
)
@click.option(
    "-p",
    "--preamble",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to preamble file",
)
@click.option("--no-tree", is_flag=True, help="Disable tree structure in output")
def main(
    repo_path: Path,
    output: Path,
    ignore_file: Path,
    preamble: Path,
    no_tree: bool,
) -> None:
    """Repod: Dump repository contents to single markdown file."""
    try:
        config = DumperConfig(
            repo_path=repo_path,
            output_path=output,
            ignore_file=ignore_file,
            preamble_file=preamble,
            include_tree=not no_tree,
        )

        dumper = RepositoryDumper(config)
        dumper.dump()

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()


if __name__ == "__main__":
    main()

```

### src/repod/py.typed

```

```

