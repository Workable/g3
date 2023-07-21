from g3.domain.message_tone import MessageTone
from g3.generate.client import OpenAIChat
from g3.generate.commit.prompts.creator import Creator as PromptCreator
from g3.generate.preview.cli import Presenter
from g3.git.client import commit


class Creator:
    def __init__(self):
        self.prompt_creator = PromptCreator()
        self.openai = OpenAIChat()

    def create(self, tone: MessageTone, jira=None, include=None) -> None:
        prompt = self.prompt_creator.create(tone, jira, include)

        message = self.openai.generate(prompt)
        reviewed_message, retry = Presenter.present(message, "commit")
        while retry:
            message = self.openai.generate(prompt)
            reviewed_message, retry = Presenter.present(message, "commit")

        commit(reviewed_message)
