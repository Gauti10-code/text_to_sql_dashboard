# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.0

    # MySQL
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "fmcg_db"
    db_user: str = "root"
    db_password: str

    # Query safety
    max_rows: int = 5000
    query_timeout_seconds: int = 30

    # App
    app_title: str = "Text-to-SQL Dashboard"
    debug: bool = False

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()