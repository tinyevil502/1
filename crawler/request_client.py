import time
import requests
import os
import logging

logger = logging.getLogger(__name__)


class RequestClient:
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    def __init__(self, timeout=30, max_retries=3, delay=3, headers=None):
        self.session = requests.Session()
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay = delay

        merged_headers = self.DEFAULT_HEADERS.copy()
        if headers:
            merged_headers.update(headers)
        self.session.headers.update(merged_headers)

    def request(self, method, url, **kwargs):
        attempt = 0
        last_exc = None

        while attempt < self.max_retries:
            try:
                resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
                if 200 <= resp.status_code < 300:
                    return resp

                logger.warning(f"HTTP {resp.status_code} for {url}, attempt {attempt + 1}")
                last_exc = RuntimeError(f"HTTP {resp.status_code} for {url}")

            except requests.RequestException as e:
                logger.warning(f"Request exception: {e}, attempt {attempt + 1}")
                last_exc = e

            attempt += 1
            if attempt < self.max_retries:
                time.sleep(self.delay)

        raise last_exc if last_exc is not None else RuntimeError("Request failed")

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def close(self):
        self.session.close()