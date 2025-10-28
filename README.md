# Kişisel Bütçe Takip Uygulaması

Bu proje, Python Flask kullanılarak geliştirilen ve Türkçe arayüze sahip kişisel bütçe yönetim uygulamasıdır. Gelir-gider işlemleri, hesap ve kategori yönetimi, aylık bütçe planlama, raporlama ve CSV dışa aktarma gibi özellikler sunar.

## Özellikler
- Kullanıcı girişi ve kayıt sistemi (Flask-Login).
- Gelir/gider işlemlerinin eklenmesi, düzenlenmesi ve silinmesi.
- Birden fazla hesap ve kategori yönetimi.
- Aylık kategori bazlı bütçe tanımlama ve bütçe aşımı uyarıları.
- Aylık özet panosu ve Chart.js ile görselleştirilmiş raporlar.
- CSV formatında işlem dışa aktarma.

## Kurulum
1. Proje dizinine gidin ve sanal ortam oluşturun (isteğe bağlı):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows için: venv\\Scripts\\activate
   ```
2. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Veritabanını oluşturun:
   ```bash
   flask --app app.py veritabani-olustur
   ```
4. Uygulamayı başlatın:
   ```bash
   python app.py
   ```

## Notlar
- Varsayılan olarak SQLite kullanılır. `DATABASE_URL` ortam değişkeni ile farklı bir veritabanı tanımlayabilirsiniz.
- Tarih alanları `GG/AA/YYYY` formatını kullanır.
- Para birimi varsayılan olarak Türk Lirası (₺) şeklinde gösterilir.
