import configparser
from pathlib import Path

from faker import Faker

from g3.config import CONFIG_DIR, CONFIG_FILE, Config
from g3.main import MessageTone

fake = Faker()


def test_creates_new_config_file(tmp_path):
    path = tmp_path / CONFIG_DIR / CONFIG_FILE
    assert not path.exists()

    config = Config(tmp_path)
    assert config.config_file.exists()


def test_returns_empty_values_for_new_config_file(tmp_path):
    config = Config(tmp_path)
    assert config.get("credentials", "github_token") is None
    assert config.get("credentials", "openai_key") is None
    assert config.get("commit", "tone") is None


def test_returns_values_from_existing_config_file(tmp_path):
    github_token = fake.uuid4()
    openai_key = fake.uuid4()
    tone = fake.random_element(MessageTone).value
    populate_config_file(tmp_path, github_token, openai_key, tone)

    config = Config(tmp_path)
    assert config.get("credentials", "github_token") == github_token
    assert config.get("credentials", "openai_key") == openai_key
    assert config.get("commit", "tone") == tone


def test_sets_values_in_config_file(tmp_path):
    populate_config_file(tmp_path)

    github_token = "a brand new token"
    config = Config(tmp_path)
    config.set("credentials", "github_token", github_token)
    config.save_config()

    config = Config(tmp_path)
    assert config.get("credentials", "github_token") == github_token


def populate_config_file(
    path: Path, github_token: str = fake.uuid4(), openai_key: str = fake.uuid4(), tone: str = MessageTone.FRIENDLY.value
):
    parser = configparser.ConfigParser()
    parser["credentials"] = {"github_token": github_token, "openai_key": openai_key}
    parser["commit"] = {"tone": tone}

    config_path = path / CONFIG_DIR
    config_path.mkdir(exist_ok=True)
    with open(config_path / CONFIG_FILE, "w") as f:
        parser.write(f)
