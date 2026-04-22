import os
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseSpider:
    def __init__(self, client, debug_dir=None):
        self.client = client
        self.debug_dir = debug_dir or os.path.join(os.path.dirname(__file__), 'html_debug')
        os.makedirs(self.debug_dir, exist_ok=True)

    def generate_batch_no(self):
        return datetime.now().strftime('%Y%m%d%H%M%S') + str(uuid.uuid4())[:8]

    def save_html_snapshot(self, html, batch_no, page_type='list'):
        if not html:
            return None

        filename = f"{page_type}_{batch_no}_{int(datetime.now().timestamp())}.html"
        filepath = os.path.join(self.debug_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"HTML snapshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save HTML snapshot: {e}")
            return None

    def fetch_list_page(self, url):
        raise NotImplementedError

    def parse_list_page(self, html):
        raise NotImplementedError

    def fetch_detail_page(self, url):
        raise NotImplementedError

    def parse_detail_page(self, html):
        raise NotImplementedError

    def crawl(self, list_urls=None, max_pages=1):
        results = []
        batch_no = self.generate_batch_no()

        for page_url in (list_urls or []):
            try:
                html = self.fetch_list_page(page_url)
                items = self.parse_list_page(html)

                for item in items:
                    item['batch_no'] = batch_no
                    item['source_url'] = item.get('source_url', page_url)

                    if item.get('detail_url'):
                        detail_html = self.fetch_detail_page(item['detail_url'])
                        detail_data = self.parse_detail_page(detail_html)
                        item.update(detail_data)

                results.extend(items)
                logger.info(f"Crawled {len(items)} items from {page_url}")

            except Exception as e:
                logger.error(f"Failed to crawl {page_url}: {e}")

        return results, batch_no