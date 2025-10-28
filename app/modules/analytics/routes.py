"""Analitik ve rapor görünümleri."""
from datetime import date

from flask import jsonify, render_template
from flask_login import current_user, login_required

from app.modules import create_blueprint
from app.services.finance import kategori_harcama_ozeti, nakit_akisi_verisi

bp = create_blueprint("analytics", __name__, url_prefix="/analiz")


@bp.route("/")
@login_required
def raporlar():
    yil = date.today().year
    nakit = nakit_akisi_verisi(current_user.id, yil)
    harcama = kategori_harcama_ozeti(current_user.id, yil, date.today().month)
    return render_template("analytics/raporlar.html", nakit=nakit, harcama=harcama, yil=yil)


@bp.route("/nakit.json")
@login_required
def nakit_json():
    yil = date.today().year
    veriler = nakit_akisi_verisi(current_user.id, yil)
    return jsonify(
        {
            "labels": [satir.etiket for satir in veriler],
            "gelir": [float(satir.gelir) for satir in veriler],
            "gider": [float(satir.gider) for satir in veriler],
        }
    )


@bp.route("/harcama.json")
@login_required
def harcama_json():
    ozet = kategori_harcama_ozeti(current_user.id, date.today().year, date.today().month)
    return jsonify(
        {
            "labels": list(ozet.keys()),
            "values": [float(deger) for deger in ozet.values()],
        }
    )
