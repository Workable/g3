from g3.domain.message_tone import MessageTone
from g3.generate.commit.prompts.creator import Creator as PromptCreator
from g3.generate.creator import Creator as MessageCreator
from g3.generate.preview.cli import Presenter
from g3.git.client import commit


class Creator(MessageCreator):
    def __init__(self):
        super().__init__()
        self.prompt_creator = PromptCreator()
        self.message_type = "commit"

    def create(self, tone: MessageTone, jira=None, include=None) -> None:
        prompt = self.prompt_creator.create(tone, jira, include)
        message = self.create_message(prompt, tone, jira, include)
        reviewed_message, retry = Presenter.present(message)
        while retry:
            self.create_message(prompt, tone, jira, include, True)
            message = self.openai.generate(prompt)
            reviewed_message, retry = Presenter.present(message)

        commit(reviewed_message)
