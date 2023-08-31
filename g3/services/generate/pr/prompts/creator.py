from typing import Optional

from g3.domain.message_tone import MessageTone
from g3.main import config
from g3.services.generate.pr.prompts.template import pr_template
from g3.services.git import git_info


class Creator:
    def create(
        self, commit_messages, tone: MessageTone, jira: Optional[str] = None, include: Optional[str] = None
    ) -> list:
        system_messages = self.create_system_messages(tone, jira, include)
        user_messages = self.create_user_messages(commit_messages)

        return system_messages + user_messages

    def create_user_messages(self, commit_messages) -> list:
        content = f"""Please provide a pull request description for the provided commit messages.
 Commits: ```{commit_messages}```. The commit messages are form a git branch named {git_info.branch}.
 The commit messages are from a git repository named {git_info.repo_name}."""

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
 in order to approve the pull request or ask for the needed changes. If Jira tickets are provided then include them in
 the pull request description. Do not use the branch or the repository name. Use the following tone when creating
 the pull request message: {tone}."""
        if include:
            content += f" Include in your response the following: {include}"
        if jira:
            content += f" Include in the end of your response the following Jira ticket: ```{jira}```."
        content += (
            f" Your response should be in Github markdown syntax format and comply on the following template:"
            f"```{pr_template}```."
        )

        return [{"role": "system", "content": content.replace("\n", "")}]
