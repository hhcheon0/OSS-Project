import os
import datetime
from sqlalchemy import create_engine, Column, String, Integer, Text, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

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
    embedding = Column(JSON, nullable=True)     # [float, float, ...] 형태의 텍스트 임베딩 벡터
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
            "embedding": self.embedding,
            "attachments": self.attachments,
            "images": self.images,
            "view_count": self.view_count,
            "source": self.source,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None
        }

# 데이터베이스 연결 설정
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()

if DB_TYPE == "postgresql":
    # Supabase 또는 PostgreSQL URL
    DATABASE_URL = os.getenv("DB_URL")
    if not DATABASE_URL:
        # URL이 없을 경우 폴백
        DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
else:
    # 로컬 SQLite
    DB_PATH = os.getenv("DB_PATH", "campus_notices.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy 엔진 및 세션 생성
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """데이터베이스 테이블 초기화"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """DB 세션 생성기"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
