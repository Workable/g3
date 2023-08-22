import os

from g3.services.git import sh
from g3.services.git.gitinfo import GitInfo


def test_shell():
    assert sh.cwd == os.getcwd()
    repo_name = sh.repo_name
    assert repo_name == "g3"


def test_gitinfo():
    info = GitInfo()

    assert info.repo == "g3"
    assert info.repo_owner == "Workable"
