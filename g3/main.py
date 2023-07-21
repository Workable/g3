import signal
from typing import Annotated

import inquirer
import typer
from rich import print
from rich.panel import Panel
from rich.text import Text

from g3.config import config
from g3.config.handler import Defaults
from g3.domain.message_tone import MessageTone
from g3.generate.commit.messages.creator import Creator as CommitMessageCreator
from g3.generate.pr.messages.creator import Creator as PRMessageCreator


def signal_handler(sig, frame):
    print("Ctrl+C pressed. Exiting...")
    exit(0)


signal.signal(signal.SIGINT, signal_handler)

app = typer.Typer(pretty_exceptions_enable=False)


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
    defaults = Defaults(config)
    questions = [
        inquirer.Text("github_token", message="Your GitHub token", default=defaults.github_token),
        inquirer.Text("openai_key", message="Your OpenAI key", default=defaults.openai_key),
        inquirer.List(
            "openai_api_type", message="OpenAI API type", choices=["open_ai", "azure"], default=defaults.api_type
        ),
        inquirer.Text(
            "openai_api_base",
            message="OpenAI API base",
            ignore=lambda answers: answers["openai_api_type"] == "open_ai",
            default=defaults.api_base,
        ),
        inquirer.Text(
            "openai_deployment_id",
            message="OpenAI deployment ID",
            ignore=lambda answers: answers["openai_api_type"] == "open_ai",
            default=defaults.deployment_id,
        ),
        inquirer.Text("openai_model", message="OpenAI model", default=defaults.model),
        inquirer.Text("openai_temperature", message="OpenAI temperature", default=defaults.temperature),
        inquirer.Text("openai_api_version", message="OpenAI API version", default=defaults.api_version),
        inquirer.List("tone", message="Default tone", choices=[t.value for t in MessageTone], default=defaults.tone),
        inquirer.Text(
            "commit_description_max_words",
            message="Commit description max words",
            default=defaults.commit_description_max_words,
        ),
        inquirer.Text(
            "pr_description_max_words", message="PR description max words", default=defaults.pr_description_max_words
        ),
    ]
    answers = inquirer.prompt(questions)

    config.set("credentials", "github_token", answers["github_token"])
    config.set("credentials", "openai_key", answers["openai_key"])
    config.set("openai", "api_type", answers["openai_api_type"])
    if answers["openai_api_type"] == "azure":
        config.set("openai", "api_base", answers["openai_api_base"])
        config.set("openai", "deployment_id", answers["openai_deployment_id"])
    config.set("openai", "model", answers["openai_model"])
    config.set("openai", "temperature", answers["openai_temperature"])
    config.set("openai", "api_version", answers["openai_api_version"])
    config.set("message", "tone", answers["tone"])
    config.set("message", "commit_description_max_words", answers["commit_description_max_words"])
    config.set("message", "pr_description_max_words", answers["pr_description_max_words"])

    config.save_config()
    print(f"✅ Config file saved at: {config.config_file}")


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
    typer.echo(f"Generating commit message with {tone.value} tone..")
    if edit:
        typer.echo(f"For existing commit: {edit}")
    if jira:
        typer.echo(f"Referencing Jira ticket: {jira}")
    if include:
        typer.echo(f"Including additional text:\n{include}")

    CommitMessageCreator(commit_hash=edit).create(
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
    typer.echo(f"Generating PR description with {tone.value} tone..")
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
