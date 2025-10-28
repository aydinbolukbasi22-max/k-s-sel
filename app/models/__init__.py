"""Veri modelleri."""
from __future__ import annotations

from datetime import datetime, date
from enum import Enum

from flask_login import UserMixin
from sqlalchemy import Enum as SqlEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.extensions import db, login_manager


class HesapTuru(Enum):
    NAKIT = "nakit"
    BANKA = "banka"
    KREDI_KARTI = "kredi_karti"
    YATIRIM = "yatirim"


class IslemTuru(Enum):
    GELIR = "gelir"
    GIDER = "gider"
    TRANSFER = "transfer"


class HatirlaticiDonemi(Enum):
    GUNLUK = "gunluk"
    HAFTALIK = "haftalik"
    AYLIK = "aylik"
    YILLIK = "yillik"


class Kullanici(UserMixin, db.Model):
    __tablename__ = "kullanicilar"

    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(120), nullable=False)
    eposta = db.Column(db.String(255), unique=True, nullable=False)
    sifre = db.Column(db.String(255), nullable=False)
    olusturulma = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    hesaplar = relationship("Hesap", back_populates="kullanici", cascade="all, delete-orphan")
    kategoriler = relationship("Kategori", back_populates="kullanici", cascade="all, delete-orphan")
    islemler = relationship("Islem", back_populates="kullanici", cascade="all, delete-orphan")
    butce_planlari = relationship("KategoriButce", back_populates="kullanici", cascade="all, delete-orphan")
    hedefler = relationship("TasarrufHedefi", back_populates="kullanici", cascade="all, delete-orphan")
    borclar = relationship("Borc", back_populates="kullanici", cascade="all, delete-orphan")
    hatirlaticilar = relationship("Hatirlatici", back_populates="kullanici", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Kullanici {self.eposta}>"


@login_manager.user_loader
def load_user(user_id: str) -> Kullanici | None:
    return Kullanici.query.get(int(user_id))


class Hesap(db.Model):
    __tablename__ = "hesaplar"

    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)
    ad = db.Column(db.String(120), nullable=False)
    tur = db.Column(SqlEnum(HesapTuru), nullable=False, default=HesapTuru.NAKIT)
    bakiye = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    aciklama = db.Column(db.String(255))
    olusturulma = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    kullanici = relationship("Kullanici", back_populates="hesaplar")
    islemler = relationship("Islem", back_populates="hesap")
    borclar = relationship("Borc", back_populates="hesap")

    __table_args__ = (UniqueConstraint("kullanici_id", "ad", name="uq_hesap_ad"),)

    def __repr__(self) -> str:
        return f"<Hesap {self.ad} ({self.tur.value})>"


class Kategori(db.Model):
    __tablename__ = "kategoriler"

    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)
    ad = db.Column(db.String(120), nullable=False)
    tur = db.Column(SqlEnum(IslemTuru), nullable=False)
    renk = db.Column(db.String(7), default="#0d6efd")

    kullanici = relationship("Kullanici", back_populates="kategoriler")
    islemler = relationship("Islem", back_populates="kategori")
    butce_planlari = relationship("KategoriButce", back_populates="kategori")

    __table_args__ = (UniqueConstraint("kullanici_id", "ad", "tur", name="uq_kategori"),)

    def __repr__(self) -> str:
        return f"<Kategori {self.ad} ({self.tur.value})>"


class Islem(db.Model):
    __tablename__ = "islemler"

    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)
    hesap_id = db.Column(db.Integer, db.ForeignKey("hesaplar.id"), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey("kategoriler.id"))
    tur = db.Column(SqlEnum(IslemTuru), nullable=False)
    tutar = db.Column(db.Numeric(12, 2), nullable=False)
    tarih = db.Column(db.Date, default=date.today, nullable=False)
    aciklama = db.Column(db.String(255))

    kullanici = relationship("Kullanici", back_populates="islemler")
    hesap = relationship("Hesap", back_populates="islemler")
    kategori = relationship("Kategori", back_populates="islemler")


class KategoriButce(db.Model):
    __tablename__ = "kategori_butceleri"

    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey("kategoriler.id"), nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    yil = db.Column(db.Integer, nullable=False)
    limit = db.Column(db.Numeric(12, 2), nullable=False)

    kullanici = relationship("Kullanici", back_populates="butce_planlari")
    kategori = relationship("Kategori", back_populates="butce_planlari")

    __table_args__ = (UniqueConstraint("kullanici_id", "kategori_id", "ay", "yil", name="uq_butce_plan"),)


class TasarrufHedefi(db.Model):
    __tablename__ = "tasarruf_hedefleri"

    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)
    ad = db.Column(db.String(120), nullable=False)
    hedef_tutar = db.Column(db.Numeric(12, 2), nullable=False)
    birikim = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    hedef_tarih = db.Column(db.Date)
    oncelik = db.Column(db.Integer, default=3)
    aciklama = db.Column(db.Text)

    kullanici = relationship("Kullanici", back_populates="hedefler")


class Borc(db.Model):
    __tablename__ = "borclar"

    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)
    hesap_id = db.Column(db.Integer, db.ForeignKey("hesaplar.id"))
    ad = db.Column(db.String(120), nullable=False)
    toplam_tutar = db.Column(db.Numeric(12, 2), nullable=False)
    kalan_tutar = db.Column(db.Numeric(12, 2), nullable=False)
    faiz_orani = db.Column(db.Numeric(5, 2), default=0)
    son_odeme_tarihi = db.Column(db.Date)
    minimum_odeme = db.Column(db.Numeric(12, 2))

    kullanici = relationship("Kullanici", back_populates="borclar")
    hesap = relationship("Hesap", back_populates="borclar")
    odemeler = relationship("BorcOdeme", back_populates="borc", cascade="all, delete-orphan")


class BorcOdeme(db.Model):
    __tablename__ = "borc_odemeleri"

    id = db.Column(db.Integer, primary_key=True)
    borc_id = db.Column(db.Integer, db.ForeignKey("borclar.id"), nullable=False)
    tutar = db.Column(db.Numeric(12, 2), nullable=False)
    tarih = db.Column(db.Date, default=date.today, nullable=False)
    aciklama = db.Column(db.String(255))

    borc = relationship("Borc", back_populates="odemeler")


class Hatirlatici(db.Model):
    __tablename__ = "hatirlaticilar"

    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)
    baslik = db.Column(db.String(150), nullable=False)
    tutar = db.Column(db.Numeric(12, 2))
    son_tarih = db.Column(db.Date, nullable=False)
    donem = db.Column(SqlEnum(HatirlaticiDonemi), nullable=False, default=HatirlaticiDonemi.AYLIK)
    aktif = db.Column(db.Boolean, default=True)

    kullanici = relationship("Kullanici", back_populates="hatirlaticilar")
    kayitlar = relationship("HatirlaticiKaydi", back_populates="hatirlatici", cascade="all, delete-orphan")


class HatirlaticiKaydi(db.Model):
    __tablename__ = "hatirlatici_kayitlari"

    id = db.Column(db.Integer, primary_key=True)
    hatirlatici_id = db.Column(db.Integer, db.ForeignKey("hatirlaticilar.id"), nullable=False)
    gerceklesme_tarihi = db.Column(db.Date, nullable=False, default=date.today)
    not_metni = db.Column(db.String(255))

    hatirlatici = relationship("Hatirlatici", back_populates="kayitlar")
