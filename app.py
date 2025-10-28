from pathlib import Path

from app import app, db
from app.models import Butce, Hesap, Islem, Kategori, Kullanici  # noqa: F401


def _sqlite_veritabani_yolu(uri: str) -> Path:
    yol = uri.replace("sqlite:///", "", 1)
    if yol.startswith("/") and len(yol) > 3 and yol[2] == ":" and yol[1].isalpha():
        yol = yol.lstrip("/")
    veritabani_yolu = Path(yol)
    if not veritabani_yolu.is_absolute():
        veritabani_yolu = Path(app.root_path) / veritabani_yolu
    return veritabani_yolu


def veritabani_kontrol_ve_olustur() -> None:
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if uri.startswith("sqlite:///"):
        veritabani_yolu = _sqlite_veritabani_yolu(uri)
        if not veritabani_yolu.exists():
            veritabani_yolu.parent.mkdir(parents=True, exist_ok=True)
            with app.app_context():
                db.create_all()
    else:
        with app.app_context():
            db.create_all()


@app.cli.command("veritabani-olustur")
def veritabani_olustur():
    """Veritabanı tablolarını manuel olarak oluşturur."""
    with app.app_context():
        db.create_all()
    print("Veritabanı tabloları oluşturuldu.")


if __name__ == "__main__":
    veritabani_kontrol_ve_olustur()
    app.run(debug=True)
