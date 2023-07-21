from abc import ABC, abstractmethod

from rich.progress import Progress, SpinnerColumn, TextColumn

from g3.domain.message_tone import MessageTone
from g3.generate.client import OpenAIChat


class Creator(ABC):
    def __init__(self):
        self.openai = OpenAIChat()
        self.message_type = None

    @abstractmethod
    def create(self, tone: MessageTone, jira=None, include=None) -> None:
        raise NotImplementedError

    def create_message(self, prompt: list[dict], tone: MessageTone, jira=None, include=None, retry=False) -> str:
        prefix = "Regenerat" if retry else "Generat"
        log_msg = self.create_log_msg(tone, jira, include)
        print()
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            id = progress.add_task(total=None, description=f"{prefix}ing {log_msg}..")
            message = self.openai.generate(prompt)
            progress.update(task_id=id, description=f"{prefix}ed {log_msg}:")
            progress.stop()
            print()

        return message

    def create_log_msg(self, tone: MessageTone, jira=None, include=None) -> str:
        log = f"{self.message_type} message with {tone.value} tone"
        if jira and include:
            log += f" referencing Jira ticket {jira} and including '{include}' phrase"
        elif jira:
            log += f" referencing Jira ticket {jira}"
        elif include:
            log += f" including '{include}' phrase"

        return log
