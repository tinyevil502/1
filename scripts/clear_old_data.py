import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.db import SessionLocal, NovelInfo, NovelRaw, KeywordStat, TrendStat

db = SessionLocal()

# Clear all incomplete data
deleted_novel_info = db.query(NovelInfo).delete()
deleted_novel_raw = db.query(NovelRaw).delete()
deleted_keyword_stat = db.query(KeywordStat).delete()
deleted_trend_stat = db.query(TrendStat).delete()

db.commit()
print(f'Deleted: NovelInfo={deleted_novel_info}, NovelRaw={deleted_novel_raw}, KeywordStat={deleted_keyword_stat}, TrendStat={deleted_trend_stat}')
db.close()
