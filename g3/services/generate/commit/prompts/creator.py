import re
from typing import Optional

from g3.domain.message_tone import MessageTone
from g3.main import config
from g3.services.git.gitinfo import GitInfo


def calculate_token_limit() -> int:
    """
    The limit is 5000 tokens for 8k model and 13000 tokens for 16k model
    """
    if re.search("16k", config.model):
        return 13000

    return 5000


class Creator:
    def create(
        self, tone: MessageTone, jira: Optional[str] = None, include: Optional[str] = None, edit: Optional[str] = None
    ) -> list:
        from g3.services.git.gitinfo import GitInfo

        git_info = GitInfo(commit=edit)
        if git_info.tokens_of_diffs and git_info.tokens_of_diffs > calculate_token_limit():
            print(
                f"Too many tokens in the git diff.\n"
                f"The limit is {calculate_token_limit()} and the diff has {git_info.tokens_of_diffs} tokens\n"
                f"As a suggestion please split your changes in multiple commits."
            )
            exit(1)

        system_messages = self.create_system_messages(tone, jira, include)
        user_messages = self.create_user_messages(git_info)

        return system_messages + user_messages

    def create_user_messages(self, git_info: GitInfo) -> list:
        content = f"""
 Please provide a commit message for the provided code. Code: ```{git_info.raw_diffs}```.
 The code is from a git branch named {git_info.branch}.
 The code is from a git repository named {git_info.repo_name}.
 The code contains changes in the following files: {git_info.filenames}."""

        return [
            {
                "role": "user",
                "content": content.replace("\n", ""),
            }
        ]

    def create_system_messages(
        self, tone: MessageTone, jira: Optional[str] = None, include: Optional[str] = None
    ) -> list:
        content = f"""You are a helpful assistant creating commit titles and commit descriptions for git commits in a
 software engineering team based on their stashed git changes which will be provided to you. We defined a good commit
 title as one that explains what was changed. The commit description if asked should contain what was changed and why
 the change was made. Don't include the provided code in your response. Also, dont include in the response the words
 commit title, or commit description. The response will be directly used by git commit command. The goal for the commit
 title is to briefly complete a sentence which starts like 'This commit if applied will:' but dont include this sentence
 in your response. Be brief on your response about the commit title using less than 80 characters, use imperative and
 start with a verb. Whatever follows should be the commit title that you suggest. The commit description if asked,
 should be a few bullets which will contain short descriptions about the changes using at most
 {config.commit_description_max_words} words. If the words provided are 0 then you should not include a commit
 description. Do not use the branch or the repository name. Use the following tone when creating the commit message:
 {tone.value}."""
        if include:
            content += f" Include in your response the following: ```{include}```."
        if jira:
            content += f" Include in the end of your response the following Jira ticket: ```{jira}```."
        content += " Your response should be in markdown format and you should split each sentence to a new line."

        return [{"role": "system", "content": content.replace("\n", "")}]
