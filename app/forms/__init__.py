from datetime import date
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    DecimalField,
    SelectField,
    DateField,
    TextAreaField,
    IntegerField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class KayitFormu(FlaskForm):
    ad = StringField("Ad Soyad", validators=[DataRequired(), Length(max=120)])
    eposta = StringField("E-posta", validators=[DataRequired(), Email(), Length(max=120)])
    sifre = PasswordField("Şifre", validators=[DataRequired(), Length(min=6)])
    sifre_tekrar = PasswordField(
        "Şifre (Tekrar)",
        validators=[DataRequired(), EqualTo("sifre", message="Şifreler eşleşmiyor.")],
    )
    submit = SubmitField("Kayıt Ol")


class GirisFormu(FlaskForm):
    eposta = StringField("E-posta", validators=[DataRequired(), Email()])
    sifre = PasswordField("Şifre", validators=[DataRequired()])
    submit = SubmitField("Giriş Yap")


class HesapFormu(FlaskForm):
    ad = StringField("Hesap Adı", validators=[DataRequired(), Length(max=120)])
    hesap_turu = SelectField(
        "Hesap Türü",
        choices=[
            ("nakit", "Nakit"),
            ("banka", "Banka"),
            ("kredi", "Kredi Kartı"),
        ],
        validators=[DataRequired()],
    )
    bakiye = DecimalField("Başlangıç Bakiyesi", places=2, rounding=None, validators=[DataRequired()])
    submit = SubmitField("Kaydet")


class SilmeFormu(FlaskForm):
    """Sadece CSRF koruması için kullanılan form."""

    pass


class KategoriFormu(FlaskForm):
    ad = StringField("Kategori Adı", validators=[DataRequired(), Length(max=120)])
    aciklama = TextAreaField("Açıklama", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Kaydet")


class IslemFormu(FlaskForm):
    islem_turu = SelectField(
        "İşlem Türü",
        choices=[("gelir", "Gelir"), ("gider", "Gider")],
        validators=[DataRequired()],
    )
    hesap_id = SelectField("Hesap", coerce=int, validators=[DataRequired()])
    kategori_id = SelectField("Kategori", coerce=int, validators=[DataRequired()])
    tutar = DecimalField("Tutar (₺)", places=2, validators=[DataRequired(), NumberRange(min=0)])
    tarih = DateField("Tarih", format="%d/%m/%Y", default=date.today, validators=[DataRequired()], render_kw={"placeholder": "GG/AA/YYYY"})
    aciklama = TextAreaField("Açıklama", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Kaydet")


class ButceFormu(FlaskForm):
    yil = IntegerField(
        "Yıl",
        validators=[DataRequired(), NumberRange(min=2000, max=2100)],
        default=date.today().year,
    )
    ay = SelectField(
        "Ay",
        choices=[
            (1, "Ocak"),
            (2, "Şubat"),
            (3, "Mart"),
            (4, "Nisan"),
            (5, "Mayıs"),
            (6, "Haziran"),
            (7, "Temmuz"),
            (8, "Ağustos"),
            (9, "Eylül"),
            (10, "Ekim"),
            (11, "Kasım"),
            (12, "Aralık"),
        ],
        coerce=int,
        validators=[DataRequired()],
    )
    kategori_id = SelectField("Kategori", coerce=int, validators=[DataRequired()])
    tutar = DecimalField("Bütçe Tutarı", places=2, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Kaydet")


class RaporFiltreFormu(FlaskForm):
    baslangic = DateField("Başlangıç Tarihi", format="%d/%m/%Y", validators=[Optional()], render_kw={"placeholder": "GG/AA/YYYY"})
    bitis = DateField("Bitiş Tarihi", format="%d/%m/%Y", validators=[Optional()], render_kw={"placeholder": "GG/AA/YYYY"})
    kategori_id = SelectField("Kategori", coerce=int, validators=[Optional()])
    hesap_id = SelectField("Hesap", coerce=int, validators=[Optional()])
    submit = SubmitField("Filtrele")
