from g3.domain.message_tone import MessageTone
from g3.generate.client import OpenAIChat
from g3.generate.pr.prompts.creator import Creator as PromptCreator
from g3.generate.preview.cli import Presenter
from g3.github.client import Client as GHClient


class Creator:
    def __init__(self):
        self.prompt_creator = PromptCreator()
        self.openai = OpenAIChat()
        self.gh = GHClient()

    def create(self, tone: MessageTone, jira=None, include=None) -> None:
        prompt = self.prompt_creator.create(tone, jira, include)
        stream = self.openai.stream(prompt)

        reviewed_message, retry = Presenter.present(stream, "pr")
        while retry:
            stream = self.openai.stream(prompt)
            reviewed_message, retry = Presenter.present(stream, "commit")

        title = reviewed_message.split("\n")[1]
        description = reviewed_message.split(title)[1]
        pr = self.gh.create_pull_request(title, description)
        print(f"Opened PR: {pr.html_url}")
