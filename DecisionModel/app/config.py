from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    data_dir: str = "./data"
    database_path: str = "./data/tpch.duckdb"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    llm_provider: str = "mock"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
