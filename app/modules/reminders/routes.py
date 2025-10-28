"""Hatırlatıcı görünümleri."""
from datetime import date
from types import SimpleNamespace

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Hatirlatici, HatirlaticiDonemi, HatirlaticiKaydi
from app.modules import create_blueprint
from app.services.finance import hatirlatici_sayaci, hatirlatici_son_tarih_guncelle

from .forms import HatirlaticiFormu, HatirlaticiTamamlamaFormu

bp = create_blueprint("reminders", __name__, url_prefix="/hatirlaticilar")


@bp.route("/", methods=["GET", "POST"])
@login_required
def liste():
    form = HatirlaticiFormu()
    if form.validate_on_submit():
        kayit = Hatirlatici(
            kullanici_id=current_user.id,
            baslik=form.baslik.data.strip(),
            tutar=form.tutar.data or 0,
            son_tarih=form.son_tarih.data,
            donem=HatirlaticiDonemi(form.donem.data),
            aktif=form.aktif.data,
        )
        db.session.add(kayit)
        db.session.commit()
        flash("Hatırlatıcı oluşturuldu.", "success")
        return redirect(url_for("reminders.liste"))
    hatirlaticilar = Hatirlatici.query.filter_by(kullanici_id=current_user.id).order_by(Hatirlatici.son_tarih).all()
    sayac = SimpleNamespace(**hatirlatici_sayaci(hatirlaticilar))
    tamamla_formu = HatirlaticiTamamlamaFormu()
    bugun = date.today()
    return render_template(
        "reminders/hatirlaticilar.html",
        form=form,
        hatirlaticilar=hatirlaticilar,
        sayac=sayac,
        tamamla_formu=tamamla_formu,
        bugun=bugun,
    )


@bp.route("/<int:hatirlatici_id>/tamamla", methods=["POST"])
@login_required
def tamamla(hatirlatici_id: int):
    form = HatirlaticiTamamlamaFormu()
    if not form.validate_on_submit():
        flash("Hatırlatıcı tamamlanamadı.", "danger")
        return redirect(url_for("reminders.liste"))
    kayit = Hatirlatici.query.filter_by(id=hatirlatici_id, kullanici_id=current_user.id).first_or_404()
    db.session.add(
        HatirlaticiKaydi(
            hatirlatici_id=kayit.id,
            gerceklesme_tarihi=date.today(),
            not_metni=form.not_metni.data,
        )
    )
    hatirlatici_son_tarih_guncelle(kayit)
    db.session.commit()
    flash("Hatırlatıcı tamamlandı ve bir sonraki tarih güncellendi.", "success")
    return redirect(url_for("reminders.liste"))


@bp.route("/<int:hatirlatici_id>/sil", methods=["POST"])
@login_required
def sil(hatirlatici_id: int):
    kayit = Hatirlatici.query.filter_by(id=hatirlatici_id, kullanici_id=current_user.id).first_or_404()
    db.session.delete(kayit)
    db.session.commit()
    flash("Hatırlatıcı silindi.", "info")
    return redirect(url_for("reminders.liste"))
