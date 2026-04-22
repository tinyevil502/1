import time
import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

logger = logging.getLogger(__name__)


class SeleniumClient:
    def __init__(self, timeout=60, delay=3):
        self.timeout = timeout
        self.delay = delay
        self.driver = None

    def start(self):
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        try:
            self.driver = webdriver.Edge(options=options)
        except Exception as e:
            logger.error(f"Edge failed: {e}")
            raise

        self.driver.set_page_load_timeout(self.timeout)
        self.driver.implicitly_wait(15)
        logger.info("Edge started")

    def get(self, url):
        if not self.driver:
            self.start()

        logger.info(f"Fetching: {url}")
        self.driver.get(url)
        time.sleep(self.delay)
        return self.driver.page_source

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None