import pymysql

conn = pymysql.connect(host='localhost', user='root', password='1234', database='novel_spider')
cursor = conn.cursor()

sql_statements = [
    """
    CREATE TABLE IF NOT EXISTS platform_source (
        id INT AUTO_INCREMENT PRIMARY KEY,
        platform_name VARCHAR(255) NOT NULL,
        platform_url VARCHAR(512),
        remark TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_platform_name (platform_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS novel_raw (
        id INT AUTO_INCREMENT PRIMARY KEY,
        platform_id INT,
        batch_no VARCHAR(50),
        source_url VARCHAR(512),
        novel_name_raw VARCHAR(255),
        author_name_raw VARCHAR(255),
        category_name_raw VARCHAR(255),
        status_raw VARCHAR(100),
        word_count_raw INT,
        intro_raw TEXT,
        update_time_raw VARCHAR(100),
        html_snapshot_path VARCHAR(512),
        crawl_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_batch_no (batch_no),
        INDEX idx_novel_name (novel_name_raw),
        INDEX idx_source_url (source_url),
        FOREIGN KEY (platform_id) REFERENCES platform_source(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS novel_info (
        id INT AUTO_INCREMENT PRIMARY KEY,
        raw_id INT,
        platform_id INT,
        novel_name VARCHAR(255) NOT NULL,
        author_name VARCHAR(255),
        category_name VARCHAR(255),
        status VARCHAR(100),
        word_count INT,
        intro TEXT,
        update_time VARCHAR(100),
        source_url VARCHAR(512),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_novel_platform (novel_name, author_name, platform_id),
        INDEX idx_category (category_name),
        INDEX idx_status (status),
        INDEX idx_update_time (update_time),
        FOREIGN KEY (platform_id) REFERENCES platform_source(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS keyword_stat (
        id INT AUTO_INCREMENT PRIMARY KEY,
        novel_id INT NOT NULL,
        category_name VARCHAR(255),
        keyword VARCHAR(100) NOT NULL,
        weight FLOAT,
        source_field VARCHAR(100),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_novel_id (novel_id),
        INDEX idx_keyword (keyword),
        INDEX idx_category (category_name),
        FOREIGN KEY (novel_id) REFERENCES novel_info(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS trend_stat (
        id INT AUTO_INCREMENT PRIMARY KEY,
        stat_date DATE NOT NULL,
        dimension_type VARCHAR(50) NOT NULL,
        dimension_value VARCHAR(100) NOT NULL,
        novel_count INT DEFAULT 0,
        update_count INT DEFAULT 0,
        avg_word_count FLOAT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uk_trend (stat_date, dimension_type, dimension_value),
        INDEX idx_stat_date (stat_date),
        INDEX idx_dimension (dimension_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    INSERT INTO platform_source (platform_name, platform_url, remark)
    VALUES ('17K小说网', 'https://www.17k.com', '17K小说网公开页面')
    """
]

for stmt in sql_statements:
    cursor.execute(stmt)

conn.commit()
print("Tables created successfully")
conn.close()