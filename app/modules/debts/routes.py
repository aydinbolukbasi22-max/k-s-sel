"""Borç yönetimi görünümleri."""
from decimal import Decimal

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Borc, BorcOdeme, Hesap
from app.modules import create_blueprint

from .forms import BorcFormu, BorcOdemeFormu

bp = create_blueprint("debts", __name__, url_prefix="/borclar")


@bp.route("/", methods=["GET", "POST"])
@login_required
def borc_listesi():
    form = BorcFormu()
    hesaplar = Hesap.query.filter_by(kullanici_id=current_user.id).all()
    form.hesap_id.choices = [(0, "Seçilmedi")] + [(h.id, h.ad) for h in hesaplar]
    if form.validate_on_submit():
        borc = Borc(
            kullanici_id=current_user.id,
            hesap_id=form.hesap_id.data or None,
            ad=form.ad.data.strip(),
            toplam_tutar=form.toplam_tutar.data,
            kalan_tutar=form.kalan_tutar.data,
            faiz_orani=form.faiz_orani.data or 0,
            son_odeme_tarihi=form.son_odeme_tarihi.data,
            minimum_odeme=form.minimum_odeme.data or 0,
            aciklama=form.aciklama.data,
        )
        db.session.add(borc)
        db.session.commit()
        flash("Borç kaydedildi.", "success")
        return redirect(url_for("debts.borc_listesi"))
    borclar = Borc.query.filter_by(kullanici_id=current_user.id).all()
    return render_template("debts/borclar.html", form=form, borclar=borclar)


@bp.route("/<int:borc_id>/odeme", methods=["POST"])
@login_required
def borc_odeme(borc_id: int):
    form = BorcOdemeFormu()
    if not form.validate_on_submit():
        flash("Ödeme bilgileri geçerli değil.", "danger")
        return redirect(url_for("debts.borc_listesi"))
    borc = Borc.query.filter_by(id=borc_id, kullanici_id=current_user.id).first_or_404()
    tutar = Decimal(form.tutar.data)
    if tutar > borc.kalan_tutar:
        flash("Ödenen tutar kalan borçtan fazla olamaz.", "warning")
        return redirect(url_for("debts.borc_listesi"))
    borc.kalan_tutar -= tutar
    odeme = BorcOdeme(borc_id=borc.id, tutar=tutar, tarih=form.tarih.data, aciklama=form.aciklama.data)
    db.session.add(odeme)
    db.session.commit()
    flash("Ödeme kaydedildi.", "success")
    return redirect(url_for("debts.borc_listesi"))


@bp.route("/<int:borc_id>/sil", methods=["POST"])
@login_required
def borc_sil(borc_id: int):
    borc = Borc.query.filter_by(id=borc_id, kullanici_id=current_user.id).first_or_404()
    db.session.delete(borc)
    db.session.commit()
    flash("Borç kaydı silindi.", "info")
    return redirect(url_for("debts.borc_listesi"))
