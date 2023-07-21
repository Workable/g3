from typing import Optional

from g3.domain.message_tone import MessageTone
from g3.generate.client import OpenAIChat
from g3.generate.pr.prompts.creator import Creator as PromptCreator
from g3.generate.preview.cli import Presenter
from g3.git.client import get_commit_messages
from g3.github.client import Client as GHClient
from g3.github.github_info import GithubInfo


class Creator:
    def __init__(self):
        self.prompt_creator = PromptCreator()
        self.openai = OpenAIChat()
        self.gh = GHClient()

    def create(self, tone: MessageTone, jira=None, include=None, edit: Optional[int] = None) -> None:
        if edit:
            pr = GHClient().get_pull_request(edit)
            commit_messages = []
            for commit in pr.get_commits():
                commit_messages.append(commit.commit.message)
            prompt = self.prompt_creator.create(tone, commit_messages, jira, include)
            stream = self.openai.stream(prompt)

            original_message = f"{pr.title}\n\n{pr.body}"

            reviewed_message, retry = Presenter.present_comparison(original_message, stream, "pr")
            while retry:
                stream = self.openai.stream(prompt)
                reviewed_message, retry = Presenter.present_comparison(original_message, stream, "pr")

            title = reviewed_message.partition("\n")[0]
            description = reviewed_message.split("\n", 1)[1]
            self.gh.update_pull_request(pr.number, title, description)
            print(f"Successfully updated PR: {pr.html_url}")
        else:
            commit_messages = get_commit_messages(GithubInfo().default_branch)
            prompt = self.prompt_creator.create(tone, commit_messages, jira, include)
            stream = self.openai.stream(prompt)

            reviewed_message, retry = Presenter.present(stream, "pr")
            while retry:
                stream = self.openai.stream(prompt)
                reviewed_message, retry = Presenter.present(stream, "pr")

            title = reviewed_message.split("\n")[1]
            description = reviewed_message.split(title)[1]
            pr = self.gh.create_pull_request(title, description)
            print(f"Opened PR: {pr.html_url}")
