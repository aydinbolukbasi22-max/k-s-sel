from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from .. import db
from ..forms import HesapFormu
from ..models import Hesap


accounts_bp = Blueprint("accounts", __name__, url_prefix="/hesaplar")


@accounts_bp.route("/", methods=["GET", "POST"])
@login_required
def listele():
    form = HesapFormu()
    hesaplar = Hesap.query.filter_by(kullanici_id=current_user.id).all()

    if form.validate_on_submit():
        hesap = Hesap(
            ad=form.ad.data,
            hesap_turu=form.hesap_turu.data,
            bakiye=form.bakiye.data,
            kullanici_id=current_user.id,
        )
        db.session.add(hesap)
        db.session.commit()
        flash("Hesap başarıyla eklendi.", "success")
        return redirect(url_for("accounts.listele"))

    return render_template("accounts/listele.html", form=form, hesaplar=hesaplar, baslik="Hesaplar")


@accounts_bp.route("/<int:hesap_id>/duzenle", methods=["GET", "POST"])
@login_required
def duzenle(hesap_id):
    hesap = Hesap.query.filter_by(id=hesap_id, kullanici_id=current_user.id).first_or_404()
    form = HesapFormu(obj=hesap)

    if form.validate_on_submit():
        hesap.ad = form.ad.data
        hesap.hesap_turu = form.hesap_turu.data
        hesap.bakiye = form.bakiye.data
        db.session.commit()
        flash("Hesap bilgileri güncellendi.", "success")
        return redirect(url_for("accounts.listele"))

    return render_template("accounts/duzenle.html", form=form, hesap=hesap, baslik="Hesap Düzenle")


@accounts_bp.route("/<int:hesap_id>/sil", methods=["POST"])
@login_required
def sil(hesap_id):
    hesap = Hesap.query.filter_by(id=hesap_id, kullanici_id=current_user.id).first_or_404()
    db.session.delete(hesap)
    db.session.commit()
    flash("Hesap silindi.", "info")
    return redirect(url_for("accounts.listele"))
