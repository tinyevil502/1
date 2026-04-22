import jieba
import jieba.analyse
from models.db import SessionLocal, NovelInfo, KeywordStat
from utils.text_utils import STOPWORDS, is_stopword, is_noise_word, is_person_name, is_valid_keyword, clean_special_chars
from utils.logger import get_logger

logger = get_logger(__name__)


def extract_keywords(text, method='tfidf', topk=10):
    if not text or not text.strip():
        return []

    text = clean_special_chars(text)

    if method == 'textrank':
        try:
            keywords = jieba.analyse.textrank(text, topK=topk, withWeight=True)
        except Exception as e:
            logger.warning(f"TextRank extraction failed: {e}")
            keywords = []
    else:
        try:
            keywords = jieba.analyse.extract_tags(text, topK=topk, withWeight=True)
        except Exception as e:
            logger.warning(f"TF-IDF extraction failed: {e}")
            keywords = []

    return [(word, weight) for word, weight in keywords]


def extract_keywords_with_filter(text, method='tfidf', topk=10, min_length=2):
    raw_keywords = extract_keywords(text, method=method, topk=topk * 2)

    filtered = []
    for word, weight in raw_keywords:
        if not is_valid_keyword(word):
            continue
        filtered.append((word, weight))

    return filtered[:topk]


def process_keywords(method='tfidf', topk=20, batch_size=100):
    db = SessionLocal()
    processed_count = 0

    try:
        novels = db.query(NovelInfo).limit(batch_size).all()
        logger.info(f"Processing keywords for {len(novels)} novels")

        for novel in novels:
            if not novel.intro and not novel.novel_name:
                continue

            source_text = novel.intro or ''
            if novel.novel_name:
                source_text = novel.novel_name + ' ' + source_text

            keywords = extract_keywords_with_filter(source_text, method=method, topk=topk)

            for keyword, weight in keywords:
                try:
                    stat = KeywordStat(
                        novel_id=novel.id,
                        category_name=novel.category_name,
                        keyword=keyword,
                        weight=weight,
                        source_field='intro' if novel.intro else 'title',
                    )
                    db.add(stat)
                    processed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to save keyword: {e}")
                    continue

        db.commit()
        logger.info(f"Keyword processing completed: {processed_count} keywords saved")
        return {'success': True, 'keywords': processed_count, 'novels': len(novels)}

    except Exception as e:
        db.rollback()
        logger.error(f"Keyword processing failed: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


def get_keywords_by_category(category_name=None, topk=50):
    db = SessionLocal()
    try:
        query = db.query(KeywordStat.keyword, KeywordStat.weight).order_by(
            KeywordStat.weight.desc()
        )

        if category_name:
            query = query.filter(KeywordStat.category_name == category_name)

        keywords = query.group_by(KeywordStat.keyword).limit(topk).all()

        return {kw.keyword: kw.weight for kw in keywords}

    finally:
        db.close()


def get_all_keywords(topk=100):
    db = SessionLocal()
    try:
        keywords = db.query(
            KeywordStat.keyword,
            KeywordStat.weight
        ).order_by(
            KeywordStat.weight.desc()
        ).group_by(
            KeywordStat.keyword
        ).limit(topk).all()

        return {kw.keyword: kw.weight for kw in keywords}

    finally:
        db.close()