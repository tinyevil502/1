import sys
sys.path.insert(0, '.')
from crawler.selenium_client import SeleniumClient
from bs4 import BeautifulSoup
import re

client = SeleniumClient(timeout=30, delay=2)
client.start()
html = client.get('https://www.17k.com/book/1741975.html')
client.close()

soup = BeautifulSoup(html, 'html.parser')

print("=== H1 elements ===")
for h1 in soup.find_all('h1'):
    print(f"  {h1.get_text(strip=True)[:80]}")

print("\n=== Elements with class containing author/bookinfo/info ===")
for elem in soup.find_all(class_=True):
    classes = ' '.join(elem.get('class', []))
    if any(k in classes.lower() for k in ['author', 'bookinfo', 'book-info', 'book-info']):
        text = elem.get_text(strip=True)[:200]
        if text:
            print(f"  CLASS={classes}")
            print(f"  TEXT={text}")
            print("  ---")

print("\n=== Links containing /author/ ===")
for a in soup.find_all('a', href=True):
    href = a.get('href', '')
    if 'author' in href.lower():
        print(f"  href={href} text={a.get_text(strip=True)}")

print("\n=== Meta Description ===")
for meta in soup.find_all('meta'):
    name = meta.get('name', '')
    content = meta.get('content', '')
    if name and 'escription' in name:
        print(f"  {content[:200]}")

print("\n=== Spans with word count ===")
for span in soup.find_all('span'):
    txt = span.get_text(strip=True)
    if txt and ('字' in txt or '万' in txt) and any(c.isdigit() for c in txt):
        print(f"  {txt}")

print("\n=== Divs with class 'intro' or 'bookintro' ===")
for div in soup.find_all('div', class_=True):
    classes = ' '.join(div.get('class', []))
    if 'intro' in classes.lower():
        text = div.get_text(strip=True)[:200]
        print(f"  CLASS={classes} TEXT={text}")

print("\n=== All divs with class containing 'book' ===")
for div in soup.find_all('div', class_=True):
    classes = ' '.join(div.get('class', []))
    if 'book' in classes.lower():
        text = div.get_text(strip=True)[:100]
        if text:
            print(f"  CLASS={classes} TEXT={text}")
