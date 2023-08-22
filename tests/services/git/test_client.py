from g3.services.git import client


def test_get_repo_info() -> None:
    assert client.get_repo_info() == ("g3", "Workable")
