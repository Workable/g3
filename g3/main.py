from enum import Enum
from typing import Annotated

import typer

app = typer.Typer()


class MessageTone(str, Enum):
    PROFESSIONAL = "professional"
    PERSONAL = "personal"
    FRIENDLY = "friendly"
    FUNNY = "funny"


@app.command()
def commit(
    tone: Annotated[
        MessageTone,
        typer.Option("--tone", "-t", help="The tone of voice that will be used to generate the commit message"),
    ] = MessageTone.FRIENDLY,
    jira: Annotated[
        str, typer.Option("--jira", "-j", help="A Jira ticket number that should be referenced in the commit message")
    ] = "",
    include: Annotated[
        str,
        typer.Option("--include", "-i", help="Text content that should be appended to the commit message"),
    ] = "",
    edit: Annotated[
        str,
        typer.Option(
            "--edit", "-e", help="A commit hash that points to a commit which will be used instead of staged changes"
        ),
    ] = "",
) -> None:
    """Generate a new commit message for staged changes"""
    typer.echo(f"Generating commit message with {tone.value} tone.")
    if edit:
        typer.echo(f"For existing commit: {edit}")
    if jira:
        typer.echo(f"Referencing Jira ticket: {jira}")
    if include:
        typer.echo(f"Including additional text:\n{include}")


@app.command()
def pr(
    tone: Annotated[
        MessageTone,
        typer.Option("--tone", "-t", help="The tone of voice that will be used to generate the PR description"),
    ] = MessageTone.FRIENDLY,
    jira: Annotated[
        str, typer.Option("--jira", "-j", help="A Jira ticket number that should be referenced in the PR description")
    ] = "",
    include: Annotated[
        str,
        typer.Option("--include", "-i", help="Text content that should be appended to the PR description"),
    ] = "",
    edit: Annotated[
        str,
        typer.Option(
            "--edit", "-e", help="A hash that points to a previous PR which will be used instead of the current branch"
        ),
    ] = "",
) -> None:
    """Generate a new pull request description for the current branch"""
    typer.echo(f"Generating PR description with {tone.value} tone.")
    if edit:
        typer.echo(f"For previous PR: {edit}")
    if jira:
        typer.echo(f"Referencing Jira ticket: {jira}")
    if include:
        typer.echo(f"Including additional text:\n{include}")


if __name__ == "__main__":
    app()
