from typing import List

from g3.services.git.shell import Shell


def commit(message: str) -> None:
    """
    Commit the current state of the index to the repository.

    :param message: The commit message.
    """
    sh = Shell()
    sh.git("commit", "-m", message)


def get_commit_messages(origin_branch: str) -> List[str]:
    """
    Get the commits between two branches.

    :param origin_branch: The origin branch.
    """
    res = []

    sh = Shell()
    assert sh.is_git()

    head = sh.git("merge-base", sh.branch_name, origin_branch)
    commits = sh.git("rev-list", f"^{head}", "HEAD")

    for cm in commits.split("\n"):
        res.append(sh.git("show", "-s", "--format=%B", cm))

    return res


def push(remote: str, branch: str, force: bool = False) -> None:
    """
    Push the current branch to the remote.
    """
    sh = Shell()
    assert sh.is_git()

    branch = sh.branch_name if not branch else branch

    if force:
        sh.git("push", remote, "--force", branch)
    else:
        sh.git("push", remote, branch)
