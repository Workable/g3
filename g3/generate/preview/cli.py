import time

import editor
import inquirer
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn


def display_selection(message, type, field="message"):
    options = [
        "Submit",
        "Edit",
        "Regenerate",
    ]

    print(f"\n[+] Generated {type} {field}:\n")
    console = Console()
    md = Markdown(message, "github-dark")
    console.print(md)

    print()
    questions = [
        inquirer.List(
            "selection",
            message="Action",
            choices=options,
        )
    ]

    selection = inquirer.prompt(questions)["selection"]

    if selection == "Edit":
        message = editor.edit(contents=message).decode()
    elif selection == "Regenerate":
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Regenerating...", total=None)
            time.sleep(5)
        # Placeholder for AI

    return message
