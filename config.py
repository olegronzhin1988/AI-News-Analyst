# config.py file, database and security object

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key:str =""
    news_api_key:str = ""
    groq_model:str = ""
    database_url:str
    openrouter_api_key: str =""
    openrouter_model: str = ""
    model_config = SettingsConfigDict(env_file=".env")
    primary_ai_provider: str = "groq"

settings = Settings()