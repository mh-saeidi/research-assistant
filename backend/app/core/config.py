from pydantic_settings import BaseSettings
from langchain_openai import ChatOpenAI

class Settings(BaseSettings):
    postgres_url: str
    openai_api_key: str
    tavily_api_key: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    REFRESH_TOKEN_EXPIRE_DAYS: int


    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

llm = ChatOpenAI(openai_api_key=settings.openai_api_key, model_name="gpt-4o", temperature=0)