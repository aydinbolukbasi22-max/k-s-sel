import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def get_secret_key():
    """Geliştirme için basit bir secret key üretimi."""
    return os.environ.get("SECRET_KEY", "gelistirme-gizli-anahtar")

class Config:
    SECRET_KEY = get_secret_key()
    varsayılan_db_yolu = (BASE_DIR / "veritabani.db").resolve().as_posix()
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{varsayılan_db_yolu}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
