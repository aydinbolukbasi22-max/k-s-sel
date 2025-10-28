"""Bütçe planlama görünümleri."""
from datetime import date
from decimal import Decimal

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import IslemTuru, Kategori, KategoriButce
from app.modules import create_blueprint
from app.services.finance import butce_kalan_tutar

from .forms import KategoriButceFormu, KategoriFormu

bp = create_blueprint("budgeting", __name__, url_prefix="/butce")


@bp.route("/planlar", methods=["GET", "POST"])
@login_required
def planlar():
    secilen_yil = request.args.get("yil", default=date.today().year, type=int)
    secilen_ay = request.args.get("ay", default=date.today().month, type=int)

    form = KategoriButceFormu()
    form.kategori_id.choices = [
        (k.id, k.ad)
        for k in Kategori.query.filter_by(kullanici_id=current_user.id, tur=IslemTuru.GIDER).order_by(Kategori.ad)
    ]
    if form.validate_on_submit():
        plan = KategoriButce(
            kullanici_id=current_user.id,
            kategori_id=form.kategori_id.data,
            ay=form.ay.data,
            yil=form.yil.data,
            limit=form.limit.data,
        )
        db.session.add(plan)
        db.session.commit()
        flash("Bütçe planı eklendi.", "success")
        return redirect(url_for("budgeting.planlar", ay=form.ay.data, yil=form.yil.data))

    planlar = (
        KategoriButce.query.filter_by(kullanici_id=current_user.id, ay=secilen_ay, yil=secilen_yil)
        .order_by(KategoriButce.limit.desc())
        .all()
    )
    kalanlar = {plan.id: kalan for plan, kalan in butce_kalan_tutar(current_user.id, secilen_yil, secilen_ay)}
    toplam_limit = sum(Decimal(plan.limit) for plan in planlar)
    toplam_kalan = sum(kalanlar.values()) if kalanlar else Decimal("0")
    return render_template(
        "budgeting/planlar.html",
        form=form,
        planlar=planlar,
        secilen_ay=secilen_ay,
        secilen_yil=secilen_yil,
        kalanlar=kalanlar,
        toplam_limit=toplam_limit,
        toplam_kalan=toplam_kalan,
    )


@bp.route("/planlar/<int:plan_id>/sil", methods=["POST"])
@login_required
def plan_sil(plan_id: int):
    plan = KategoriButce.query.filter_by(id=plan_id, kullanici_id=current_user.id).first_or_404()
    ay = plan.ay
    yil = plan.yil
    db.session.delete(plan)
    db.session.commit()
    flash("Bütçe planı silindi.", "info")
    return redirect(url_for("budgeting.planlar", ay=ay, yil=yil))


@bp.route("/kategoriler", methods=["GET", "POST"])
@login_required
def kategoriler():
    form = KategoriFormu()
    if form.validate_on_submit():
        kategori = Kategori(
            kullanici_id=current_user.id,
            ad=form.ad.data.strip(),
            tur=IslemTuru(form.tur.data),
            renk=form.renk.data or "#0d6efd",
        )
        db.session.add(kategori)
        db.session.commit()
        flash("Kategori eklendi.", "success")
        return redirect(url_for("budgeting.kategoriler"))
    gelir_kategorileri = Kategori.query.filter_by(kullanici_id=current_user.id, tur=IslemTuru.GELIR).all()
    gider_kategorileri = Kategori.query.filter_by(kullanici_id=current_user.id, tur=IslemTuru.GIDER).all()
    return render_template(
        "budgeting/kategoriler.html",
        form=form,
        gelir_kategorileri=gelir_kategorileri,
        gider_kategorileri=gider_kategorileri,
    )
