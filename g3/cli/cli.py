
import inquirer
import time
import editor
from rich.progress import Progress, SpinnerColumn, TextColumn

def display_selection(messages, type, field="message"):
    options = [
        "[Edit]",
        "[Regenerate]",
    ]
    questions = [inquirer.List('selection',
                                message=f"Choose a {type} {field}",
                                choices=messages+options,
                                )]

    selection = inquirer.prompt(questions)["selection"]

    if selection == "[Edit]":
        questions = [inquirer.List('selection',
                                message=f"Choose a {type} {field} to edit",
                                choices=messages,
                                )]
        selection = inquirer.prompt(questions)["selection"]
        selection = editor.edit(contents=selection)
        print(selection.decode())
    elif selection == "[Regenerate]":
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Regenerating...", total=None)
            time.sleep(5)
        # Placeholder for AI

    return selection
