"""
ChartCapture Pro - Utility Functions
Yardımcı fonksiyonlar.
"""

import os
import random
import time
from datetime import datetime
from typing import Optional

from .config import (
    PathConfig,
    SeleniumConfig,
    Timeframe,
    Theme,
    USER_AGENTS
)


def get_random_user_agent() -> str:
    """
    Rastgele user-agent döndürür.
    
    Returns:
        User-agent string
    """
    return random.choice(USER_AGENTS)


def random_delay(
    min_seconds: float = None, 
    max_seconds: float = None
) -> float:
    """
    Rastgele bekleme yapar.
    
    Args:
        min_seconds: Minimum bekleme süresi
        max_seconds: Maximum bekleme süresi
        
    Returns:
        Beklenen süre (saniye)
    """
    min_s = min_seconds or SeleniumConfig.MIN_RANDOM_DELAY
    max_s = max_seconds or SeleniumConfig.MAX_RANDOM_DELAY
    
    delay = random.uniform(min_s, max_s)
    time.sleep(delay)
    return delay


def ensure_directory(path: str) -> str:
    """
    Klasörün var olduğundan emin olur, yoksa oluşturur.
    
    Args:
        path: Klasör yolu
        
    Returns:
        Klasör yolu
    """
    os.makedirs(path, exist_ok=True)
    return path


def generate_screenshot_filename(
    symbol: str,
    exchange: str,
    timeframe: str,
    extension: str = "png"
) -> str:
    """
    Screenshot dosya adı oluşturur.
    
    Args:
        symbol: Sembol adı
        exchange: Borsa adı
        timeframe: Zaman dilimi
        extension: Dosya uzantısı
        
    Returns:
        Dosya adı string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Özel karakterleri temizle
    safe_symbol = symbol.replace("/", "_").replace(":", "_")
    safe_exchange = exchange.replace("/", "_").replace(":", "_")
    
    return f"{safe_symbol}_{safe_exchange}_{timeframe}_{timestamp}.{extension}"


def get_screenshot_path(
    symbol: str,
    exchange: str,
    timeframe: str,
    base_dir: str = None
) -> str:
    """
    Screenshot tam yolunu oluşturur.
    
    Args:
        symbol: Sembol adı
        exchange: Borsa adı
        timeframe: Zaman dilimi
        base_dir: Ana klasör (default: screenshots/)
        
    Returns:
        Tam dosya yolu
    """
    base = base_dir or PathConfig.SCREENSHOT_DIR
    ensure_directory(base)
    
    filename = generate_screenshot_filename(symbol, exchange, timeframe)
    return os.path.join(base, filename)


def parse_timeframe(timeframe_str: str) -> str:
    """
    Timeframe string'i normalize eder.
    
    Args:
        timeframe_str: Kullanıcı girişi (ör: "1d", "4H", "15m")
        
    Returns:
        TradingView formatına uygun timeframe
    """
    tf_upper = timeframe_str.upper().strip()
    
    # Mapping
    mapping = {
        "1M": "1",
        "3M": "3",
        "5M": "5",
        "15M": "15",
        "30M": "30",
        "45M": "45",
        "1H": "1H",
        "2H": "2H",
        "3H": "3H",
        "4H": "4H",
        "1D": "1D",
        "D": "1D",
        "1W": "1W",
        "W": "1W",
        "1MO": "1M",  # Monthly
        "MO": "1M",
    }
    
    # Direkt eşleşme kontrol
    if tf_upper in mapping:
        return mapping[tf_upper]
    
    # Sayısal değerler için
    if tf_upper.isdigit():
        return tf_upper
    
    # Default: girilen değeri döndür
    return timeframe_str


def validate_symbol(symbol: str) -> str:
    """
    Sembol adını temizler ve validate eder.
    
    Args:
        symbol: Sembol adı
        
    Returns:
        Temizlenmiş sembol
    """
    # Boşlukları kaldır
    cleaned = symbol.strip().upper()
    
    # Özel karakterleri kaldır (/ ve : hariç)
    allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/-:._")
    cleaned = "".join(c for c in cleaned if c in allowed_chars)
    
    return cleaned


def validate_exchange(exchange: str) -> str:
    """
    Borsa adını temizler.
    
    Args:
        exchange: Borsa adı
        
    Returns:
        Temizlenmiş borsa adı
    """
    return exchange.strip().upper()


def format_duration(seconds: float) -> str:
    """
    Süreyi okunabilir formata çevirir.
    
    Args:
        seconds: Saniye cinsinden süre
        
    Returns:
        Formatlanmış süre string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def sanitize_path(path: str) -> str:
    """
    Dosya yolunu güvenli hale getirir.
    
    Args:
        path: Dosya yolu
        
    Returns:
        Sanitize edilmiş yol
    """
    # Windows için geçersiz karakterleri kaldır
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        path = path.replace(char, '_')
    return path
