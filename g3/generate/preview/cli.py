from typing import Tuple

import editor
import inquirer
from rich.console import Console
from rich.markdown import Markdown

options = ["Submit", "Edit", "Regenerate", "Cancel"]


class Presenter:
    @staticmethod
    def present(message: str) -> Tuple[str, bool]:
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
        if selection == "Cancel":
            exit(0)
        elif selection == "Edit":
            message = editor.edit(contents=message).decode()
        elif selection == "Regenerate":
            return message, True

        return message, False
