from typing import Optional

from g3.domain.message_tone import MessageTone
from g3.generate.client import OpenAIChat
from g3.generate.pr.prompts.creator import Creator as PromptCreator
from g3.generate.preview.cli import Presenter
from g3.git.client import get_commit_messages
from g3.github.client import Client as GHClient


class Creator:
    def __init__(self, pr_id: Optional[int] = None):
        self.pr = GHClient().get_pull_request(pr_id)
        self.prompt_creator = PromptCreator()
        self.openai = OpenAIChat()
        self.gh = GHClient()

    def create(self, tone: MessageTone, jira=None, include=None) -> None:
        if self.pr:
            commit_messages = []
            for commit in self.pr.get_commits():
                commit_messages.append(commit.commit.message)
            prompt = self.prompt_creator.create(tone, commit_messages, jira, include)
            stream = self.openai.generate(prompt)

            original_message = f"{self.pr.title}\n\n{self.pr.body}"

            reviewed_message, retry = Presenter.present_comparison(original_message, stream, "pr")
            while retry:
                stream = self.openai.generate(prompt)
                reviewed_message, retry = Presenter.present_comparison(original_message, stream, "pr")

            title = reviewed_message.partition("\n")[0]
            description = reviewed_message.split("\n", 1)[1]
            pr = self.gh.update_pull_request(self.pr.id, title, description)
            print(f"Opened PR: {pr.html_url}")
        else:
            commit_messages = get_commit_messages("main")
            prompt = self.prompt_creator.create(tone, commit_messages, jira, include)
            stream = self.openai.generate(prompt)

            reviewed_message, retry = Presenter.present(stream, "pr")
            while retry:
                stream = self.openai.generate(prompt)
                reviewed_message, retry = Presenter.present(stream, "pr")

            title = reviewed_message.split("\n")[1]
            description = reviewed_message.split(title)[1]
            pr = self.gh.create_pull_request(title, description)
            print(f"Opened PR: {pr.html_url}")
