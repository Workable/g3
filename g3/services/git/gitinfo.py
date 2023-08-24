from typing import List, Optional

import tiktoken
from github.Commit import Commit
from pydantic import BaseModel

from g3.config import config
from g3.services.git.client import (
    get_branch_name,
    get_diff_names,
    get_diffs,
    get_repo_info,
)


class Diff(BaseModel):
    filename: str
    patch: str


class GitInfo(BaseModel):
    commit: Optional[Commit] = None

    repo_name: str = ""
    repo_owner: str = ""
    branch: str = ""
    filenames: List[str] = []
    diffs: List[Diff] = []

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo_name, self.repo_owner = get_repo_info()
        self.branch = get_branch_name()
        if self.commit:
            # Init diffs/filenames from commit
            self.filenames = [file.filename for file in self.commit.files]
            self.diffs = [Diff(filename=file.filename, patch=file.patch) for file in self.commit.files]
        else:
            # Init diffs/filenames from stage
            self.filenames = get_diff_names()
            self.diffs = [Diff(filename=filename, patch=get_diffs(filename)) for filename in self.filenames]

    @property
    def raw_diffs(self) -> str:
        return "\n".join([diff.patch for diff in self.diffs or []])

    @property
    def tokens_of_diffs(self) -> Optional[int]:
        if not self.diffs:
            return None

        encoding = tiktoken.encoding_for_model(config.model)
        return sum(len(encoding.encode(diff.patch + diff.filename)) for diff in self.diffs)
