from models.db import SessionLocal, NovelInfo, TrendStat
from collections import defaultdict
from utils.time_utils import get_current_date
from utils.logger import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)


def get_batch_count(db):
    batches = db.query(NovelInfo.batch_no).filter(
        NovelInfo.batch_no != None
    ).distinct().all()
    return len([b for b in batches if b.batch_no])


def get_novels_by_batch(db):
    novels = db.query(NovelInfo).all()
    batches = defaultdict(list)
    for novel in novels:
        batch = novel.batch_no or 'unknown'
        batches[batch].append(novel)
    return batches


def aggregate_by_category(novels, stat_date):
    stats = defaultdict(lambda: {'novel_count': 0, 'total_words': 0})
    for novel in novels:
        cat = novel.category_name or '未知'
        stats[cat]['novel_count'] += 1
        if novel.word_count:
            stats[cat]['total_words'] += novel.word_count
    total = len(novels)
    result = {}
    for cat, data in stats.items():
        result[cat] = {
            'novel_count': data['novel_count'],
            'avg_word_count': round(data['total_words'] / data['novel_count'], 0) if data['novel_count'] > 0 else 0,
            'share_value': round(data['novel_count'] / total, 4) if total > 0 else 0,
        }
    return result


def aggregate_by_status(novels, stat_date):
    stats = defaultdict(lambda: {'novel_count': 0, 'total_words': 0})
    for novel in novels:
        status = novel.status or '未知'
        stats[status]['novel_count'] += 1
        if novel.word_count:
            stats[status]['total_words'] += novel.word_count
    total = len(novels)
    result = {}
    for status, data in stats.items():
        result[status] = {
            'novel_count': data['novel_count'],
            'avg_word_count': round(data['total_words'] / data['novel_count'], 0) if data['novel_count'] > 0 else 0,
            'share_value': round(data['novel_count'] / total, 4) if total > 0 else 0,
        }
    return result


def parse_update_date(update_time_str):
    if not update_time_str:
        return None
    try:
        if isinstance(update_time_str, str):
            date_part = update_time_str[:10] if len(update_time_str) >= 10 else update_time_str
            return datetime.strptime(date_part, '%Y-%m-%d')
    except Exception:
        pass
    return None


def aggregate_by_update_time(novels, stat_date, days=30):
    stats = defaultdict(lambda: {'novel_count': 0, 'update_count': 0})
    
    dates = []
    for novel in novels:
        dt = parse_update_date(novel.update_time)
        if dt:
            dates.append(dt)
    
    if not dates:
        return {'dates': [], 'counts': [], 'active_counts': []}
    
    max_date = max(dates)
    start_date = max_date - timedelta(days=days)
    
    for novel in novels:
        dt = parse_update_date(novel.update_time)
        if dt and dt >= start_date:
            date_key = dt.strftime('%Y-%m-%d')
            stats[date_key]['update_count'] += 1
    
    all_dates = sorted(stats.keys())
    return {
        'dates': all_dates,
        'counts': [stats[d]['update_count'] for d in all_dates],
        'active_counts': [stats[d]['novel_count'] for d in all_dates],
    }


def compute_active_trend(batches_by_date, active_window_days=7):
    all_dates = sorted(batches_by_date.keys())
    result = {}
    for i, date_str in enumerate(all_dates):
        current_novels = batches_by_date[date_str]
        current_names = {(n.novel_name, n.author_name) for n in current_novels}
        active_names = set()
        for j in range(max(0, i - active_window_days + 1), i + 1):
            check_date = all_dates[j]
            for n in batches_by_date[check_date]:
                active_names.add((n.novel_name, n.author_name))
        active_count = len(current_names & active_names)
        total_count = len(current_names)
        result[date_str] = {
            'active_count': active_count,
            'total_count': total_count,
            'active_rate': round(active_count / total_count, 4) if total_count > 0 else 0,
        }
    return result


def compute_growth_rate(current_val, previous_val):
    if previous_val is None or previous_val == 0:
        return None
    return round((current_val - previous_val) / previous_val, 4)


