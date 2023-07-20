from pydantic import BaseModel

from g3.git.shell import Shell


class GitInfo(BaseModel):
    repo_owner: str
    repo: str
    branch: str


def get_git_info() -> GitInfo:
    sh = Shell()
    assert sh.is_git()

    branch = sh.git("rev-parse", "--abbrev-ref", "HEAD")
    repo_info = sh.git("config", "--get", "remote.origin.url").split("/")
    repo = repo_info[-1]
    repo_owner = repo_info[-2]

    return GitInfo(repo_owner=repo_owner, repo=repo, branch=branch)
