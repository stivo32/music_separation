import os
from pydantic import BaseSettings


BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Settings(BaseSettings):
    DB_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/data/db.sqlite3"
    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = os.path.join(BASE_DIR, ".env")


settings = Settings()
database_url = settings.DB_URL