def calculate_trends():
    db = SessionLocal()
    try:
        batches_by_date = get_novels_by_batch(db)
        batch_count = get_batch_count(db)
        logger.info(f"Found {batch_count} batches for trend calculation")

        all_novels = db.query(NovelInfo).all()
        stat_date = get_current_date()
        total_novels = len(all_novels)

        if batch_count <= 1:
            logger.info("Single batch detected, computing distribution only")
            cat_stats = aggregate_by_category(all_novels, stat_date)
            for dimension_value, data in cat_stats.items():
                save_trend_stat(db, stat_date, 'category', dimension_value, data)

            status_stats = aggregate_by_status(all_novels, stat_date)
            for dimension_value, data in status_stats.items():
                save_trend_stat(db, stat_date, 'status', dimension_value, data)

            update_stats = aggregate_by_update_time(all_novels, stat_date, days=30)
            for i, date in enumerate(update_stats['dates']):
                save_trend_stat(db, date, 'update_trend', date, {
                    'update_count': update_stats['counts'][i],
                    'novel_count': update_stats['active_counts'][i],
                })

            db.commit()
            logger.info("Single-batch trend calculation completed")
            return {'success': True, 'novels': total_novels, 'batches': batch_count, 'mode': 'distribution'}

        sorted_dates = sorted(batches_by_date.keys())
        previous_stats = {}
        for date_str in sorted_dates:
            novels = batches_by_date[date_str]
            cat_stats = aggregate_by_category(novels, date_str)
            for dimension_value, data in cat_stats.items():
                prev_data = previous_stats.get(('category', dimension_value))
                if prev_data is not None:
                    data['growth_rate'] = compute_growth_rate(data['novel_count'], prev_data.get('novel_count', 0))
                save_trend_stat(db, date_str, 'category', dimension_value, data)
                previous_stats[('category', dimension_value)] = data

            status_stats = aggregate_by_status(novels, date_str)
            for dimension_value, data in status_stats.items():
                prev_data = previous_stats.get(('status', dimension_value))
                if prev_data is not None:
                    data['growth_rate'] = compute_growth_rate(data['novel_count'], prev_data.get('novel_count', 0))
                save_trend_stat(db, date_str, 'status', dimension_value, data)
                previous_stats[('status', dimension_value)] = data

        active_trend = compute_active_trend(batches_by_date)
        for date_str, data in active_trend.items():
            save_trend_stat(db, date_str, 'update_trend', date_str, {
                'update_count': data['active_count'],
                'novel_count': data['total_count'],
                'active_count': data['active_count'],
                'share_value': data['active_rate'],
            })

        db.commit()
        logger.info(f"Multi-batch trend calculation completed for {len(sorted_dates)} dates")
        return {'success': True, 'novels': total_novels, 'batches': batch_count, 'mode': 'trend'}

    except Exception as e:
        db.rollback()
        logger.error(f"Trend calculation failed: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


def save_trend_stat(db, stat_date, dimension_type, dimension_value, data):
    existing = db.query(TrendStat).filter(
        TrendStat.stat_date == stat_date,
        TrendStat.dimension_type == dimension_type,
        TrendStat.dimension_value == dimension_value
    ).first()

    if existing:
        existing.novel_count = data.get('novel_count', existing.novel_count)
        existing.update_count = data.get('update_count', existing.update_count or 0)
        existing.avg_word_count = data.get('avg_word_count', existing.avg_word_count)
        existing.active_count = data.get('active_count', existing.active_count or 0)
        existing.share_value = data.get('share_value', existing.share_value)
        existing.growth_rate = data.get('growth_rate', existing.growth_rate)
        existing.trend_score = data.get('trend_score', existing.trend_score)
    else:
        trend = TrendStat(
            stat_date=stat_date,
            dimension_type=dimension_type,
            dimension_value=dimension_value,
            novel_count=data.get('novel_count', 0),
            update_count=data.get('update_count', 0),
            avg_word_count=data.get('avg_word_count'),
            active_count=data.get('active_count', 0),
            share_value=data.get('share_value'),
            growth_rate=data.get('growth_rate'),
            trend_score=data.get('trend_score'),
        )
        db.add(trend)


def get_trend_stats(dimension_type=None, days=30):
    db = SessionLocal()
    try:
        query = db.query(TrendStat)
        if dimension_type:
            query = query.filter(TrendStat.dimension_type == dimension_type)
        stats = query.order_by(TrendStat.stat_date.desc()).limit(days).all()
        return [
            {
                'stat_date': s.stat_date,
                'dimension_type': s.dimension_type,
                'dimension_value': s.dimension_value,
                'novel_count': s.novel_count,
                'update_count': s.update_count,
                'avg_word_count': s.avg_word_count,
                'active_count': s.active_count,
                'share_value': s.share_value,
                'growth_rate': s.growth_rate,
                'trend_score': s.trend_score,
            }
            for s in stats
        ]
    finally:
        db.close()
