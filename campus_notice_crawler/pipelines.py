import os
import requests
from scrapy.exceptions import DropItem
from campus_notice_crawler.utils.html_cleaner import clean_html
from campus_notice_crawler.utils.db_connection import init_db, SessionLocal, Notice

class HtmlCleaningPipeline:
    """본문의 불필요한 HTML 태그를 정제하고 Normalize하는 파이프라인"""
    def process_item(self, item, spider):
        if 'content' in item:
            original_len = len(item['content'])
            item['content'] = clean_html(item['content'])
            cleaned_len = len(item['content'])
            spider.logger.info(f"HtmlCleaningPipeline: Cleaned content for '{item['title'][:20]}...' (Length: {original_len} -> {cleaned_len})")
        return item

class DuplicateFilterPipeline:
    """데이터베이스를 조회하여 이미 수집된 notice_id인 경우 DropItem 처리하는 중복 방지 파이프라인"""
    def __init__(self):
        # 파이프라인 시작 시 DB 초기화 실행 (테이블 자동 생성)
        init_db()
        self.db = SessionLocal()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        notice_id = item.get('notice_id')
        if not notice_id:
            return item

        # DB에 존재하는지 확인
        exists = self.db.query(Notice).filter(Notice.notice_id == notice_id).first()
        if exists:
            spider.logger.info(f"DuplicateFilterPipeline: Dropped duplicate notice_id: {notice_id}")
            raise DropItem(f"Duplicate item found: {notice_id}")
            
        return item

from campus_notice_crawler.utils.ai_helper import analyze_notice_with_ai

class DatabasePipeline:
    """수집된 학사공지 데이터를 SQLite 또는 PostgreSQL(Supabase)에 영구 저장하는 파이프라인"""
    def __init__(self):
        self.db = SessionLocal()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        notice_id = item.get('notice_id')
        
        # AI 분석 가동 (카테고리, 3줄 요약, 핵심태그 생성)
        ai_res = analyze_notice_with_ai(item.get('title', ''), item.get('content', ''))
        
        # SQLAlchemy Notice 객체 생성
        notice_db = Notice(
            notice_id=notice_id,
            title=item.get('title'),
            url=item.get('url'),
            author=item.get('author'),
            created_at=item.get('created_at'),
            is_pinned=item.get('is_pinned', False),
            content=item.get('content'),
            category=ai_res.get('category', '행정안내'),
            summary=ai_res.get('summary', []),
            key_points=ai_res.get('keyPoints', []),
            attachments=item.get('attachments', []),
            images=item.get('images', []),
            view_count=item.get('view_count', 0),
            source=item.get('source', 'daegu_university')
        )

        try:
            self.db.merge(notice_db) # 존재하면 덮어쓰기(Upsert), 없으면 Insert
            self.db.commit()
            spider.logger.info(f"DatabasePipeline: Successfully saved notice '{item['title'][:20]}...' (Category: {ai_res.get('category')}) to DB.")
        except Exception as e:
            self.db.rollback()
            spider.logger.error(f"DatabasePipeline: Failed to save notice {notice_id} to DB: {e}")
            
        return item

class AISummaryWebhookPipeline:
    """수집 완료된 신규 공지를 AI 요약 서버에 Webhook 전송하는 파이프라인"""
    def __init__(self):
        self.webhook_url = os.getenv("AI_SUMMARY_WEBHOOK_URL")

    def process_item(self, item, spider):
        if not self.webhook_url:
            spider.logger.info("AISummaryWebhookPipeline: AI_SUMMARY_WEBHOOK_URL is not set. Skipping Webhook.")
            return item

        # AI 요약 포맷으로 데이터 가공
        payload = {
            "title": item.get('title'),
            "content": item.get('content'),
            "summary_target": True
        }

        try:
            spider.logger.info(f"AISummaryWebhookPipeline: Sending Webhook to AI Server: {self.webhook_url}")
            # 비동기 성격을 감안하되 크롤링 흐름에 지장을 주지 않기 위해 타임아웃 3초 설정
            response = requests.post(self.webhook_url, json=payload, timeout=3.0)
            if response.status_code == 200:
                spider.logger.info(f"AISummaryWebhookPipeline: Webhook sent successfully. Response: {response.text}")
            else:
                spider.logger.warning(f"AISummaryWebhookPipeline: Webhook failed with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            # AI 서버가 아직 준비되지 않은 상태일 수 있으므로 Warning 로그만 남김 (전체 수집에 지장 없도록 함)
            spider.logger.warning(f"AISummaryWebhookPipeline: AI Summary Server Webhook is unreachable: {e}")

        return item
