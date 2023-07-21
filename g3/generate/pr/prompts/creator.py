from typing import Optional

from g3.domain.message_tone import MessageTone
from g3.generate.pr.prompts.template import pr_template
from g3.git.client import get_commit_messages
from g3.git.gitinfo import GitInfo
from g3.github.github_info import GithubInfo
from g3.main import config


class Creator:
    def __init__(self):
        self.git_info = GitInfo()
        self.github_info = GithubInfo()
        self.commit_messages: list[str] = get_commit_messages(self.github_info.default_branch)

    def create(self, tone: MessageTone, jira: Optional[str] = None, include: Optional[str] = None) -> list:
        system_messages = self.create_system_messages(tone, jira, include)
        return system_messages + self.user_messages

    @property
    def user_messages(self) -> list:
        content = f"""Please provide a pull request description for the provided commit messages.
 Commits: ```{self.commit_messages}```.
 The commit messages are form a git branch named {self.git_info.branch}.
 The commit messages are from a git repository named {self.git_info.repo}."""

        return [
            {
                "role": "user",
                "content": content.replace("\n", ""),
            }
        ]

    def create_system_messages(
        self, tone: MessageTone, jira: Optional[str] = None, include: Optional[str] = None
    ) -> list:
        content = f"""You are a helpful assistant creating Pull Request titles and descriptions for a software
 engineering team. The pull request title and description should be created from a commit message or a
 series of commit messages that will be provided. A commit message, is a message which explains briefly
 what was changed in this commit. A pull request is a github event that takes place in software development
 when a contributor is ready to begin the process of merging new code changes with the main project
 repository. The pull request contains a description of what changed and why it changed.
 The pull request's title should be a sentence containing a title summing up the provided commits.
 Leave an new empty line always after the title. The pull reuqest's description should be under
 {config.pr_description_max_words} words in total and it should be helpful to the reader in order to
 understand the changes made. The reader of the pull request description needs to understand the changes
 in order to approve the pull request or ask for the needed changes. If the commit messages have referenced
 jira tickets, then include them in the pull request description too, but not in the title. Also, if the user
 provides any additional jira tickets, then include them in the pull request description too.
 Put the jira tickets in bullet points using the template provided.
 Use the following tone when creating the pull request
 message: {tone}.
 {pr_template}"""
        if include:
            content += f" Include in your response the following: ```{include}```."
        if jira:
            content += f" Incorporate the following Jira ticket: ```{jira}```."
        content += (
            "Your response should be in Github markdown syntax format and you should split each "
            "sentence to a new line."
        )

        return [{"role": "system", "content": content.replace("\n", "")}]
