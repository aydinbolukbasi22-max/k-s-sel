from sqlalchemy.exc import IntegrityError
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from .. import db
from ..forms import ButceFormu
from ..models import Butce, Kategori


budgets_bp = Blueprint("budgets", __name__, url_prefix="/butceler")


@budgets_bp.route("/", methods=["GET", "POST"])
@login_required
def listele():
    form = ButceFormu()
    form.kategori_id.choices = [
        (kategori.id, kategori.ad)
        for kategori in Kategori.query.filter_by(kullanici_id=current_user.id).order_by(Kategori.ad)
    ]

    butceler = (
        Butce.query.filter_by(kullanici_id=current_user.id)
        .order_by(Butce.yil.desc(), Butce.ay.desc())
        .all()
    )

    if form.validate_on_submit():
        butce = Butce(
            yil=form.yil.data,
            ay=form.ay.data,
            kategori_id=form.kategori_id.data,
            tutar=form.tutar.data,
            kullanici_id=current_user.id,
        )
        db.session.add(butce)
        try:
            db.session.commit()
            flash("Bütçe kaydedildi.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Bu kategori için belirtilen ay ve yıl için zaten bütçe mevcut.", "warning")
        return redirect(url_for("budgets.listele"))

    return render_template("budgets/listele.html", form=form, butceler=butceler, baslik="Bütçeler")


@budgets_bp.route("/<int:butce_id>/sil", methods=["POST"])
@login_required
def sil(butce_id):
    butce = Butce.query.filter_by(id=butce_id, kullanici_id=current_user.id).first_or_404()
    db.session.delete(butce)
    db.session.commit()
    flash("Bütçe silindi.", "info")
    return redirect(url_for("budgets.listele"))
