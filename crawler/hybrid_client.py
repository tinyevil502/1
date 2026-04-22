import time
import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from .request_client import RequestClient

logger = logging.getLogger(__name__)


class HybridClient:
    """Try Selenium first, fall back to requests if Selenium fails."""

    def __init__(self, timeout=60, delay=3):
        self.timeout = timeout
        self.delay = delay
        self.driver = None
        self.request_client = None
        self.use_selenium = True

    def start(self):
        # Try Selenium first
        try:
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            self.driver = webdriver.Edge(options=options)
            self.driver.set_page_load_timeout(self.timeout)
            self.driver.implicitly_wait(15)
            logger.info("Edge started (Selenium mode)")
            return
        except Exception as e:
            logger.warning(f"Selenium Edge failed: {e}, falling back to requests")
            self.use_selenium = False

        # Fallback to requests
        self.request_client = RequestClient(timeout=self.timeout, delay=self.delay)
        logger.info("RequestClient started (HTTP mode)")

    def get(self, url):
        if self.use_selenium:
            try:
                if not self.driver:
                    self.start()
                logger.info(f"Fetching (Selenium): {url}")
                self.driver.get(url)
                time.sleep(self.delay)
                return self.driver.page_source
            except Exception as e:
                logger.warning(f"Selenium fetch failed: {e}, switching to requests")
                self.use_selenium = False
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                if not self.request_client:
                    self.request_client = RequestClient(timeout=self.timeout, delay=self.delay)

        # Use requests
        logger.info(f"Fetching (HTTP): {url}")
        resp = self.request_client.get(url)
        time.sleep(self.delay)
        return resp.text

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        if self.request_client:
            self.request_client.close()
            self.request_client = None
