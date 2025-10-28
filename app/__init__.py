"""Uygulamanın başlangıç noktasını ve fabrikasını barındırır."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Type

from flask import Flask

from .extensions import csrf, db, login_manager, migrate
from .services.notifications import register_scheduled_jobs


def create_app(config_class: Optional[Type[object]] = None) -> Flask:
    """Flask uygulamasını oluştur ve yapılandır."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")
    if config_class is not None:
        app.config.from_object(config_class)

    _ensure_data_directory(app)
    _register_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    register_scheduled_jobs(app)
    _register_cli_commands(app)
    _register_context_processors(app)

    return app


def _ensure_data_directory(app: Flask) -> None:
    data_path = Path(app.config["DATABASE_PATH"]).expanduser().resolve()
    data_path.parent.mkdir(parents=True, exist_ok=True)


def _register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.giris"
    login_manager.login_message = "Lütfen devam etmeden önce oturum açın."


def _register_blueprints(app: Flask) -> None:
    from .modules.auth import bp as auth_bp
    from .modules.dashboard import bp as dashboard_bp
    from .modules.ledger import bp as ledger_bp
    from .modules.budgeting import bp as budgeting_bp
    from .modules.goals import bp as goals_bp
    from .modules.debts import bp as debts_bp
    from .modules.reminders import bp as reminders_bp
    from .modules.analytics import bp as analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(ledger_bp)
    app.register_blueprint(budgeting_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(debts_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(analytics_bp)


def _register_error_handlers(app: Flask) -> None:
    from flask import render_template

    @app.errorhandler(403)
    def forbidden(error):  # type: ignore[override]
        return render_template("partials/hata.html", kod=403, mesaj="Erişim reddedildi."), 403

    @app.errorhandler(404)
    def not_found(error):  # type: ignore[override]
        return render_template("partials/hata.html", kod=404, mesaj="Aradığınız sayfa bulunamadı."), 404

    @app.errorhandler(500)
    def internal_error(error):  # type: ignore[override]
        db.session.rollback()
        return (
            render_template(
                "partials/hata.html",
                kod=500,
                mesaj="Beklenmeyen bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
            ),
            500,
        )


def _register_cli_commands(app: Flask) -> None:
    from click import echo

    @app.cli.command("veritabani-olustur")
    def veritabani_olustur() -> None:
        """Veritabanı tablolarını oluştur."""
        with app.app_context():
            try:
                db.create_all()
            except Exception as exc:  # pragma: no cover - yalnızca CLI kullanımında tetiklenir
                echo(f"Tablolar oluşturulurken hata oluştu: {exc}")
                raise
            else:
                echo("Veritabanı tabloları başarıyla oluşturuldu.")


def _register_context_processors(app: Flask) -> None:
    from datetime import date

    @app.context_processor
    def inject_globals():
        return {"current_year": date.today().year}
