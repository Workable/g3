from typing import Generator, Tuple

import editor
import inquirer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

options = ["Submit", "Edit", "Regenerate", "Cancel"]
commit_comparison_options = ["Regenerate", "Copy to clipboard", "Cancel"]
pr_comparison_options = ["Submit", "Edit", "Regenerate", "Cancel"]


class Presenter:
    @staticmethod
    def present(stream: Generator, type: str) -> Tuple[str, bool]:
        if type not in ("pr", "commit"):
            raise ValueError("Invalid message type")

        print(f"\n[+] Generated {type} message:\n")
        console = Console()
        message = ""
        with Live(console=console) as live:
            for chunk in stream:
                message += chunk
                md = Markdown(message, "github-dark")
                live.update(md)
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
    def present_comparison(original_message: str, stream: Generator, type: str) -> Tuple[str, bool]:
        if type not in ("pr", "commit"):
            raise ValueError("Invalid message type")

        console = Console()

        console.print("\n[-] Original message:\n")
        console.print(Markdown(original_message, "github-dark"))

        message = ""
        console.print("\n[+] Generated message:\n")
        with Live(console=console) as live:
            for chunk in stream:
                message += chunk
                md = Markdown(message, "github-dark")
                live.update(md)

        questions = [
            inquirer.List(
                "selection",
                message="Action",
                choices=commit_comparison_options if type == "commit" else pr_comparison_options,
            )
        ]

        selection = inquirer.prompt(questions)["selection"]
        if selection == "Cancel":
            exit(0)
        elif selection == "Regenerate":
            print("Regenerating..")
            return message, True
        elif selection == "Edit":
            message = editor.edit(contents=message).decode()

        return message, False
