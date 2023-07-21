import signal
from typing import Annotated

import typer
from rich import print
from rich.panel import Panel
from rich.prompt import FloatPrompt, Prompt
from rich.text import Text

from g3.config import config
from g3.domain.message_tone import MessageTone
from g3.generate.commit.messages.creator import Creator as CommitMessageCreator
from g3.generate.pr.messages.creator import Creator as PRMessageCreator


def signal_handler(sig, frame):
    print("Ctrl+C pressed. Exiting...")
    exit(0)


signal.signal(signal.SIGINT, signal_handler)

app = typer.Typer()


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

    openai_api_type = Prompt.ask("OpenAI API type", choices=["open_ai", "azure"], default="open_ai")
    config.set("openai", "api_type", openai_api_type)
    if openai_api_type == "azure":
        openai_api_base = Prompt.ask("OpenAI API base")
        config.set("openai", "api_base", openai_api_base)
        openai_deployment_id = Prompt.ask("OpenAI deployment ID")
        config.set("openai", "deployment_id", openai_deployment_id)

    openai_model = Prompt.ask("OpenAI model", default="gpt-4-0613")
    config.set("openai", "model", openai_model)

    openai_temperature = FloatPrompt.ask("OpenAI temperature", default=0.0)
    config.set("openai", "temperature", str(openai_temperature))

    openai_api_version = Prompt.ask("OpenAI API version", default="latest")
    config.set("openai", "api_version", openai_api_version)

    tone = Prompt.ask("Default tone", choices=[t.value for t in MessageTone], default=MessageTone.FRIENDLY.value)
    config.set("message", "tone", tone)

    commit_description_max_words = Prompt.ask("Commit description max words", default=50)
    config.set("message", "commit_description_max_words", commit_description_max_words)

    pr_description_max_words = Prompt.ask("PR description max words", default=500)
    config.set("message", "pr_description_max_words", pr_description_max_words)

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
        raise NotImplementedError("The --edit option is not supported yet")
    if jira:
        typer.echo(f"Referencing Jira ticket: {jira}")
    if include:
        typer.echo(f"Including additional text:\n{include}")

    CommitMessageCreator().create(
        tone=tone,
        jira=jira,
        include=include,
    )


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
        raise NotImplementedError("The --edit option is not supported yet")
    if jira:
        typer.echo(f"Referencing Jira ticket: {jira}")
    if include:
        typer.echo(f"Including additional text:\n{include}")

    PRMessageCreator().create(
        tone=tone,
        jira=jira,
        include=include,
    )


if __name__ == "__main__":
    app()
