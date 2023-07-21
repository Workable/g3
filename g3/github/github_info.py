from pydantic.main import BaseModel

from g3.github.client import Client


class GithubInfo(BaseModel):
    def __init__(self):
        self.client = Client()
        self.__post_init__()

    def __post_init__(self):
        self.default_branch = self.client.repo.default_branch
