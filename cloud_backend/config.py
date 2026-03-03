from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    DEBUG: bool = False

    class Config:
        env_file = 'cloud_backend/.env'

settings = Settings()
