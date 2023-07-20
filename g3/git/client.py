from g3.git.shell import Shell


def commit(message: str) -> None:
    """
    Commit the current state of the index to the repository.

    :param message: The commit message.
    """
    sh = Shell()
    sh.git("commit", "-m", message)
