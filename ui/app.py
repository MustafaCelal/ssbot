import streamlit as st
import sys
import os

# root dizini path'e ekleyelim ki core paketini bulabilsin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.bot import ChartCapture

def main():
    st.set_page_config(page_title="ChartCapture Pro", layout="centered")
    
    st.title("📊 ChartCapture Pro UI")
    st.markdown("---")
    
    st.sidebar.header("Ayarlar")
    symbol = st.sidebar.text_input("Sembol", value="BTCUSDT")
    exchange = st.sidebar.selectbox("Borsa", ["BINANCE", "BYBIT", "NASDAQ"])
    timeframe = st.sidebar.selectbox("Zaman Dilimi", ["1D", "4H", "1H", "15m"])
    
    if st.button("Screenshot Al"):
        with st.spinner("Bot çalışıyor..."):
            # Örnek kullanım (Core entegrasyonu)
            # bot = ChartCapture(headless=True)
            # success, path = bot.take_screenshot(symbol, exchange, timeframe)
            st.success(f"Bu bir demodur. {symbol} için screenshot alma kodu buraya gelecek.")

if __name__ == "__main__":
    main()
