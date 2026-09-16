import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamically resolve the absolute path to the .env file in the root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# RepoLens/backend/app/core -> RepoLens
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), ".env")


class Settings(BaseSettings):
    database_url: str

    groq_api_key: str = ""
    github_token: str = ""
    hf_token: str = ""

    frontend_url: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()