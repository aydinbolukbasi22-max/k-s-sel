"""Ana kontrol paneli."""
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from flask import render_template
from flask_login import current_user, login_required

from app.models import Hesap, Islem, KategoriButce, TasarrufHedefi
from app.modules import create_blueprint
from app.services.finance import aylik_islem_ozeti, hatirlatici_sayaci, nakit_akisi_verisi

bp = create_blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def ozet():
    yil = date.today().year
    ay = date.today().month
    hesaplar = Hesap.query.filter_by(kullanici_id=current_user.id).order_by(Hesap.olusturulma.desc()).all()
    butce_planlari = KategoriButce.query.filter_by(kullanici_id=current_user.id, yil=yil, ay=ay).all()
    hedefler = TasarrufHedefi.query.filter_by(kullanici_id=current_user.id).all()
    ozet = SimpleNamespace(**aylik_islem_ozeti(current_user.id, yil, ay))
    toplam_bakiye = sum(Decimal(h.bakiye) for h in hesaplar)
    toplam_hedef = sum(Decimal(h.hedef_tutar) for h in hedefler)
    gerceklesme = sum(Decimal(h.birikim) for h in hedefler)
    nakit = nakit_akisi_verisi(current_user.id, yil)
    hatirlatici_durumu = SimpleNamespace(**hatirlatici_sayaci(current_user.hatirlaticilar))
    son_islemler = (
        Islem.query.filter_by(kullanici_id=current_user.id)
        .order_by(Islem.tarih.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "dashboard/ozet.html",
        hesaplar=hesaplar,
        ozet=ozet,
        toplam_bakiye=toplam_bakiye,
        toplam_hedef=toplam_hedef,
        gerceklesme=gerceklesme,
        butce_planlari=butce_planlari,
        nakit=nakit,
        hatirlatici_durumu=hatirlatici_durumu,
        son_islemler=son_islemler,
        yil=yil,
    )
