from pydantic.main import BaseModel

from g3.services.github.client import Client


class GithubInfo(BaseModel):
    default_branch: str = ""

    def __init__(self):
        super().__init__()
        self.__post_init__()

    def __post_init__(self):
        client = Client()
        self.default_branch = client.repo.default_branch
