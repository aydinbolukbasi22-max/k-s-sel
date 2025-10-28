from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from datetime import datetime

# Uzantılar
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_class=None):
    """Flask uygulama örneğini oluşturur ve döndürür."""
    app = Flask(__name__)

    if config_class is None:
        from config import Config
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view = "auth.giris"
    login_manager.login_message = "Lütfen önce oturum açın."

    @app.template_filter("turkce_tarih")
    def turkce_tarih(value):
        if isinstance(value, datetime):
            return value.strftime("%d/%m/%Y")
        return value

    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.accounts import accounts_bp
    from .routes.transactions import transactions_bp
    from .routes.categories import categories_bp
    from .routes.budgets import budgets_bp
    from .routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(reports_bp)

    # Veritabanı tablolarının varlığını garanti altına al
    with app.app_context():
        db.create_all()

    return app
