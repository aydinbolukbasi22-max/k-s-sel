"""Tasarruf hedefi formları."""
from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class TasarrufHedefiFormu(FlaskForm):
    ad = StringField("Hedef Başlığı", validators=[DataRequired(), Length(max=120)])
    hedef_tutar = DecimalField("Hedef Tutarı", places=2, validators=[DataRequired(), NumberRange(min=0)])
    birikim = DecimalField("Mevcut Birikim", places=2, validators=[NumberRange(min=0)], default=0)
    hedef_tarih = DateField("Hedef Tarihi", default=date.today)
    oncelik = IntegerField("Öncelik", default=3, validators=[NumberRange(min=1, max=5)])
    aciklama = TextAreaField("Açıklama", validators=[Length(max=500)])
    gonder = SubmitField("Kaydet")
