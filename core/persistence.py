import json
import os
from typing import List, Dict, Any
from .logger import get_logger
from .config import PathConfig

class JobPersistence:
    """
    Zamanlanmış görevlerin (jobs) kalıcı hale getirilmesi için sınıf.
    JSON tabanlı basit bir depolama kullanır.
    """
    
    def __init__(self, filename: str = "jobs.json"):
        self.logger = get_logger()
        self.filepath = os.path.join(PathConfig.PROJECT_ROOT, filename)
        
    def save_jobs(self, jobs: List[Dict[str, Any]]) -> bool:
        """
        Görev listesini dosyaya kaydeder.
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=4, ensure_ascii=False)
            self.logger.info(f"Görevler kaydedildi: {self.filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Görevler kaydedilemedi: {str(e)}")
            return False
            
    def load_jobs(self) -> List[Dict[str, Any]]:
        """
        Kayıtlı görevleri dosyadan okur.
        """
        if not os.path.exists(self.filepath):
            return []
            
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Görevler okunamadı: {str(e)}")
            return []
            
    def clear_jobs(self) -> bool:
        """
        Kayıtlı görevleri temizler.
        """
        try:
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
            return True
        except Exception as e:
            self.logger.error(f"Görevler temizlenemedi: {str(e)}")
            return False

# Global instance
persistence = JobPersistence()
