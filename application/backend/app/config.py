from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "LoanBoard API"
    database_url: str = "postgresql+psycopg://postgres@localhost:5432/loanboard"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
