from datetime import datetime, date
from sqlalchemy import func
from flask_login import UserMixin

from .. import db, login_manager

class ZamanDamgasiMixin:
    olusturulma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    guncellenme_tarihi = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Kullanici(UserMixin, ZamanDamgasiMixin, db.Model):
    __tablename__ = "kullanicilar"

    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(120), nullable=False)
    eposta = db.Column(db.String(120), unique=True, nullable=False)
    sifre = db.Column(db.String(255), nullable=False)

    hesaplar = db.relationship("Hesap", backref="kullanici", lazy=True)
    islemler = db.relationship("Islem", backref="kullanici", lazy=True)
    butceler = db.relationship("Butce", backref="kullanici", lazy=True)

    def __repr__(self):
        return f"<Kullanici {self.eposta}>"

@login_manager.user_loader
def kullanici_yukleyici(kullanici_id):
    return Kullanici.query.get(int(kullanici_id))

class Hesap(ZamanDamgasiMixin, db.Model):
    __tablename__ = "hesaplar"

    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(120), nullable=False)
    bakiye = db.Column(db.Numeric(12, 2), default=0)
    hesap_turu = db.Column(db.String(50), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)

    islemler = db.relationship("Islem", backref="hesap", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Hesap {self.ad}>"

class Kategori(ZamanDamgasiMixin, db.Model):
    __tablename__ = "kategoriler"

    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(120), nullable=False)
    aciklama = db.Column(db.String(255))
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)

    islemler = db.relationship("Islem", backref="kategori", lazy=True, cascade="all, delete-orphan")
    butceler = db.relationship("Butce", backref="kategori", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Kategori {self.ad}>"

class Islem(ZamanDamgasiMixin, db.Model):
    __tablename__ = "islemler"

    id = db.Column(db.Integer, primary_key=True)
    islem_turu = db.Column(db.String(20), nullable=False)  # gelir veya gider
    tutar = db.Column(db.Numeric(12, 2), nullable=False)
    tarih = db.Column(db.Date, nullable=False, default=date.today)
    aciklama = db.Column(db.String(255))

    hesap_id = db.Column(db.Integer, db.ForeignKey("hesaplar.id"), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey("kategoriler.id"), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)

    def __repr__(self):
        return f"<Islem {self.islem_turu} {self.tutar}>"

class Butce(ZamanDamgasiMixin, db.Model):
    __tablename__ = "butceler"

    id = db.Column(db.Integer, primary_key=True)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    tutar = db.Column(db.Numeric(12, 2), nullable=False)

    kategori_id = db.Column(db.Integer, db.ForeignKey("kategoriler.id"), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("yil", "ay", "kategori_id", name="uc_butce_kategori_ay"),
    )

    @property
    def kalan_tutar(self):
        harcama = (
            db.session.query(func.coalesce(func.sum(Islem.tutar), 0))
            .filter(
                Islem.kategori_id == self.kategori_id,
                Islem.kullanici_id == self.kullanici_id,
                Islem.islem_turu == "gider",
                func.strftime('%Y', Islem.tarih) == str(self.yil),
                func.strftime('%m', Islem.tarih) == f"{self.ay:02d}",
            )
            .scalar()
        )
        return float(self.tutar) - float(harcama)

    def __repr__(self):
        return f"<Butce {self.yil}-{self.ay} {self.tutar}>"
