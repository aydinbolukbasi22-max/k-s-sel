"""Uygulamanın çalıştırılabilir giriş noktası."""
from app import create_app, db

app = create_app()


if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
        except Exception as exc:  # pragma: no cover
            app.logger.error("Veritabanı tabloları oluşturulamadı: %s", exc)
            raise
        else:
            app.logger.info("Veritabanı tabloları hazır.")
    app.run(debug=True)
