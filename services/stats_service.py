from models.db import SessionLocal, NovelRaw, NovelInfo, PlatformSource
from collections import defaultdict
from utils.logger import get_logger

logger = get_logger(__name__)


def get_raw_stats():
    db = SessionLocal()
    try:
        total = db.query(NovelRaw).count()
        by_batch = defaultdict(int)
        batches = db.query(NovelRaw.batch_no).distinct().all()
        for b in batches:
            if b.batch_no:
                by_batch[b.batch_no] += 1

        return {
            'total': total,
            'batches': len(by_batch),
            'batch_details': [{'batch_no': k, 'count': v} for k, v in by_batch.items()]
        }
    finally:
        db.close()


def get_cleaned_stats():
    db = SessionLocal()
    try:
        total = db.query(NovelInfo).count()

        by_category = defaultdict(int)
        categories = db.query(NovelInfo.category_name).filter(NovelInfo.category_name != None).all()
        for c in categories:
            if c.category_name:
                by_category[c.category_name] += 1

        by_status = defaultdict(int)
        statuses = db.query(NovelInfo.status).filter(NovelInfo.status != None).all()
        for s in statuses:
            if s.status:
                by_status[s.status] += 1

        return {
            'total': total,
            'by_category': dict(by_category),
            'by_status': dict(by_status)
        }
    finally:
        db.close()


def get_batches():
    db = SessionLocal()
    try:
        batches = db.query(
            NovelRaw.batch_no,
            NovelRaw.crawl_time
        ).distinct().order_by(
            NovelRaw.crawl_time.desc()
        ).all()

        result = []
        for batch in batches:
            if batch.batch_no:
                count = db.query(NovelRaw).filter(NovelRaw.batch_no == batch.batch_no).count()
                result.append({
                    'batch_no': batch.batch_no,
                    'crawl_time': str(batch.crawl_time) if batch.crawl_time else None,
                    'count': count
                })

        return result
    finally:
        db.close()


def get_platforms():
    db = SessionLocal()
    try:
        platforms = db.query(PlatformSource).all()
        return [
            {
                'id': p.id,
                'platform_name': p.platform_name,
                'platform_url': p.platform_url,
                'remark': p.remark,
                'created_at': str(p.created_at) if p.created_at else None
            }
            for p in platforms
        ]
    finally:
        db.close()