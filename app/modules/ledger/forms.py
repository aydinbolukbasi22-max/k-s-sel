"""Hesap ve işlem formları."""
from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange

from app.models import HesapTuru, IslemTuru


class HesapFormu(FlaskForm):
    ad = StringField("Hesap Adı", validators=[DataRequired(), Length(max=120)])
    tur = SelectField(
        "Hesap Türü",
        choices=[(tur.value, tur.name.replace("_", " ")) for tur in HesapTuru],
        validators=[DataRequired()],
    )
    bakiye = DecimalField("Başlangıç Bakiyesi", places=2, rounding=None, validators=[NumberRange(min=0)])
    aciklama = TextAreaField("Açıklama", validators=[Length(max=255)])
    gonder = SubmitField("Kaydet")


class IslemFormu(FlaskForm):
    tarih = DateField("Tarih", default=date.today, validators=[DataRequired()])
    hesap_id = SelectField("Hesap", coerce=int, validators=[DataRequired()])
    kategori_id = SelectField("Kategori", coerce=int, validators=[DataRequired()])
    tur = SelectField(
        "Tür",
        choices=[(tur.value, tur.name.title()) for tur in (IslemTuru.GELIR, IslemTuru.GIDER)],
        validators=[DataRequired()],
    )
    tutar = DecimalField("Tutar", places=2, validators=[DataRequired(), NumberRange(min=0)])
    aciklama = TextAreaField("Açıklama", validators=[Length(max=255)])
    gonder = SubmitField("Kaydet")


class TransferFormu(FlaskForm):
    tarih = DateField("Tarih", default=date.today, validators=[DataRequired()])
    kaynak_hesap_id = SelectField("Kaynak Hesap", coerce=int, validators=[DataRequired()])
    hedef_hesap_id = SelectField("Hedef Hesap", coerce=int, validators=[DataRequired()])
    tutar = DecimalField("Tutar", places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    aciklama = TextAreaField("Not", validators=[Length(max=255)])
    gonder = SubmitField("Transfer Yap")


class IslemFiltreFormu(FlaskForm):
    hesap_id = SelectField("Hesap", coerce=int, choices=[], validate_choice=False)
    kategori_id = SelectField("Kategori", coerce=int, choices=[], validate_choice=False)
    tur = SelectField(
        "Tür",
        choices=[("", "Tümü"), (IslemTuru.GELIR.value, "Gelir"), (IslemTuru.GIDER.value, "Gider")],
        default="",
    )
    gonder = SubmitField("Filtrele")
