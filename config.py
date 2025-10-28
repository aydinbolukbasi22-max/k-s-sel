import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def get_secret_key():
    """Geliştirme için basit bir secret key üretimi."""
    return os.environ.get("SECRET_KEY", "gelistirme-gizli-anahtar")

class Config:
    SECRET_KEY = get_secret_key()
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'veritabani.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
