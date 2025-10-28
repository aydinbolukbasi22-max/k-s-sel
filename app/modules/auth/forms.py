"""Kimlik doğrulama formları."""
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class KayitFormu(FlaskForm):
    ad = StringField("Ad Soyad", validators=[DataRequired(message="Ad gerekli."), Length(max=120)])
    eposta = EmailField("E-posta", validators=[DataRequired(), Email()])
    sifre = PasswordField(
        "Şifre",
        validators=[DataRequired(), Length(min=6, message="Şifre en az 6 karakter olmalıdır.")],
    )
    sifre_tekrar = PasswordField(
        "Şifre (Tekrar)",
        validators=[DataRequired(), EqualTo("sifre", message="Şifreler eşleşmiyor.")],
    )
    gonder = SubmitField("Hesap Oluştur")


class GirisFormu(FlaskForm):
    eposta = EmailField("E-posta", validators=[DataRequired(), Email()])
    sifre = PasswordField("Şifre", validators=[DataRequired()])
    gonder = SubmitField("Giriş Yap")


class ProfilFormu(FlaskForm):
    ad = StringField("Ad Soyad", validators=[DataRequired(), Length(max=120)])
    gonder = SubmitField("Profili Güncelle")
