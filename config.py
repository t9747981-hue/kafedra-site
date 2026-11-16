from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./kafedra.db"
    secret_key: str = "super-secret-key-for-kafedra"

settings = Settings()