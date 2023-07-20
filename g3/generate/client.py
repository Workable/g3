from typing import Any, Dict, List

import openai
from g3.config import openai_config as config


class OpenAI:
    def __init__(self):
        openai.api_key = config.api_key
        if config.api_type:
            openai.api_key = config.api_type
        if config.api_base:
            openai.api_key = config.api_base
        if config.api_version:
            openai.api_key = config.api_version

    def generate(self, message: str, **kwargs: Any) -> str:
        kwargs = config.args | kwargs
        resp = openai.Completion.create(
            prompt=message,
            **kwargs,
        )
        return resp["choices"][0]["text"]


class OpenAIChat(OpenAI):
    def generate(self, message: List[Dict], **kwargs: Any) -> str:
        kwargs = config.args | kwargs
        resp = openai.ChatCompletion.create(
            messages=message,
            **kwargs,
        )
        return resp["choices"][0]["message"]["content"]
