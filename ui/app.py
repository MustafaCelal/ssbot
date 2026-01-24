import streamlit as st
import sys
import os
from PIL import Image
import time

# root dizini path'e ekleyelim ki core paketini bulabilsin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.bot import ChartCapture

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

def main():
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

        # İstatistikler
        if 'bot' in st.session_state:
            stats = st.session_state.bot.get_stats()
            st.markdown("---")
            m1, m2 = st.columns(2)
            m1.metric("Başarılı", stats['success'])
            m2.metric("Hata", stats['failed'], delta_color="inverse")

    with view_col:
        if capture_btn:
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
                        st.image(image, use_column_width=True)
                        
                        with open(path, "rb") as file:
                            st.download_button("💾 Kaydet", data=file, file_name=os.path.basename(path), use_container_width=True)
                    else:
                        st.error("❌ Hata: Görüntü alınamadı. Parametreleri kontrol edin.")
            except Exception as e:
                st.error(f"⚠️ Hata: {str(e)}")
        else:
            st.info("Sol taraftan ayarları yapıp butona basın. Görüntü bu alanda belirecektir.")

    # Footer
    st.markdown("""
        <div style="position: fixed; bottom: 10px; right: 20px; color: grey; font-size: 10px;">
            ChartCapture Pro • Powered by Antigravity
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()