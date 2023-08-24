from g3.services.git import client
from g3.services.git.gitinfo import GitInfo

git_info = GitInfo()

__all__ = ["GitInfo", "git_info", "client"]
