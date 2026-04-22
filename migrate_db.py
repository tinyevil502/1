from sqlalchemy import text
from models.db import engine

def migrate():
    with engine.connect() as conn:
        migrations = [
            ('ALTER TABLE novel_info ADD COLUMN crawl_date VARCHAR(20)', 'crawl_date'),
            ('ALTER TABLE novel_info ADD COLUMN batch_no VARCHAR(50)', 'batch_no'),
            ('ALTER TABLE novel_info ADD INDEX idx_crawl_date (crawl_date)', 'idx_crawl_date'),
            ('ALTER TABLE novel_info ADD INDEX idx_batch_no (batch_no)', 'idx_batch_no'),
            ('ALTER TABLE trend_stat ADD COLUMN active_count INT DEFAULT 0', 'active_count'),
            ('ALTER TABLE trend_stat ADD COLUMN share_value FLOAT', 'share_value'),
            ('ALTER TABLE trend_stat ADD COLUMN growth_rate FLOAT', 'growth_rate'),
            ('ALTER TABLE trend_stat ADD COLUMN trend_score FLOAT', 'trend_score'),
        ]
        
        for sql, name in migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"Added {name}")
            except Exception as e:
                if 'Duplicate' in str(e):
                    print(f"{name} already exists")
                else:
                    print(f"Error adding {name}: {e}")

    print("Migration completed!")

if __name__ == '__main__':
    migrate()
