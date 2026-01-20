"""
ChartCapture Pro - Configuration Module
Tüm yapılandırılabilir parametreler ve sabitler.
"""

from enum import Enum
from typing import List
import os


# ========================
# TIMEFRAME DEFINITIONS
# ========================
class Timeframe(Enum):
    """TradingView desteklenen zaman dilimleri."""
    M1 = "1"
    M3 = "3"
    M5 = "5"
    M15 = "15"
    M30 = "30"
    M45 = "45"
    H1 = "1H"
    H2 = "2H"
    H3 = "3H"
    H4 = "4H"
    D1 = "1D"
    W1 = "1W"
    M1_MONTH = "1M"


# ========================
# THEME OPTIONS
# ========================
class Theme(Enum):
    """TradingView tema seçenekleri."""
    LIGHT = "light"
    DARK = "dark"


# ========================
# SCREENSHOT MODES
# ========================
class ScreenshotMode(Enum):
    """Screenshot alma yöntemleri."""
    QUICK = "quick"   # Direkt element capture (Hızlı ve gizli)
    CLEAN = "clean"   # TradingView snapshot butonu (Resmi ve temiz)


# ========================
# SUPPORTED EXCHANGES
# ========================
SUPPORTED_EXCHANGES: List[str] = [
    "BINANCE",
    "BYBIT",
    "COINBASE",
    "KRAKEN",
    "BITSTAMP",
    "NASDAQ",
    "NYSE",
    "AMEX",
    "BIST",  # Borsa Istanbul
    "FX",
    "FOREXCOM",
    "OANDA",
    "CME_MINI",
    "COMEX",
]


# ========================
# USER AGENT POOL
# ========================
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
]


# ========================
# SELENIUM SETTINGS
# ========================
class SeleniumConfig:
    """Selenium ile ilgili yapılandırma."""
    
    # Bekleme süreleri (saniye)
    PAGE_LOAD_TIMEOUT: int = 30
    IMPLICIT_WAIT: int = 10
    ELEMENT_WAIT_TIMEOUT: int = 15
    
    # Screenshot ayarları
    MIN_RANDOM_DELAY: float = 0.5
    MAX_RANDOM_DELAY: float = 1.5
    
    # Retry ayarları
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 2.0
    
    # Window size
    WINDOW_WIDTH: int = 1920
    WINDOW_HEIGHT: int = 1080


# ========================
# TRADINGVIEW URLS
# ========================
class TradingViewURLs:
    """TradingView URL şablonları."""
    
    BASE_URL: str = "https://www.tradingview.com"
    CHART_URL: str = "https://www.tradingview.com/chart"
    
    @staticmethod
    def get_symbol_url(symbol: str, exchange: str = None, timeframe: str = "1D", theme: str = "dark") -> str:
        """
        Sembol URL'i oluşturur.
        
        Args:
            symbol: İşlem çifti (ör: BTCUSDT)
            exchange: Borsa adı (ör: BINANCE)
            timeframe: Zaman dilimi (ör: 1D, 5, 1H)
            theme: Tema (light/dark)
            
        Returns:
            Tam TradingView URL'i
        """
        if exchange:
            full_symbol = f"{exchange}:{symbol}"
        else:
            full_symbol = symbol
            
        return f"https://www.tradingview.com/chart/?symbol={full_symbol}&interval={timeframe}&theme={theme}"


# ========================
# FILE PATHS
# ========================
class PathConfig:
    """Dosya yolları yapılandırması."""
    
    # Proje kök dizini (bir seviye yukarı: core -> root)
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Screenshot klasörü
    SCREENSHOT_DIR: str = os.path.join(PROJECT_ROOT, "screenshots")
    
    # Log klasörü
    LOG_DIR: str = os.path.join(PROJECT_ROOT, "logs")
    
    # Screenshot dosya formatı
    SCREENSHOT_FORMAT: str = "{symbol}_{exchange}_{timeframe}_{timestamp}.png"


# ========================
# CSS SELECTORS
# ========================
class Selectors:
    """TradingView element selectors."""
    
    # Snapshot button (üst toolbar)
    SNAPSHOT_BUTTON: str = '[data-name="take-screenshot"]'
    SNAPSHOT_BUTTON_ALT: str = 'button[aria-label="Take a snapshot"]'
    
    # Chart container
    CHART_CONTAINER: str = ".chart-container, .chart-container-border, .chart-gui-wrapper, .layout__area--center"
    CHART_WIDGET: str = "#chart-area"
    
    # Loading indicators
    LOADING_SPINNER: str = ".tv-loader, .tv-spinner, .loading-indicator"
    CHART_LOADING: str = ".chart-loading-indicator"
    
    # Dialog/Modal
    SNAPSHOT_DIALOG: str = ".tv-dialog__modal-container, #overlap-manager-root .dialog-29_Z9_cn"
    DOWNLOAD_BUTTON: str = '[data-name="download-chart-image"], [data-name="save-chart-image"]'
    COPY_LINK_BUTTON: str = '[data-name="copy-link-to-the-chart-image"]'
    
    # Cookie consent / Popups
    COOKIE_ACCEPT_BUTTON: str = "button.accept-cookies, .cookie-policy-button-accept, [data-role='accept-all'], #overlap-manager-root button"
    
    # Login elements
    LOGIN_BUTTON: str = '[data-name="header-user-menu-sign-in"]'
    EMAIL_INPUT: str = 'input[name="id_username"]'
    PASSWORD_INPUT: str = 'input[name="id_password"]'


# ========================
# LOGIN CREDENTIALS (Optional)
# ========================
class LoginConfig:
    """Login yapılandırması (environment variable'lardan okunur)."""
    
    # Credentials - güvenlik için environment variable kullanılır
    USERNAME: str = os.environ.get("TV_USERNAME", "")
    PASSWORD: str = os.environ.get("TV_PASSWORD", "")
    
    @classmethod
    def has_credentials(cls) -> bool:
        """Credential var mı kontrol eder."""
        return bool(cls.USERNAME and cls.PASSWORD)
