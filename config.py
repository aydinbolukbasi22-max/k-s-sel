import os
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

def _default_secret() -> str:
    return os.environ.get("SECRET_KEY", "cok-gizli-olmayan-anahtar")


def _sqlite_uri(file_name: str) -> str:
    db_path = (DATA_DIR / file_name).resolve().as_posix()
    return f"sqlite:///{db_path}"


class Config:
    SECRET_KEY = _default_secret()
    DATABASE_PATH = str((DATA_DIR / "butce.db").resolve())
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", _sqlite_uri("butce.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    WTF_CSRF_TIME_LIMIT = 8 * 60 * 60  # 8 saat
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
