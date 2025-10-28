import csv
from io import StringIO
from datetime import date
from flask import Blueprint, render_template, request, Response
from flask_login import login_required, current_user
from sqlalchemy import func

from .. import db
from ..forms import RaporFiltreFormu
from ..models import Islem, Kategori, Hesap


reports_bp = Blueprint("reports", __name__, url_prefix="/raporlar")


@reports_bp.route("/", methods=["GET", "POST"])
@login_required
def raporlar():
    form = RaporFiltreFormu(request.form)
    kategoriler = Kategori.query.filter_by(kullanici_id=current_user.id).order_by(Kategori.ad).all()
    hesaplar = Hesap.query.filter_by(kullanici_id=current_user.id).order_by(Hesap.ad).all()

    form.kategori_id.choices = [(0, "Tüm Kategoriler")] + [(k.id, k.ad) for k in kategoriler]
    form.hesap_id.choices = [(0, "Tüm Hesaplar")] + [(h.id, h.ad) for h in hesaplar]

    if request.method == "GET":
        form.baslangic.data = date.today().replace(day=1)
        form.bitis.data = date.today()
        form.kategori_id.data = 0
        form.hesap_id.data = 0

    filtreler = [Islem.kullanici_id == current_user.id]

    if form.validate_on_submit() or request.method == "GET":
        baslangic = form.baslangic.data
        bitis = form.bitis.data
        kategori_id = form.kategori_id.data
        hesap_id = form.hesap_id.data

        if baslangic:
            filtreler.append(Islem.tarih >= baslangic)
        if bitis:
            filtreler.append(Islem.tarih <= bitis)
        if kategori_id and kategori_id != 0:
            filtreler.append(Islem.kategori_id == kategori_id)
        if hesap_id and hesap_id != 0:
            filtreler.append(Islem.hesap_id == hesap_id)

    sorgu = Islem.query.filter(*filtreler).order_by(Islem.tarih.desc())
    islemler = sorgu.all()

    toplam_gelir = sum(float(islem.tutar) for islem in islemler if islem.islem_turu == "gelir")
    toplam_gider = sum(float(islem.tutar) for islem in islemler if islem.islem_turu == "gider")
    net_durum = toplam_gelir - toplam_gider

    kategori_ozet = (
        db.session.query(Kategori.ad, Islem.islem_turu, func.coalesce(func.sum(Islem.tutar), 0))
        .join(Kategori, Kategori.id == Islem.kategori_id)
        .filter(*filtreler)
        .group_by(Kategori.ad, Islem.islem_turu)
        .all()
    )

    grafik_verisi = {}
    for kategori, tur, toplam in kategori_ozet:
        grafik_verisi.setdefault(kategori, {"gelir": 0, "gider": 0})
        grafik_verisi[kategori][tur] = float(toplam)

    if request.args.get("export") == "csv":
        csv_buffer = StringIO()
        yazici = csv.writer(csv_buffer)
        yazici.writerow(["Tarih", "İşlem Türü", "Kategori", "Hesap", "Tutar", "Açıklama"])
        for islem in reversed(islemler):
            yazici.writerow([
                islem.tarih.strftime("%d/%m/%Y"),
                "Gelir" if islem.islem_turu == "gelir" else "Gider",
                islem.kategori.ad,
                islem.hesap.ad,
                f"{float(islem.tutar):.2f}",
                islem.aciklama or "",
            ])
        csv_buffer.seek(0)
        return Response(
            csv_buffer.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=rapor.csv"},
        )

    return render_template(
        "reports/raporlar.html",
        form=form,
        islemler=islemler,
        toplam_gelir=toplam_gelir,
        toplam_gider=toplam_gider,
        net_durum=net_durum,
        grafik_verisi=grafik_verisi,
    )
