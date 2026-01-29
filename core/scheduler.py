"""
ChartCapture Pro - Scheduler Module
APScheduler tabanlı otomasyon sistemi.
"""

from datetime import datetime
from typing import Optional, Callable, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .logger import get_logger


class ScreenshotScheduler:
    """
    APScheduler ile screenshot otomasyon yöneticisi.
    Background thread'de çalışır ve UI'a callback ile bildirim gönderir.
    """
    
    def __init__(self):
        """Scheduler'ı başlatır."""
        self.logger = get_logger()
        self.scheduler: Optional[BackgroundScheduler] = None
        self.current_job = None
        self._is_running = False
        
    def start_schedule(
        self,
        interval_minutes: float,
        callback_fn: Callable,
        run_immediately: bool = True,
        **screenshot_params
    ) -> bool:
        """
        Zamanlayıcıyı başlatır.
        
        Args:
            interval_minutes: Tekrar süresi (dakika)
            callback_fn: Her screenshot sonrası çağrılacak fonksiyon
                         Signature: callback_fn(success: bool, filepath: str)
            run_immediately: İlk screenshot'ı hemen al
            **screenshot_params: Screenshot parametreleri (symbol, exchange, timeframe, mode)
            
        Returns:
            Başarılı mı
        """
        try:
            # Varolan scheduler'ı durdur
            if self._is_running:
                self.stop_schedule()
            
            # Yeni scheduler oluştur
            self.scheduler = BackgroundScheduler()
            
            # İlk screenshot'ı hemen al
            if run_immediately:
                self.logger.info("İlk screenshot hemen alınıyor...")
                try:
                    callback_fn(**screenshot_params)
                except Exception as e:
                    self.logger.error(f"İlk screenshot hatası: {str(e)}")
            
            # Job ekle
            self.current_job = self.scheduler.add_job(
                func=self._run_screenshot_task,
                trigger=IntervalTrigger(minutes=interval_minutes),
                args=[callback_fn, screenshot_params],
                id='screenshot_job',
                replace_existing=True,
                max_instances=1  # Aynı anda birden fazla job çalışmasın
            )
            
            # Scheduler'ı başlat
            self.scheduler.start()
            self._is_running = True
            
            self.logger.info(
                f"Zamanlayıcı başlatıldı: Her {interval_minutes} dakikada bir "
                f"{screenshot_params.get('symbol', 'UNKNOWN')} screenshot alınacak"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Zamanlayıcı başlatma hatası: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def _run_screenshot_task(self, callback_fn: Callable, params: Dict[str, Any]):
        """
        Screenshot görevi (APScheduler tarafından çağrılır).
        
        Args:
            callback_fn: Sonuç callback fonksiyonu
            params: Screenshot parametreleri
        """
        try:
            self.logger.info(f"Zamanlanmış screenshot başlatılıyor: {params.get('symbol', 'N/A')}")
            
            # Callback fonksiyonunu çağır ve parametreleri geç
            # NOT: Callback fonksiyonu içinde screenshot alınacak
            callback_fn(**params)
            
        except Exception as e:
            self.logger.error(f"Zamanlanmış screenshot hatası: {str(e)}")
    
    def stop_schedule(self) -> bool:
        """
        Zamanlayıcıyı durdurur.
        
        Returns:
            Başarılı mı
        """
        try:
            if self.scheduler and self._is_running:
                self.scheduler.shutdown(wait=False)
                self.scheduler = None
                self.current_job = None
                self._is_running = False
                self.logger.info("Zamanlayıcı durduruldu")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Zamanlayıcı durdurma hatası: {str(e)}")
            return False
    
    def is_running(self) -> bool:
        """
        Zamanlayıcı çalışıyor mu?
        
        Returns:
            Durum
        """
        return self._is_running
    
    def get_next_run_time(self) -> Optional[datetime]:
        """
        Bir sonraki çalışma zamanını döndürür.
        
        Returns:
            Sonraki çalışma zamanı veya None
        """
        try:
            if self.current_job and self._is_running:
                return self.current_job.next_run_time
            return None
        except:
            return None
    
    def __del__(self):
        """Destructor - temizlik."""
        self.stop_schedule()
