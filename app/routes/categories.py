from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from .. import db
from ..forms import KategoriFormu
from ..models import Kategori


categories_bp = Blueprint("categories", __name__, url_prefix="/kategoriler")


@categories_bp.route("/", methods=["GET", "POST"])
@login_required
def listele():
    form = KategoriFormu()
    kategoriler = Kategori.query.filter_by(kullanici_id=current_user.id).order_by(Kategori.ad).all()

    if form.validate_on_submit():
        kategori = Kategori(
            ad=form.ad.data,
            aciklama=form.aciklama.data,
            kullanici_id=current_user.id,
        )
        db.session.add(kategori)
        db.session.commit()
        flash("Kategori eklendi.", "success")
        return redirect(url_for("categories.listele"))

    return render_template("categories/listele.html", form=form, kategoriler=kategoriler, baslik="Kategoriler")


@categories_bp.route("/<int:kategori_id>/sil", methods=["POST"])
@login_required
def sil(kategori_id):
    kategori = Kategori.query.filter_by(id=kategori_id, kullanici_id=current_user.id).first_or_404()
    db.session.delete(kategori)
    db.session.commit()
    flash("Kategori silindi.", "info")
    return redirect(url_for("categories.listele"))
