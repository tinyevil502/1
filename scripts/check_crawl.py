import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.db import SessionLocal, NovelRaw

db = SessionLocal()
rows = db.query(NovelRaw).filter(NovelRaw.batch_no == '202604210934574baac9ac').limit(5).all()
for r in rows:
    intro_preview = r.intro_raw[:50] if r.intro_raw else '(empty)'
    print(f'Name={r.novel_name_raw}')
    print(f'  Author={r.author_name_raw}')
    print(f'  Cat={r.category_name_raw}')
    print(f'  Status={r.status_raw}')
    print(f'  Words={r.word_count_raw}')
    print(f'  Update={r.update_time_raw}')
    print(f'  Intro={intro_preview}')
    print('---')
db.close()
