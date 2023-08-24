import os

from g3.services.git import git_info
from g3.services.git.shell import Shell


def test_shell():
    assert Shell().cwd == os.getcwd()


def test_gitinfo():
    assert git_info.repo_name == "g3"
    assert git_info.repo_owner == "Workable"
