import scrapy
import re
from urllib.parse import urljoin, quote
from campus_notice_crawler.items import NoticeItem

class DaeguNoticeSpider(scrapy.Spider):
    name = "daegu_notice"
    allowed_domains = ["daegu.ac.kr"]
    start_urls = ["https://www.daegu.ac.kr/article/DG159/list"]

    # 파싱 대상 페이지 제한 (과도한 부하 방지 및 속도 향상, 1~3페이지 수집 기본값)
    max_pages = 3
    current_page = 1

    def parse(self, response):
        self.logger.info(f"Parsing notice list page: {response.url}")

        # 게시판 테이블 검색
        table = response.css('table')
        if not table:
            self.logger.warning("No table found on list page!")
            return

        rows = table.css('tr')
        # 첫 번째 행은 헤더이므로 제외
        for row in rows[1:]:
            # 각 td 컬럼 추출
            cols = row.css('td')
            if len(cols) < 5:
                continue

            # 1. 상단 고정 여부 (첫 번째 td에 텍스트가 없거나 이미지 아이콘이 있는 경우 또는 '공지'가 명시된 경우)
            num_text = cols[0].css('::text').get()
            num_text = num_text.strip() if num_text else ""
            is_pinned = False
            # 숫자가 아닌 문자(예: '공지' 아이콘 등)이거나 비어있으면 상단 고정으로 판단
            if not num_text.isdigit():
                is_pinned = True

            # 2. 제목 및 상세 URL 추출 (보통 세 번째 td 내에 a 링크 존재)
            title_link = cols[2].css('a')
            if not title_link:
                continue
                
            title = title_link.css('::text').get()
            if title:
                title = title.strip()
            else:
                title = ""

            href = title_link.attrib.get('href', '')
            onclick = title_link.attrib.get('onclick', '')
            
            notice_id = None
            if href and 'detail/' in href:
                match_id = re.search(r'detail/(\d+)', href)
                if match_id:
                    notice_id = match_id.group(1)
            
            if not notice_id and onclick:
                match_onclick = re.search(r'goDetail\s*\(\s*\'?(\d+)\'?\s*\)', onclick)
                if match_onclick:
                    notice_id = match_onclick.group(1)
                    href = f"/article/DG159/detail/{notice_id}"

            if not notice_id:
                match_num = re.search(r'(\d+)', href or '')
                if match_num:
                    notice_id = match_num.group(1)
                elif href and href != "#none" and not href.startswith("javascript:"):
                    notice_id = str(hash(urljoin(response.url, href)))
                else:
                    continue

            # 절대 경로로 변환
            detail_url = urljoin(response.url, href)

            # 3. 작성자 (네 번째 td)
            author = cols[3].css('::text').get()
            author = author.strip() if author else ""

            # 4. 작성일 (다섯 번째 td)
            created_at = cols[4].css('::text').get()
            created_at = created_at.strip() if created_at else ""

            # 5. 조회수 (여섯 번째 td, 존재 시)
            view_count = 0
            if len(cols) >= 6:
                view_text = cols[5].css('::text').get()
                if view_text:
                    view_text = view_text.strip()
                    if view_text.isdigit():
                        view_count = int(view_text)

            # Item 생성 및 데이터 매핑
            item = NoticeItem()
            item['notice_id'] = notice_id
            item['title'] = title
            item['url'] = detail_url
            item['author'] = author
            item['created_at'] = created_at
            item['is_pinned'] = is_pinned
            item['view_count'] = view_count
            item['source'] = 'daegu_university'

            # 상세 페이지 크롤링 요청 발송
            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                meta={'item': item},
                dont_filter=True  # 동일 공지가 재수집될 수 있으므로 Pipeline에서 중복 제거 처리
            )

        # 페이지네이션 처리
        if self.current_page < self.max_pages:
            self.current_page += 1
            next_url = f"https://www.daegu.ac.kr/article/DG159/list?pageIndex={self.current_page}"
            yield scrapy.Request(url=next_url, callback=self.parse)

    def parse_detail(self, response):
        item = response.meta['item']
        self.logger.info(f"Parsing notice detail page: {response.url}")

        table = response.css('table.board_tbl_view')
        if not table:
            self.logger.warning(f"Detail table board_tbl_view not found for {response.url}")
            item['content'] = ""
            item['attachments'] = []
            item['images'] = []
            yield item
            return

        rows = table.css('tr')
        
        content_html = ""
        attachments = []
        images = []

        for row in rows:
            th_text = row.css('th::text').get()
            th_text = th_text.strip() if th_text else ""
            
            td = row.css('td')
            if not td:
                continue

            td_html = td.get()
            td_text = td.css('::text').getall()
            td_text_combined = " ".join(td_text).strip()

            # 1. 첨부파일 행 식별 (th나 td 텍스트에 '첨부파일'이 포함되는 경우)
            if "첨부파일" in th_text or "첨부파일" in td_text_combined:
                # td 내의 모든 a 링크 탐색
                links = td.css('a')
                for link in links:
                    href = link.attrib.get('href', '')
                    # javascript:downGO('파일명','경로','시스템파일명') 패턴 추출
                    match = re.search(r"downGO\s*\(\s*'(.*?)'\s*,\s*'(.*?)'\s*,\s*'(.*?)'\s*\)", href)
                    if match:
                        file_nm = match.group(1)
                        file_path = match.group(2)
                        file_sys_nm = match.group(3)
                        
                        # 실제 다이렉트 다운로드 주소 조립
                        # /cmmn/fileDown.do?filename={파일명}&filepath={경로}&filerealname={실제파일명}
                        download_url = f"https://www.daegu.ac.kr/cmmn/fileDown.do?filename={quote(file_nm)}&filepath={file_path}&filerealname={file_sys_nm}"
                        attachments.append({
                            "name": file_nm,
                            "url": download_url
                        })
                    elif href and not href.startswith('javascript:'):
                        # javascript가 아닌 일반 링크가 첨부파일인 경우 대응
                        file_url = urljoin(response.url, href)
                        file_name = link.css('::text').get()
                        file_name = file_name.strip() if file_name else "첨부파일"
                        attachments.append({
                            "name": file_name,
                            "url": file_url
                        })

            # 2. 공유/SNS 행 식별 (건너뜀)
            elif "URL복사" in td_text_combined or "페이스북" in td_text_combined or "트위터" in td_text_combined:
                continue

            # 3. 본문 행 식별 (작성자 등 헤더 행 제외하고 텍스트가 매우 풍부한 4번째 행 근처 영역)
            elif not th_text and len(td_text_combined) > 0:
                # 가장 긴 HTML 텍스트를 가진 td를 본문으로 임시 매핑
                if len(td_html) > len(content_html):
                    content_html = td_html

                # 본문 내 이미지 추출
                imgs = td.css('img')
                for img in imgs:
                    src = img.attrib.get('src', '')
                    if src:
                        img_url = urljoin(response.url, src)
                        if img_url not in images:
                            images.append(img_url)

        item['content'] = content_html
        item['attachments'] = attachments
        item['images'] = images

        yield item
