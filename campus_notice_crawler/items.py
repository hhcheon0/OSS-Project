import scrapy

class NoticeItem(scrapy.Item):
    notice_id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    created_at = scrapy.Field()
    is_pinned = scrapy.Field()
    content = scrapy.Field()
    attachments = scrapy.Field()
    images = scrapy.Field()
    view_count = scrapy.Field()
    source = scrapy.Field()
