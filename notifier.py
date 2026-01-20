"""
ChartCapture Pro - Notification Module
Bildirim gönderme sistemini soyutlayan modül.
"""

import os
from abc import ABC, abstractmethod
from typing import List
from logger import get_logger

class NotificationProvider(ABC):
    """Bildirim servisleri için taban sınıf."""
    @abstractmethod
    def send(self, title: str, message: str) -> bool:
        pass


class MacOSNotificationProvider(NotificationProvider):
    """macOS sistem bildirimleri."""
    def send(self, title: str, message: str) -> bool:
        try:
            command = f'display notification "{message}" with title "{title}"'
            os.system(f"osascript -e '{command}'")
            return True
        except Exception:
            return False


class DiscordNotificationProvider(NotificationProvider):
    """Discord Webhook bildirimleri (Gelecek için hazırlık)."""
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.environ.get("DISCORD_WEBHOOK_URL")

    def send(self, title: str, message: str) -> bool:
        if not self.webhook_url:
            return False
        # Not: requests kütüphanesi gerekebilir.
        # Gelecekte buraya requests ile POST isteği eklenecek.
        return True


class NotificationManager:
    """Birden fazla bildirim sağlayıcısını yönetir."""
    def __init__(self):
        self.providers: List[NotificationProvider] = []
        self.logger = get_logger()
        
        # Varsayılan sağlayıcılar (Platforma göre eklenebilir)
        if os.uname().sysname == 'Darwin':
            self.providers.append(MacOSNotificationProvider())
            
        # Environment variable varsa Discord'u da ekle
        if os.environ.get("DISCORD_WEBHOOK_URL"):
            self.providers.append(DiscordNotificationProvider())

    def add_provider(self, provider: NotificationProvider):
        """Yeni bir bildirim sağlayıcısı ekler (WhatsApp, Telegram vs)."""
        self.providers.append(provider)

    def notify(self, title: str, message: str):
        """Tüm kayıtlı sağlayıcılara bildirim gönderir."""
        for provider in self.providers:
            success = provider.send(title, message)
            if not success:
                self.logger.debug(f"Bildirim sağlayıcı başarısız: {type(provider).__name__}")

# Global instance
notifier = NotificationManager()
