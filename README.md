# 🤖 ChartCapture Pro (SSBot)

[![Python Support](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.15+-green.svg)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/license-MIT-important.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)

TradingView grafiklerini otomatik olarak yakalayan, borsa ve sembol bazlı özelleştirilebilir profesyonel otomasyon aracı. Modern Selenium altyapısı ve gelişmiş anti-bot önlemleri ile donatılmıştır.

---

## ✨ Temel Özellikler

- 🎯 **Hassas Yakalama:** İstediğiniz sembol, borsa ve zaman diliminde yüksek çözünürlüklü grafikler
- ⏰ **Otomasyon ve Zamanlayıcı:** Seçilen periyotta (5dk, 15dk, 30dk, 1sa, 4sa) otomatik screenshot alma
- 📸 **Çift Mod Desteği:**
  - `Quick Mode`: Grafik alanını doğrudan yakalar (hızlı ve sessiz)
  - `Clean Mode`: TradingView'ın resmi snapshot butonunu kullanır (ultra-temiz)
- 🌓 **Dinamik Tema Seçimi:** Koyu (Dark) ve Açık (Light) tema desteği
- 🖥️ **Özelleştirilebilir Çözünürlük:** Full HD, 2K, 4K ve Mobil Dikey modlar
- 🛡️ **Anti-Bot Gelişmişliği:** Rastgele user-agent havuzu ve stealth mode
- 🐳 **Docker Entegrasyonu:** Tam izole çalışma ortamı ve tek komutla kurulum
- 🎨 **Streamlit UI:** Kullanıcı dostu web arayüzü
- 📊 **Son Yakalananlar:** Otomatik ve manuel çekimlerin geçmişini görüntüleme

---

## 📋 Gereksinimler

- **Python:** 3.8 veya üzeri
- **Google Chrome:** En son sürüm önerilir
- **İşletim Sistemi:** macOS, Linux veya Windows

---

## 🚀 Kurulum

### 🐳 Docker ile Kurulum (Önerilen)

Docker kullanarak uygulamayı izole bir ortamda, bağımlılık derdi olmadan çalıştırabilirsiniz.

**1. UI ve Botu Başlatın:**
```bash
docker-compose up --build
```

**2. Tarayıcınızdan Erişin:**

