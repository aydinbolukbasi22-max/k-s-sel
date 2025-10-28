from datetime import datetime

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

login_manager.login_view = "auth.giris"
login_manager.login_message = "Lütfen önce oturum açın."


@app.template_filter("turkce_tarih")
def turkce_tarih(value):
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    return value


from .routes.auth import auth_bp  # noqa: E402  pylint: disable=wrong-import-position
from .routes.dashboard import dashboard_bp  # noqa: E402  pylint: disable=wrong-import-position
from .routes.accounts import accounts_bp  # noqa: E402  pylint: disable=wrong-import-position
from .routes.transactions import transactions_bp  # noqa: E402  pylint: disable=wrong-import-position
from .routes.categories import categories_bp  # noqa: E402  pylint: disable=wrong-import-position
from .routes.budgets import budgets_bp  # noqa: E402  pylint: disable=wrong-import-position
from .routes.reports import reports_bp  # noqa: E402  pylint: disable=wrong-import-position

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(accounts_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(budgets_bp)
app.register_blueprint(reports_bp)

__all__ = ("app", "db", "login_manager", "migrate", "csrf")
