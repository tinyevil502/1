import pytest
from crawler.hybrid_client import HybridClient
from crawler.seventeenk_spider import SeventeenKSpider


@pytest.fixture
def spider():
    client = HybridClient(timeout=30, delay=1)
    client.start()
    spider = SeventeenKSpider(client)
    yield spider
    client.close()


class TestCrawlService:
    def test_run_crawl_task(self):
        from services.crawl_service import run_crawl_task
        result = run_crawl_task(pages=1, category='dushi')
        assert 'success' in result


class TestSpiderParsing:
    def test_parse_list_page(self, spider):
        html = spider.fetch_list_page('https://www.17k.com/all/book/2_0_0_0_0_2_0_0_1.html')
        items = spider.parse_list_page(html)
        assert len(items) > 0
        assert 'novel_name_raw' in items[0]
        assert 'source_url' in items[0]

    def test_fetch_and_parse_detail(self, spider):
        urls = spider.get_list_urls(category='dushi', pages=1)
        assert len(urls) > 0

        html = spider.fetch_list_page(urls[0])
        items = spider.parse_list_page(html)
        assert len(items) > 0

        item = items[0]
        detail_url = item.get('detail_url')
        if detail_url:
            detail_html = spider.fetch_detail_page(detail_url)
            detail_data = spider.parse_detail_page(detail_html)
            assert isinstance(detail_data, dict)
