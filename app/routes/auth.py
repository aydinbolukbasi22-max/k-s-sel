from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db
from ..forms import KayitFormu, GirisFormu
from ..models import Kullanici


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/kayit", methods=["GET", "POST"])
def kayit():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.anasayfa"))

    form = KayitFormu()
    if form.validate_on_submit():
        if Kullanici.query.filter_by(eposta=form.eposta.data.lower()).first():
            flash("Bu e-posta ile zaten kayıt bulunuyor.", "danger")
            return redirect(url_for("auth.kayit"))

        kullanici = Kullanici(
            ad=form.ad.data,
            eposta=form.eposta.data.lower(),
            sifre=generate_password_hash(form.sifre.data),
        )
        db.session.add(kullanici)
        db.session.commit()
        flash("Kayıt işlemi tamamlandı. Şimdi giriş yapabilirsiniz.", "success")
        return redirect(url_for("auth.giris"))

    return render_template("auth/kayit.html", form=form, baslik="Kayıt Ol")


@auth_bp.route("/giris", methods=["GET", "POST"])
def giris():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.anasayfa"))

    form = GirisFormu()
    if form.validate_on_submit():
        kullanici = Kullanici.query.filter_by(eposta=form.eposta.data.lower()).first()
        if kullanici and check_password_hash(kullanici.sifre, form.sifre.data):
            login_user(kullanici)
            flash("Hoş geldiniz!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard.anasayfa"))
        flash("E-posta veya şifre hatalı.", "danger")

    return render_template("auth/giris.html", form=form, baslik="Giriş Yap")


@auth_bp.route("/cikis")
@login_required
def cikis():
    logout_user()
    flash("Başarıyla çıkış yapıldı.", "info")
    return redirect(url_for("auth.giris"))
