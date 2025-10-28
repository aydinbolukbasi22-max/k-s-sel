"""Tasarruf hedefi görünümleri."""
from decimal import Decimal

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import TasarrufHedefi
from app.modules import create_blueprint
from app.services.finance import hedef_tamamlanma_orani

from .forms import TasarrufHedefiFormu

bp = create_blueprint("goals", __name__, url_prefix="/hedefler")


@bp.route("/", methods=["GET", "POST"])
@login_required
def hedef_listesi():
    form = TasarrufHedefiFormu()
    if form.validate_on_submit():
        hedef = TasarrufHedefi(
            kullanici_id=current_user.id,
            ad=form.ad.data.strip(),
            hedef_tutar=form.hedef_tutar.data,
            birikim=form.birikim.data or 0,
            hedef_tarih=form.hedef_tarih.data,
            oncelik=form.oncelik.data,
            aciklama=form.aciklama.data,
        )
        db.session.add(hedef)
        db.session.commit()
        flash("Tasarruf hedefi kaydedildi.", "success")
        return redirect(url_for("goals.hedef_listesi"))
    hedefler = TasarrufHedefi.query.filter_by(kullanici_id=current_user.id).order_by(TasarrufHedefi.oncelik).all()
    ilerlemeler = {hedef.id: hedef_tamamlanma_orani(hedef) for hedef in hedefler}
    return render_template("goals/hedefler.html", form=form, hedefler=hedefler, ilerlemeler=ilerlemeler)


@bp.route("/<int:hedef_id>/guncelle", methods=["POST"])
@login_required
def hedef_guncelle(hedef_id: int):
    hedef = TasarrufHedefi.query.filter_by(id=hedef_id, kullanici_id=current_user.id).first_or_404()
    artisim = Decimal(request.form.get("eklenen_tutar", 0) or 0)
    hedef.birikim += artisim
    if hedef.birikim > hedef.hedef_tutar:
        hedef.birikim = hedef.hedef_tutar
    db.session.commit()
    flash("Hedef birikimi güncellendi.", "success")
    return redirect(url_for("goals.hedef_listesi"))


@bp.route("/<int:hedef_id>/sil", methods=["POST"])
@login_required
def hedef_sil(hedef_id: int):
    hedef = TasarrufHedefi.query.filter_by(id=hedef_id, kullanici_id=current_user.id).first_or_404()
    db.session.delete(hedef)
    db.session.commit()
    flash("Tasarruf hedefi silindi.", "info")
    return redirect(url_for("goals.hedef_listesi"))
