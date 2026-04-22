from models.db import SessionLocal, NovelRaw, NovelInfo
from utils.text_utils import clean_html_tags, clean_special_chars, normalize_whitespace, parse_word_count
from utils.time_utils import parse_datetime
from utils.logger import get_logger

logger = get_logger(__name__)


def is_duplicate(db, novel_name, author_name, platform_id, source_url=None):
    if author_name:
        existing = db.query(NovelInfo).filter(
            NovelInfo.novel_name == novel_name,
            NovelInfo.author_name == author_name,
            NovelInfo.platform_id == platform_id
        ).first()
        if existing:
            return True
    if source_url:
        existing = db.query(NovelInfo).filter(
            NovelInfo.source_url == source_url
        ).first()
        if existing:
            return True
    return False


def clean_novel(raw):
    name = raw.get('novel_name_raw') or raw.get('novel_name') or ''
    author = raw.get('author_name_raw') or raw.get('author_name') or ''
    category = raw.get('category_name_raw') or raw.get('category_name') or ''
    category = normalize_category(category)
    status = raw.get('status_raw') or raw.get('status') or ''
    status = normalize_status(status)
    word_count = raw.get('word_count_raw') or raw.get('word_count')
    if isinstance(word_count, str):
        word_count = parse_word_count(word_count)
    intro = raw.get('intro_raw') or raw.get('intro') or ''
    intro = clean_html_tags(intro)
    intro = clean_special_chars(intro)
    update_time = raw.get('update_time_raw') or raw.get('update_time') or ''
    update_time = parse_datetime(update_time) or update_time

    name_str = str(name).strip() if name else ''
    if not name_str or len(name_str) < 2:
        source_url = raw.get('source_url', '')
        if source_url:
            name_str = source_url.split('/')[-1].replace('.html', '') or '未知小说'

    return {
        'novel_name': name_str,
        'author_name': str(author).strip() if author else '',
        'category_name': category,
        'status': status,
        'word_count': word_count,
        'intro': intro,
        'update_time': update_time,
        'source_url': raw.get('source_url', ''),
    }


VALID_GENRES = {'玄幻', '奇幻', '仙侠', '都市', '历史', '军事', '游戏', '体育', '科幻', '言情', '穿越', '架空', '悬疑', '武侠', '轻小说', '同人'}

CATEGORY_STANDARDIZATION = {
    '玄幻': '玄幻',
    '奇幻': '奇幻',
    '仙侠': '仙侠',
    '都市': '都市',
    '历史': '历史',
    '军事': '军事',
    '游戏': '游戏',
    '体育': '体育',
    '科幻': '科幻',
    '言情': '言情',
    '穿越': '穿越',
    '架空': '架空',
    '悬疑': '悬疑',
    '武侠': '武侠',
    '轻小说': '轻小说',
    '同人': '同人',
    '修真': '仙侠',
    '修线': '仙侠',
    '修仙': '仙侠',
    '校园': '都市',
    '职场': '都市',
    '秦汉': '历史',
    '三国': '历史',
    '唐宋': '历史',
    '明清': '历史',
    '宫斗': '言情',
    '宅斗': '言情',
    '甜宠': '言情',
    '虐恋': '言情',
    '青春': '言情',
    '衍生': '同人',
}


def normalize_category(category):
    if not category:
        return '玄幻'
    category = str(category).strip()
    if not category:
        return '玄幻'
    if category in ('连载小说', '完本小说', '连载中', '已完结', '完结', '连载', '未知', '暂停'):
        return '玄幻'
    for key, value in CATEGORY_STANDARDIZATION.items():
        if key in category:
            return value
    if category in VALID_GENRES:
        return category
    return '玄幻'


def normalize_status(status):
    if not status:
        return '连载中'
    status = str(status).strip().lower()
    if any(kw in status for kw in ['连载', '更新', '进行', 'ing', '连载中']):
        return '连载中'
    elif any(kw in status for kw in ['完结', '结束', '已完成', 'completed', '已完结']):
        return '已完结'
    elif any(kw in status for kw in ['暂停', '停更', '休刊']):
        return '暂停'
    return status if status else '连载中'


def clean_batch(batch_no=None):
    db = SessionLocal()
    cleaned_count = 0
    skipped_count = 0

    try:
        query = db.query(NovelRaw)
        if batch_no:
            query = query.filter(NovelRaw.batch_no == batch_no)

        raw_records = query.all()
        logger.info(f"Cleaning {len(raw_records)} raw records")

        for raw in raw_records:
            raw_data = {
                'novel_name_raw': raw.novel_name_raw,
                'author_name_raw': raw.author_name_raw,
                'category_name_raw': raw.category_name_raw,
                'status_raw': raw.status_raw,
                'word_count_raw': raw.word_count_raw,
                'intro_raw': raw.intro_raw,
                'update_time_raw': raw.update_time_raw,
                'source_url': raw.source_url,
            }

            cleaned = clean_novel(raw_data)

            if not cleaned['novel_name']:
                skipped_count += 1
                continue

            if is_duplicate(db, cleaned['novel_name'], cleaned['author_name'], raw.platform_id, cleaned.get('source_url')):
                skipped_count += 1
                continue

            try:
                crawl_dt = raw.crawl_time.strftime('%Y-%m-%d') if raw.crawl_time else None
                novel = NovelInfo(
                    raw_id=raw.id,
                    platform_id=raw.platform_id,
                    novel_name=cleaned['novel_name'],
                    author_name=cleaned['author_name'],
                    category_name=cleaned['category_name'],
                    status=cleaned['status'],
                    word_count=cleaned['word_count'],
                    intro=cleaned['intro'],
                    update_time=cleaned['update_time'],
                    source_url=cleaned['source_url'],
                    crawl_date=crawl_dt,
                    batch_no=raw.batch_no,
                )
                db.add(novel)
                cleaned_count += 1

            except Exception as e:
                logger.warning(f"Failed to save cleaned novel: {e}")
                continue

        db.commit()
        logger.info(f"Cleaning completed: {cleaned_count} saved, {skipped_count} skipped")
        return {'success': True, 'cleaned': cleaned_count, 'skipped': skipped_count}

    except Exception as e:
        db.rollback()
        logger.error(f"Cleaning batch failed: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()