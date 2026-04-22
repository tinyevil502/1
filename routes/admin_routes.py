from flask import Blueprint
from datetime import datetime
from services import stats_service
from models.db import SessionLocal, NovelRaw, NovelInfo, KeywordStat, TrendStat, PlatformSource
from utils.response import make_response, error_response
from utils.logger import get_logger

logger = get_logger(__name__)

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/batches', methods=['GET'])
def admin_batches():
    try:
        batches = stats_service.get_batches()
        return make_response(True, {'batches': batches, 'total': len(batches)}, 'OK')
    except Exception as e:
        logger.error(f"admin_batches failed: {e}")
        return error_response(str(e))


@admin_bp.route('/admin/stats/raw', methods=['GET'])
def admin_stats_raw():
    try:
        stats = stats_service.get_raw_stats()
        return make_response(True, stats, 'OK')
    except Exception as e:
        logger.error(f"admin_stats_raw failed: {e}")
        return error_response(str(e))


@admin_bp.route('/admin/stats/cleaned', methods=['GET'])
def admin_stats_cleaned():
    try:
        stats = stats_service.get_cleaned_stats()
        return make_response(True, stats, 'OK')
    except Exception as e:
        logger.error(f"admin_stats_cleaned failed: {e}")
        return error_response(str(e))


@admin_bp.route('/admin/platforms', methods=['GET'])
def admin_platforms():
    try:
        platforms = stats_service.get_platforms()
        return make_response(True, {'platforms': platforms, 'total': len(platforms)}, 'OK')
    except Exception as e:
        logger.error(f"admin_platforms failed: {e}")
        return error_response(str(e))


@admin_bp.route('/admin/health-check', methods=['POST', 'GET'])
def admin_health_check():
    result = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'dependencies': {},
        'tables': {},
    }

    db_ok = False
    try:
        db = SessionLocal()
        result['tables']['platform_source'] = db.query(PlatformSource).count()
        result['tables']['novel_raw'] = db.query(NovelRaw).count()
        result['tables']['novel_info'] = db.query(NovelInfo).count()
        result['tables']['keyword_stat'] = db.query(KeywordStat).count()
        result['tables']['trend_stat'] = db.query(TrendStat).count()
        db.close()
        db_ok = True
    except Exception as e:
        result['dependencies']['db_error'] = str(e)

    result['dependencies']['db'] = 'ok' if db_ok else 'error'

    selenium_ok = False
    try:
        import selenium
        result['dependencies']['selenium_version'] = selenium.__version__
        selenium_ok = True
    except ImportError:
        pass

    result['dependencies']['selenium'] = 'ok' if selenium_ok else 'not_installed'

    jieba_ok = False
    try:
        import jieba
        jieba_ok = True
    except ImportError:
        pass

    result['dependencies']['jieba'] = 'ok' if jieba_ok else 'not_installed'

    overall = 'healthy' if (db_ok and selenium_ok and jieba_ok) else 'degraded'
    result['status'] = overall

    return make_response(True, result, f'System status: {overall}')


@admin_bp.route('/admin/logs', methods=['GET'])
def admin_logs():
    try:
        import os
        from flask import request

        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(log_dir):
            return make_response(True, {'logs': [], 'total': 0}, 'No log dir')

        lines = int(request.args.get('lines', 50))
        files = sorted([f for f in os.listdir(log_dir) if f.endswith('.log')], reverse=True)

        if not files:
            return make_response(True, {'logs': [], 'total': 0}, 'No log files')

        latest = files[0]
        filepath = os.path.join(log_dir, latest)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.readlines()

        tail = content[-lines:]
        return make_response(True, {
            'file': latest,
            'lines': len(tail),
            'logs': [line.rstrip() for line in tail],
        }, 'OK')
    except Exception as e:
        logger.error(f"admin_logs failed: {e}")
        return error_response(str(e))
