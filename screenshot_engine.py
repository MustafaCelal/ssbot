"""
TradingView Screenshot Bot - Screenshot Engine
Screenshot alma mantığı ve retry mekanizması.
"""

import os
import time
from typing import Optional, Tuple
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from browser_manager import BrowserManager
from config import SeleniumConfig, Selectors, TradingViewURLs, PathConfig
from logger import get_logger
from utils import random_delay, get_screenshot_path, ensure_directory


class ScreenshotEngine:
    """
    TradingView'dan screenshot alma motoru.
    Retry mekanizması ve hata yönetimi.
    """
    
    def __init__(self, browser_manager: BrowserManager):
        """
        ScreenshotEngine'i başlatır.
        
        Args:
            browser_manager: BrowserManager instance
        """
        self.browser = browser_manager
        self.driver = browser_manager.driver
        self.logger = get_logger()
        
    def wait_for_chart_load(self, timeout: int = 20) -> bool:
        """
        Chart'ın tamamen yüklenmesini bekler.
        
        Args:
            timeout: Maximum bekleme süresi
            
        Returns:
            Yüklendi mi
        """
        try:
            # Önce herhangi bir canvas elementinin gelmesini bekle (TradingView grafikleri canvas kullanır)
            self.logger.debug("Grafik kanvası bekleniyor...")
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "canvas"))
                )
            except TimeoutException:
                self.logger.warning("Kanvas elementi bulunamadı, yine de devam ediliyor...")

            # Alternatif: Ana container'lardan birinin görünmesini bekle
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, Selectors.CHART_CONTAINER))
                )
            except TimeoutException:
                pass
            
            # Ekstra bekleme (verilerin dolması ve render için önemli)
            time.sleep(5)
            
            self.logger.debug("Chart yükleme kontrolü tamamlandı.")
            return True
            
        except Exception as e:
            self.logger.warning(f"Chart yükleme kontrolünde beklenmedik durum: {str(e)}")
            return True # Hata olsa bile devam et, belki grafik yüklenmiştir
            
        except TimeoutException:
            # Debug için ekran görüntüsü al
            debug_path = os.path.join(PathConfig.LOG_DIR, f"debug_timeout_{int(time.time())}.png")
            try:
                ensure_directory(PathConfig.LOG_DIR)
                self.driver.save_screenshot(debug_path)
                self.logger.warning(f"Chart yükleme timeout! Debug screenshot kaydedildi: {debug_path}")
            except Exception as e:
                self.logger.warning(f"Chart yükleme timeout! (Debug screenshot alınamadı: {str(e)})")
            return False
            
    def _find_snapshot_button(self):
        """
        Snapshot butonunu bulur.
        
        Returns:
            WebElement veya None
        """
        # Birden fazla selector dene
        selectors = [
            Selectors.SNAPSHOT_BUTTON,
            Selectors.SNAPSHOT_BUTTON_ALT,
            '[data-tooltip="Take a snapshot"]',
            'button[data-name="save-load-menu"]',  # Alternatif
        ]
        
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                if element:
                    self.logger.debug(f"Snapshot butonu bulundu: {selector}")
                    return element
            except (TimeoutException, NoSuchElementException):
                continue
                
        # Keyboard shortcut ile dene (Alt+S)
        self.logger.debug("Buton bulunamadı, keyboard shortcut deneniyor...")
        return None
    
    def _click_snapshot_button(self) -> bool:
        """
        Snapshot butonuna tıklar.
        
        Returns:
            Başarılı mı
        """
        try:
            button = self._find_snapshot_button()
            
            if button:
                # Önce scroll into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(0.5)
                
                # JavaScript ile tıkla (daha güvenilir)
                self.driver.execute_script("arguments[0].click();", button)
                self.logger.debug("Snapshot butonuna tıklandı.")
                return True
            else:
                # Keyboard shortcut kullan (Alt+S)
                actions = ActionChains(self.driver)
                actions.key_down(Keys.ALT).send_keys('s').key_up(Keys.ALT).perform()
                time.sleep(1)
                return True
                
        except ElementClickInterceptedException:
            self.logger.warning("Snapshot butonuna tıklanamadı - element engellenmiş.")
            return False
        except Exception as e:
            self.logger.error(f"Snapshot buton hatası: {str(e)}")
            return False
    
    def _wait_for_snapshot_dialog(self, timeout: int = 10) -> bool:
        """
        Snapshot dialog'unun açılmasını bekler.
        
        Args:
            timeout: Bekleme süresi
            
        Returns:
            Dialog açıldı mı
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, Selectors.SNAPSHOT_DIALOG))
            )
            return True
        except TimeoutException:
            return False
    
    def _download_snapshot(self, filepath: str) -> bool:
        """
        Snapshot'ı indirir veya sayfa screenshot'ı alır.
        
        Args:
            filepath: Kayıt yolu
            
        Returns:
            Başarılı mı
        """
        try:
            # Dialog açıksa download butonuna tıkla
            download_selectors = [
                Selectors.DOWNLOAD_BUTTON,
                '[data-name="save-chart-image"]',
                'button:has-text("Download")',
            ]
            
            for selector in download_selectors:
                try:
                    btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if btn and btn.is_displayed():
                        btn.click()
                        time.sleep(2)
                        self.logger.debug("Download butonuna tıklandı.")
                        # Not: Gerçek indirme için download directory ayarı gerekir
                        # Burada fallback olarak sayfa screenshot'ı alıyoruz
                        break
                except NoSuchElementException:
                    continue
            
            # Fallback: Sayfa screenshot'ı al
            # Dialog'u kapat
            self._close_dialogs()
            time.sleep(1)
            
            # Chart alanının screenshot'ını al
            return self._capture_chart_area(filepath)
            
        except Exception as e:
            self.logger.error(f"Download hatası: {str(e)}")
            return False
    
    def _close_dialogs(self) -> None:
        """Açık dialog'ları kapatır."""
        try:
            # ESC tuşu ile kapat
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(0.5)
        except Exception:
            pass
    
    def _capture_chart_area(self, filepath: str) -> bool:
        """
        Chart alanının screenshot'ını alır.
        
        Args:
            filepath: Kayıt yolu
            
        Returns:
            Başarılı mı
        """
        try:
            # Önce chart container'ı bul
            chart_selectors = [
                '.chart-container',
                '.chart-markup-table',
                '#chart-area',
                '.layout__area--center',
            ]
            
            chart_element = None
            for selector in chart_selectors:
                try:
                    chart_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if chart_element:
                        break
                except NoSuchElementException:
                    continue
            
            if chart_element:
                # Element screenshot
                chart_element.screenshot(filepath)
                self.logger.debug(f"Chart screenshot alındı: {filepath}")
                return True
            else:
                # Fallback: Tam sayfa screenshot
                self.driver.save_screenshot(filepath)
                self.logger.debug(f"Tam sayfa screenshot alındı: {filepath}")
                return True
                
        except Exception as e:
            self.logger.error(f"Chart capture hatası: {str(e)}")
            return False
    
    def take_screenshot(
        self,
        symbol: str,
        exchange: str,
        timeframe: str = "1D",
        theme: str = "dark",
        output_dir: str = None,
        retry_count: int = 0
    ) -> Tuple[bool, str, str]:
        """
        Belirtilen sembol için screenshot alır.
        
        Args:
            symbol: Sembol adı (ör: BTCUSDT)
            exchange: Borsa adı (ör: BINANCE)
            timeframe: Zaman dilimi
            theme: Tema (light/dark)
            output_dir: Çıktı klasörü
            retry_count: Mevcut retry sayısı
            
        Returns:
            Tuple(success, filepath, error_message)
        """
        filepath = get_screenshot_path(symbol, exchange, timeframe, output_dir)
        error_msg = ""
        
        try:
            # URL oluştur
            url = TradingViewURLs.get_symbol_url(symbol, exchange, theme)
            self.logger.info(f"Screenshot alınıyor: {exchange}:{symbol} ({timeframe})")
            
            # Sayfaya git
            if not self.browser.navigate_to(url):
                raise Exception("Sayfa yüklenemedi")
            
            # Popup'ları kapat
            self.browser.dismiss_popups()
            
            # Chart'ın yüklenmesini bekle
            if not self.wait_for_chart_load():
                raise Exception("Chart yüklenemedi")
            
            # Timeframe değiştir (gerekirse)
            self._set_timeframe(timeframe)
            
            # Random bekleme (anti-bot)
            delay = random_delay()
            self.logger.debug(f"Random bekleme: {delay:.1f}s")
            
            # Snapshot al
            if self._click_snapshot_button():
                time.sleep(1)
                
                # Dialog açıldı mı kontrol et
                if self._wait_for_snapshot_dialog(timeout=5):
                    # Dialog üzerinden indir
                    if not self._download_snapshot(filepath):
                        # Fallback
                        self._close_dialogs()
                        self._capture_chart_area(filepath)
                else:
                    # Direkt chart screenshot
                    self._capture_chart_area(filepath)
            else:
                # Buton bulunamadı, direkt screenshot
                self._capture_chart_area(filepath)
            
            # Dosya oluştu mu kontrol et
            if os.path.exists(filepath):
                self.logger.screenshot_result(
                    symbol, exchange, True, filepath, retry_count=retry_count
                )
                return (True, filepath, "")
            else:
                raise Exception("Screenshot dosyası oluşturulamadı")
                
        except Exception as e:
            error_msg = str(e)
            self.logger.screenshot_result(
                symbol, exchange, False, error=error_msg, retry_count=retry_count
            )
            
            # Retry kontrolü
            if retry_count < SeleniumConfig.MAX_RETRIES:
                self.logger.info(f"Retry deneniyor... ({retry_count + 1}/{SeleniumConfig.MAX_RETRIES})")
                time.sleep(SeleniumConfig.RETRY_DELAY)
                return self.take_screenshot(
                    symbol, exchange, timeframe, theme, output_dir, retry_count + 1
                )
            
            return (False, "", error_msg)
    
    def _set_timeframe(self, timeframe: str) -> bool:
        """
        Timeframe'i değiştirir.
        
        Args:
            timeframe: Hedef timeframe
            
        Returns:
            Başarılı mı
        """
        try:
            # Timeframe menüsünü aç
            tf_button = self.driver.find_element(
                By.CSS_SELECTOR, 
                '[data-name="time-interval-menu-button"]'
            )
            if tf_button:
                tf_button.click()
                time.sleep(0.5)
                
                # Timeframe seç
                tf_option = self.driver.find_element(
                    By.CSS_SELECTOR,
                    f'[data-value="{timeframe}"]'
                )
                if tf_option:
                    tf_option.click()
                    time.sleep(1)
                    return True
                    
        except Exception as e:
            self.logger.debug(f"Timeframe değiştirme atlandı: {str(e)}")
        
        return False
