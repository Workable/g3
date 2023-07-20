import configparser
from pathlib import Path
from typing import Optional

CONFIG_DIR = ".g3"
CONFIG_FILE = "config"


class Config:
    def __init__(self, config_path: Path = Path.home()):
        self.config_path = config_path / CONFIG_DIR
        self.config_file = self.config_path / CONFIG_FILE
        self.config = self.load_config()

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

    def save_config(self):
        with open(self.config_file, "w") as f:
            self.config.write(f)
