import os
import datetime
from sqlalchemy import create_engine, Column, String, Integer, Text, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from campus_notice_crawler.utils.env_loader import load_project_env

# 프로젝트 루트 `.env`만 명시적으로 로드
load_project_env()

Base = declarative_base()

class Notice(Base):
    __tablename__ = 'notices'

    notice_id = Column(String(50), primary_key=True)
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    author = Column(String(100))
    created_at = Column(String(20))  # YYYY-MM-DD 형식
    is_pinned = Column(Boolean, default=False)
    content = Column(Text)
    attachments = Column(JSON, default=list)  # [{"name": "...", "url": "..."}] 형태
    images = Column(JSON, default=list)       # ["http://...", ...] 형태
    category = Column(String(50), default='행정안내')
    summary = Column(JSON, default=list)       # ["요약1", "요약2", "요약3"] 형태
    key_points = Column(JSON, default=list)    # ["태그1", "태그2", ...] 형태
    view_count = Column(Integer, default=0)
    source = Column(String(100), default='daegu_university')
    scraped_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "notice_id": self.notice_id,
            "title": self.title,
            "url": self.url,
            "author": self.author,
            "created_at": self.created_at,
            "is_pinned": self.is_pinned,
            "content": self.content,
            "category": self.category,
            "summary": self.summary,
            "keyPoints": self.key_points,
            "attachments": self.attachments,
            "images": self.images,
            "view_count": self.view_count,
            "source": self.source,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None
        }

# 데이터베이스 연결 설정 (로컬 SQLite 고정)
DB_TYPE = "sqlite"
DB_PATH = os.getenv("DB_PATH", "campus_notices.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy 엔진 및 세션 생성
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """데이터베이스 테이블 초기화 및 구버전 스키마 보정"""
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_notices_table()


def _migrate_sqlite_notices_table():
    """
    기존 SQLite DB의 notices 테이블에 신규 컬럼이 없을 경우 안전하게 추가합니다.
    """
    if DB_TYPE != "sqlite":
        return

    required_columns = {
        "category": "TEXT DEFAULT '행정안내'",
        "summary": "TEXT",
        "key_points": "TEXT",
        "source": "TEXT DEFAULT 'daegu_university'",
        "scraped_at": "DATETIME",
    }

    with engine.begin() as conn:
        table_exists = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='notices'")
        ).fetchone()
        if not table_exists:
            return

        existing_columns = {
            row[1] for row in conn.execute(text("PRAGMA table_info(notices)")).fetchall()
        }

        for column_name, column_def in required_columns.items():
            if column_name not in existing_columns:
                conn.execute(text(f"ALTER TABLE notices ADD COLUMN {column_name} {column_def}"))

def get_db():
    """DB 세션 생성기"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
