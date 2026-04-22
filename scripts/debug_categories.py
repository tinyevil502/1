import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.selenium_client import SeleniumClient
from crawler.seventeenk_spider import SeventeenKSpider

categories = {
    'xuanhuan': '玄幻',
    'dushi': '都市',
    'xianxia': '仙侠',
    'lishi': '历史',
    'junshi': '军事',
    'youxi': '游戏',
    'kehuan': '科幻',
    'xuanyi': '悬疑',
    'qingxiaoshuo': '轻小说',
}

client = SeleniumClient(timeout=60, delay=3)
client.start()
spider = SeventeenKSpider(client)

for slug, name in categories.items():
    urls = spider.get_list_urls(category=slug, pages=1)
    url = urls[0]
    print(f'\n=== {name} ({slug}) ===')
    print(f'URL: {url}')
    try:
        html = spider.fetch_list_page(url)
        soup_len = len(html) if html else 0
        print(f'HTML length: {soup_len}')

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        links = soup.find_all('a', href=True)
        book_links = []
        for a in links:
            href = a.get('href', '')
            if '/book/' in href:
                title = a.get_text(strip=True)
                if title and len(title) >= 2:
                    if title not in ['登录', '注册', '首页', '排行榜', '分类', '写书', '充值', '书架', '消息']:
                        book_links.append((href, title))

        print(f'Found {len(book_links)} book links')
        if book_links:
            for href, title in book_links[:3]:
                print(f'  - {title}: {href}')
        else:
            print('  No book links found!')
            print('  Checking page title:', soup.find('title').get_text() if soup.find('title') else 'No title')

    except Exception as e:
        print(f'Error: {e}')

client.close()
