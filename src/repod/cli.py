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
