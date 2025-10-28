"""Kimlik doğrulama işlemleri."""
from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import Kullanici
from app.modules import create_blueprint
from app.services.finance import varsayilan_kategorileri_olustur

from .forms import GirisFormu, KayitFormu, ProfilFormu

bp = create_blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/kayit", methods=["GET", "POST"])
def kayit():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.ozet"))

    form = KayitFormu()
    if form.validate_on_submit():
        if Kullanici.query.filter_by(eposta=form.eposta.data.lower()).first():
            flash("Bu e-posta adresiyle zaten kayıt olunmuş.", "warning")
        else:
            kullanici = Kullanici(
                ad=form.ad.data.strip(),
                eposta=form.eposta.data.lower(),
                sifre=generate_password_hash(form.sifre.data),
                olusturulma=datetime.utcnow(),
            )
            db.session.add(kullanici)
            db.session.commit()
            varsayilan_kategorileri_olustur(kullanici.id)
            flash("Hesabınız oluşturuldu, şimdi giriş yapabilirsiniz.", "success")
            return redirect(url_for("auth.giris"))
    return render_template("auth/kayit.html", form=form)


@bp.route("/giris", methods=["GET", "POST"])
def giris():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.ozet"))

    form = GirisFormu()
    if form.validate_on_submit():
        kullanici = Kullanici.query.filter_by(eposta=form.eposta.data.lower()).first()
        if kullanici and check_password_hash(kullanici.sifre, form.sifre.data):
            login_user(kullanici)
            flash("Hoş geldiniz!", "success")
            hedef = request.args.get("next") or url_for("dashboard.ozet")
            return redirect(hedef)
        flash("E-posta veya şifre hatalı.", "danger")
    return render_template("auth/giris.html", form=form)


@bp.route("/cikis")
@login_required
def cikis():
    logout_user()
    flash("Güvenli çıkış yaptınız.", "info")
    return redirect(url_for("auth.giris"))


@bp.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    form = ProfilFormu(obj=current_user)
    if form.validate_on_submit():
        current_user.ad = form.ad.data.strip()
        db.session.commit()
        flash("Profil bilgileriniz güncellendi.", "success")
        return redirect(url_for("auth.profil"))
    return render_template("auth/profil.html", form=form)
