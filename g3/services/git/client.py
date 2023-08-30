from enum import Enum
from logging import getLogger
from typing import List, Tuple

from g3.config.exclude import EXCLUDED_FILES
from g3.services.git.shell import Shell
from g3.utils.context_managers import suppress_stdout_stderr

logger = getLogger(__name__)
sh = Shell()


class GitProtocol(str, Enum):
    HTTPS = "https"
    SSH = "git"


def get_repo_info() -> Tuple[str, str]:
    """
    Returns a tuple with the repo's name (first) and the owner (second).
    For example:
    ```
    ('g3', 'Workable')
    ```
    """
    url = sh.git("config", "--get", "remote.origin.url")
    if url.startswith(GitProtocol.HTTPS.value):
        parts = url.split("/")
    elif url.startswith(GitProtocol.SSH.value):
        parts = url.split(":")[1].split("/")
    else:
        raise ValueError("Git protocol not supported")

    repo_name = parts[-1].removesuffix(".git")
    repo_owner = parts[-2]

    return repo_name, repo_owner


def get_branch_name() -> str:
    """Returns the name of the current git branch."""
    return sh.git("rev-parse", "--abbrev-ref", "HEAD")


def get_diff_names() -> List[str]:
    """Returns the names of the changed files in the stage of the current git branch."""
    files = sh.git("diff", "--name-only", "--staged", "HEAD").splitlines()

    return list(filter(lambda x: x not in EXCLUDED_FILES, files))


def get_diffs(filename: str) -> str:
    """Returns the changed code diffs in the stage of the current git branch for the provided filename."""
    diffs = ""
    try:
        with suppress_stdout_stderr():
            diffs = sh.git("diff", "HEAD", "--function-context", "--", filename)
        logger.debug(f"git diff HEAD --function-context {filename} found diffs:\n{diffs}")
    except Exception as e:
        logger.warn(f"git diff HEAD --function-context {filename} failed cause:\n{e}")

    return diffs


def commit(message: str) -> None:
    """
    Commit the current state of the index to the repository.

    :param message: The commit message.
    """
    sh.git("commit", "-m", message)


def get_commit_messages(default_branch: str, current_branch: str) -> List[str]:
    """
    Get the commits between the provided branches.

    :param default_branch: The repo's default branch (i.e. main).
    :param current_branch: The repo's current branch.
    """
    res = []
    head = sh.git("merge-base", current_branch, default_branch)
    commits = sh.git("rev-list", f"^{head}", "HEAD")

    for cm in commits.split("\n"):
        res.append(sh.git("show", "-s", "--format=%B", cm))

    return res


def push(remote: str, branch: str, force: bool = False) -> None:
    """
    Push the current branch to the remote.
    """
    if force:
        sh.git("push", "--set-upstream", remote, "--force", branch)
    else:
        sh.git("push", "--set-upstream", remote, branch)
