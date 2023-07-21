from typing import Tuple

import editor
import inquirer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

options = ["Submit", "Edit", "Regenerate", "Cancel"]
comparison_options = ["Regenerate", "Copy to clipboard", "Cancel"]


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

    @staticmethod
    def present_comparison(original_message: str, generated_message: str, type: str) -> Tuple[str, bool]:
        if type not in ("pr", "commit"):
            raise ValueError("Invalid message type")

        console = Console()
        console.print(
            Panel(
                Markdown(original_message, "github-dark"),
                title="Original message",
                padding=1,
            )
        )
        console.print(
            Panel(
                Markdown(generated_message, "github-dark"),
                title="Generated message",
                style="blue bold",
                padding=1,
            )
        )

        questions = [
            inquirer.List(
                "selection",
                message="Action",
                choices=comparison_options,
            )
        ]

        selection = inquirer.prompt(questions)["selection"]
        if selection == "Cancel":
            exit(0)
        elif selection == "Regenerate":
            print("Regenerating..")
            return generated_message, True

        return generated_message, False
