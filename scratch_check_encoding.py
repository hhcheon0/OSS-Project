import requests

url = "https://www.daegu.ac.kr/article/DG159/list"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

response = requests.get(url, headers=headers)
print("Content-Type Header:", response.headers.get("Content-Type"))
print("Apparent Encoding:", response.apparent_encoding)
print("Encoding:", response.encoding)

# Let's print some text in UTF-8
text = response.text
if "공지" in text:
    print("Found '공지' in response.text with default encoding!")
else:
    print("'공지' not found in response.text with default encoding")

# Try parsing first few characters and encoding/decoding to cp949/utf-8
try:
    print(text[:1000])
except Exception as e:
    print("Error printing:", e)
