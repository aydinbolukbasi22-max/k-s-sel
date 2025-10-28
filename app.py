from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

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


def _tablolari_olustur() -> None:
    try:
        with app.app_context():
            db.create_all()
    except SQLAlchemyError as exc:
        app.logger.error("Veritabanı tabloları oluşturulurken hata oluştu: %s", exc)
        raise RuntimeError(
            "Veritabanı tabloları oluşturulamadı. Lütfen yapılandırmayı kontrol edin."
        ) from exc


def veritabani_kontrol_ve_olustur() -> None:
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if uri.startswith("sqlite:///"):
        veritabani_yolu = _sqlite_veritabani_yolu(uri)
        if not veritabani_yolu.exists():
            veritabani_yolu.parent.mkdir(parents=True, exist_ok=True)
            _tablolari_olustur()
        else:
            _tablolari_olustur()
    else:
        _tablolari_olustur()


@app.cli.command("veritabani-olustur")
def veritabani_olustur():
    """Veritabanı tablolarını manuel olarak oluşturur."""
    _tablolari_olustur()
    print("Veritabanı tabloları oluşturuldu.")


if __name__ == "__main__":
    veritabani_kontrol_ve_olustur()
    app.run(debug=True)
