from g3.git.gitinfo import parse_git_remote_info


def test_parse_git_remote_info() -> None:
    ssh_test = "git@github.com:Workable/g3.git"
    https_test = "https://github.com/Workable/g3.git"

    assert parse_git_remote_info(https_test) == ["g3", "Workable"]
    assert parse_git_remote_info(ssh_test) == ["g3", "Workable"]
