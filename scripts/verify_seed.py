import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.db import SessionLocal, NovelInfo, TrendStat

db = SessionLocal()

batch_count = db.query(NovelInfo.batch_no).filter(NovelInfo.batch_no != None).distinct().count()
novel_count = db.query(NovelInfo).count()
trend_count = db.query(TrendStat).count()

print(f'Batch count: {batch_count}')
print(f'novel_info rows: {novel_count}')
print(f'trend_stat rows: {trend_count}')

print('\nSample trends:')
trends = db.query(TrendStat).filter(TrendStat.dimension_type == 'category').limit(5).all()
for t in trends:
    print(f'  date={t.stat_date}, cat={t.dimension_value}, growth={t.growth_rate}')

db.close()
