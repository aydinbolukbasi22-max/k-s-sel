from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from .. import db
from ..models import Islem, Hesap, Butce, Kategori


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def anasayfa():
    bugun = date.today()
    ay_baslangic = bugun.replace(day=1)
    ay_isimleri = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    ay_adi = ay_isimleri[bugun.month - 1]

    toplam_gelir = (
        db.session.query(func.coalesce(func.sum(Islem.tutar), 0))
        .filter(
            Islem.kullanici_id == current_user.id,
            Islem.islem_turu == "gelir",
            Islem.tarih >= ay_baslangic,
            Islem.tarih <= bugun,
        )
        .scalar()
    )

    toplam_gider = (
        db.session.query(func.coalesce(func.sum(Islem.tutar), 0))
        .filter(
            Islem.kullanici_id == current_user.id,
            Islem.islem_turu == "gider",
            Islem.tarih >= ay_baslangic,
            Islem.tarih <= bugun,
        )
        .scalar()
    )

    hesaplar = Hesap.query.filter_by(kullanici_id=current_user.id).all()
    butceler = (
        Butce.query.filter_by(kullanici_id=current_user.id, yil=bugun.year, ay=bugun.month)
        .join(Kategori)
        .all()
    )

    kategori_ozet = (
        db.session.query(Kategori.ad, func.coalesce(func.sum(Islem.tutar), 0).label("toplam"))
        .join(Islem, Islem.kategori_id == Kategori.id)
        .filter(
            Kategori.kullanici_id == current_user.id,
            Islem.islem_turu == "gider",
            Islem.tarih >= ay_baslangic,
            Islem.tarih <= bugun,
        )
        .group_by(Kategori.ad)
        .all()
    )

    net_durum = float(toplam_gelir) - float(toplam_gider)

    grafik_verisi = {
        "etiketler": [kategori for kategori, _ in kategori_ozet],
        "degerler": [float(toplam) for _, toplam in kategori_ozet],
    }

    return render_template(
        "dashboard.html",
        toplam_gelir=float(toplam_gelir),
        toplam_gider=float(toplam_gider),
        net_durum=net_durum,
        hesaplar=hesaplar,
        butceler=butceler,
        bugun=bugun,
        ay_adi=ay_adi,
        grafik_verisi=grafik_verisi,
    )
