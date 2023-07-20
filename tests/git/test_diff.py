from g3.git.diff import exclude_files


def test_exclude_files():
    files = ["test.txt", "package-lock.json", "poetry.lock", "Gemfile.lock"]

    assert exclude_files(files) == ["test.txt"]


def test_get_files_changed():
    pass
