from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime
import os
from urllib.parse import quote_plus

MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '1234')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'novel_spider')

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    f'mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
)
engine = create_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PlatformSource(Base):
    __tablename__ = 'platform_source'

    id = Column(Integer, primary_key=True, index=True)
    platform_name = Column(String(255), nullable=False)
    platform_url = Column(String(512))
    remark = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class NovelRaw(Base):
    __tablename__ = 'novel_raw'

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey('platform_source.id'))
    batch_no = Column(String(50))
    source_url = Column(String(512))
    novel_name_raw = Column(String(255))
    author_name_raw = Column(String(255))
    category_name_raw = Column(String(255))
    status_raw = Column(String(100))
    word_count_raw = Column(Integer)
    intro_raw = Column(Text)
    update_time_raw = Column(String(100))
    html_snapshot_path = Column(String(512))
    crawl_time = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index('idx_batch_no', 'batch_no'),
        Index('idx_novel_name_raw', 'novel_name_raw'),
        Index('idx_source_url', 'source_url'),
    )


class NovelInfo(Base):
    __tablename__ = 'novel_info'

    id = Column(Integer, primary_key=True, index=True)
    raw_id = Column(Integer)
    platform_id = Column(Integer, ForeignKey('platform_source.id'))
    novel_name = Column(String(255), nullable=False)
    author_name = Column(String(255))
    category_name = Column(String(255))
    status = Column(String(100))
    word_count = Column(Integer)
    intro = Column(Text)
    update_time = Column(String(100))
    source_url = Column(String(512))
    crawl_date = Column(String(20))
    batch_no = Column(String(50))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('novel_name', 'author_name', 'platform_id', name='uk_novel_platform'),
        Index('idx_category_name', 'category_name'),
        Index('idx_status', 'status'),
        Index('idx_update_time', 'update_time'),
        Index('idx_crawl_date', 'crawl_date'),
        Index('idx_batch_no', 'batch_no'),
    )


class KeywordStat(Base):
    __tablename__ = 'keyword_stat'

    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, nullable=False)
    category_name = Column(String(255))
    keyword = Column(String(100), nullable=False)
    weight = Column(Float)
    source_field = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index('idx_novel_id', 'novel_id'),
        Index('idx_keyword', 'keyword'),
        Index('idx_category_name', 'category_name'),
    )


class TrendStat(Base):
    __tablename__ = 'trend_stat'

    id = Column(Integer, primary_key=True, index=True)
    stat_date = Column(String(20), nullable=False)
    dimension_type = Column(String(50), nullable=False)
    dimension_value = Column(String(100), nullable=False)
    novel_count = Column(Integer, default=0)
    update_count = Column(Integer, default=0)
    active_count = Column(Integer, default=0)
    avg_word_count = Column(Float)
    share_value = Column(Float)
    growth_rate = Column(Float)
    trend_score = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('stat_date', 'dimension_type', 'dimension_value', name='uk_trend'),
        Index('idx_stat_date', 'stat_date'),
        Index('idx_dimension_type', 'dimension_type'),
    )


def init_db():
    Base.metadata.create_all(bind=engine)