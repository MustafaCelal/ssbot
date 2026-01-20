"""
ChartCapture Pro - Logger Module
Dosya ve konsol logging sistemi.
"""

import logging
import os
from datetime import datetime
from typing import Optional
from .config import PathConfig


class BotLogger:
    """
    Bot için özelleştirilmiş logger sınıfı.
    Hem dosyaya hem konsola log yazar.
    """
    
    _instance: Optional['BotLogger'] = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern - tek instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, log_level: int = logging.INFO):
        """
        Logger'ı başlatır.
        
        Args:
            log_level: Logging seviyesi (default: INFO)
        """
        if self._initialized:
            return
            
        self._initialized = True
        self.logger = logging.getLogger("ChartCapturePro")
        self.logger.setLevel(log_level)
        
        # Önceki handler'ları temizle
        self.logger.handlers.clear()
        
        # Log dizinini oluştur
        os.makedirs(PathConfig.LOG_DIR, exist_ok=True)
        
        # Log formatı
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Konsol handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Dosya handler (günlük log dosyası)
        log_filename = f"bot_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = os.path.join(PathConfig.LOG_DIR, log_filename)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.info(f"Logger başlatıldı. Log dosyası: {log_path}")
    
    def info(self, message: str) -> None:
        """Info seviyesinde log."""
        self.logger.info(message)
    
    def debug(self, message: str) -> None:
        """Debug seviyesinde log."""
        self.logger.debug(message)
    
    def warning(self, message: str) -> None:
        """Warning seviyesinde log."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Error seviyesinde log."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Critical seviyesinde log."""
        self.logger.critical(message)
    
    def screenshot_result(
        self, 
        symbol: str, 
        exchange: str, 
        success: bool, 
        filepath: str = None,
        error: str = None,
        retry_count: int = 0
    ) -> None:
        """
        Screenshot işlem sonucunu loglar.
        
        Args:
            symbol: Sembol adı
            exchange: Borsa adı
            success: Başarılı mı
            filepath: Kaydedilen dosya yolu
            error: Hata mesajı (varsa)
            retry_count: Retry sayısı
        """
        if success:
            self.info(
                f"✓ SCREENSHOT BAŞARILI | {exchange}:{symbol} | "
                f"Dosya: {filepath} | Retry: {retry_count}"
            )
        else:
            self.error(
                f"✗ SCREENSHOT BAŞARISIZ | {exchange}:{symbol} | "
                f"Hata: {error} | Retry: {retry_count}"
            )
    


def get_logger(log_level: int = logging.INFO) -> BotLogger:
    """
    Logger instance döndürür.
    
    Args:
        log_level: Logging seviyesi
        
    Returns:
        BotLogger instance
    """
    return BotLogger(log_level)
