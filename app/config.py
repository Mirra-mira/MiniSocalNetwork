import os
from pathlib import Path

from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


settings = Settings()

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL chưa được thiết lập trong .env")

if not settings.JWT_SECRET:
    raise ValueError("JWT_SECRET chưa được thiết lập trong .env")
