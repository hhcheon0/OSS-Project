import re
from bs4 import BeautifulSoup

def clean_html(html_content: str) -> str:
    """
    HTML 콘텐츠에서 태그와 스타일, 스크립트를 제거하고 텍스트만 정제합니다.
    AI 요약기에 입력하기 좋은 깔끔한 구조로 텍스트를 정규화(Normalize)합니다.
    """
    if not html_content:
        return ""

    # BeautifulSoup 파싱
    soup = BeautifulSoup(html_content, 'html.parser')

    # 불필요한 태그 제거 (스크립트, 스타일, 주석 등)
    for element in soup(["script", "style", "noscript", "iframe", "head", "meta"]):
        element.decompose()

    # 인라인 스타일 속성 제거
    for tag in soup.find_all(True):
        if 'style' in tag.attrs:
            del tag['style']
        if 'class' in tag.attrs:
            del tag['class']
        # event listener 관련 속성 제거
        for attr in list(tag.attrs.keys()):
            if attr.startswith('on'):
                del tag[attr]

    # 텍스트 추출
    text = soup.get_text(separator='\n')

    # HTML 엔티티 치환 및 정제
    text = text.replace('\xa0', ' ')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

    # 줄바꿈 정규화
    # 3개 이상의 연속된 줄바꿈을 2개로 축소
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 각 행의 좌우 공백 제거
    lines = [line.strip() for line in text.split('\n')]
    
    # 빈 행이 연속해서 나오는 현상 방지하면서 재조합
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        if line:
            cleaned_lines.append(line)
            prev_empty = False
        elif not prev_empty:
            cleaned_lines.append('')
            prev_empty = True

    return '\n'.join(cleaned_lines).strip()
