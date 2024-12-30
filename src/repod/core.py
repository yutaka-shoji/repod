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
