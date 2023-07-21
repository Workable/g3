from typing import Optional

from pydantic.main import BaseModel

from g3.github.client import Client


class GithubInfo(BaseModel):
    default_branch: Optional[str] = None

    def __init__(self):
        super().__init__()
        self.__post_init__()

    def __post_init__(self):
        client = Client()
        self.default_branch = client.repo.default_branch
