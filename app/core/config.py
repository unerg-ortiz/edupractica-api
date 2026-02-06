from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduPractica API"
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    SECRET_KEY: str = "INSECURE_SECRET_KEY_FOR_DEV_ONLY" # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days

    class Config:
        env_file = ".env"

settings = Settings()
