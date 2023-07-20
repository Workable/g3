import os

from g3.git.git import GitInfo
from g3.git.shell import Shell


def test_shell():
    sh = Shell()
    assert sh.cwd == os.getcwd()

    assert sh.is_git()

    repo_name = sh.repo_name
    assert repo_name == "g3"


def test_gitinfo():
    info = GitInfo()

    assert info.repo_name == "g3"
    assert info.repo_owner == "Workable"
