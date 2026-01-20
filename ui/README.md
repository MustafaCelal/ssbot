# UI Geliştirme Notları

Bu klasör, uygulamanın görsel arayüzü (UI) için ayrılmıştır.

## Seçilen Teknoloji: Streamlit
Hızlı geliştirme süreci, Python dışına çıkmama imkanı ve modern tasarımı nedeniyle **Streamlit** seçilmiştir.

### Çalıştırma Hazırlığı
1. Gerekli kütüphaneyi yükleyin:
   ```bash
   pip install streamlit
   ```
2. Uygulamayı başlatın (Root dizinindeyken):
   ```bash
   streamlit run ui/app.py
   ```

### Entegrasyon Notu
- UI kodu her zaman `core/` klasöründeki sınıfları kullanmalıdır.
- `ui/app.py` içinde `sys.path` ayarı yapılarak `core` paketine erişim sağlanmıştır.
- Bot mantığı ve UI mantığı birbirine karıştırılmamalıdır.
