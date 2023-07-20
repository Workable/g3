from typing import Optional

from pydantic import BaseModel

from g3.git.shell import Shell


class GitInfo(BaseModel):
    repo_owner: Optional[str] = None
    repo: Optional[str] = None
    branch: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__post_init__()

    def __post_init__(self):
        sh = Shell()
        assert sh.is_git()

        self.branch = sh.git("rev-parse", "--abbrev-ref", "HEAD")
        repo_info = sh.git("config", "--get", "remote.origin.url").split("/")
        self.repo = repo_info[-1]
        self.repo_owner = repo_info[-2]
