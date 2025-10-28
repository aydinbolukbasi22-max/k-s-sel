"""Hatırlatıcı formları."""
from datetime import date

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, DecimalField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

from app.models import HatirlaticiDonemi


class HatirlaticiFormu(FlaskForm):
    baslik = StringField("Başlık", validators=[DataRequired(), Length(max=150)])
    tutar = DecimalField("Tutar", places=2, validators=[NumberRange(min=0)], default=0)
    son_tarih = DateField("Son Tarih", default=date.today, validators=[DataRequired()])
    donem = SelectField(
        "Tekrar Sıklığı",
        choices=[(donem.value, donem.name.title()) for donem in HatirlaticiDonemi],
        validators=[DataRequired()],
    )
    aktif = BooleanField("Aktif", default=True)
    gonder = SubmitField("Kaydet")


class HatirlaticiTamamlamaFormu(FlaskForm):
    not_metni = StringField("Not", validators=[Length(max=255)])
    gonder = SubmitField("Tamamlandı")
