import sys
sys.path.insert(0, '.')
from crawler.selenium_client import SeleniumClient
from bs4 import BeautifulSoup

client = SeleniumClient(timeout=30, delay=2)
client.start()
html = client.get('https://www.17k.com/book/1741975.html')
client.close()

soup = BeautifulSoup(html, 'html.parser')

# Find BookInfo div and print its full HTML structure
book_info = soup.find('div', class_='BookInfo')
if book_info:
    print("=== BookInfo HTML ===")
    print(book_info.prettify()[:3000])

print("\n=== AuthorInfo HTML ===")
author_info = soup.find('div', class_='AuthorInfo')
if author_info:
    print(author_info.prettify()[:1000])

print("\n=== All anchor links in BookInfo ===")
if book_info:
    for a in book_info.find_all('a', href=True):
        print(f"  href={a.get('href')} text={a.get_text(strip=True)}")

print("\n=== All spans in BookInfo ===")
if book_info:
    for span in book_info.find_all('span'):
        txt = span.get_text(strip=True)
        if txt:
            print(f"  class={span.get('class')} text={txt[:100]}")

print("\n=== Looking for category/status links ===")
for a in soup.find_all('a', href=True):
    href = a.get('href', '')
    text = a.get_text(strip=True)
    if any(k in href for k in ['/list/', '/all/', 'category', 'type', 'fenlei']):
        print(f"  href={href} text={text}")
    if text in ['玄幻', '都市', '仙侠', '历史', '军事', '游戏', '科幻', '悬疑', '轻小说', '连载中', '已完结']:
        print(f"  MATCH: text={text} href={href}")
