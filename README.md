# Ses Kalitesi Test ve İyileştirme Sistemi

Fiziksel Cihaz | FastAPI | PostgreSQL | Docker

---

## Genel Bakış

Bu proje, bir cihazın ses kalitesi test süreçlerini dijitalleştirmeyi ve yapay zeka destekli sinyal iyileştirme algoritmalarını doğrulamayı hedeflemektedir. Kullanıcı tarayıcı üzerinden ses kaydeder, sistem bu sesi otomatik olarak işler ve ham ile temizlenmiş versiyonları PostgreSQL veritabanında saklar.

---

## Seçilen Yöntem: Fiziksel Cihaz

Ses kaydı alma yöntemi olarak **Fiziksel Cihaz** seçilmiştir.

Kullanıcının bilgisayarına bağlı gerçek mikrofon donanımı, Web Audio API aracılığıyla tarayıcıdan erişilmektedir. Ham PCM verisi JavaScript tarafında WAV formatına dönüştürülüp backend'e gönderilmektedir.

### Neden Fiziksel Cihaz?

- Gerçek ortam koşullarında ses kalitesi testi yapılabilmesi
- Simülasyon yerine gerçek gürültü verisi üretilmesi
- Filtreleme algoritmalarının gerçek senaryolarda doğrulanması
- FFmpeg gibi harici araç gerektirmeden tarayıcı tabanlı WAV üretimi

### Ses Kaydı Parametreleri

```
Örnekleme Frekansı : 16.000 Hz
Kanal Sayısı       : 1 (Mono)
Bit Derinliği      : 16-bit PCM
Çıktı Formatı      : WAV (.wav)
API                : Web Audio API - ScriptProcessorNode
Chunk Boyutu       : 4096 sample
```

---

## Filtreleme Algoritması

Ses işleme modülü (`noice.py`) iki aşamalı bir pipeline uygulamaktadır. Kayıt tamamlandığı anda Python sinyal işleme modülü otomatik olarak tetiklenmektedir.

### Pipeline Akışı

```
1. WAV dosyası yüklenir          (librosa)
2. Düşük geçiren filtre uygulanır  (scipy - Butterworth)
3. Gürültü azaltma uygulanır     (noisereduce - Spectral Gating)
4. Temizlenmiş ses kaydedilir    (soundfile)
5. Ham ve temiz ses DB'ye yazılır  (PostgreSQL - BYTEA)
```

### Aşama 1 — Düşük Geçiren Filtre (Low-Pass Filter)

Butterworth düşük geçiren filtre ile yüksek frekanslı gürültü bileşenleri bastırılır. İnsan sesi 300–3400 Hz aralığında yoğunlaştığından cutoff frekansı 3000 Hz seçilmiştir.

```
Filtre Türü     : Butterworth Low-Pass
Cutoff Frekansı : 3000 Hz
Filtre Derecesi : 5
Kütüphane       : scipy.signal (butter, lfilter)
```

Kod imzası:

```python
def low_pass_filter(data, cutoff, sr):
    nyquist = 0.5 * sr
    normal_cutoff = cutoff / nyquist
    b, a = butter(5, normal_cutoff, btype='low')
    return lfilter(b, a, data)
```

### Aşama 2 — Gürültü Azaltma (Noise Reduction)

Spectral gating yöntemi ile arka plan gürültüsü istatistiksel olarak modellenerek sinyalden ayrıştırılır.

```
Yöntem         : Spectral Gating
Kütüphane      : noisereduce (nr.reduce_noise)
Giriş          : Low-pass filtreden geçmiş sinyal
Gürültü Profil : Otomatik (stationary noise estimation)
Çıktı          : Temizlenmiş float32 numpy array
```

---

## Veritabanı Yapısı

Ham ve işlenmiş ses dosyaları PostgreSQL'de BYTEA olarak saklanır. Metadata ayrı tabloda tutulur.

### audio_files

```sql
id        SERIAL PRIMARY KEY
filename  VARCHAR(255)   -- kayit_x.wav / clean_kayit_x.wav
data      BYTEA          -- ham veya işlenmiş ses (binary)
```

### audio_metadata

```sql
id         SERIAL PRIMARY KEY
file_id    INTEGER        -- audio_files.id (foreign key)
device_id  VARCHAR(100)   -- kayıt cihazı kimliği
duration   FLOAT          -- süre (saniye)
created_at TIMESTAMP      -- kayıt tarihi ve saati
```

---

## Gereksinimler

### Python Kütüphaneleri

```
fastapi
uvicorn
psycopg2-binary
librosa
noisereduce
soundfile
scipy
numpy
```

### Sistem Gereksinimleri

- Docker ve Docker Compose kurulu olmalıdır
- Python 3.10 veya üzeri
- PostgreSQL 15

---

## Kurulum ve Çalıştırma

### 1. Repoyu klonlayın

```bash
git clone <repo-url>
cd <proje-klasörü>
```

### 2. Docker ile çalıştırın

```bash
docker-compose down -v
docker-compose up --build
```

### 3. Uygulamaya erişin

```
http://localhost:8000
```

### Notlar

- `docker-compose down -v` komutu veritabanı verilerini siler, dikkatli kullanın
- `init.sql` dosyası ilk çalıştırmada tabloları otomatik oluşturur
- Backend, veritabanı hazır olana kadar otomatik yeniden bağlanmayı dener

---

## Teknoloji Stack

```
Frontend    : HTML5, Web Audio API, JavaScript
Backend     : Python, FastAPI, Uvicorn
Sinyal İşl. : librosa, scipy, noisereduce, soundfile
Veritabanı  : PostgreSQL 15 (BYTEA depolama)
Konteyner   : Docker, Docker Compose
```
