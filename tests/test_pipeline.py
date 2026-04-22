import pytest
from services import crawl_service, clean_service, keyword_service, trend_service
from models.db import SessionLocal, NovelRaw, NovelInfo, KeywordStat, TrendStat


class TestPipeline:
    def test_crawl_step(self):
        crawl_result = crawl_service.run_crawl_task(pages=1, category='dushi')
        assert crawl_result.get('success') is True
        assert crawl_result.get('saved', 0) > 0
        return crawl_result['batch_no']

    def test_clean_step(self):
        batch_no = self.test_crawl_step()
        clean_result = clean_service.clean_batch(batch_no=batch_no)
        assert clean_result.get('success') is True

        db = SessionLocal()
        info_count = db.query(NovelInfo).count()
        db.close()
        assert info_count > 0

    def test_keyword_step(self):
        batch_no = self.test_crawl_step()
        clean_service.clean_batch(batch_no=batch_no)

        kw_result = keyword_service.process_keywords(method='tfidf', topk=20)
        assert kw_result.get('success') is True
        assert kw_result.get('keywords', 0) > 0

        db = SessionLocal()
        kw_count = db.query(KeywordStat).count()
        db.close()
        assert kw_count > 0

    def test_trend_step(self):
        batch_no = self.test_crawl_step()
        clean_service.clean_batch(batch_no=batch_no)
        keyword_service.process_keywords(method='tfidf', topk=20)

        trend_result = trend_service.calculate_trends()
        assert trend_result.get('success') is True

        db = SessionLocal()
        trend_count = db.query(TrendStat).count()
        db.close()
        assert trend_count > 0
