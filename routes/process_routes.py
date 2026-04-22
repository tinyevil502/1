from flask import Blueprint, request
from services import crawl_service, clean_service, keyword_service, trend_service
from utils.response import make_response, error_response
from utils.logger import get_logger

logger = get_logger(__name__)

process_bp = Blueprint('process', __name__)


@process_bp.route('/process/clean', methods=['POST'])
def process_clean():
    try:
        json_data = request.get_json(silent=True) or {}
        batch_no = json_data.get('batch_no')
        result = clean_service.clean_batch(batch_no=batch_no)
        return make_response(result.get('success', False), result, 'Cleaning completed')
    except Exception as e:
        logger.error(f"process_clean failed: {e}")
        return error_response(str(e))


@process_bp.route('/process/keywords', methods=['POST'])
def process_keywords():
    try:
        json_data = request.get_json(silent=True) or {}
        method = json_data.get('method', 'tfidf')
        topk = int(json_data.get('topk', 20))
        result = keyword_service.process_keywords(method=method, topk=topk)
        return make_response(result.get('success', False), result, 'Keyword extraction completed')
    except Exception as e:
        logger.error(f"process_keywords failed: {e}")
        return error_response(str(e))


@process_bp.route('/process/trends', methods=['POST'])
def process_trends():
    try:
        result = trend_service.calculate_trends()
        return make_response(result.get('success', False), result, 'Trend calculation completed')
    except Exception as e:
        logger.error(f"process_trends failed: {e}")
        return error_response(str(e))


@process_bp.route('/process/crawl', methods=['POST'])
def process_crawl():
    try:
        json_data = request.get_json(silent=True) or {}
        pages = int(json_data.get('pages', 5))
        category = json_data.get('category', 'xuanhuan')
        result = crawl_service.run_crawl_task(pages=pages, category=category)
        return make_response(result.get('success', False), result, 'Crawl task completed')
    except Exception as e:
        logger.error(f"process_crawl failed: {e}")
        return error_response(str(e))


@process_bp.route('/process/crawl-all', methods=['POST'])
def process_crawl_all():
    try:
        json_data = request.get_json(silent=True) or {}
        pages = int(json_data.get('pages', 5))
        result = crawl_service.crawl_all_categories(pages=pages)
        return make_response(result.get('success', False), result, 'Crawl all categories completed')
    except Exception as e:
        logger.error(f"process_crawl_all failed: {e}")
        return error_response(str(e))


@process_bp.route('/process/crawl-multi', methods=['POST'])
def process_crawl_multi():
    try:
        json_data = request.get_json(silent=True) or {}
        categories = json_data.get('categories')
        per_category = int(json_data.get('per_category', 15))
        pages_per_cat = int(json_data.get('pages_per_cat', 2))
        result = crawl_service.crawl_multi_category(
            categories=categories,
            per_category=per_category,
            pages_per_cat=pages_per_cat
        )
        return make_response(result.get('success', False), result, 'Multi-category crawl completed')
    except Exception as e:
        logger.error(f"process_crawl_multi failed: {e}")
        return error_response(str(e))
