import argparse
from typing import List
from .config import SUPPORTED_EXCHANGES

def parse_arguments() -> argparse.Namespace:
    """
    CLI argümanlarını parse eder.
    """
    parser = argparse.ArgumentParser(
        description="ChartCapture Pro - Otomatik chart screenshot aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  # Tekli screenshot
  python main.py --symbol BTCUSDT --exchange BINANCE --timeframe 1D
  
  # Light theme, headed mod
  python main.py --symbol AAPL --exchange NASDAQ --theme light --no-headless
        """
    )
    
    parser.add_argument("--symbol", "-s", type=str, required=True, help="Sembol adı (ör: BTCUSDT)")
    parser.add_argument("--exchange", "-e", type=str, default="BINANCE", choices=SUPPORTED_EXCHANGES, help="Borsa adı (default: BINANCE)")
    parser.add_argument("--timeframe", "-t", type=str, default="1D", help="Zaman dilimi (ör: 1H, 4H, 1D, 1W)")
    parser.add_argument("--theme", type=str, choices=["light", "dark"], default="dark", help="Tema seçimi (default: dark)")
    parser.add_argument("--no-headless", action="store_true", help="Browser'ı görünür modda çalıştır")
    parser.add_argument("--width", type=int, default=1920, help="Browser genişliği (default: 1920)")
    parser.add_argument("--height", type=int, default=1080, help="Browser yüksekliği (default: 1080)")
    parser.add_argument("--login", action="store_true", help="TradingView'a giriş yap (TV_USERNAME, TV_PASSWORD env vars gerekli)")
    parser.add_argument("--output", "-o", type=str, default=None, help="Screenshot çıktı klasörü (default: ./screenshots)")
    parser.add_argument("--mode", "-m", type=str, choices=["quick", "clean"], default="quick", help="Screenshot modu: quick (hızlı), clean (resmi) (default: quick)")
    parser.add_argument("--interval", "-i", type=int, default=0, help="Dakika cinsinden periyodik çalıştırma (0: sadece bir kez)")
    
    return parser.parse_args()
