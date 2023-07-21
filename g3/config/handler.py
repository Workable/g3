import configparser
from pathlib import Path
from typing import Any, Optional

CONFIG_DIR = ".g3"
CONFIG_FILE = "config"


class ConfigHandler:
    def __init__(self, config_path: Path = Path.home()):
        self.config_path = config_path / CONFIG_DIR
        self.config_file = self.config_path / CONFIG_FILE
        self.config = self.load_config()
        self.properties = self.load_properties()

    @property
    def as_dict(self) -> dict[str, Any]:
        return self.properties

    @property
    def github_token(self) -> str:
        return self.properties.get("github_token", "")

    @property
    def openai_key(self) -> str:
        return self.properties.get("openai_key", "")

    @property
    def api_base(self) -> Optional[str]:
        return self.properties.get("api_base")

    @property
    def deployment_id(self) -> Optional[str]:
        return self.properties.get("deployment_id")

    @property
    def api_type(self) -> Optional[str]:
        return self.properties.get("api_type")

    @property
    def model(self) -> str:
        return self.properties.get("model", "gpt-4-0613")

    @property
    def temperature(self) -> Optional[float]:
        if not self.properties.get("temperature"):
            return None

        return float(self.properties.get("temperature", "0"))

    @property
    def api_version(self) -> Optional[str]:
        return self.properties.get("api_version")

    @property
    def tone(self) -> Optional[str]:
        return self.properties.get("tone")

    @property
    def commit_description_max_words(self) -> int:
        return int(self.properties.get("commit_description_max_words", "50"))

    @property
    def pr_description_max_words(self) -> int:
        return int(self.properties.get("pr_description_max_words", "500"))

    def has_been_configured(self) -> bool:
        return self.config.has_section("credentials")

    def get(self, section: str, key: str, default: Optional[str] = None) -> Optional[str]:
        try:
            return self.config[section][key]
        except KeyError:
            return default

    def set(self, section: str, key: str, value: str):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

    def load_config(self) -> configparser.ConfigParser:
        self.config_path.mkdir(exist_ok=True)
        self.config_file.touch(exist_ok=True)

        parser = configparser.ConfigParser()
        parser.read(self.config_file)
        return parser

    def load_properties(self) -> dict[str, Any]:
        properties = {}
        for section in self.config.sections():
            for key, value in self.config.items(section):
                properties[key] = value

        return properties

    def save_config(self):
        with open(self.config_file, "w") as f:
            self.config.write(f)
