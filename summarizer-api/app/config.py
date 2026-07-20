from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    anthropic_api_key: str
    log_level: str = "INFO"
    port: int = 8000
    model: str = "claude-opus-4-8"
    max_tokens: int = 512


settings = Settings()
