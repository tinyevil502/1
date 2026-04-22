import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.text_utils import is_noise_word, is_person_name
import pymysql

conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='1234',
    database='novel_spider'
)

try:
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT keyword FROM keyword_stat')
    all_keywords = [row[0] for row in cur.fetchall()]

    bad_keywords = []
    for kw in all_keywords:
        if is_noise_word(kw) or is_person_name(kw):
            bad_keywords.append(kw)

    print(f'待删除的干扰词: {len(bad_keywords)} 个')
    for kw in bad_keywords[:30]:
        print(f'  - {kw}')
    if len(bad_keywords) > 30:
        print(f'  ... 还有 {len(bad_keywords) - 30} 个')

    if bad_keywords:
        placeholders = ','.join(['%s'] * len(bad_keywords))
        cur.execute(f"DELETE FROM keyword_stat WHERE keyword IN ({placeholders})", bad_keywords)
        conn.commit()
        print(f'\n已删除 {cur.rowcount} 条干扰词记录')

    cur.execute('SELECT COUNT(*) FROM keyword_stat')
    print(f'剩余关键词记录数: {cur.fetchone()[0]}')

    cur.execute("""
        SELECT keyword, SUM(weight) as total_weight, COUNT(*) as freq 
        FROM keyword_stat 
        GROUP BY keyword 
        ORDER BY total_weight DESC 
        LIMIT 20
    """)
    print('\n当前 TOP20 关键词:')
    for row in cur.fetchall():
        print(f'  {row[0]}: weight={row[1]:.2f}, freq={row[2]}')
finally:
    conn.close()
