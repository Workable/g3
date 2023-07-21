import os

from g3.git.diff import exclude_files


def test_exclude_files():
    files = ["test.txt", "package-lock.json", "poetry.lock", "Gemfile.lock"]

    assert exclude_files(files) == ["test.txt"]


def test_get_files_changed():
    from g3.git.gitinfo import GitInfo
    from g3.git.shell import Shell

    sh = Shell()

    # Create temporary file in this directory and add it to the git index
    with open("test.txt", "w") as f:
        f.write("hello world")

    sh.git("add", "test.txt")
    git_info = GitInfo()
    assert "test.txt" in git_info.filenames

    sh.git("rm", "--cached", "test.txt")
    os.remove("test.txt")
