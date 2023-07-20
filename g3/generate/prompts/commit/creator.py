import os
import re

import openai

from g3.generate.prompts.commit.examples.node import node_sample
from g3.generate.prompts.commit.examples.python import python_sample
from g3.generate.prompts.commit.examples.ruby import ruby_sample
from g3.git.data import get_data_for_model as git
from g3.main import config

PY_PATTERN = re.compile(".*py")
JS_PATTERN = re.compile(".*js")
RB_PATTERN = re.compile(".*rb")


class Creator:
    def __init__(self):
        self.ruby_sample = ruby_sample
        self.node_sample = node_sample
        self.python_sample = python_sample
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def create(self, code, jira: str, include: str) -> list:
        code_data = git()
        system_messages = self.create_system_message(include, jira)
        # examples_messages = self.create_example_message(code_data)
        user_messages = self.create_user_message(code, code_data)
        return system_messages + user_messages

    def create_user_message(self, code, code_data) -> list:
        return [
            {
                "role": "user",
                "content": f"Please provide a commit message for the provided code. Code: ```{code}```."
                f"The code is from a git branch named {code_data.branch_name}. "
                f"The code is from a git repository named {code_data.repo_name}. "
                f"The code contains changes in the following files: {code_data.filenames}. ",
            }
        ]

    def create_system_message(self, include, jira) -> list:
        return [
            {
                "role": "system",
                "content": "You are a helpful assistant creating commit titles and commit descriptions for git commits "
                "in a software engineering team based on their stashed git changes which will be provided to you."
                "We defined a good commit title as one that explains what was changed."
                "The commit description if asked should contain what was changed and why the change was made."
                "Don't include the provided code in your response. "
                "Also, dont include in the response the words commit title, or commit description. The response "
                "will be directly used by git commit command. "
                "The goal for the commit title is to briefly complete a sentence which starts like 'This commit "
                "if applied will:' but dont include this sentence in your response. "
                "Be brief on your response about the commit title using less than 80 characters, use imperative"
                " and start with a verb. "
                "Whatever follows should be the commit title that you suggest. "
                "The commit description if asked, should be a few bullets which will contain short "
                "descriptions about the"
                f" changes using at most {config.commit_description_max_words} words. If the words "
                f"provided are"
                f"0 then you should not include a commit description."
                f'{f"Include in your response the following: {include} ."}'
                f'{f"Incorporate the following Jira ticket: {jira} ."}'
                f"Use the following tone when creating the commit message: {config.tone}. "
                "Your response should be in markdown format and you should split each sentence to a "
                "new line.",
            }
        ]

    def create_example_message(self, code_data) -> list:
        code_stack = self.get_code_stack(code_data)
        sample = self.set_sample(code_stack)
        if not sample:
            return []

        return [
            {
                "role": "user",
                "content": f"Please provide a commit message for the provided code. Code: ```{sample.get('code')}```"
                f'{f"Dont include a commit description. Provide just a commit title." if config.commit_description_max_words == 0 else ""}',
            },
            {"role": "assistant", "content": sample.get("message")},
        ]

    def get_code_stack(self, code_data) -> str:
        py_sum = sum(1 for x in code_data.filenames if PY_PATTERN.match(x))
        js_sum = sum(1 for x in code_data.filenames if JS_PATTERN.match(x))
        rb_sum = sum(1 for x in code_data.filenames if RB_PATTERN.match(x))
        return self.most_files(py_sum, js_sum, rb_sum)

    def most_files(self, py_sum, js_sum, rb_sum):
        max_value, name = py_sum, "python"
        if js_sum > max_value:
            max_value, name = js_sum, "node"
        if rb_sum > max_value:
            max_value, name = rb_sum, "ruby"
            if js_sum > rb_sum:
                max_value, name = js_sum, "node"
        return name

    def set_sample(self, stack: str) -> dict | None:
        if stack == "ruby":
            return self.ruby_sample
        elif stack == "node":
            return self.node_sample
        elif stack == "python":
            return self.python_sample

        return None
