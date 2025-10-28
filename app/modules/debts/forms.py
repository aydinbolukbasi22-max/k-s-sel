"""Borç yönetimi formları."""
from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class BorcFormu(FlaskForm):
    ad = StringField("Borç Başlığı", validators=[DataRequired(), Length(max=120)])
    hesap_id = SelectField("İlişkili Hesap", coerce=int, validators=[Optional()])
    toplam_tutar = DecimalField("Toplam Tutar", places=2, validators=[DataRequired(), NumberRange(min=0)])
    kalan_tutar = DecimalField("Kalan Tutar", places=2, validators=[DataRequired(), NumberRange(min=0)])
    faiz_orani = DecimalField("Faiz Oranı (%)", places=2, validators=[NumberRange(min=0)], default=0)
    son_odeme_tarihi = DateField("Son Ödeme Tarihi", default=date.today, validators=[Optional()])
    minimum_odeme = DecimalField("Asgari Ödeme", places=2, validators=[NumberRange(min=0)], default=0)
    aciklama = TextAreaField("Açıklama", validators=[Length(max=255)])
    gonder = SubmitField("Kaydet")


class BorcOdemeFormu(FlaskForm):
    tutar = DecimalField("Ödenen Tutar", places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    tarih = DateField("Ödeme Tarihi", default=date.today, validators=[DataRequired()])
    aciklama = StringField("Not", validators=[Length(max=255)])
    gonder = SubmitField("Ödemeyi Kaydet")
