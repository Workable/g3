import re
from typing import Optional

from github.Commit import Commit

from g3.domain.message_tone import MessageTone
from g3.generate.commit.prompts.examples.node import node_sample
from g3.generate.commit.prompts.examples.python import python_sample
from g3.generate.commit.prompts.examples.ruby import ruby_sample
from g3.git.gitinfo import GitInfo
from g3.main import config

PY_PATTERN = re.compile(".*py")
JS_PATTERN = re.compile(".*js")
TS_PATTERN = re.compile(".*ts")
RB_PATTERN = re.compile(".*rb")


class Creator:
    def __init__(self, commit: Optional[Commit] = None):
        self.ruby_sample = ruby_sample()
        self.node_sample = node_sample()
        self.python_sample = python_sample()
        self.git_info = GitInfo(commit=commit)

    def create(self, tone: MessageTone, jira: Optional[str] = None, include: Optional[str] = None) -> list:
        system_messages = self.create_system_messages(tone, jira, include)

        # return system_messages + self.examples_messages + self.user_messages
        return system_messages + self.user_messages

    @property
    def user_messages(self) -> list:
        content = f"""
 Please provide a commit message for the provided code. Code: ```{self.git_info.raw_diffs}```.
 The code is from a git branch named {self.git_info.branch}.
 The code is from a git repository named {self.git_info.repo}.
 The code contains changes in the following files: {self.git_info.filenames}."""

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
 description. Do not use the branch name in the commit description. Use the following tone when creating the commit
 message: {tone.value}."""
        if include:
            content += f" Include in your response the following: ```{include}```."
        if jira:
            content += f" Incorporate the following Jira ticket: ```{jira}```."
        content += " Your response should be in markdown format and you should split each sentence to a new line."

        return [{"role": "system", "content": content.replace("\n", "")}]

    @property
    def example_messages(self) -> list:
        tech_stack = self.find_tech_stack()
        sample = self.get_sample(tech_stack)
        if not sample:
            return []

        return [
            {
                "role": "user",
                "content": f"Please provide a commit message for the provided code. Code: ```{sample.get('code')}```",
            },
            {"role": "assistant", "content": sample.get("message")},
        ]

    def find_tech_stack(self) -> str:
        if not self.git_info.filenames:
            return ""

        py_sum = sum(True for x in self.git_info.filenames if PY_PATTERN.match(x))
        js_sum = sum(True for x in self.git_info.filenames if JS_PATTERN.match(x) or TS_PATTERN.match(x))
        rb_sum = sum(True for x in self.git_info.filenames if RB_PATTERN.match(x))

        return self.most_files(py_sum, js_sum, rb_sum)

    def most_files(self, py_sum: int, js_sum: int, rb_sum: int):
        max_value, name = py_sum, "python"
        if js_sum > max_value:
            max_value, name = js_sum, "node"
        if rb_sum > max_value:
            max_value, name = rb_sum, "ruby"

        return name

    def get_sample(self, stack: str) -> dict | None:
        if stack == "ruby":
            return self.ruby_sample
        elif stack == "node":
            return self.node_sample
        elif stack == "python":
            return self.python_sample

        return None
