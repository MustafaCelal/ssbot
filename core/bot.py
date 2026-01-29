"""
ChartCapture Pro - Main Bot Class
OOP tabanlı ana kontrol sınıfı.
"""

import time
import threading
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from .browser import BrowserManager
from .engine import ScreenshotEngine
from .config import (
    SeleniumConfig, 
    Theme, 
    PathConfig,
    TradingViewURLs,
    LoginConfig,
    Selectors
)
from .logger import get_logger
from .utils import (
    random_delay, 
    ensure_directory, 
    validate_symbol, 
    validate_exchange,
    parse_timeframe,
    format_duration
)


class ChartCapture:
    """
    ChartCapture Pro ana sınıfı.
    Guest ve Login mod desteği ile screenshot alma.
    Thread-safe screenshot alımı için Lock mekanizması içerir.
    """
    
    def __init__(
        self,
        headless: bool = True,
        theme: str = "dark",
        output_dir: str = None,
        login_mode: bool = False,
        width: int = 1920,
        height: int = 1080
    ):
        """
        ChartCapture'i başlatır.
        """
        self.headless = headless
        self.theme = theme.lower() if theme else "dark"
        self.output_dir = output_dir or PathConfig.SCREENSHOT_DIR
        self.login_mode = login_mode
        self.width = width
        self.height = height
        
        self.logger = get_logger()
        self.browser: Optional[BrowserManager] = None
        self.screenshot_engine: Optional[ScreenshotEngine] = None
        self._lock = threading.Lock()
        
        self._is_initialized = False
        self._is_logged_in = False
        
        # İstatistikler
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "start_time": None
        }
        
        # Çıktı klasörünü oluştur
        ensure_directory(self.output_dir)
        
    def initialize(self) -> bool:
        """
        Bot'u başlatır ve browser'ı açar.
        """
        if self._is_initialized:
            return True
            
        try:
            self.logger.info("=" * 60)
            self.logger.info("ChartCapture Pro başlatılıyor...")
            self.logger.info(f"Mod: {'Login' if self.login_mode else 'Guest'}")
            self.logger.info(f"Theme: {self.theme}")
            self.logger.info(f"Headless: {self.headless}")
            self.logger.info("=" * 60)
            
            # Browser'ı başlat
            self.browser = BrowserManager(
                headless=self.headless,
                width=self.width,
                height=self.height
            )
            self.browser.start()
            
            # Screenshot engine'i oluştur
            self.screenshot_engine = ScreenshotEngine(self.browser)
            
            # Login modundaysa giriş yap
            if self.login_mode:
                if not self._login():
                    self.logger.warning("Login başarısız, guest modda devam ediliyor...")
                    
            self._is_initialized = True
            self.stats["start_time"] = datetime.now()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Başlatma hatası: {str(e)}")
            return False
    
    def _login(self) -> bool:
        """
        TradingView'a giriş yapar.
        """
        if not LoginConfig.has_credentials():
            self.logger.warning("Login credentials bulunamadı (TV_USERNAME, TV_PASSWORD)")
            return False
            
        try:
            self.logger.info("TradingView'a giriş yapılıyor...")
            
            # Login sayfasına git
            self.browser.navigate_to(TradingViewURLs.BASE_URL)
            time.sleep(2)
            
            # Login butonuna tıkla
            login_btn = self.browser.wait_for_element(
                Selectors.LOGIN_BUTTON, 
                clickable=True
            )
            if login_btn:
                login_btn.click()
                time.sleep(2)
                
                # Email gir
                email_input = self.browser.wait_for_element(Selectors.EMAIL_INPUT)
                if email_input:
                    email_input.send_keys(LoginConfig.USERNAME)
                    
                # Password gir
                password_input = self.browser.wait_for_element(Selectors.PASSWORD_INPUT)
                if password_input:
                    password_input.send_keys(LoginConfig.PASSWORD)
                    
                # Submit (Enter tuşu ile)
                password_input.submit()
                time.sleep(5)
                
                self._is_logged_in = True
                self.logger.info("Login başarılı!")
                return True
                
        except Exception as e:
            self.logger.error(f"Login hatası: {str(e)}")
            
        return False
    
    def take_screenshot(
        self,
        symbol: str,
        exchange: str = "BINANCE",
        timeframe: str = "1D",
        mode: str = "quick"
    ) -> Tuple[bool, str]:
        """
        Thread-safe screenshot alımı.
        """
        with self._lock:
            # Başlatılmamışsa başlat
            if not self._is_initialized:
                if not self.initialize():
                    return (False, "")
            
            # Parametreleri validate et
            symbol = validate_symbol(symbol)
            exchange = validate_exchange(exchange)
            timeframe = parse_timeframe(timeframe)
            
            self.stats["total"] += 1
            
            # Screenshot al
            success, filepath, error = self.screenshot_engine.take_screenshot(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                theme=self.theme,
                output_dir=self.output_dir,
                mode=mode
            )
            
            if success:
                self.stats["success"] += 1
            else:
                self.stats["failed"] += 1
                
            return (success, filepath)
    
    def get_stats(self) -> Dict:
        """İstatistikleri döndürür."""
        return self.stats.copy()
    
    def close(self) -> None:
        """
        Bot'u ve browser'ı kapatır.
        """
        if self.browser:
            self.browser.close()
            self.browser = None
            
        self.screenshot_engine = None
        self._is_initialized = False
        self._is_logged_in = False
        
        self.logger.info("ChartCapture Pro kapatıldı.")
    
    def __enter__(self):
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def __del__(self):
        self.close()
