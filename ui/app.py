import streamlit as st
import sys
import os
from PIL import Image
import time
from datetime import datetime

# root dizini path'e ekleyelim ki core paketini bulabilsin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.bot import ChartCapture
from core.scheduler import ScreenshotScheduler

# Sayfa Yapılandırması
st.set_page_config(
    page_title="ChartCapture Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# UI/UX Optimizasyonu için Custom CSS
st.markdown("""
<style>
    /* Streamlit varsayılan bileşenlerini gizle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stDecoration"] {display:none;}
    
    /* Üst boşlukları daralt */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Header minimalist tasarımı */
    .compact-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        padding: 0.5rem 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }

    /* Kartlar ve kutular için kompakt yapı */
    div[data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(255, 255, 255, 0.02);
    }
    
    /* Butonun yüksekliğini ve stilini sabitle */
    .stButton>button {
        height: 3em;
        background: #4f46e5;
        border: none;
        font-weight: bold;
    }

    /* Görselin ekrana sığması için max-height */
    .stImage img {
        max-height: 65vh;
        object-fit: contain;
    }
</style>
""", unsafe_allow_html=True)

def initialize_bot(headless=True, theme="dark", width=1920, height=1080):
    # Eğer bot hiç yoksa veya headless modu değişmişse botu yeniden başlat
    if ('bot' not in st.session_state or 
        st.session_state.get('current_headless') != headless):
        
        if 'bot' in st.session_state:
            try: st.session_state.bot.close()
            except: pass
        
        st.session_state.bot = ChartCapture(
            headless=headless, 
            theme=theme, 
            width=width, 
            height=height
        )
        st.session_state.bot.initialize()
        st.session_state.current_headless = headless
        st.session_state.current_width = width
        st.session_state.current_height = height
    
    # Tema değişmişse objenin içindeki değeri güncelle
    st.session_state.bot.theme = theme
    st.session_state.current_theme = theme
    
    # Çözünürlük değişmişse dinamik olarak browser boyutunu güncelle (Restart gerektirmez)
    if (st.session_state.get('current_width') != width or 
        st.session_state.get('current_height') != height):
        
        if st.session_state.bot.browser and st.session_state.bot.browser.driver:
            st.session_state.bot.browser.driver.set_window_size(width, height)
            st.session_state.current_width = width
            st.session_state.current_height = height
            
    return st.session_state.bot

def initialize_session_state():
    """Session state değişkenlerini başlatır."""
    if 'scheduler' not in st.session_state:
        st.session_state.scheduler = ScreenshotScheduler()
    if 'is_scheduling' not in st.session_state:
        st.session_state.is_scheduling = False
    if 'recent_captures' not in st.session_state:
        st.session_state.recent_captures = []
    if 'schedule_params' not in st.session_state:
        st.session_state.schedule_params = {}
    if 'last_screenshot_count' not in st.session_state:
        screenshot_dir = "./screenshots"
        initial_count = 0
        if os.path.exists(screenshot_dir):
            initial_count = len([f for f in os.listdir(screenshot_dir) if f.endswith('.png')])
        st.session_state.last_screenshot_count = initial_count
    if 'total_scheduled_count' not in st.session_state:
        st.session_state.total_scheduled_count = st.session_state.last_screenshot_count

def on_scheduled_capture(bot, symbol, exchange, timeframe, mode):
    """
    Zamanlanmış screenshot callback fonksiyonu.
    APScheduler tarafından çağrılır.
    NOT: UI güncellemesi yapmaz, sadece screenshot alır.
    """
    from core.logger import get_logger
    logger = get_logger()
    
    try:
        logger.info(f"⏰ Zamanlanmış screenshot: {symbol} @ {exchange}")
        
        success, filepath = bot.take_screenshot(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            mode=mode
        )
        
        if success and os.path.exists(filepath):
            logger.info(f"✅ Screenshot başarılı: {filepath}")
        else:
            logger.error(f"❌ Screenshot başarısız: {symbol}")
            
    except Exception as e:
        logger.error(f"⚠️ Zamanlanmış capture hatası: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def load_recent_screenshots(screenshot_dir="./screenshots", limit=10):
    """
    Screenshot klasöründen son dosyaları yükler.
    Bu sayede scheduled screenshots otomatik görünür.
    """
    try:
        if not os.path.exists(screenshot_dir):
            return []
        
        # Tüm PNG dosyalarını bul
        screenshots = []
        for filename in os.listdir(screenshot_dir):
            if filename.endswith('.png'):
                filepath = os.path.join(screenshot_dir, filename)
                file_stat = os.stat(filepath)
                
                # Dosya adından bilgileri çıkar (örn: BTCUSDT_BINANCE_1H_20240120_153045.png)
                parts = filename.replace('.png', '').split('_')
                if len(parts) >= 3:
                    screenshots.append({
                        'path': filepath,
                        'timestamp': datetime.fromtimestamp(file_stat.st_mtime),
                        'symbol': parts[0] if len(parts) > 0 else 'N/A',
                        'exchange': parts[1] if len(parts) > 1 else 'N/A',
                        'timeframe': parts[2] if len(parts) > 2 else 'N/A',
                        'size': file_stat.st_size
                    })
        
        # Zamana göre sırala (en yeni önce)
        screenshots.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return screenshots[:limit]
        
    except Exception as e:
        return []

def main():
    # Session state'i başlat
    initialize_session_state()
    
    # OTOMATIK YENİLEME: Scheduler aktifse klasörü kontrol et
    if st.session_state.is_scheduling:
        import time as time_module
        
        # Screenshots klasöründeki dosya sayısını kontrol et
        screenshot_dir = "./screenshots"
        current_count = 0
        
        if os.path.exists(screenshot_dir):
            current_count = len([f for f in os.listdir(screenshot_dir) if f.endswith('.png')])
        
        # Yeni screenshot eklendiyse sayfayı yenile
        if current_count > st.session_state.last_screenshot_count:
            st.session_state.last_screenshot_count = current_count
            st.session_state.total_scheduled_count = current_count
            st.rerun()
        
        # Son sayıyı güncelle
        st.session_state.last_screenshot_count = current_count
        
        # UI'da görünmesi için son kontrol zamanı
        st.session_state.last_check_time = datetime.now().strftime("%H:%M:%S")
        
        # Çok sık yenileyip UI'ı kitlememek için sadece otomasyon panelinde 
        # bir 'refresh' tetikleyicisi gibi davranacak bir mekanizma kuruyoruz.
        # Bu satır, sayfanın en altında bir timer gibi çalışacak.
    
    # --- TOP BAR ---
    st.markdown("""
        <div class="compact-header">
            <h3 style="margin:0;">📊 ChartCapture <span style="font-weight:200; font-size:15px;">v1.0</span></h3>
            <p style="margin:0; font-size:13px; opacity:0.8;">Smart Screenshot Engine</p>
        </div>
    """, unsafe_allow_html=True)

    # --- ÜÇ KOLONLU KOKPİT ---
    ctrl_col, view_col = st.columns([1, 3], gap="medium")

    with ctrl_col:
        st.subheader("⚙️ Ayarlar")
        
        # Sembol ve Borsa
        c1, c2 = st.columns(2)
        symbol = c1.text_input("Sembol", value="BTCUSDT").upper()
        exchange = c2.text_input("Borsa", value="BINANCE").upper()
        
        # Zaman
        timeframe = st.selectbox("Zaman Dilimi", ["1m", "5m", "15m", "1H", "4H", "1D", "1W"], index=4)
        
        st.markdown("---")
    
        # ANA AKSİYON BUTONU
        capture_btn = st.button("🚀 SCREENSHOT AL", use_container_width=True)
        
        st.markdown("---")
        
        # Gelişmiş Ayarlar
        with st.expander("🛠️ Gelişmiş Özellikler", expanded=True):
            mode = st.radio("Çekim Modu", ["quick", "clean"], horizontal=True)
            theme = st.radio("Tema", ["dark", "light"], horizontal=True)
            
            # Çözünürlük Seçenekleri (İstediğinizDropdown)
            resolutions = {
                "Full HD (1920x1080)": (1920, 1080),
                "2K (2560x1440)": (2560, 1440),
                "4K (3840x2160)": (3840, 2160),
                "Kare (1080x1080)": (1080, 1080),
                "Mobil Dikey (1080x1920)": (1080, 1920)
            }
            res_label = st.selectbox("Çözünürlük Seçin", list(resolutions.keys()), index=0)
            width, height = resolutions[res_label]
            
            headless = st.toggle("Headless Mode", value=True)
            
            st.markdown("---")
            
            # ZAMANLAYICI KONTROLÜ
            st.markdown("#### ⏰ Otomasyon")
            
            # Esnek interval girişi (0 = Tek seferlik)
            col1, col2 = st.columns([3, 1])
            with col1:
                interval_minutes = st.number_input(
                    "Periyot (dakika)",
                    min_value=0.0,
                    max_value=1440.0,  # 24 saat
                    value=0.0,
                    step=0.5,
                    format="%.1f",
                    help="0 = Tek seferlik, >0 = Otomatik tekrar (örn: 1, 1.5, 5, 15 dakika)"
                )
            with col2:
                st.caption(" ")  # Boşluk için
                if interval_minutes == 0:
                    st.caption("**Tek seferlik**")
                else:
                    st.caption(f"**{interval_minutes:.1f}** dk")
            
            # Durum göstergesi (sadece otomasyon aktifse)
            if st.session_state.is_scheduling:
                next_run = st.session_state.scheduler.get_next_run_time()
                
                # Sayaç ve Durum Bilgisi
                c1, c2, c3 = st.columns(3)
                c1.metric("Toplam SS", st.session_state.get('total_scheduled_count', 0))
                
                if next_run:
                    # Kalan süreyi saniye cinsinden hesapla
                    now = datetime.now(next_run.tzinfo) if next_run.tzinfo else datetime.now()
                    remaining_seconds = int((next_run - now).total_seconds())
                    
                    if remaining_seconds < 0: remaining_seconds = 0
                    c2.metric("Sıradaki", f"{remaining_seconds} sn")
                
                c3.metric("Son Kontrol", st.session_state.get('last_check_time', '-'))
                st.info(f"▶️ **Otomasyon Aktif**")
                
                # Durdurma butonu (Daha belirgin)
                if st.button("🛑 OTOMASYONU DURDUR", use_container_width=True, type="primary"):
                    st.session_state.scheduler.stop_schedule()
                    st.session_state.is_scheduling = False
                    st.session_state.schedule_params = {}
                    st.warning("⏸️ Otomasyon durduruldu.")
                    st.rerun()

                # Mevcut parametreleri göster
                if st.session_state.schedule_params:
                    params = st.session_state.schedule_params
                    interval_val = params.get('interval', 0)
                    st.caption(
                        f"📊 {params.get('symbol')} @ {params.get('exchange')} "
                        f"({params.get('timeframe')}) - Her {interval_val:.1f} dakika"
                    )

        # İstatistikler
        if 'bot' in st.session_state:
            stats = st.session_state.bot.get_stats()
            st.markdown("---")
            m1, m2 = st.columns(2)
            m1.metric("Başarılı", stats['success'])
            m2.metric("Hata", stats['failed'], delta_color="inverse")

    with view_col:
        if capture_btn:
            # Interval değerine göre karar ver
            if interval_minutes == 0:
                # TEK SEFERLİK SCREENSHOT
                try:
                    with st.spinner(f"**{symbol}** yakalanıyor..."):
                        # Botu yeni parametrelerle initialize et (Dinamik güncelleme içerir)
                        bot = initialize_bot(headless=headless, theme=theme, width=width, height=height)
                        
                        success, path = bot.take_screenshot(
                            symbol=symbol,
                            exchange=exchange,
                            timeframe=timeframe,
                            mode=mode
                        )

                        if success and os.path.exists(path):
                            st.success(f"✅ {symbol} görüntüsü hazır!")
                            image = Image.open(path)
                            st.image(image, use_container_width=True)
                            
                            with open(path, "rb") as file:
                                st.download_button("💾 Kaydet", data=file, file_name=os.path.basename(path), use_container_width=True)
                        else:
                            st.error("❌ Hata: Görüntü alınamadı. Parametreleri kontrol edin.")
                except Exception as e:
                    st.error(f"⚠️ Hata: {str(e)}")
            else:
                # OTOMASYONU BAŞLAT
                try:
                    # Önce varolan scheduler'ı durdur
                    if st.session_state.is_scheduling:
                        st.session_state.scheduler.stop_schedule()
                        st.session_state.is_scheduling = False
                    
                    # Botu başlat
                    bot = initialize_bot(headless=headless, theme=theme, width=width, height=height)
                    
                    # Callback wrapper
                    def callback_wrapper(**params):
                        on_scheduled_capture(bot, **params)
                    
                    # Scheduler'ı başlat
                    st.session_state.scheduler.start_schedule(
                        interval_minutes=interval_minutes,
                        callback_fn=callback_wrapper,
                        symbol=symbol,
                        exchange=exchange,
                        timeframe=timeframe,
                        mode=mode
                    )
                    
                    st.session_state.is_scheduling = True
                    st.session_state.schedule_params = {
                        'symbol': symbol,
                        'exchange': exchange,
                        'timeframe': timeframe,
                        'interval': interval_minutes
                    }
                    
                    st.success(f"✅ Otomasyon başlatıldı! Her **{interval_minutes:.1f} dakika**da screenshot alınacak.")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"⚠️ Otomasyon hatası: {str(e)}")
        
        # SON YAKALANANLAR PANELİ (Klasörden dinamik yükleme)
        recent_screenshots = load_recent_screenshots(limit=5)
        
        if recent_screenshots:
            st.markdown("---")
            st.subheader("📸 Son Yakalananlar")
            
            # En fazla 5 tanesini göster
            for i, capture in enumerate(recent_screenshots):
                if os.path.exists(capture['path']):
                    with st.expander(
                        f"🖼️ {capture['symbol']} @ {capture['exchange']} - "
                        f"{capture['timestamp'].strftime('%H:%M:%S')}",
                        expanded=(i == 0)  # İlk olanı açık göster
                    ):
                        # Thumbnail görüntü
                        try:
                            img = Image.open(capture['path'])
                            st.image(img, use_container_width=True)
                            
                            # Detaylar
                            col1, col2, col3 = st.columns(3)
                            col1.caption(f"⏱️ {capture['timeframe']}")
                            col2.caption(f"📅 {capture['timestamp'].strftime('%d/%m/%Y')}")
                            col3.caption(f"🕐 {capture['timestamp'].strftime('%H:%M:%S')}")
                            
                            # İndir butonu
                            with open(capture['path'], "rb") as file:
                                st.download_button(
                                    "💾 İndir",
                                    data=file,
                                    file_name=os.path.basename(capture['path']),
                                    key=f"download_{i}_{int(capture['timestamp'].timestamp())}"
                                )
                        except Exception as e:
                            st.error(f"Görüntü yüklenemedi: {str(e)}")
        
        if not capture_btn and not recent_screenshots:
            st.info("Sol taraftan ayarları yapıp butona basın. Görüntü bu alanda belirecektir.")

    # Footer
    st.markdown("""
        <div style="position: fixed; bottom: 10px; right: 20px; color: grey; font-size: 10px;">
            ChartCapture Pro • Powered by Antigravity
        </div>
    """, unsafe_allow_html=True)

    # HEARTBEAT: Otomasyon aktifse 5 sn'de bir yenile
    if st.session_state.is_scheduling:
        import time as time_module
        time_module.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main()