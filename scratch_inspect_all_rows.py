import requests
from scrapy.selector import Selector

url = "https://www.daegu.ac.kr/article/DG159/list"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
html = response.text

selector = Selector(text=html)
table = selector.css('table')
rows = table.css('tr')

print(f"Total rows found: {len(rows)}")
for idx, row in enumerate(rows[1:], 1):
    cols = row.css('td')
    if len(cols) < 3:
        print(f"Row {idx}: less than 3 columns")
        continue
    title_link = cols[2].css('a')
    hrefs = [a.attrib.get('href', '') for a in title_link]
    onclicks = [a.attrib.get('onclick', '') for a in title_link]
    text = "".join(title_link.css('::text').getall()).strip()
    print(f"Row {idx}: title={text[:40]}... | hrefs={hrefs} | onclicks={onclicks}")
