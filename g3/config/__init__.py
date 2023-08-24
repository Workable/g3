from g3.config.handler import ConfigHandler
from g3.config.log import LogConfig
from g3.config.openai import OpenAIConfig

config = ConfigHandler()
log_config = LogConfig()
openai_config = OpenAIConfig.create()
