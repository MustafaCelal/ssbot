# 🤖 TradingView Screenshot Bot (SSBot)

[![Python Support](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.15+-green.svg)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/license-MIT-important.svg)](LICENSE)

**TradingView Screenshot Bot**, TradingView grafiklerini otomatik olarak yakalayan, borsa ve sembol bazlı özelleştirilebilir bir otomasyon aracıdır. Modern Selenium altyapısı ve gelişmiş anti-bot önlemleri ile donatılmıştır.

---

## ✨ Temel Özellikler

*   🎯 **Hassas Yakalama:** İstediğiniz sembol, borsa ve zaman diliminde (timeframe) yüksek çözünürlüklü grafikler.
*   📸 **Çift Mod Desteği:**
    *   `Quick Mode`: Grafik alanını doğrudan yakalar (Hızlı ve sessiz).
    *   `Clean Mode`: TradingView'ın resmi snapshot butonunu kullanır (Resmi ve ultra-temiz).
*   🌓 **Tema Seçimi:** Koyu (Dark) ve Açık (Light) tema desteği.
*   🚀 **Esnek Çalışma:** Headless (arka plan) ve Headed (görünür) mod desteği.
*   ⏰ **Otomasyon:** Belirlenen aralıklarla (`--interval`) periyodik ekran görüntüsü alma.
*   🛡️ **Anti-Bot Gelişmişliği:** Rastgele user-agent havuzu ve insan benzeri bekleme süreleri.
*   🔔 **Bildirim Sistemi:** İşlem tamamlandığında macOS sistem bildirimi veya Discord (opsiyonel) üzerinden haber verme.
*   🔐 **Giriş Desteği:** Hesabınıza giriş yaparak kayıtlı göstergelerinizi (indicators) kullanabilme.

---

## � Gereksinimler

*   **Python:** 3.8 veya üzeri.
*   **Google Chrome:** En son sürüm önerilir.
*   **İşletim Sistemi:** macOS (Bildirim sistemi için), Linux veya Windows (Notification modülü genişletilebilir).

---

## �🛠️ Kurulum

1.  **Depoyu Klonlayın:**
    ```bash
    git clone https://github.com/MustafaCelal/ssbot.git
    cd ssbot
    ```

