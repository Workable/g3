from enum import Enum
from typing import List, Optional

import tiktoken
from pydantic import BaseModel

from g3.config import config
from g3.git.diff import Diff, get_filenames, get_files_changed
from g3.git.shell import Shell


# Make an enum with git protocol options
class GitProtocol(str, Enum):
    HTTPS = "https"
    SSH = "git"


def parse_git_remote_info(repo_info: str) -> List[str]:
    if repo_info.startswith(GitProtocol.HTTPS.value):
        result = repo_info.split("/")
        return [result[-1].removesuffix(".git"), result[-2]]
    elif repo_info.startswith(GitProtocol.SSH.value):
        result = repo_info.split(":")[1].split("/")
        return [result[-1].removesuffix(".git"), result[-2]]
    else:
        raise ValueError("Git protocol not supported")


class GitInfo(BaseModel):
    repo_owner: Optional[str] = None
    repo: Optional[str] = None
    branch: Optional[str] = None
    filenames: Optional[List[str]] = None
    diffs: Optional[List[Diff]] = None

    @property
    def tokens_of_diffs(self) -> Optional[int]:
        if not self.diffs:
            return None

        encoding = tiktoken.encoding_for_model(config.model)
        return sum(len(encoding.encode(diff)) for diff in self.diffs)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__post_init__()

    def __post_init__(self):
        sh = Shell()
        assert sh.is_git()

        self.branch = sh.git("rev-parse", "--abbrev-ref", "HEAD")
        repo_info = sh.git("config", "--get", "remote.origin.url")
        self.repo, self.repo_owner = parse_git_remote_info(repo_info)

        self.filenames = get_filenames(sh)
        self.diffs = ([diff for diff in get_files_changed(sh)],)
