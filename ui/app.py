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
from core.persistence import persistence
from ui.utils import load_recent_screenshots, get_screenshot_count

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
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stDecoration"] {display:none;}
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
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

    .stButton>button {
        height: 3em;
        background: #4f46e5;
        border: none;
        font-weight: bold;
    }

    .stImage img {
        max-height: 65vh;
        object-fit: contain;
    }
    
    .status-badge {
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
    }
    .status-idle { background: #374151; color: #9ca3af; }
    .status-capturing { background: #fbbf24; color: #000; }
    .status-success { background: #10b981; color: #fff; }
    .status-error { background: #ef4444; color: #fff; }
</style>
""", unsafe_allow_html=True)

def initialize_bot(headless=True, theme="dark", width=1920, height=1080):
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
    
    st.session_state.bot.theme = theme
    st.session_state.current_theme = theme
    
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
    
    if 'active_jobs' not in st.session_state:
        saved_jobs = persistence.load_jobs()
        st.session_state.active_jobs = {}
        for job_params in saved_jobs:
            # Re-initialize status for existing jobs
            job_params['status'] = 'idle'
            start_scheduled_task(job_params)
            
    if 'recent_captures' not in st.session_state:
        st.session_state.recent_captures = []
        
    current_count = get_screenshot_count()
    if 'last_screenshot_count' not in st.session_state:
        st.session_state.last_screenshot_count = current_count

def start_scheduled_task(params):
    """Yeni bir zamanlanmış görev başlatır."""
    bot = initialize_bot(
        headless=params.get('headless', True),
        theme=params.get('theme', 'dark'),
        width=params.get('width', 1920),
        height=params.get('height', 1080)
    )
    
    job_id = params.get('job_id') or f"{params['symbol']}_{int(time.time())}"
    params['job_id'] = job_id
    params['status'] = params.get('status', 'idle')
    
    def callback_wrapper(**p):
        # Durumu güncelle (Yakalanıyor)
        if job_id in st.session_state.active_jobs:
            st.session_state.active_jobs[job_id]['status'] = 'capturing'
            # st.toast(f"📸 {p.get('symbol')} çekimi başladı...") # Background thread'de çalıştıığı için toast UI thread'ine düşmeyebilir, state kontrolü yeterli.
        
        success, _ = bot.take_screenshot(**p)
        
        # Durumu güncelle (Sonuç)
        if job_id in st.session_state.active_jobs:
            st.session_state.active_jobs[job_id]['status'] = 'success' if success else 'error'
            time.sleep(2) # Durumu görmek için kısa bekleme
            if job_id in st.session_state.active_jobs:
                st.session_state.active_jobs[job_id]['status'] = 'idle'
    
    st.session_state.scheduler.start_schedule(
        interval_minutes=params.get('interval', 15),
        callback_fn=callback_wrapper,
        job_id=job_id,
        run_immediately=False,
        **{k: v for k, v in params.items() if k not in ['interval', 'job_id', 'headless', 'theme', 'width', 'height', 'status']}
    )
    
    st.session_state.active_jobs[job_id] = params
    persistence.save_jobs(list(st.session_state.active_jobs.values()))
    return job_id

def main():
    initialize_session_state()
    
    # OTOMATIK YENİLEME
    current_count = get_screenshot_count()
    if current_count > st.session_state.last_screenshot_count:
        st.session_state.last_screenshot_count = current_count
        st.rerun()
    
    st.session_state.last_check_time = datetime.now().strftime("%H:%M:%S")
    
    st.markdown("""
        <div class="compact-header">
            <h3 style="margin:0;">📊 ChartCapture <span style="font-weight:200; font-size:15px;">v1.0</span></h3>
            <p style="margin:0; font-size:13px; opacity:0.8;">Multi-Bot Edition</p>
        </div>
    """, unsafe_allow_html=True)

    ctrl_col, view_col = st.columns([1, 2.5], gap="medium")

    with ctrl_col:
        st.subheader("➕ Yeni Görev Ekle")
        c1, c2 = st.columns(2)
        symbol = c1.text_input("Sembol", value="BTCUSDT").upper()
        exchange = c2.text_input("Borsa", value="BINANCE").upper()
        timeframe = st.selectbox("Zaman Dilimi", ["1m", "5m", "15m", "1H", "4H", "1D", "1W"], index=4)
        
        interval_minutes = st.number_input(
            "Otomasyon Periyodu (Dakika)",
            min_value=0.0, max_value=1440.0, value=0.0, step=1.0,
            help="0 girilirse sadece tek seferlik çekim yapılır."
        )

        capture_btn = st.button("🚀 GÖREVİ BAŞLAT", use_container_width=True)
        
        with st.expander("🛠️ Gelişmiş Ayarlar"):
            mode = st.radio("Çekim Modu", ["quick", "clean"], horizontal=True)
            theme = st.radio("Tema", ["dark", "light"], horizontal=True)
            resolutions = {
                "Full HD (1920x1080)": (1920, 1080),
                "2K (2560x1440)": (2560, 1440),
                "4K (3840x2160)": (3840, 2160)
            }
            res_label = st.selectbox("Çözünürlük", list(resolutions.keys()), index=0)
            width, height = resolutions[res_label]
            headless = st.toggle("Headless Mode", value=True)

        st.markdown("---")
        st.subheader("🤖 Aktif Botlar")
        
        if not st.session_state.active_jobs:
            st.info("Henüz aktif bir otomasyon görevi yok.")
        else:
            for jid, params in list(st.session_state.active_jobs.items()):
                status = params.get('status', 'idle')
                status_labels = {
                    'idle': '😴 Beklemede',
                    'capturing': '📸 Yakalanıyor...',
                    'success': '✅ Tamamlandı',
                    'error': '❌ Hata!'
                }
                status_class = f"status-{status}"
                
                with st.container(border=True):
                    cols = st.columns([3, 1])
                    cols[0].markdown(f"**{params['symbol']}** <span class='status-badge {status_class}'>{status_labels[status]}</span>", unsafe_allow_html=True)
                    cols[0].caption(f"{params['exchange']} | {params['timeframe']} | {params['interval']} dk")
                    
                    if cols[1].button("🗑️", key=f"stop_{jid}"):
                        st.session_state.scheduler.stop_job(jid)
                        del st.session_state.active_jobs[jid]
                        persistence.save_jobs(list(st.session_state.active_jobs.values()))
                        st.rerun()
                    
                    next_run = st.session_state.scheduler.get_next_run_time(jid)
                    if next_run:
                        now = datetime.now(next_run.tzinfo) if next_run.tzinfo else datetime.now()
                        rem = int((next_run - now).total_seconds())
                        st.caption(f"Sıradaki çekime: {max(0, rem)} saniye")
                    
                    # Eğer herhangi bir bot ss alıyorsa UI'ı sık yenile
                    if any(p.get('status') == 'capturing' for p in st.session_state.active_jobs.values()):
                        st.empty() # Placeholder for rerun trigger logic if needed

    with view_col:
        if capture_btn:
            if interval_minutes == 0:
                try:
                    with st.spinner(f"**{symbol}** yakalanıyor..."):
                        bot = initialize_bot(headless=headless, theme=theme, width=width, height=height)
                        success, path = bot.take_screenshot(symbol=symbol, exchange=exchange, timeframe=timeframe, mode=mode)
                        if success:
                            st.image(Image.open(path), use_container_width=True)
                            st.toast(f"✅ {symbol} başarıyla yakalandı!")
                except Exception as e: st.error(str(e))
            else:
                params = {
                    'symbol': symbol, 'exchange': exchange, 'timeframe': timeframe, 
                    'interval': interval_minutes, 'mode': mode, 'theme': theme,
                    'width': width, 'height': height, 'headless': headless,
                    'status': 'idle'
                }
                start_scheduled_task(params)
                st.success(f"✅ {symbol} için otomasyon başlatıldı!")
                st.rerun()
        
        recent_screenshots = load_recent_screenshots(limit=5)
        if recent_screenshots:
            st.markdown("---")
            st.subheader("📸 Son Yakalananlar")
            for i, capture in enumerate(recent_screenshots):
                if os.path.exists(capture['path']):
                    with st.expander(f"🖼️ {capture['symbol']} @ {capture['exchange']} - {capture['timestamp'].strftime('%H:%M:%S')}", expanded=(i == 0)):
                        try:
                            st.image(Image.open(capture['path']), use_container_width=True)
                            c1, c2, c3 = st.columns(3)
                            c1.caption(f"⏱️ {capture['timeframe']}")
                            c2.caption(f"📅 {capture['timestamp'].strftime('%d/%m/%Y')}")
                            c3.caption(f"🕐 {capture['timestamp'].strftime('%H:%M:%S')}")
                        except Exception as e: st.error(f"Yükleme hatası: {str(e)}")
        
        if not capture_btn and not recent_screenshots:
            st.info("Sol taraftan ayarları yapıp butona basın.")

    st.markdown("""<div style="position: fixed; bottom: 10px; right: 20px; color: grey; font-size: 10px;">ChartCapture • Multi-Bot Edition</div>""", unsafe_allow_html=True)

    # Eğer aktif botlar varsa veya bir bot ss alıyorsa periyodik yenileme
    if st.session_state.active_jobs:
        refresh_rate = 1 if any(p.get('status') == 'capturing' for p in st.session_state.active_jobs.values()) else 5
        time.sleep(refresh_rate)
        st.rerun()

if __name__ == "__main__":
    main()