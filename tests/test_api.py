import pytest


class TestNovelRoutes:
    def test_list_page_1(self, client):
        r = client.get('/api/novels', query_string={'page': '1', 'size': '10'})
        result = r.get_json()
        assert result['success'] is True
        assert 'items' in result['data']
        assert 'total' in result['data']

    def test_list_page_2(self, client):
        r = client.get('/api/novels', query_string={'page': '2', 'size': '5'})
        result = r.get_json()
        assert result['success'] is True

    def test_filter_by_category(self, client):
        r = client.get('/api/novels', query_string={'category': '都市'})
        result = r.get_json()
        assert result['success'] is True

    def test_filter_by_status(self, client):
        r = client.get('/api/novels', query_string={'status': '连载中'})
        result = r.get_json()
        assert result['success'] is True

    def test_filter_by_keyword(self, client):
        r = client.get('/api/novels', query_string={'keyword': 'test'})
        result = r.get_json()
        assert result['success'] is True

    def test_search_with_query(self, client):
        r = client.get('/api/novels/search', query_string={'q': 'test', 'page': '1', 'size': '10'})
        result = r.get_json()
        assert result['success'] is True

    def test_search_empty_query(self, client):
        r = client.get('/api/novels/search', query_string={'q': '', 'page': '1', 'size': '10'})
        result = r.get_json()
        assert result['success'] is False

    def test_search_with_category(self, client):
        r = client.get('/api/novels/search', query_string={'q': '都市', 'category': '都市小说', 'page': '1', 'size': '5'})
        result = r.get_json()
        assert result['success'] is True

    def test_detail_found(self, client):
        r = client.get('/api/novels', query_string={'page': '1', 'size': '1'})
        novel_data = r.get_json()
        if novel_data['success'] and novel_data['data']['items']:
            novel_id = novel_data['data']['items'][0]['id']
            r = client.get(f'/api/novels/{novel_id}')
            result = r.get_json()
            assert result['success'] is True

    def test_detail_not_found(self, client):
        r = client.get('/api/novels/999999')
        result = r.get_json()
        assert result['success'] is False


class TestAnalysisRoutes:
    def test_category_distribution(self, client):
        r = client.get('/api/analysis/category-distribution')
        result = r.get_json()
        assert result['success'] is True

    def test_status_distribution(self, client):
        r = client.get('/api/analysis/status-distribution')
        result = r.get_json()
        assert result['success'] is True

    def test_update_trend_30_days(self, client):
        r = client.get('/api/analysis/update-trend', query_string={'days': '30'})
        result = r.get_json()
        assert result['success'] is True

    def test_update_trend_7_days(self, client):
        r = client.get('/api/analysis/update-trend', query_string={'days': '7'})
        result = r.get_json()
        assert result['success'] is True

    def test_all_trends(self, client):
        r = client.get('/api/trends', query_string={'days': '30'})
        result = r.get_json()
        assert result['success'] is True

    def test_trends_by_type(self, client):
        r = client.get('/api/trends', query_string={'dimension_type': 'update_trend', 'days': '10'})
        result = r.get_json()
        assert result['success'] is True

    def test_word_trend_day(self, client):
        r = client.get('/api/analysis/word-trend', query_string={'granularity': 'day', 'days': '30'})
        result = r.get_json()
        assert result['success'] is True

    def test_word_trend_week(self, client):
        r = client.get('/api/analysis/word-trend', query_string={'granularity': 'week', 'days': '12'})
        result = r.get_json()
        assert result['success'] is True

    def test_word_trend_month(self, client):
        r = client.get('/api/analysis/word-trend', query_string={'granularity': 'month', 'days': '6'})
        result = r.get_json()
        assert result['success'] is True

    def test_category_trend(self, client):
        r = client.get('/api/analysis/category-trend', query_string={'days': '30', 'top_categories': '5'})
        result = r.get_json()
        assert result['success'] is True


class TestKeywordRoutes:
    def test_keywords_top_20(self, client):
        r = client.get('/api/keywords', query_string={'topk': '20'})
        result = r.get_json()
        assert result['success'] is True

    def test_keywords_top_5(self, client):
        r = client.get('/api/keywords', query_string={'topk': '5'})
        result = r.get_json()
        assert result['success'] is True

    def test_global_keywords(self, client):
        r = client.get('/api/keywords/global', query_string={'topk': '20'})
        result = r.get_json()
        assert result['success'] is True

    def test_global_keywords_by_intro(self, client):
        r = client.get('/api/keywords/global', query_string={'topk': '10', 'source_field': 'intro'})
        result = r.get_json()
        assert result['success'] is True

    def test_keywords_by_category(self, client):
        r = client.get('/api/keywords/by-category', query_string={'topk': '10'})
        result = r.get_json()
        assert result['success'] is True


class TestAdminRoutes:
    def test_batches(self, client):
        r = client.get('/api/admin/batches')
        result = r.get_json()
        assert result['success'] is True

    def test_raw_stats(self, client):
        r = client.get('/api/admin/stats/raw')
        result = r.get_json()
        assert result['success'] is True

    def test_cleaned_stats(self, client):
        r = client.get('/api/admin/stats/cleaned')
        result = r.get_json()
        assert result['success'] is True

    def test_platforms(self, client):
        r = client.get('/api/admin/platforms')
        result = r.get_json()
        assert result['success'] is True

    def test_health_check_post(self, client):
        r = client.post('/api/admin/health-check', json={})
        result = r.get_json()
        assert result['success'] is True

    def test_health_check_get(self, client):
        r = client.get('/api/admin/health-check')
        result = r.get_json()
        assert result['success'] is True

    def test_logs(self, client):
        r = client.get('/api/admin/logs', query_string={'lines': '10'})
        result = r.get_json()
        assert result['success'] is True


class TestFrontendPages:
    def test_index_page(self, client):
        r = client.get('/')
        assert r.status_code == 200
        assert b'<!DOCTYPE html>' in r.data

    def test_analysis_page(self, client):
        r = client.get('/analysis')
        assert r.status_code == 200
        assert b'<!DOCTYPE html>' in r.data

    def test_admin_page(self, client):
        r = client.get('/admin')
        assert r.status_code == 200
        assert b'<!DOCTYPE html>' in r.data
