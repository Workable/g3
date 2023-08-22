import os

import pytest

from g3.services.git import sh
from g3.services.git.diff import exclude_files
from g3.services.git.gitinfo import GitInfo


@pytest.fixture()
def with_staged_file():
    with open("test.txt", "w") as f:
        f.write("hello world")

    sh.git("add", "test.txt")
    yield
    sh.git("rm", "--cached", "test.txt")
    os.remove("test.txt")


def test_exclude_files():
    files = ["test.txt", "package-lock.json", "poetry.lock", "Gemfile.lock"]
    assert exclude_files(files) == ["test.txt"]


def test_get_files_changed(with_staged_file):
    git_info = GitInfo()
    assert "test.txt" in git_info.filenames
