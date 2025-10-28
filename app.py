from app import create_app, db
from app.models import Kullanici, Hesap, Kategori, Islem, Butce

app = create_app()


@app.cli.command("veritabani-olustur")
def veritabani_olustur():
    """Veritabanı tablolarını oluşturur."""
    db.create_all()
    print("Veritabanı tabloları oluşturuldu.")


if __name__ == "__main__":
    app.run(debug=True)
