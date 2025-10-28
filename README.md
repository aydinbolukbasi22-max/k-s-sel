# Bütçe Rehberi

Tamamen Türkçe arayüzlü bu proje, kişisel finans yönetimi için modern bir Flask uygulamasıdır. Gelir–gider takibi, bütçe planlama, tasarruf hedefleri, borç yönetimi ve tekrar eden hatırlatıcılar gibi gelişmiş modüller içerir.

## Başlıca Özellikler

- 🔐 **Kimlik Doğrulama** – Flask-Login ile şifrelenmiş kayıt, giriş ve profil güncelleme.
- 🧾 **Defter Modülü** – Hesaplar, işlemler, CSV dışa aktarma ve hesaplar arası transfer.
- 📊 **Bütçe Yönetimi** – Kategori bazlı aylık limitler, kalan tutar hesaplama ve kategori yönetimi.
- 🎯 **Tasarruf Hedefleri** – Önceliklendirme, ilerleme yüzdesi ve hızlı katkı girişleri.
- 💳 **Borç Takibi** – Borç kayıtları, ödeme planı ve faiz alanları.
- ⏰ **Hatırlatıcılar** – Tekrarlayan görevler, durum rozetleri ve tamamlandı kaydı.
- 📈 **Analitik** – Nakit akışı ve kategori harcamaları için Chart.js grafikleri.

## Kurulum

```bash
python -m venv venv
source venv/bin/activate  # Windows için: venv\Scripts\activate
pip install -r requirements.txt
```

### Ortam Değerleri

`config.py` varsayılan olarak `data/butce.db` dosyasını kullanır. İsterseniz aşağıdaki değerleri tanımlayabilirsiniz:

- `SECRET_KEY`
- `DATABASE_URL`

## Çalıştırma

```bash
python app.py
```

İlk çalıştırmada veritabanı tabloları otomatik olarak oluşturulur. Uygulama `http://127.0.0.1:5000` adresinde debug modunda çalışır.

## Proje Yapısı

```
app/
  __init__.py            # Flask uygulama fabrikası
  extensions.py          # Uzantı nesneleri
  models/                # SQLAlchemy modelleri
  services/              # Finansal hesaplamalar ve yardımcılar
  modules/               # Blueprint bazlı modüller
  templates/             # Bootstrap 5 arayüzleri
  static/                # CSS ve JS dosyaları
```

## Komut Satırı

Tabloları CLI üzerinden oluşturmak için:

```bash
flask --app app veritabani-olustur
```

## Test

Sadece sözdizimi kontrolü için:

```bash
python -m compileall app
```

## Lisans

Bu proje eğitim amaçlı hazırlanmıştır. Tüm metinler ve arayüz Türkçedir.
