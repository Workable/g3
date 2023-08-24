from pydantic import BaseSettings


class LogConfig(BaseSettings):
    level: str = "critical"

    class Config:
        env_prefix = "LOG_"
