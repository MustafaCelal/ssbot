"""
ChartCapture Pro - Browser Manager
WebDriver lifecycle ve anti-bot önlemleri.
"""

import random
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from config import SeleniumConfig, USER_AGENTS, Selectors
from logger import get_logger
from utils import get_random_user_agent


class BrowserManager:
    """
    Chrome WebDriver yönetimi.
    Anti-bot önlemleri ve stealth mode desteği.
    """
    
    def __init__(
        self,
        headless: bool = True,
        user_agent: str = None,
        disable_images: bool = False,
        width: int = 1920,
        height: int = 1080
    ):
        """
        BrowserManager'ı başlatır.
        
        Args:
            headless: Headless modda çalıştır
            user_agent: Özel user-agent (None ise random seçilir)
            disable_images: Görselleri devre dışı bırak (hızlandırma için)
            width: Pencere genişliği
            height: Pencere yüksekliği
        """
        self.headless = headless
        self.user_agent = user_agent or get_random_user_agent()
        self.disable_images = disable_images
        self.width = width
        self.height = height
        self.driver: Optional[webdriver.Chrome] = None
        self.logger = get_logger()
        
    def _get_chrome_options(self) -> Options:
        """
        Chrome options oluşturur (anti-bot önlemleri dahil).
        
        Returns:
            Chrome Options objesi
        """
        options = Options()
        
        # Headless mode
        if self.headless:
            options.add_argument("--headless=new")
        
        # Window size
        options.add_argument(
            f"--window-size={self.width},{self.height}"
        )
        
        # User agent
        options.add_argument(f"--user-agent={self.user_agent}")
        
        # ========================
        # ANTI-BOT ÖNLEMLERI
        # ========================
        
        # WebDriver detection bypass
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Sandbox ve security options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # Fingerprint masking
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        
        # Memory optimization
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        # Performance
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        
        # Görsel devre dışı bırakma (opsiyonel)
        if self.disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        # Dil ayarı
        options.add_argument("--lang=en-US")
        
        return options
    
    def start(self) -> webdriver.Chrome:
        """
        WebDriver'ı başlatır.
        
        Returns:
            Chrome WebDriver instance
            
        Raises:
            WebDriverException: Driver başlatılamazsa
        """
        try:
            self.logger.info(f"Chrome WebDriver başlatılıyor... (Headless: {self.headless})")
            
            options = self._get_chrome_options()
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Timeouts
            self.driver.set_page_load_timeout(SeleniumConfig.PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(SeleniumConfig.IMPLICIT_WAIT)
            
            # Anti-bot: navigator.webdriver'ı gizle
            self._inject_stealth_scripts()
            
            self.logger.info("Chrome WebDriver başarıyla başlatıldı.")
            return self.driver
            
        except WebDriverException as e:
            self.logger.error(f"WebDriver başlatma hatası: {str(e)}")
            raise
    
    def _inject_stealth_scripts(self) -> None:
        """
        Stealth JavaScript'leri enjekte eder.
        navigator.webdriver'ı gizler.
        """
        if not self.driver:
            return
            
        # navigator.webdriver özelliğini undefined yap
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Chrome detection'ı bypass
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    
                    // Permissions API'yi mask'le
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """
            }
        )
    
    def navigate_to(self, url: str, wait_for_load: bool = True) -> bool:
        """
        Belirtilen URL'ye gider.
        
        Args:
            url: Hedef URL
            wait_for_load: Sayfa yüklenmesini bekle
            
        Returns:
            Başarılı mı
        """
        if not self.driver:
            self.logger.error("Driver başlatılmamış!")
            return False
            
        try:
            self.logger.info(f"Sayfa açılıyor: {url}")
            self.driver.get(url)
            
            if wait_for_load:
                # Sayfanın yüklenmesini bekle
                WebDriverWait(self.driver, SeleniumConfig.PAGE_LOAD_TIMEOUT).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
            return True
            
        except TimeoutException:
            self.logger.warning(f"Sayfa yükleme timeout: {url}")
            return False
        except Exception as e:
            self.logger.error(f"Navigasyon hatası: {str(e)}")
            return False
    
    def wait_for_element(
        self, 
        selector: str, 
        by: By = By.CSS_SELECTOR,
        timeout: int = None,
        clickable: bool = False
    ):
        """
        Element'in görünmesini bekler.
        
        Args:
            selector: CSS selector veya XPath
            by: Seçici türü
            timeout: Bekleme süresi
            clickable: Tıklanabilir olmasını bekle
            
        Returns:
            WebElement veya None
        """
        if not self.driver:
            return None
            
        timeout = timeout or SeleniumConfig.ELEMENT_WAIT_TIMEOUT
        
        try:
            if clickable:
                condition = EC.element_to_be_clickable((by, selector))
            else:
                condition = EC.presence_of_element_located((by, selector))
                
            element = WebDriverWait(self.driver, timeout).until(condition)
            return element
            
        except TimeoutException:
            self.logger.debug(f"Element bulunamadı: {selector}")
            return None
    
    def clear_overlays(self) -> None:
        """
        Onboarding tooltips, ads ve diğer engelleyici elementleri temizler.
        """
        if not self.driver:
            return
            
        script = """
        (function() {
            // 1. 'Got it' veya 'Anladım' yazan butonlara tıkla
            const buttons = Array.from(document.querySelectorAll('button, div[role="button"]'));
            const gotItButtons = buttons.filter(b => {
                const txt = b.textContent.toLowerCase();
                return txt.includes('got it') || txt.includes('anladım') || txt.includes('tamam');
            });
            gotItButtons.forEach(b => {
                try { b.click(); } catch(e) {}
            });

            // 2. Onboarding ve discovery elementlerini kaldır
            const selectors = [
                '#overlap-manager-root',
                '[class*="onboarding-tooltip"]',
                '[class*="feature-discovery"]',
                '[class*="dialog"]',
                '.tv-dialog',
                '.cookie-banner-container',
                '[id*="cookies-policy"]'
            ];
            
            selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    try { el.remove(); } catch(e) {}
                });
            });
            
            return true;
        })();
        """
        try:
            self.driver.execute_script(script)
            self.logger.debug("Overlays temizlendi.")
        except Exception as e:
            self.logger.debug(f"Overlay temizleme hatası: {str(e)}")

    def dismiss_popups(self) -> None:
        """
        Cookie consent ve diğer popup'ları kapatır.
        """
        if not self.driver:
            return
            
        popup_selectors = [
            Selectors.COOKIE_ACCEPT_BUTTON,
            '[data-role="accept-all"]',
            'button.accept-cookies',
            '.cookie-consent-accept',
            '[aria-label="Close"]',
        ]
        
        # HIZLANDIRMA: Popup kontrolü için implicit wait'i geçici olarak kapat
        self.driver.implicitly_wait(0.1)
        
        for selector in popup_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        element.click()
                        self.logger.debug(f"Popup kapatıldı: {selector}")
                        break
            except Exception:
                pass
                
        # Implicit wait'i eski haline getir
        self.driver.implicitly_wait(SeleniumConfig.IMPLICIT_WAIT)
    
    def rotate_user_agent(self) -> None:
        """
        User-agent'ı değiştirir (yeni oturumda kullanılır).
        """
        self.user_agent = get_random_user_agent()
        self.logger.debug(f"User-agent değiştirildi: {self.user_agent[:50]}...")
    
    def get_page_source(self) -> str:
        """Sayfa kaynağını döndürür."""
        if self.driver:
            return self.driver.page_source
        return ""
    
    def take_full_screenshot(self, filepath: str) -> bool:
        """
        Tam sayfa screenshot alır.
        
        Args:
            filepath: Kayıt yolu
            
        Returns:
            Başarılı mı
        """
        if not self.driver:
            return False
            
        try:
            self.driver.save_screenshot(filepath)
            return True
        except Exception as e:
            self.logger.error(f"Screenshot hatası: {str(e)}")
            return False
    
    def close(self) -> None:
        """
        WebDriver'ı düzgün şekilde kapatır.
        Memory leak önleme.
        """
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver kapatıldı.")
            except Exception as e:
                self.logger.warning(f"Driver kapatma uyarısı: {str(e)}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """Context manager desteği."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - otomatik kapanış."""
        self.close()
        return False
