from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/fairness_opinion"

    # Any OpenAI-compatible endpoint works here, not just OpenAI itself. Defaults to
    # Groq's free tier (https://console.groq.com/keys) so the app runs at no cost;
    # point openai_base_url at OpenAI, Gemini, or anything else that speaks the same
    # chat completions format and adjust openai_model to match.
    openai_api_key: str = ""
    openai_base_url: str = "https://api.groq.com/openai/v1"
    openai_model: str = "llama-3.3-70b-versatile"
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
