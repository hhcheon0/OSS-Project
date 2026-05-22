BOT_NAME = "campus_notice_crawler"

SPIDER_MODULES = ["campus_notice_crawler.spiders"]
NEWSPIDER_MODULE = "campus_notice_crawler.spiders"

# Obey robots.txt rules (학사 공지 게시판의 크롤러 접근 허용성을 고려하여 실무적으로 False 설정하되 딜레이 부여)
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 4

# Configure a delay for requests for the same website (default: 0)
# IP 차단 방지 및 서버 부하 경감을 위해 1초 대기 적용
DOWNLOAD_DELAY = 1.0

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Configure item pipelines
# 순서대로: HTML 청소 -> 중복 필터링 -> 데이터베이스 영구 저장 -> AI 요약 서버로 Webhook 전송
ITEM_PIPELINES = {
    "campus_notice_crawler.pipelines.HtmlCleaningPipeline": 100,
    "campus_notice_crawler.pipelines.DuplicateFilterPipeline": 200,
    "campus_notice_crawler.pipelines.DatabasePipeline": 300,
    "campus_notice_crawler.pipelines.AISummaryWebhookPipeline": 400,
}

# Set settings to avoid deprecation warnings
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
