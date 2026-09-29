from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    typesafe_api_key: str | None = None
    jev_enabled: bool = True
    hindsight_api_key: str | None = None
    hindsight_base_url: str = 'https://api.hindsight.vectorize.io'
    hindsight_bank_id: str = 'deploymind'
    groq_api_key: str | None = None
    groq_model: str = 'openai/gpt-oss-20b'
    frontend_origin: str = 'http://localhost:5173'

@lru_cache
def get_settings() -> Settings:
    return Settings()
