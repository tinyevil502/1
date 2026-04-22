import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.db import SessionLocal, NovelInfo

db = SessionLocal()
rows = db.query(NovelInfo).limit(5).all()
for r in rows:
    intro_preview = r.intro[:30] if r.intro else '(empty)'
    print(f'Name={r.novel_name}')
    print(f'  Author={r.author_name}')
    print(f'  Cat={r.category_name}')
    print(f'  Status={r.status}')
    print(f'  Words={r.word_count}')
    print(f'  Update={r.update_time}')
    print(f'  Intro={intro_preview}')
    print('---')
print(f'Total NovelInfo count: {db.query(NovelInfo).count()}')
db.close()
