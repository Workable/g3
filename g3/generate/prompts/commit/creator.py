import os

import openai

from g3.generate.prompts.commit.examples.ruby import ruby_sample
from g3.generate.prompts.commit.examples.node import node_sample
from g3.generate.prompts.commit.examples.python import python_sample


class Creator:

    def __init__(self, tone, jira, include):
        self.tone = tone
        self.jira = jira
        self.include = include
        self.ruby_sample = ruby_sample
        self.node_sample = node_sample
        self.python_sample = python_sample
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def create(self, code, stack: str = "python") -> str:
        sample = self.set_sample(stack)
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant creating commit messages for git commits in a software "
                           "engineering team based on their stashed git changes which will be provided to you."
                           "We defined a good commit message as one that explains what was changed, and if usefull, why"
                           " the change was made. Don't include the provided code in your response or the words commit "
                           "message. Be brief on your response using less than 7-10 words, use imperative and start "
                           "with a verb. The goal is to briefly complete a sentence which starts like 'This commit if "
                           "applied will:' but dont include this sentence in your response. "
                           "Whatever follows should be the commit message that you suggest. "
                           f"Include in your reponse the following: {self.include}. " if self.include else ""
                           f"Incorporate the following Jira ticket: {self.jira}. " if self.jira else ""
                           f"Use the following tone when creating the commit message: {self.tone}. " if self.tone else ""
                           "Your response should be in markdown format."

            },
            {
                "role": "user",
                "content": f"Please provide a commit message for the provided code. Code: ```{sample.get('code')}```"
            },
            {
                "role": "assistant",
                "content": sample.get("message")
            },
            {
                "role": "user",
                "content": f"Please provide a commit message for the provided code. Code: ```{code}```"
            }
        ]
        openai_response = openai.ChatCompletion.create(model="gpt-4", messages=messages, temperature=0)
        return openai_response['choices'][0]['message']['content']

    def set_sample(self, stack: str) -> dict:
        if stack == "ruby":
            return self.ruby_sample
        elif stack == "node":
            return self.node_sample
        else:
            return self.python_sample
