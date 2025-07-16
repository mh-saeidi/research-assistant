from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    REFRESH_TOKEN_EXPIRE_DAYS: int


    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()