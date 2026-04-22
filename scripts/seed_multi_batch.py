import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import random
from models.db import SessionLocal, NovelInfo, TrendStat

CATEGORIES = ['玄幻', '都市', '仙侠', '科幻', '网游', '历史', '悬疑', '武侠', '奇幻', '言情']
STATUSES = ['连载中', '已完结']
AUTHORS = ['唐家三少', '天蚕土豆', '辰东', '我吃西红柿', '耳根', '猫腻', '烽火戏诸侯', '忘语', '梦入神机', '蝴蝶蓝']
NOVEL_NAMES = [
    '斗罗大陆', '斗破苍穹', '遮天', '星辰变', '仙逆', '将夜', '雪中悍刀行', '凡人修仙传',
    '神墓', '全职高手', '完美世界', '大主宰', '圣墟', '一念永恒', '三寸人间', '元尊',
    '沧元图', '飞剑问道', '诡秘之主', '牧神记', '天道图书馆', '最强反套路系统', '超神机械师',
    '夜的命名术', '深空彼岸', '明克街13号', '第一序列', '这游戏也太真实了', '赤心巡天', '长夜余火'
]


def seed_multi_batch_data(days=60):
    db = SessionLocal()
    try:
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=days)

        # Generate novels
        novels = []
        for i, name in enumerate(NOVEL_NAMES):
            novels.append({
                'novel_name': name,
                'author_name': AUTHORS[i % len(AUTHORS)],
                'category_name': CATEGORIES[i % len(CATEGORIES)],
                'status': STATUSES[i % 2],
                'word_count': random.randint(500000, 5000000),
                'update_time': (today - datetime.timedelta(days=random.randint(0, 5))).strftime('%Y-%m-%d %H:%M:%S'),
            })

        # Create multiple crawl batches (every 3 days)
        batch_dates = []
        current = start_date
        while current <= today:
            batch_dates.append(current)
            current += datetime.timedelta(days=3)

        print(f'Creating {len(batch_dates)} crawl batches from {start_date} to {today}')

        inserted = 0
        for batch_idx, batch_date in enumerate(batch_dates):
            batch_no = f'BATCH_{batch_idx + 1}'
            crawl_date_str = batch_date.strftime('%Y-%m-%d')

            # Each batch has a subset of novels (simulating active novels on that day)
            active_count = random.randint(15, len(novels))
            active_novels = random.sample(novels, active_count)

            for novel in active_novels:
                # Vary word count over time (increasing)
                days_elapsed = (batch_date - start_date).days
                base_word_count = novel['word_count'] - days_elapsed * random.randint(1000, 5000)
                word_count = max(100000, base_word_count)

                # Update time is around the crawl date
                update_day_offset = random.randint(-2, 0)
                update_dt = batch_date + datetime.timedelta(days=update_day_offset)
                update_time_str = update_dt.strftime('%Y-%m-%d %H:%M:%S')

                record = NovelInfo(
                    novel_name=novel['novel_name'],
                    author_name=novel['author_name'],
                    category_name=novel['category_name'],
                    status=novel['status'],
                    word_count=word_count,
                    update_time=update_time_str,
                    crawl_date=crawl_date_str,
                    batch_no=batch_no,
                )
                db.add(record)
                inserted += 1

        db.commit()
        print(f'Inserted {inserted} records into novel_info')

        # Generate trend_stat data for category growth rates
        trend_inserted = 0
        for batch_date in batch_dates:
            stat_date_str = batch_date.strftime('%Y-%m-%d')

            # Count novels per category up to this date
            category_counts = {}
            for i, novel in enumerate(novels):
                cat = novel['category_name']
                # Randomly include novels that appeared before this batch date
                if random.random() < 0.7:
                    category_counts[cat] = category_counts.get(cat, 0) + 1

            for cat, count in category_counts.items():
                # Check if record already exists
                existing = db.query(TrendStat).filter(
                    TrendStat.stat_date == stat_date_str,
                    TrendStat.dimension_type == 'category',
                    TrendStat.dimension_value == cat
                ).first()

                if existing:
                    continue

                # Calculate growth rate (simulated)
                prev_count = max(1, count - random.randint(0, 3))
                growth_rate = round((count - prev_count) / prev_count, 4) if prev_count > 0 else 0

                trend = TrendStat(
                    stat_date=stat_date_str,
                    dimension_type='category',
                    dimension_value=cat,
                    novel_count=count,
                    update_count=random.randint(5, 20),
                    active_count=random.randint(1, max(1, count)),
                    avg_word_count=random.uniform(1000000, 3000000),
                    share_value=round(count / sum(category_counts.values()), 4),
                    growth_rate=growth_rate,
                    trend_score=round(random.uniform(0.3, 0.9), 4),
                )
                db.add(trend)
                trend_inserted += 1

        db.commit()
        print(f'Inserted {trend_inserted} records into trend_stat')
        print('Done!')

    except Exception as e:
        db.rollback()
        print(f'Error: {e}')
        raise
    finally:
        db.close()


if __name__ == '__main__':
    seed_multi_batch_data(days=60)
