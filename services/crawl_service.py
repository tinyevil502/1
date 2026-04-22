from crawler.hybrid_client import HybridClient
from crawler.seventeenk_spider import SeventeenKSpider
from models.db import SessionLocal, PlatformSource, NovelRaw
from utils.logger import get_logger
from utils.time_utils import get_current_datetime

logger = get_logger(__name__)

ALL_CATEGORIES = ['xuanhuan','dushi','xianxia','lishi','junshi','youxi','kehuan','xuanyi','qingxiaoshuo']


def get_or_create_platform(db, name, url):
    platform = db.query(PlatformSource).filter(PlatformSource.platform_name == name).first()
    if not platform:
        platform = PlatformSource(platform_name=name, platform_url=url)
        db.add(platform)
        db.commit()
        db.refresh(platform)
    return platform


def save_raw_data(db, items, batch_no, platform_id):
    saved_count = 0
    seen_urls = set()

    for item in items:
        url = item.get('source_url', '')
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        try:
            raw = NovelRaw(
                platform_id=platform_id,
                batch_no=batch_no,
                source_url=url,
                novel_name_raw=item.get('novel_name_raw', ''),
                author_name_raw=item.get('author_name_raw', ''),
                category_name_raw=item.get('category_name_raw', ''),
                status_raw=item.get('status_raw', ''),
                word_count_raw=item.get('word_count_raw'),
                intro_raw=item.get('intro_raw', ''),
                update_time_raw=item.get('update_time_raw', ''),
                html_snapshot_path=item.get('html_snapshot_path'),
                crawl_time=get_current_datetime(),
            )
            db.add(raw)
            saved_count += 1
        except Exception as e:
            logger.warning(f"Failed to save raw item: {e}")
            continue

    db.commit()
    return saved_count


def run_crawl_task(pages=1, category='xuanhuan'):
    db = SessionLocal()
    client = None

    try:
        logger.info(f"Starting crawl: pages={pages}, category={category}")

        platform = get_or_create_platform(db, '17K小说网', 'https://www.17k.com')

        client = HybridClient(timeout=60, delay=3)
        client.start()
        spider = SeventeenKSpider(client)

        list_urls = spider.get_list_urls(category=category, pages=pages)

        all_items = []
        batch_no = spider.generate_batch_no()
        category_name = spider.get_category_name(category)

        for page_url in list_urls:
            try:
                html = spider.fetch_list_page(page_url)
                items = spider.parse_list_page(html)

                for item in items:
                    item['batch_no'] = batch_no
                    if not item.get('category_name_raw'):
                        item['category_name_raw'] = category_name

                    detail_url = item.get('detail_url')
                    if detail_url:
                        try:
                            detail_html = spider.fetch_detail_page(detail_url)
                            detail_data = spider.parse_detail_page(detail_html)
                            item.update(detail_data)
                        except Exception as e:
                            logger.warning(f"Failed to fetch detail for {detail_url}: {e}")

                all_items.extend(items)
                logger.info(f"Crawled {len(items)} from {page_url}")

            except Exception as e:
                logger.error(f"Failed to crawl {page_url}: {e}")

        if all_items:
            saved = save_raw_data(db, all_items, batch_no, platform.id)
            logger.info(f"Crawl completed: {saved} saved, batch={batch_no}")
            return {'success': True, 'batch_no': batch_no, 'saved': saved, 'total': len(all_items)}
        else:
            logger.warning("No items scraped")
            return {'success': True, 'batch_no': batch_no, 'saved': 0, 'total': 0}

    except Exception as e:
        logger.error(f"Crawl failed: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()
        if client:
            client.close()


def crawl_multi_category(categories=None, per_category=15, pages_per_cat=2):
    """Crawl multiple categories, limiting to per_category novels per category.
    Returns a summary with per-category results.
    """
    if categories is None:
        categories = ALL_CATEGORIES

    db = SessionLocal()
    client = None
    all_items = []
    batch_no = None
    summary = {}

    try:
        logger.info(f"Starting multi-category crawl: categories={categories}, per_category={per_category}")

        platform = get_or_create_platform(db, '17K小说网', 'https://www.17k.com')

        client = HybridClient(timeout=60, delay=3)
        client.start()
        spider = SeventeenKSpider(client)

        batch_no = spider.generate_batch_no()

        for category in categories:
            category_name = spider.get_category_name(category)
            list_urls = spider.get_list_urls(category=category, pages=pages_per_cat)

            cat_items = []
            for page_url in list_urls:
                if len(cat_items) >= per_category:
                    break
                try:
                    html = spider.fetch_list_page(page_url)
                    items = spider.parse_list_page(html)

                    for item in items:
                        if len(cat_items) >= per_category:
                            break
                        item['batch_no'] = batch_no
                        item['category_name_raw'] = category_name

                        detail_url = item.get('detail_url')
                        if detail_url:
                            try:
                                detail_html = spider.fetch_detail_page(detail_url)
                                detail_data = spider.parse_detail_page(detail_html)
                                item.update(detail_data)
                            except Exception as e:
                                logger.warning(f"Failed to fetch detail for {detail_url}: {e}")

                        cat_items.append(item)

                    logger.info(f"Crawled {len(items)} from {page_url} ({category_name})")

                except Exception as e:
                    logger.error(f"Failed to crawl {page_url}: {e}")

            cat_items = cat_items[:per_category]
            all_items.extend(cat_items)
            summary[category_name] = {'count': len(cat_items), 'category': category}
            logger.info(f"Category {category_name}: collected {len(cat_items)} novels")

        if all_items:
            saved = save_raw_data(db, all_items, batch_no, platform.id)
            logger.info(f"Multi-category crawl completed: {saved} saved, batch={batch_no}")
            return {'success': True, 'batch_no': batch_no, 'saved': saved, 'total': len(all_items), 'summary': summary}
        else:
            logger.warning("No items scraped")
            return {'success': True, 'batch_no': batch_no, 'saved': 0, 'total': 0, 'summary': summary}

    except Exception as e:
        logger.error(f"Multi-category crawl failed: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()
        if client:
            client.close()


def crawl_all_categories(pages: int = 5):
    """Crawl all known categories sequentially.
    Returns a summary per category.
    """
    results = {}
    for cat in ALL_CATEGORIES:
        res = run_crawl_task(pages=pages, category=cat)
        results[cat] = res
    return {'success': True, 'results': results, 'total_categories': len(ALL_CATEGORIES)}
