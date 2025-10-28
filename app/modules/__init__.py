"""Blueprint paketleri için ortak araçlar."""
from flask import Blueprint


def create_blueprint(name: str, import_name: str, url_prefix: str = "") -> Blueprint:
    return Blueprint(name, import_name, url_prefix=url_prefix)
