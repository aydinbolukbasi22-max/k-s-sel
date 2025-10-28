"""Bütçe formları."""
from datetime import date

from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class KategoriButceFormu(FlaskForm):
    kategori_id = SelectField("Kategori", coerce=int, validators=[DataRequired()])
    ay = IntegerField("Ay", default=date.today().month, validators=[NumberRange(min=1, max=12)])
    yil = IntegerField("Yıl", default=date.today().year, validators=[NumberRange(min=2000, max=2100)])
    limit = DecimalField("Limit", places=2, validators=[DataRequired(), NumberRange(min=0)])
    gonder = SubmitField("Bütçeyi Kaydet")


class KategoriFormu(FlaskForm):
    ad = StringField("Kategori Adı", validators=[DataRequired(), Length(max=120)])
    tur = SelectField(
        "Tür",
        choices=[("gelir", "Gelir"), ("gider", "Gider")],
        validators=[DataRequired()],
    )
    renk = StringField("Renk Kodu", validators=[Length(max=7)])
    gonder = SubmitField("Kaydet")
