"""Finansal hesaplama ve yardımcı fonksiyonlar."""
from __future__ import annotations

from calendar import monthrange
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Iterable, List, Tuple

from app.extensions import db
from app.models import (
    Hatirlatici,
    HatirlaticiDonemi,
    Hesap,
    Islem,
    IslemTuru,
    Kategori,
    KategoriButce,
    TasarrufHedefi,
)


@dataclass
class NakitAkisSatiri:
    etiket: str
    gelir: Decimal
    gider: Decimal


def aylik_islem_ozeti(kullanici_id: int, yil: int, ay: int) -> Dict[str, Decimal]:
    gelir = Decimal("0")
    gider = Decimal("0")
    islemler = (
        Islem.query.filter_by(kullanici_id=kullanici_id)
        .filter(db.extract("year", Islem.tarih) == yil)
        .filter(db.extract("month", Islem.tarih) == ay)
        .all()
    )
    for islem in islemler:
        if islem.tur == IslemTuru.GELIR:
            gelir += Decimal(islem.tutar)
        elif islem.tur == IslemTuru.GIDER:
            gider += Decimal(islem.tutar)
    return {"gelir": gelir, "gider": gider, "net": gelir - gider}


def kategori_harcama_ozeti(kullanici_id: int, yil: int, ay: int) -> Dict[str, Decimal]:
    harcamalar: Dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    islemler = (
        Islem.query.filter_by(kullanici_id=kullanici_id, tur=IslemTuru.GIDER)
        .filter(db.extract("year", Islem.tarih) == yil)
        .filter(db.extract("month", Islem.tarih) == ay)
        .all()
    )
    for islem in islemler:
        ad = islem.kategori.ad if islem.kategori else "Genel"
        harcamalar[ad] += Decimal(islem.tutar)
    return dict(harcamalar)


def butce_kalan_tutar(kullanici_id: int, yil: int, ay: int) -> List[Tuple[KategoriButce, Decimal]]:
    sonuc: List[Tuple[KategoriButce, Decimal]] = []
    planlar = KategoriButce.query.filter_by(kullanici_id=kullanici_id, yil=yil, ay=ay).all()
    for plan in planlar:
        harcanan = (
            db.session.query(db.func.coalesce(db.func.sum(Islem.tutar), 0))
            .filter_by(kullanici_id=kullanici_id, kategori_id=plan.kategori_id, tur=IslemTuru.GIDER)
            .filter(db.extract("year", Islem.tarih) == yil)
            .filter(db.extract("month", Islem.tarih) == ay)
            .scalar()
        )
        kalan = Decimal(plan.limit) - Decimal(harcanan)
        sonuc.append((plan, kalan))
    return sonuc


def hesap_bakiye_guncelle(hesap: Hesap) -> None:
    toplam = (
        db.session.query(
            db.func.coalesce(db.func.sum(
                db.case(
                    (Islem.tur == IslemTuru.GELIR, Islem.tutar),
                    (Islem.tur == IslemTuru.GIDER, -Islem.tutar),
                    else_=0,
                )
            )),
        )
        .filter_by(hesap_id=hesap.id)
        .scalar()
        or 0
    )
    hesap.bakiye = toplam


def varsayilan_kategorileri_olustur(kullanici_id: int) -> None:
    mevcut = Kategori.query.filter_by(kullanici_id=kullanici_id).count()
    if mevcut:
        return
    sablonlar = [
        ("Maaş", IslemTuru.GELIR, "#198754"),
        ("Ek Gelir", IslemTuru.GELIR, "#20c997"),
        ("Gıda", IslemTuru.GIDER, "#d63384"),
        ("Ulaşım", IslemTuru.GIDER, "#fd7e14"),
        ("Kira", IslemTuru.GIDER, "#6f42c1"),
        ("Eğlence", IslemTuru.GIDER, "#0d6efd"),
    ]
    for ad, tur, renk in sablonlar:
        db.session.add(Kategori(kullanici_id=kullanici_id, ad=ad, tur=tur, renk=renk))
    db.session.commit()


def hatirlatici_son_tarih_guncelle(hatirlatici: Hatirlatici) -> None:
    if hatirlatici.donem == HatirlaticiDonemi.GUNLUK:
        hatirlatici.son_tarih += timedelta(days=1)
    elif hatirlatici.donem == HatirlaticiDonemi.HAFTALIK:
        hatirlatici.son_tarih += timedelta(days=7)
    elif hatirlatici.donem == HatirlaticiDonemi.AYLIK:
        ay = hatirlatici.son_tarih.month + 1
        yil = hatirlatici.son_tarih.year + (ay - 1) // 12
        ay = ((ay - 1) % 12) + 1
        gun = min(hatirlatici.son_tarih.day, monthrange(yil, ay)[1])
        hatirlatici.son_tarih = date(yil, ay, gun)
    else:
        try:
            hatirlatici.son_tarih = hatirlatici.son_tarih.replace(year=hatirlatici.son_tarih.year + 1)
        except ValueError:
            hatirlatici.son_tarih += timedelta(days=365)


def hedef_tamamlanma_orani(hedef: TasarrufHedefi) -> int:
    if not hedef.hedef_tutar:
        return 0
    oran = (Decimal(hedef.birikim) / Decimal(hedef.hedef_tutar)) * 100
    return min(int(oran), 100)


def nakit_akisi_verisi(kullanici_id: int, yil: int) -> List[NakitAkisSatiri]:
    sonuc: List[NakitAkisSatiri] = []
    for ay in range(1, 13):
        ozet = aylik_islem_ozeti(kullanici_id, yil, ay)
        sonuc.append(
            NakitAkisSatiri(
                etiket=f"{ay:02d}/{yil}",
                gelir=ozet["gelir"],
                gider=ozet["gider"],
            )
        )
    return sonuc


def toplam_varlik_borclar(kullanici_id: int) -> Tuple[Decimal, Decimal]:
    hesap_toplam = (
        db.session.query(db.func.coalesce(db.func.sum(Hesap.bakiye), 0))
        .filter_by(kullanici_id=kullanici_id)
        .scalar()
    )
    borc_toplam = (
        db.session.query(db.func.coalesce(db.func.sum(Islem.tutar), 0))
        .filter_by(kullanici_id=kullanici_id, tur=IslemTuru.GIDER)
        .scalar()
    )
    return Decimal(hesap_toplam), Decimal(borc_toplam)


def hatirlatici_sayaci(hatirlaticilar: Iterable[Hatirlatici]) -> Dict[str, int]:
    sayac = {"bugun": 0, "gecmis": 0, "yaklasan": 0}
    bugun = date.today()
    for item in hatirlaticilar:
        if item.son_tarih < bugun:
            sayac["gecmis"] += 1
        elif item.son_tarih == bugun:
            sayac["bugun"] += 1
        else:
            sayac["yaklasan"] += 1
    return sayac
