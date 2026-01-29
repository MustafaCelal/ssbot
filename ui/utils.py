import os
from datetime import datetime
from PIL import Image
from core.bot import ChartCapture
from core.logger import get_logger

logger = get_logger()

def load_recent_screenshots(screenshot_dir="./screenshots", limit=10):
    """
    Screenshot klasöründen son dosyaları yükler.
    """
    try:
        if not os.path.exists(screenshot_dir):
            return []
        
        screenshots = []
        for filename in os.listdir(screenshot_dir):
            if filename.endswith('.png'):
                filepath = os.path.join(screenshot_dir, filename)
                file_stat = os.stat(filepath)
                
                parts = filename.replace('.png', '').split('_')
                if len(parts) >= 3:
                    screenshots.append({
                        'path': filepath,
                        'timestamp': datetime.fromtimestamp(file_stat.st_mtime),
                        'symbol': parts[0] if len(parts) > 0 else 'N/A',
                        'exchange': parts[1] if len(parts) > 1 else 'N/A',
                        'timeframe': parts[2] if len(parts) > 2 else 'N/A',
                        'size': file_stat.st_size
                    })
        
        screenshots.sort(key=lambda x: x['timestamp'], reverse=True)
        return screenshots[:limit]
        
    except Exception as e:
        logger.error(f"Screenshot yükleme hatası: {str(e)}")
        return []

def get_screenshot_count(screenshot_dir="./screenshots"):
    """Screenshot klasöründeki dosya sayısını döndürür."""
    if not os.path.exists(screenshot_dir):
        return 0
    return len([f for f in os.listdir(screenshot_dir) if f.endswith('.png')])
