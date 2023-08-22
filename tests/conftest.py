from pathlib import Path
from unittest.mock import patch

import pytest
from github import Github

from g3 import config
from g3.config import ConfigHandler


class MockedConfigHandler(ConfigHandler):
    def __init__(self):
        self.config_path = Path.cwd()
        self.config_file = self.config_path / Path("tests/fixtures/config")
        self.config = self.load_config()
        self.properties = self.load_properties()


def pytest_configure():
    config.config = MockedConfigHandler()


class MockedRepository:
    @property
    def name(self):
        return "g3"

    @property
    def default_branch(self):
        return "main"


@pytest.fixture(scope="session", autouse=True)
def github_repo():
    with patch.object(Github, "get_repo", return_value=MockedRepository()):
        yield
