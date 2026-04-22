import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-2024')

    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '1234')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'novel_spider')

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    CRAWLER_TIMEOUT = int(os.environ.get('CRAWLER_TIMEOUT', 30))
    CRAWLER_RETRY = int(os.environ.get('CRAWLER_RETRY', 3))
    CRAWLER_DELAY = int(os.environ.get('CRAWLER_DELAY', 3))

    CRAWLER_BASE_URL = os.environ.get('CRAWLER_BASE_URL', 'https://www.17k.com')
    CRAWLER_LIST_PATH = os.environ.get('CRAWLER_LIST_PATH', '/book/adv/0/0/0/0/0/0/1.html')

    PAGINATION_SIZE = int(os.environ.get('PAGINATION_SIZE', 20))
    KEYWORD_TOPK = int(os.environ.get('KEYWORD_TOPK', 20))

    DEBUG_MODE = os.environ.get('DEBUG_MODE', 'True').lower() == 'true'