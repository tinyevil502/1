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
    
    cur.execute("SELECT COUNT(*) FROM keyword_stat WHERE keyword REGEXP '^[0-9]+$'")
    numeric_count = cur.fetchone()[0]
    print(f'待删除的数字关键词记录: {numeric_count}')
    
    cur.execute("DELETE FROM keyword_stat WHERE keyword REGEXP '^[0-9]+$'")
    conn.commit()
    print(f'已删除 {cur.rowcount} 条数字关键词记录')
    
    cur.execute('SELECT COUNT(*) FROM keyword_stat')
    remaining = cur.fetchone()[0]
    print(f'剩余关键词记录数: {remaining}')
    
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
