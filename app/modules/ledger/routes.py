"""Hesap ve işlem görünümleri."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from io import StringIO

from flask import Response, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Hesap, HesapTuru, Islem, IslemTuru, Kategori
from app.modules import create_blueprint
from app.services.finance import kategori_harcama_ozeti, hesap_bakiye_guncelle

from .forms import HesapFormu, IslemFiltreFormu, IslemFormu, TransferFormu

bp = create_blueprint("ledger", __name__, url_prefix="/defter")


@bp.route("/hesaplar", methods=["GET", "POST"])
@login_required
def hesap_listesi():
    form = HesapFormu()
    if form.validate_on_submit():
        hesap = Hesap(
            kullanici_id=current_user.id,
            ad=form.ad.data.strip(),
            tur=HesapTuru(form.tur.data),
            bakiye=form.bakiye.data or 0,
            aciklama=form.aciklama.data,
        )
        db.session.add(hesap)
        db.session.commit()
        flash("Hesap başarıyla oluşturuldu.", "success")
        return redirect(url_for("ledger.hesap_listesi"))
    hesaplar = Hesap.query.filter_by(kullanici_id=current_user.id).all()
    toplam_bakiye = sum(Decimal(h.bakiye) for h in hesaplar)
    return render_template("ledger/hesaplar.html", form=form, hesaplar=hesaplar, toplam_bakiye=toplam_bakiye)


@bp.route("/hesaplar/<int:hesap_id>/duzenle", methods=["GET", "POST"])
@login_required
def hesap_duzenle(hesap_id: int):
    hesap = Hesap.query.filter_by(id=hesap_id, kullanici_id=current_user.id).first_or_404()
    form = HesapFormu(obj=hesap)
    if form.validate_on_submit():
        hesap.ad = form.ad.data.strip()
        hesap.tur = HesapTuru(form.tur.data)
        hesap.bakiye = form.bakiye.data or 0
        hesap.aciklama = form.aciklama.data
        db.session.commit()
        flash("Hesap güncellendi.", "success")
        return redirect(url_for("ledger.hesap_listesi"))
    return render_template("ledger/hesap_duzenle.html", form=form, hesap=hesap)


@bp.route("/hesaplar/<int:hesap_id>/sil", methods=["POST"])
@login_required
def hesap_sil(hesap_id: int):
    hesap = Hesap.query.filter_by(id=hesap_id, kullanici_id=current_user.id).first_or_404()
    if hesap.islemler:
        flash("Bu hesaba bağlı işlemler olduğu için silinemez.", "warning")
        return redirect(url_for("ledger.hesap_listesi"))
    db.session.delete(hesap)
    db.session.commit()
    flash("Hesap silindi.", "info")
    return redirect(url_for("ledger.hesap_listesi"))


@bp.route("/islemler", methods=["GET", "POST"])
@login_required
def islem_listesi():
    form = IslemFormu()
    form.hesap_id.choices = [(h.id, h.ad) for h in Hesap.query.filter_by(kullanici_id=current_user.id)]
    form.kategori_id.choices = [
        (k.id, f"{k.ad} ({'Gelir' if k.tur == IslemTuru.GELIR else 'Gider'})")
        for k in Kategori.query.filter_by(kullanici_id=current_user.id).order_by(Kategori.ad)
    ]
    if form.validate_on_submit():
        islem = Islem(
            kullanici_id=current_user.id,
            hesap_id=form.hesap_id.data,
            kategori_id=form.kategori_id.data,
            tur=IslemTuru(form.tur.data),
            tutar=form.tutar.data,
            tarih=form.tarih.data,
            aciklama=form.aciklama.data,
        )
        db.session.add(islem)
        db.session.flush()
        hesap_bakiye_guncelle(islem.hesap)
        db.session.commit()
        flash("İşlem kaydedildi.", "success")
        return redirect(url_for("ledger.islem_listesi"))

    filtre_formu = IslemFiltreFormu(request.args)
    hesap_choices = [(0, "Tümü")] + [(h.id, h.ad) for h in Hesap.query.filter_by(kullanici_id=current_user.id)]
    kategori_choices = [(0, "Tümü")] + [
        (k.id, k.ad) for k in Kategori.query.filter_by(kullanici_id=current_user.id).order_by(Kategori.ad)
    ]
    filtre_formu.hesap_id.choices = hesap_choices
    filtre_formu.kategori_id.choices = kategori_choices

    sorgu = Islem.query.filter_by(kullanici_id=current_user.id)
    if filtre_formu.validate():
        if filtre_formu.hesap_id.data:
            sorgu = sorgu.filter_by(hesap_id=filtre_formu.hesap_id.data)
        if filtre_formu.kategori_id.data:
            sorgu = sorgu.filter_by(kategori_id=filtre_formu.kategori_id.data)
        if filtre_formu.tur.data:
            sorgu = sorgu.filter_by(tur=IslemTuru(filtre_formu.tur.data))
    islemler = sorgu.order_by(Islem.tarih.desc()).all()
    aylik_ozet = kategori_harcama_ozeti(current_user.id, date.today().year, date.today().month)
    return render_template(
        "ledger/islemler.html",
        form=form,
        filtre_formu=filtre_formu,
        islemler=islemler,
        aylik_ozet=aylik_ozet,
    )


@bp.route("/islemler/<int:islem_id>/duzenle", methods=["GET", "POST"])
@login_required
def islem_duzenle(islem_id: int):
    islem = Islem.query.filter_by(id=islem_id, kullanici_id=current_user.id).first_or_404()
    form = IslemFormu(obj=islem)
    form.hesap_id.choices = [(h.id, h.ad) for h in Hesap.query.filter_by(kullanici_id=current_user.id)]
    form.kategori_id.choices = [
        (k.id, f"{k.ad} ({'Gelir' if k.tur == IslemTuru.GELIR else 'Gider'})")
        for k in Kategori.query.filter_by(kullanici_id=current_user.id).order_by(Kategori.ad)
    ]
    if form.validate_on_submit():
        onceki_hesap = islem.hesap
        islem.hesap_id = form.hesap_id.data
        islem.kategori_id = form.kategori_id.data
        islem.tur = IslemTuru(form.tur.data)
        islem.tutar = form.tutar.data
        islem.tarih = form.tarih.data
        islem.aciklama = form.aciklama.data
        db.session.flush()
        hesap_bakiye_guncelle(islem.hesap)
        if onceki_hesap.id != islem.hesap_id:
            hesap_bakiye_guncelle(onceki_hesap)
        db.session.commit()
        flash("İşlem güncellendi.", "success")
        return redirect(url_for("ledger.islem_listesi"))
    return render_template("ledger/islem_duzenle.html", form=form, islem=islem)


@bp.route("/islemler/<int:islem_id>/sil", methods=["POST"])
@login_required
def islem_sil(islem_id: int):
    islem = Islem.query.filter_by(id=islem_id, kullanici_id=current_user.id).first_or_404()
    hesap = islem.hesap
    db.session.delete(islem)
    db.session.flush()
    hesap_bakiye_guncelle(hesap)
    db.session.commit()
    flash("İşlem silindi.", "info")
    return redirect(url_for("ledger.islem_listesi"))


@bp.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    form = TransferFormu()
    hesaplar = Hesap.query.filter_by(kullanici_id=current_user.id).all()
    form.kaynak_hesap_id.choices = [(h.id, h.ad) for h in hesaplar]
    form.hedef_hesap_id.choices = [(h.id, h.ad) for h in hesaplar]
    if form.validate_on_submit():
        if form.kaynak_hesap_id.data == form.hedef_hesap_id.data:
            flash("Kaynak ve hedef hesap aynı olamaz.", "warning")
            return redirect(url_for("ledger.transfer"))
        kaynak = Hesap.query.get(form.kaynak_hesap_id.data)
        hedef = Hesap.query.get(form.hedef_hesap_id.data)
        tutar = Decimal(form.tutar.data)
        if kaynak.bakiye < tutar:
            flash("Yetersiz bakiye.", "danger")
            return redirect(url_for("ledger.transfer"))
        kaynak.bakiye -= tutar
        hedef.bakiye += tutar
        db.session.commit()
        flash("Transfer tamamlandı.", "success")
        return redirect(url_for("ledger.hesap_listesi"))
    return render_template("ledger/transfer.html", form=form)


@bp.route("/islemler/csv")
@login_required
def islemleri_indir():
    islemler = Islem.query.filter_by(kullanici_id=current_user.id).order_by(Islem.tarih).all()
    dosya = StringIO()
    dosya.write("Tarih,Tur,Hesap,Kategori,Tutar,Açıklama\n")
    for islem in islemler:
        dosya.write(
            f"{islem.tarih:%d/%m/%Y},{islem.tur.value},{islem.hesap.ad},{islem.kategori.ad if islem.kategori else ''},{islem.tutar},{islem.aciklama or ''}\n"
        )
    dosya.seek(0)
    return Response(
        dosya.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=islemler.csv"},
    )
