from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:2005@127.0.0.1:5432/test"
    SECRET_KEY: str = "2005"  # Use a secure, randomly generated key
    DEBUG: bool = True

settings = Settings()
