from decimal import Decimal
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from .. import db
from ..forms import IslemFormu
from ..models import Islem, Hesap, Kategori


transactions_bp = Blueprint("transactions", __name__, url_prefix="/islemler")


def _hesap_bakiyesini_guncelle(hesap, tutar, islem_turu, ters=False):
    """Gelir/Gider durumuna göre hesap bakiyesini günceller."""
    if hesap is None:
        return

    carpim = Decimal("-1") if ters else Decimal("1")
    tutar = Decimal(tutar)

    if islem_turu == "gelir":
        hesap.bakiye += tutar * carpim
    else:
        hesap.bakiye -= tutar * carpim


@transactions_bp.route("/", methods=["GET", "POST"])
@login_required
def listele():
    form = IslemFormu()
    form.hesap_id.choices = [
        (hesap.id, hesap.ad)
        for hesap in Hesap.query.filter_by(kullanici_id=current_user.id).all()
    ]
    form.kategori_id.choices = [
        (kategori.id, kategori.ad)
        for kategori in Kategori.query.filter_by(kullanici_id=current_user.id).all()
    ]

    islemler = (
        Islem.query.filter_by(kullanici_id=current_user.id)
        .order_by(Islem.tarih.desc())
        .all()
    )

    if form.validate_on_submit():
        if not form.hesap_id.choices or not form.kategori_id.choices:
            flash("İşlem eklemek için önce hesap ve kategori oluşturmalısınız.", "warning")
            return redirect(url_for("transactions.listele"))

        islem = Islem(
            islem_turu=form.islem_turu.data,
            hesap_id=form.hesap_id.data,
            kategori_id=form.kategori_id.data,
            tutar=form.tutar.data,
            tarih=form.tarih.data,
            aciklama=form.aciklama.data,
            kullanici_id=current_user.id,
        )

        hesap = Hesap.query.filter_by(id=islem.hesap_id, kullanici_id=current_user.id).first()
        _hesap_bakiyesini_guncelle(hesap, islem.tutar, islem.islem_turu)

        db.session.add(islem)
        db.session.commit()
        flash("İşlem başarıyla kaydedildi.", "success")
        return redirect(url_for("transactions.listele"))

    return render_template("transactions/listele.html", form=form, islemler=islemler, baslik="İşlemler")


@transactions_bp.route("/<int:islem_id>/duzenle", methods=["GET", "POST"])
@login_required
def duzenle(islem_id):
    islem = Islem.query.filter_by(id=islem_id, kullanici_id=current_user.id).first_or_404()
    form = IslemFormu(obj=islem)
    form.hesap_id.choices = [
        (hesap.id, hesap.ad)
        for hesap in Hesap.query.filter_by(kullanici_id=current_user.id).all()
    ]
    form.kategori_id.choices = [
        (kategori.id, kategori.ad)
        for kategori in Kategori.query.filter_by(kullanici_id=current_user.id).all()
    ]

    if form.validate_on_submit():
        eski_hesap = Hesap.query.filter_by(id=islem.hesap_id, kullanici_id=current_user.id).first()
        _hesap_bakiyesini_guncelle(eski_hesap, islem.tutar, islem.islem_turu, ters=True)

        islem.islem_turu = form.islem_turu.data
        islem.hesap_id = form.hesap_id.data
        islem.kategori_id = form.kategori_id.data
        islem.tutar = form.tutar.data
        islem.tarih = form.tarih.data
        islem.aciklama = form.aciklama.data

        yeni_hesap = Hesap.query.filter_by(id=islem.hesap_id, kullanici_id=current_user.id).first()
        _hesap_bakiyesini_guncelle(yeni_hesap, islem.tutar, islem.islem_turu)

        db.session.commit()
        flash("İşlem güncellendi.", "success")
        return redirect(url_for("transactions.listele"))

    return render_template("transactions/duzenle.html", form=form, islem=islem, baslik="İşlem Düzenle")


@transactions_bp.route("/<int:islem_id>/sil", methods=["POST"])
@login_required
def sil(islem_id):
    islem = Islem.query.filter_by(id=islem_id, kullanici_id=current_user.id).first_or_404()
    hesap = Hesap.query.filter_by(id=islem.hesap_id, kullanici_id=current_user.id).first()
    _hesap_bakiyesini_guncelle(hesap, islem.tutar, islem.islem_turu, ters=True)

    db.session.delete(islem)
    db.session.commit()
    flash("İşlem silindi.", "info")
    return redirect(url_for("transactions.listele"))
