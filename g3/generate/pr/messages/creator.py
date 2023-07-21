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
        message = self.openai.generate(prompt)

        reviewed_message, retry = Presenter.present(message, "pr")
        while retry:
            message = self.openai.generate(prompt)
            reviewed_message, retry = Presenter.present(message, "commit")

        title = reviewed_message.partition("\n")[0]
        description = reviewed_message.split("\n", 1)[1]
        pr = self.gh.open_pull_request(title, description)
        print(f"Opened PR: {pr.html_url}")
