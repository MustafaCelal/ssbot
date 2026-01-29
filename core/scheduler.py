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
    Çoklu görev (job) yönetimini destekler.
    """
    
    def __init__(self):
        """Scheduler'ı başlatır."""
        self.logger = get_logger()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self._jobs: Dict[str, Any] = {}
        
    def start_schedule(
        self,
        interval_minutes: float,
        callback_fn: Callable,
        run_immediately: bool = True,
        job_id: str = None,
        **screenshot_params
    ) -> str:
        """
        Yeni bir zamanlı görev başlatır.
        
        Args:
            interval_minutes: Tekrar süresi (dakika)
            callback_fn: Screenshot fonksiyonu
            run_immediately: İlkini hemen al
            job_id: Benzersiz görev ID (None ise otomatik oluşturulur)
            **screenshot_params: Parametreler
            
        Returns:
            job_id: Atanan ID
        """
        try:
            if not job_id:
                job_id = f"{screenshot_params.get('symbol', 'UNKNOWN')}_{int(time.time())}"
            
            # Eğer aynı ID varsa durdur
            if job_id in self._jobs:
                self.stop_job(job_id)
            
            # Hemen çalıştır
            if run_immediately:
                try:
                    callback_fn(**screenshot_params)
                except Exception as e:
                    self.logger.error(f"Hemen çalıştırma hatası ({job_id}): {str(e)}")
            
            # Job ekle
            job = self.scheduler.add_job(
                func=self._run_screenshot_task,
                trigger=IntervalTrigger(minutes=interval_minutes),
                args=[callback_fn, screenshot_params, job_id],
                id=job_id,
                replace_existing=True,
                max_instances=1
            )
            
            self._jobs[job_id] = {
                'job': job,
                'params': screenshot_params,
                'interval': interval_minutes
            }
            
            self.logger.info(f"Görev eklendi: {job_id} (Her {interval_minutes} dk)")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Görev başlatma hatası: {str(e)}")
            return ""
    
    def _run_screenshot_task(self, callback_fn: Callable, params: Dict[str, Any], job_id: str):
        """İçsel görev çalıştırıcı."""
        try:
            self.logger.info(f"Görevi çalıştırılıyor: {job_id}")
            callback_fn(**params)
        except Exception as e:
            self.logger.error(f"Görev çalışma hatası ({job_id}): {str(e)}")
    
    def stop_job(self, job_id: str) -> bool:
        """Belirli bir görevi durdurur."""
        try:
            if job_id in self._jobs:
                self.scheduler.remove_job(job_id)
                del self._jobs[job_id]
                self.logger.info(f"Görev durduruldu: {job_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Görev durdurma hatası ({job_id}): {str(e)}")
            return False
            
    def stop_all(self):
        """Tüm görevleri durdurur."""
        for job_id in list(self._jobs.keys()):
            self.stop_job(job_id)
            
    def is_running(self, job_id: str = None) -> bool:
        """Scheduler veya belirli bir job çalışıyor mu?"""
        if job_id:
            return job_id in self._jobs
        return self.scheduler.running
    
    def get_next_run_time(self, job_id: str) -> Optional[datetime]:
        """Bir sonraki çalışma zamanı."""
        if job_id in self._jobs:
            return self._jobs[job_id]['job'].next_run_time
        return None

    def get_all_jobs(self) -> Dict[str, Dict]:
        """Tüm aktif görevleri ve parametrelerini döner."""
        result = {}
        for jid, data in self._jobs.items():
            result[jid] = {
                'params': data['params'],
                'interval': data['interval'],
                'next_run': data['job'].next_run_time
            }
        return result
    
    def __del__(self):
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
        except:
            pass