👉 [http://localhost:8501](http://localhost:8501)

**3. CLI Kullanımı (Docker):**
```bash
# Yardım menüsünü görüntüle
docker-compose run --rm ssbot python main.py --help

# Örnek kullanım
docker-compose run --rm ssbot python main.py --symbol BTCUSDT --exchange BINANCE --timeframe 1H
```

**Alternatif Docker Komutu:**
```bash
# İmaj oluşturma
docker build -t ssbot .

# Çalıştırma
docker run --rm \
  --shm-size=2gb \
  -v $(pwd)/screenshots:/app/screenshots \
  -v $(pwd)/logs:/app/logs \
  -e TV_USERNAME=kullanici_adiniz \
  -e TV_PASSWORD=sifreniz \
  ssbot python main.py --symbol BTCUSDT --timeframe 1D
```

> **💡 İpucu:** Docker üzerinde `shm_size: '2gb'` ayarı ve `--disable-dev-shm-usage` argümanı Chrome'un stabil çalışması için kritiktir.

---

### 🛠️ Yerel Kurulum (Manuel)

Geliştirme yapmak veya özelleştirme için bu yöntemi kullanın.

**1. Depoyu Klonlayın:**
```bash
git clone https://github.com/MustafaCelal/ssbot.git
cd ssbot
```

**2. Sanal Ortam Oluşturun:**
```bash
python -m venv venv

# Aktivasyon
source venv/bin/activate      # macOS/Linux
.\venv\Scripts\activate       # Windows
```

**3. Bağımlılıkları Yükleyin:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 💻 Kullanım

### CLI Örnekleri

**Temel Kullanım:**
```bash
python main.py --symbol BTCUSDT --exchange BINANCE --timeframe 1H
```

**Açık Tema ile:**
```bash
python main.py --symbol AAPL --exchange NASDAQ --theme light --no-headless
```

**Clean Mode (Resmi Snapshot):**
```bash
python main.py --symbol XAUUSD --exchange FOREXCOM --mode clean
```

**Periyodik Otomasyon (Her 15 dakikada):**
```bash
python main.py --symbol ETHUSDT --interval 15
```

---

### 📋 Parametreler

| Parametre | Kısa | Açıklama | Varsayılan |
|-----------|------|----------|------------|
| `--symbol` | `-s` | Takip edilecek sembol (örn: BTCUSDT) | **Zorunlu** |
| `--exchange` | `-e` | Borsa adı (örn: BINANCE, NASDAQ) | `BINANCE` |
| `--timeframe` | `-t` | Zaman dilimi (örn: 5, 1H, 4H, 1D) | `1D` |
| `--theme` | | Tema (`light`, `dark`) | `dark` |
| `--mode` | `-m` | Yakalama modu (`quick`, `clean`) | `quick` |
| `--interval` | `-i` | Tekrar süresi (dakika, 0=tek sefer) | `0` |
| `--no-headless` | | Browser'ı görünür modda çalıştır | `False` |
| `--login` | | TradingView'a giriş yap | `False` |
| `--output` | `-o` | Çıktı klasörü | `./screenshots` |
| `--width` | | Pencere genişliği | `1920` |
| `--height` | | Pencere yüksekliği | `1080` |

---

## 📊 Desteklenen Borsalar

Bot, TradingView üzerindeki tüm borsaları destekler:

**Kripto:**
- `BINANCE`, `BYBIT`, `COINBASE`, `KRAKEN`, `KUCOIN`

**Hisse Senedi:**
- `BIST` (Borsa İstanbul), `NASDAQ`, `NYSE`, `AMEX`

**Forex & Emtia:**
- `FX`, `FOREXCOM`, `OANDA`, `CME_MINI`, `COMEX`

*TradingView üzerindeki herhangi bir borsa kodunu kullanabilirsiniz.*

---

## 🔔 Bildirim Sistemi

### macOS Bildirimleri
macOS kullanıcıları için sistem bildirimleri otomatik olarak aktiftir.

### Discord Webhook
Discord bildirimlerini etkinleştirmek için:

**1. Discord Webhook URL'i Oluşturun**

**2. Environment Variable Olarak Ekleyin:**
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

---

## 🔐 Giriş Bilgileri (Opsiyonel)

Kendi göstergelerinizi kullanmak için TradingView hesabınıza giriş yapabilirsiniz:

```bash
export TV_USERNAME="kullanici_adiniz"
export TV_PASSWORD="sifreniz"
```

Ardından `--login` parametresi ile çalıştırın:
```bash
python main.py --symbol BTCUSDT --login
```

---

## 🏗️ Proje Yapısı

```
ssbot/
├── main.py                 # CLI giriş noktası
├── config.py              # Ayarlar ve konfigürasyon
├── screenshot_engine.py   # Ekran görüntüsü mantığı
├── browser_manager.py     # Selenium WebDriver yönetimi
├── notifier.py           # Bildirim sistemi
├── requirements.txt      # Python bağımlılıkları
├── docker-compose.yml    # Docker yapılandırması
└── screenshots/          # Çıktı klasörü
```

---

## 📂 Çıktı Formatı

Ekran görüntüleri şu formatta kaydedilir:

```
SEMBOL_BORSA_TIMEFRAME_TARIH_SAAT.png
```

**Örnek:** `BTCUSDT_BINANCE_1H_20240120_153045.png`

**Varsayılan Konum:** `./screenshots/`

---

## 🛠️ Sorun Giderme

### Chrome Driver Hatası
Bot, `webdriver-manager` ile sürücüyü otomatik yükler. Chrome tarayıcınızın güncel olduğundan emin olun.

### Element Bulunamadı
TradingView arayüzü değişirse, `config.py` dosyasındaki `Selectors` sınıfını güncelleyin.

### Timeout Hatası
İnternet hızınız yavaşsa `config.py` içindeki `PAGE_LOAD_TIMEOUT` değerini artırın.

### Giriş Sorunları
İki faktörlü doğrulama (2FA) aktifse, ilk girişi `--no-headless` ile manuel yapın.

---

## 🗺️ Yol Haritası

- [x] Streamlit Web Arayüzü
- [x] Docker Container Desteği
- [x] Otomasyon ve Zamanlayıcı (APScheduler)
- [ ] Telegram Bot Entegrasyonu
- [ ] E-posta Gönderim Desteği
- [ ] Çoklu Sembol Listesi (Batch Processing)
- [ ] Otomatik Indicator Ekleme
- [ ] Scheduler Persistence (Sayfa yenilemede korunma)

---

## ⚠️ Bilinen Sorunlar

**UI Çözünürlük Ayarı:** Streamlit UI üzerinden seçilen çözünürlük, browser oturumu açıkken dinamik olarak değişmeyebilir. Tam etki için botun yenilenmesi gerekebilir.

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları izleyin:

1. Projeyi fork'layın
2. Feature branch oluşturun (`git checkout -b feature/yeniozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeniozellik`)
5. Pull Request oluşturun

---

## 📝 Lisans

Bu proje MIT lisansı ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 👥 Geliştiriciler

- [Mustafa](https://github.com/MustafaCelal)
- [Rico](https://github.com/ricoglr)

---

## ⚖️ Yasal Uyarı

Bu araç **sadece eğitim ve kişisel kullanım** amaçlıdır. TradingView'ın [kullanım koşullarına](https://www.tradingview.com/policies/) uymayı unutmayın. Ticari kullanım için TradingView'dan izin almanız gerekebilir.

---

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!**