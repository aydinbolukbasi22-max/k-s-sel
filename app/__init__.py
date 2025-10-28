from datetime import datetime

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()


def turkce_tarih(value):
    """Tarih alanlarını Türkçe biçimde döndürür."""
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    return value


def create_app(config_class: type[Config] = Config) -> Flask:
    """Flask uygulamasını oluşturur ve yapılandırır."""

    uygulama = Flask(__name__)
    uygulama.config.from_object(config_class)

    db.init_app(uygulama)
    login_manager.init_app(uygulama)
    migrate.init_app(uygulama, db)
    csrf.init_app(uygulama)

    login_manager.login_view = "auth.giris"
    login_manager.login_message = "Lütfen önce oturum açın."

    uygulama.add_template_filter(turkce_tarih, name="turkce_tarih")

    from .routes.auth import auth_bp  # noqa: E402  pylint: disable=import-outside-toplevel
    from .routes.dashboard import dashboard_bp  # noqa: E402  pylint: disable=import-outside-toplevel
    from .routes.accounts import accounts_bp  # noqa: E402  pylint: disable=import-outside-toplevel
    from .routes.transactions import transactions_bp  # noqa: E402  pylint: disable=import-outside-toplevel
    from .routes.categories import categories_bp  # noqa: E402  pylint: disable=import-outside-toplevel
    from .routes.budgets import budgets_bp  # noqa: E402  pylint: disable=import-outside-toplevel
    from .routes.reports import reports_bp  # noqa: E402  pylint: disable=import-outside-toplevel

    uygulama.register_blueprint(auth_bp)
    uygulama.register_blueprint(dashboard_bp)
    uygulama.register_blueprint(accounts_bp)
    uygulama.register_blueprint(transactions_bp)
    uygulama.register_blueprint(categories_bp)
    uygulama.register_blueprint(budgets_bp)
    uygulama.register_blueprint(reports_bp)

    try:
        with uygulama.app_context():
            sonuc = db.session.execute(text("SELECT 1"))
            sonuc.close()
    except SQLAlchemyError as exc:
        uygulama.logger.error("Veritabanına bağlanılamadı: %s", exc)
        raise RuntimeError(
            "Veritabanı bağlantısı kurulamadı. Lütfen yapılandırmayı kontrol edin."
        ) from exc

    return uygulama


app = create_app()

__all__ = ("app", "db", "login_manager", "migrate", "csrf", "create_app")
