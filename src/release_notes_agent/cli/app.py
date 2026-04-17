"""Typer CLI for release-notes-agent."""

from __future__ import annotations

from datetime import date
from typing import Annotated

import typer

from release_notes_agent.models.schemas import GenerateRequest
from release_notes_agent.pipeline import generate_release_notes

app = typer.Typer(add_completion=False, help="release-notes-agent CLI")


@app.command()
def generate(
    srs: Annotated[
        list[str],
        typer.Option("--srs", help="SRS file or folder. Repeat for multiple."),
    ],
    sample: Annotated[str, typer.Option("--sample", help="Sample release-notes file.")],
    product: Annotated[str, typer.Option("--product", help="Product name.")],
    version: Annotated[str, typer.Option("--version", help="Release version string.")],
    release_date: Annotated[
        str, typer.Option("--date", help="Release date (YYYY-MM-DD).")
    ],
    audience: Annotated[
        str, typer.Option("--audience", help="internal | external | both")
    ] = "both",
    output_format: Annotated[
        str, typer.Option("--format", help="md | html | docx | pdf")
    ] = "md",
    out: Annotated[
        str, typer.Option("--out", help="Output file path.")
    ] = "release_notes.md",
) -> None:
    """Generate release notes from SRS files."""
    req = GenerateRequest(
        srs_paths=list(srs),
        sample_path=sample,
        product_name=product,
        version=version,
        release_date=date.fromisoformat(release_date),
        audience=audience,  # type: ignore[arg-type]
        output_format=output_format,  # type: ignore[arg-type]
        output_path=out,
    )
    result = generate_release_notes(req)
    typer.echo("Wrote:")
    for path in result.output_paths:
        typer.echo(f"  {path}")


@app.command()
def chat() -> None:
    """Interactive chat REPL."""
    from release_notes_agent.agents.orchestrator import create_orchestrator

    agent = create_orchestrator()
    typer.echo("release-notes-agent — chat (type 'exit' to quit)")
    typer.echo("-" * 60)
    while True:
        try:
            query = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            typer.echo("\nGoodbye!")
            break
        if not query or query.lower() in ("exit", "quit"):
            typer.echo("Goodbye!")
            break
        typer.echo(f"\nAgent: {agent(query)}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
