from typing import Optional

import pyperclip
from rich import print

from g3.domain.message_tone import MessageTone
from g3.generate.client import OpenAIChat
from g3.generate.commit.prompts.creator import Creator as PromptCreator
from g3.generate.preview.cli import Presenter
from g3.git.client import commit
from g3.github.client import Client


class Creator:
    def __init__(self, commit_hash: Optional[str] = None):
        self.commit = Client().get_commit(commit_hash=commit_hash)
        self.prompt_creator = PromptCreator(commit=self.commit)
        self.openai = OpenAIChat()

    def create(self, tone: MessageTone, jira=None, include=None) -> None:
        prompt = self.prompt_creator.create(tone, jira, include)

        stream = self.openai.generate(prompt)
        if self.commit:
            original_message = self.commit.commit.message
            reviewed_message, retry = Presenter.present_comparison(original_message, stream, "commit")
            while retry:
                stream = self.openai.generate(prompt)
                reviewed_message, retry = Presenter.present_comparison(original_message, stream, "commit")

            pyperclip.copy(reviewed_message)
            print("✅ Generated message has been copied to clipboard.")
        else:
            reviewed_message, retry = Presenter.present(stream, "commit")
            while retry:
                stream = self.openai.generate(prompt)
                reviewed_message, retry = Presenter.present(stream, "commit")

            commit(reviewed_message)
