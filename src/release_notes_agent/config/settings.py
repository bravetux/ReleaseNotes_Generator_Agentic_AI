"""Application settings loaded from environment variables via pydantic-settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # AWS credentials
    aws_access_key_id: str = Field(default="", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="", alias="AWS_SECRET_ACCESS_KEY")
    aws_session_token: str = Field(default="", alias="AWS_SESSION_TOKEN")
    aws_region: str = Field(default="us-east-1", alias="AWS_DEFAULT_REGION")

    # LLM
    bedrock_model_id: str = Field(
        default="anthropic.claude-sonnet-4-20250514-v1:0",
        alias="BEDROCK_MODEL_ID",
    )
    agent_temperature: float = Field(default=0.1, alias="AGENT_TEMPERATURE")
    agent_top_p: float = Field(default=0.9, alias="AGENT_TOP_P")
    agent_max_tokens: int = Field(default=4096, alias="AGENT_MAX_TOKENS")

    # Session
    session_backend: str = Field(default="file", alias="SESSION_BACKEND")
    session_dir: str = Field(default=".sessions", alias="SESSION_DIR")


# Singleton — imported everywhere
settings = Settings()