2.  **Sanal Ortam Oluşturun (Önerilir):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    # veya
    .\venv\Scripts\activate  # Windows
    ```

3.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 Kullanım

Botu CLI üzerinden kolayca yönetebilirsiniz.

### Temel Örnekler

**1. Tek Seferlik Hızlı Screenshot:**
```bash
python main.py --symbol BTCUSDT --exchange BINANCE --timeframe 1H
```

**2. Açık Tema ve Görünür Browser Modu:**
```bash
python main.py --symbol AAPL --exchange NASDAQ --theme light --no-headless
```

**3. Resmi Snapshot Modu (Clean):**
```bash
python main.py --symbol XAUUSD --exchange FOREXCOM --mode clean
```

**4. Periyodik Otomasyon (Örn: Her 15 dakikada bir):**
```bash
python main.py --symbol ETHUSDT --interval 15
```

### Tüm Parametreler

| Argüman | Açıklama | Varsayılan |
| :--- | :--- | :--- |
| `--symbol`, `-s` | Takip edilecek sembol (ör: BTCUSDT) | **Zorunlu** |
| `--exchange`, `-e` | Borsa adı (ör: BINANCE, NASDAQ, BIST) | `BINANCE` |
| `--timeframe`, `-t` | Zaman dilimi (ör: 5, 1H, 4H, 1D) | `1D` |
| `--theme` | Tema seçimi (`light`, `dark`) | `dark` |
| `--mode`, `-m` | Yakalama modu (`quick`, `clean`) | `quick` |
| `--interval`, `-i` | Dakika bazlı tekrar süresi (0 = tek sefer) | `0` |
| `--no-headless` | Browser'ı görünür modda çalıştırır | `False` |
| `--login` | TradingView hesabına giriş yapar | `False` |
| `--output`, `-o` | Çıktı klasörü yolu | `./screenshots` |
| `--width` / `--height`| Browser pencere boyutu | `1920x1080` |

---

## 📊 Desteklenen Borsalar (Örnekler)

Bot, TradingView üzerindeki hemen hemen tüm borsaları destekler. Sık kullanılanlardan bazıları:

*   **Kripto:** `BINANCE`, `BYBIT`, `COINBASE`, `KRAKEN`
*   **Hisse Senedi:** `BIST` (Borsa İstanbul), `NASDAQ`, `NYSE`, `AMEX`
*   **Forex & Emtia:** `FX`, `FOREXCOM`, `OANDA`, `CME_MINI`, `COMEX`

*(Diğer borsalar için TradingView üzerindeki borsa kodunu kullanabilirsiniz.)*

---

## 🔔 Bildirim Sistemi Yapılandırması

Bot, işlem tamamlandığında sizi bilgilendirebilir:

###  macOS Bildirimleri
macOS kullanıyorsanız, herhangi bir ayar yapmanıza gerek yoktur. Bot otomatik olarak sistem bildirimlerini kullanır.

### 💬 Discord Bildirimi
Ekran görüntüsü alındığında Discord kanalınıza mesaj gelmesini istiyorsanız:
1. Discord kanal ayarlarından bir **Webhook URL** oluşturun.
2. Bilgisayarınıza environment variable olarak ekleyin:
   ```bash
   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
   ```

---

## ⚙️ Yapılandırma ve Özelleştirme

### Dosya Yapısı

*   `main.py`: Uygulamanın giriş noktası ve CLI yönetimi.
*   `config.py`: Tüm ayarlar, CSS selector'lar ve borsa tanımları.
*   `screenshot_engine.py`: Ekran görüntüsü alma mantığı ve retry mekanizması.
*   `browser_manager.py`: Selenium WebDriver yönetimi.
*   `notifier.py`: Bildirim sağlayıcıları (macOS, Discord).

### Giriş Bilgileri (Opsiyonel)

Kendi göstergelerinizi veya favori ayarlarınızı kullanmak için giriş yapabilirsiniz. Güvenlik için bilgilerinizi environment variable olarak tanımlayın:

```bash
export TV_USERNAME="kullanici_adiniz"
export TV_PASSWORD="sifreniz"
```

---

## 🏗️ Teknik Mimari

Bot, modüler bir yapı üzerine inşa edilmiştir:

1.  **Entry Point (`main.py`):** CLI argümanlarını işler ve botun yaşam döngüsünü yönetir.
2.  **Bot Logic (`tradingview_bot.py`):** Browser ve Engine arasındaki koordinasyonu sağlar.
3.  **Engine (`screenshot_engine.py`):** TradingView elementleri ile etkileşime girer, timeframe değiştirir ve görüntüyü yakalar.
4.  **Browser Manager (`browser_manager.py`):** Selenium driver'ını konfigüre eder (User-agent, proxy, window size).
5.  **Config (`config.py`):** CSS selector'lar ve uygulama ayarlarını merkezi bir yerde toplar.

---

## 🛠️ Sorun Giderme (Troubleshooting)

*   **Chrome Driver Hatası:** Bot, `webdriver-manager` kullanarak sürücüyü otomatik yükler. Eğer hata alırsanız Chrome tarayıcınızın güncel olduğundan emin olun.
*   **Element Bulunamadı:** TradingView bazen arayüzünü günceller. Bu durumda `config.py` dosyasındaki `Selectors` sınıfındaki CSS selector'larını güncellemeniz gerekebilir.
*   **Zaman Aşımı (Timeout):** İnternet hızınız yavaşsa `config.py` içerisindeki `PAGE_LOAD_TIMEOUT` değerini artırın.
*   **Giriş Sorunları:** İki faktörlü doğrulama (2FA) aktifse, login modu headless modda çalışmayabilir. İlk girişi `--no-headless` ile manuel yapmanız gerekebilir.

---

## 🗺️ Yol Haritası (Roadmap)

- [ ] 🖥️ Masaüstü Arayüzü (GUI) geliştirme (Terminal kullanmak istemeyenler için).
- [ ] 📱 Telegram Bot entegrasyonu.
- [ ] 📧 E-posta gönderim desteği.
- [ ] 📄 Çoklu sembol listesi desteği (Batch processing).
- [ ] 🐳 Docker Container desteği.

---

## 📂 Çıktı Formatı

Ekran görüntüleri varsayılan olarak `screenshots/` klasörüne şu formatta kaydedilir:
`SEMBOL_BORSA_TIMEFRAME_TARIH_SAAT.png`

Örneğin: `BTCUSDT_BINANCE_1H_20240120_153045.png`

---

## 🤝 Katkıda Bulunma

1. Bu projeyi fork'layın.
2. Yeni bir feature branch oluşturun (`git checkout -b feature/yeniozellik`).
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`).
4. Branch'inizi push edin (`git push origin feature/yeniozellik`).
5. Bir Pull Request oluşturun.

---

## 📝 Lisans

Bu proje MIT lisansı ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakabilirsiniz.

---

**Geliştiriciler:** [Mustafa](https://github.com/MustafaCelal) ve [Rico](https://github.com/ricoglr)  
**Not:** Bu araç sadece eğitim ve kişisel kullanım amaçlıdır. TradingView kullanım koşullarına uymayı unutmayın.
