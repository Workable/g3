from typing import List, Optional

from pydantic import BaseModel

from g3.git.diff import Diff, get_filenames, get_files_changed
from g3.git.shell import Shell


class ModelData(BaseModel):
    filenames: List[str]
    diffs: List[Diff]
    repo_name: str
    branch_name: str


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

    def get_data_for_model(self) -> ModelData:
        sh = Shell()
        assert sh.is_git()

        return ModelData(
            filenames=get_filenames(sh),
            diffs=[diff for diff in get_files_changed(sh)],
            repo_name=sh.repo_name,
            branch_name=sh.branch_name,
        )
