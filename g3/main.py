from enum import Enum
from typing import Annotated

import typer
from g3.config import config
from rich import print
from rich.panel import Panel
from rich.prompt import FloatPrompt, Prompt
from rich.text import Text

app = typer.Typer()


class MessageTone(str, Enum):
    PROFESSIONAL = "professional"
    PERSONAL = "personal"
    FRIENDLY = "friendly"
    FUNNY = "funny"


@app.callback()
def callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand == "configure":
        return

    if not config.has_been_configured():
        print(
            Panel(
                Text("g3 has not been configured yet. Run `g3 configure` to get started.", justify="center"),
                title="🚨 Warning",
                style="red bold",
                padding=1,
            )
        )
        raise typer.Exit()


@app.command()
def configure() -> None:
    """Configure G3 tool by providing credentials and preferences"""
    print(
            Panel(
                Text("Welcome to g3! Please provide the following information to get started. ", justify="center"),
                title="👋 Hello there!",
                style="blue bold",
                padding=1,
            )
        )

    github_token = Prompt.ask("Your GitHub token")
    config.set("credentials", "github_token", github_token)

    openai_key = Prompt.ask("Your OpenAI key")
    config.set("credentials", "openai_key", openai_key)

    openai_api_type = Prompt.ask("OpenAI API type", choices=["openai", "azure"], default="openai")
    config.set("openai", "api_type", openai_api_type)
    if openai_api_type == "azure":
        openai_api_base = Prompt.ask("OpenAI API base")
        config.set("openai", "api_base", openai_api_base)
        openai_deployment_id = Prompt.ask("OpenAI deployment ID")
        config.set("openai", "deployment_id", openai_deployment_id)

    openai_model = Prompt.ask("OpenAI model", default="gpt-4")
    config.set("openai", "model", openai_model)

    openai_temperature = FloatPrompt.ask("OpenAI temperature", default=0.0)
    config.set("openai", "temperature", str(openai_temperature))

    openai_api_version = Prompt.ask("OpenAI API version", default="latest")
    config.set("openai", "api_version", openai_api_version)

    tone = Prompt.ask("Default tone", choices=[t.value for t in MessageTone], default=MessageTone.FRIENDLY.value)
    config.set("message", "tone", tone)

    config.save_config()

    typer.echo(f"✅ Config file located at: {config.config_file}")


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
