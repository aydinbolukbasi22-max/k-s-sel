"""Hatırlatıcı ve bildirim yardımcıları."""
from __future__ import annotations

from flask import Flask


def register_scheduled_jobs(app: Flask) -> None:
    """Gelecekteki zamanlanmış işler için yer tutucu."""
    app.logger.debug("Zamanlanmış işler kaydedildi.")
