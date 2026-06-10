# config.py file, database and security object

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key:str
    news_api_key:str
    groq_model:str = "llama3-8b-8192"
    database_url:str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()