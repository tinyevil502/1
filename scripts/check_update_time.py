import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawler.selenium_client import SeleniumClient
from bs4 import BeautifulSoup
import re

client = SeleniumClient(timeout=30, delay=2)
client.start()
html = client.get('https://www.17k.com/book/1741975.html')
client.close()

soup = BeautifulSoup(html, 'html.parser')

# Check all divs with class 'author'
print("=== All div.author elements ===")
author_divs = soup.find_all('div', class_='author')
print(f"Found {len(author_divs)} author divs")
for i, div in enumerate(author_divs):
    text = div.get_text(strip=True)
    print(f"  [{i}] {text[:100]}")
    date_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', text)
    if date_match:
        print(f"      DATE FOUND: {date_match.group(1)}")

# Also check the BookInfo div for update time
print("\n=== BookInfo dt elements ===")
book_info = soup.find('div', class_='BookInfo')
if book_info:
    for dt in book_info.find_all('dt'):
        print(f"  DT: {dt.get_text(strip=True)[:100]}")
    for em in book_info.find_all('em'):
        print(f"  EM: {em.get_text(strip=True)[:100]}")
    for span in book_info.find_all('span'):
        txt = span.get_text(strip=True)
        if txt:
            print(f"  SPAN: {txt[:100]}")
