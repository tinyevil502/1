import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.db import SessionLocal, NovelRaw

db = SessionLocal()
batch = '2026042123123242975de6'
records = db.query(NovelRaw).filter(NovelRaw.batch_no == batch).all()
print(f'Records in batch {batch}: {len(records)}')
for r in records[:5]:
    print(f'  id={r.id} name={r.novel_name_raw} author={r.author_name_raw} cat={r.category_name_raw}')
db.close()
