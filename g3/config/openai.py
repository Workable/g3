from typing import Optional

from pydantic import BaseSettings, Extra

from g3.utils.dictionary import without_nulls


class OpenAIConfig(BaseSettings):
    api_key: str = ""
    api_type: Optional[str] = "openai"
    api_version: Optional[str] = None
    api_base: Optional[str] = None
    deployment_id: Optional[str] = None
    model: str = "gpt-4"
    temperature: float = 0

    class Config:
        extra = Extra.ignore
        env_prefix = "OPENAI_"

    @property
    def args(self):
        return without_nulls(
            {
                "model": self.model,
                "temperature": self.temperature,
                "deployment_id": self.deployment_id,
            }
        )

    @staticmethod
    def create():
        from g3.config import config

        return OpenAIConfig(
            api_key=config.openai_key,
            api_type=config.api_type,
            api_version=config.api_version if config.api_version != "latest" else None,
            api_base=config.api_base,
            deployment_id=config.deployment_id,
            model=config.model,
            temperature=config.temperature,
        )
