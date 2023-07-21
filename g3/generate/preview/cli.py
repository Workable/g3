from typing import Tuple

import editor
import inquirer
from rich.console import Console
from rich.markdown import Markdown

options = ["Submit", "Edit", "Regenerate", "Cancel"]


class Presenter:
    @staticmethod
    def present(message: str, type: str) -> Tuple[str, bool]:
        if type not in ("pr", "commit"):
            raise ValueError("Invalid message type")

        print(f"\n[+] Generated {type} message:\n")
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
            print("Regenerating..")
            return message, True

        return message, False
