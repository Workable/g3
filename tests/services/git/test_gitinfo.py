import os

import pytest

from g3.services.git.gitinfo import GitInfo
from g3.services.git.shell import Shell

sh = Shell()


@pytest.fixture()
def with_staged_file():
    with open("test.txt", "w") as f:
        f.write("hello world")

    sh.git("add", "test.txt")
    yield
    sh.git("rm", "--cached", "test.txt")
    os.remove("test.txt")


def test_get_files_changed(with_staged_file):
    assert "test.txt" in GitInfo().filenames
