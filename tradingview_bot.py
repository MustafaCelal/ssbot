"""
TradingView Screenshot Bot - Main Bot Class
OOP tabanlı ana kontrol sınıfı.
"""

import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from browser_manager import BrowserManager
from screenshot_engine import ScreenshotEngine
from config import (
    SeleniumConfig, 
    Theme, 
    PathConfig,
    TradingViewURLs,
    LoginConfig,
    Selectors
)
from logger import get_logger
from utils import (
    random_delay, 
    ensure_directory, 
    validate_symbol, 
    validate_exchange,
    parse_timeframe,
    format_duration
)


class TradingViewBot:
    """
    TradingView Screenshot Bot ana sınıfı.
    Guest ve Login mod desteği ile screenshot alma.
    """
    
    def __init__(
        self,
        headless: bool = True,
        theme: str = "dark",
        output_dir: str = None,
        login_mode: bool = False
    ):
        """
        TradingViewBot'u başlatır.
        
        Args:
            headless: Headless modda çalıştır
            theme: Tema (light/dark)
            output_dir: Screenshot çıktı klasörü
            login_mode: Login modda çalıştır
        """
        self.headless = headless
        self.theme = theme.lower() if theme else "dark"
        self.output_dir = output_dir or PathConfig.SCREENSHOT_DIR
        self.login_mode = login_mode
        
        self.logger = get_logger()
        self.browser: Optional[BrowserManager] = None
        self.screenshot_engine: Optional[ScreenshotEngine] = None
        
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
        
        Returns:
            Başarılı mı
        """
        if self._is_initialized:
            return True
            
        try:
            self.logger.info("=" * 60)
            self.logger.info("TradingView Screenshot Bot başlatılıyor...")
            self.logger.info(f"Mod: {'Login' if self.login_mode else 'Guest'}")
            self.logger.info(f"Theme: {self.theme}")
            self.logger.info(f"Headless: {self.headless}")
            self.logger.info("=" * 60)
            
            # Browser'ı başlat
            self.browser = BrowserManager(headless=self.headless)
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
        
        Returns:
            Başarılı mı
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
        timeframe: str = "1D"
    ) -> Tuple[bool, str]:
        """
        Tek sembol için screenshot alır.
        
        Args:
            symbol: Sembol adı (ör: BTCUSDT)
            exchange: Borsa adı
            timeframe: Zaman dilimi
            
        Returns:
            Tuple(success, filepath)
        """
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
            output_dir=self.output_dir
        )
        
        if success:
            self.stats["success"] += 1
        else:
            self.stats["failed"] += 1
            
        return (success, filepath)
    
    def batch_screenshot(
        self,
        symbols: List[str],
        exchange: str = "BINANCE",
        timeframe: str = "1D"
    ) -> Dict[str, Tuple[bool, str]]:
        """
        Birden fazla sembol için batch screenshot alır.
        
        Args:
            symbols: Sembol listesi
            exchange: Borsa adı
            timeframe: Zaman dilimi
            
        Returns:
            Dict[symbol] = (success, filepath)
        """
        results = {}
        
        if not self._is_initialized:
            if not self.initialize():
                return results
        
        self.logger.info(f"Batch screenshot başlıyor: {len(symbols)} sembol")
        
        for i, symbol in enumerate(symbols, 1):
            self.logger.info(f"[{i}/{len(symbols)}] İşleniyor: {symbol}")
            
            success, filepath = self.take_screenshot(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe
            )
            
            results[symbol] = (success, filepath)
            
            # Son sembol değilse random bekleme
            if i < len(symbols):
                delay = random_delay()
                self.logger.debug(f"Sonraki sembol için bekleniyor: {delay:.1f}s")
        
        # Özet log
        self._log_batch_summary()
        
        return results
    
    def batch_screenshot_multi_timeframe(
        self,
        symbols: List[str],
        exchange: str = "BINANCE",
        timeframes: List[str] = None
    ) -> Dict[str, Dict[str, Tuple[bool, str]]]:
        """
        Birden fazla sembol ve timeframe için screenshot alır.
        
        Args:
            symbols: Sembol listesi
            exchange: Borsa adı
            timeframes: Timeframe listesi
            
        Returns:
            Dict[symbol][timeframe] = (success, filepath)
        """
        timeframes = timeframes or ["1D"]
        results = {}
        
        if not self._is_initialized:
            if not self.initialize():
                return results
        
        total_ops = len(symbols) * len(timeframes)
        self.logger.info(f"Multi-timeframe batch başlıyor: {total_ops} operasyon")
        
        op_count = 0
        for symbol in symbols:
            results[symbol] = {}
            
            for tf in timeframes:
                op_count += 1
                self.logger.info(f"[{op_count}/{total_ops}] {symbol} @ {tf}")
                
                success, filepath = self.take_screenshot(
                    symbol=symbol,
                    exchange=exchange,
                    timeframe=tf
                )
                
                results[symbol][tf] = (success, filepath)
                
                # Bekleme
                if op_count < total_ops:
                    random_delay()
        
        self._log_batch_summary()
        return results
    
    def _log_batch_summary(self) -> None:
        """Batch işlem özetini loglar."""
        if self.stats["start_time"]:
            duration = (datetime.now() - self.stats["start_time"]).total_seconds()
        else:
            duration = 0
            
        self.logger.batch_summary(
            total=self.stats["total"],
            success=self.stats["success"],
            failed=self.stats["failed"],
            duration_seconds=duration
        )
    
    def get_stats(self) -> Dict:
        """İstatistikleri döndürür."""
        return self.stats.copy()
    
    def close(self) -> None:
        """
        Bot'u ve browser'ı kapatır.
        Memory leak önleme.
        """
        if self.browser:
            self.browser.close()
            self.browser = None
            
        self.screenshot_engine = None
        self._is_initialized = False
        self._is_logged_in = False
        
        self.logger.info("TradingView Bot kapatıldı.")
    
    def __enter__(self):
        """Context manager desteği."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - otomatik kapanış."""
        self.close()
        return False
    
    def __del__(self):
        """Destructor - temizlik."""
        self.close()
