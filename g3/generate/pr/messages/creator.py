from g3.generate.commit.prompts.creator import Creator as PromptCreator
from g3.generate.creator import Creator as MessageCreator
from g3.generate.preview.cli import Presenter
from g3.github.client import Client as GHClient
from g3.main import MessageTone


class Creator(MessageCreator):
    def __init__(self):
        super().__init__()
        self.prompt_creator = PromptCreator()
        self.gh = GHClient()
        self.message_type = "PR"

    def create(self, tone: MessageTone, jira=None, include=None) -> None:
        prompt = self.prompt_creator.create(tone, jira, include)
        message = self.create_message(prompt, tone, jira, include)
        reviewed_message, retry = Presenter.present(message)
        while retry:
            message = self.create_message(prompt, tone, jira, include)
            reviewed_message, retry = Presenter.present(message)

        title = reviewed_message.partition("\n")[0]
        description = reviewed_message.split("\n", 1)[1]
        pr = self.gh.open_pull_request(title, description)
        print(f"Opened PR: {pr.html_url}")
