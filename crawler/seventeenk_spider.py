from .base_spider import BaseSpider
from bs4 import BeautifulSoup
import re
import logging
import os

logger = logging.getLogger(__name__)

VALID_GENRES = {'玄幻', '奇幻', '仙侠', '都市', '历史', '军事', '游戏', '体育', '科幻', '言情', '穿越', '架空', '悬疑', '武侠', '轻小说', '同人'}

CATEGORY_MAP = {
    '玄幻': '玄幻', '奇幻': '奇幻', '仙侠': '仙侠', '都市': '都市',
    '历史': '历史', '军事': '军事', '游戏': '游戏', '体育': '体育',
    '科幻': '科幻', '言情': '言情', '穿越': '穿越', '架空': '架空',
    '悬疑': '悬疑', '武侠': '武侠', '轻小说': '轻小说', '同人': '同人',
}


class SeventeenKSpider(BaseSpider):
    BASE_URL = 'https://www.17k.com'

    CATEGORY_URLS = {
        'xuanhuan': 'https://www.17k.com/all/book/1_0_0_0_0_2_0_0_1.html',
        'dushi': 'https://www.17k.com/all/book/2_0_0_0_0_2_0_0_1.html',
        'xianxia': 'https://www.17k.com/all/book/3_0_0_0_0_2_0_0_1.html',
        'lishi': 'https://www.17k.com/all/book/5_0_0_0_0_2_0_0_1.html',
        'junshi': 'https://www.17k.com/all/book/6_0_0_0_0_2_0_0_1.html',
        'youxi': 'https://www.17k.com/all/book/7_0_0_0_0_2_0_0_1.html',
        'kehuan': 'https://www.17k.com/all/book/8_0_0_0_0_2_0_0_1.html',
        'xuanyi': 'https://www.17k.com/all/book/9_0_0_0_0_2_0_0_1.html',
        'qingxiaoshuo': 'https://www.17k.com/all/book/10_0_0_0_0_2_0_0_1.html',
    }

    CATEGORY_PAGE_IDS = {
        'xuanhuan': '1',
        'dushi': '2',
        'xianxia': '3',
        'lishi': '5',
        'junshi': '6',
        'youxi': '7',
        'kehuan': '8',
        'xuanyi': '9',
        'qingxiaoshuo': '10',
    }

    CATEGORY_NAMES = {
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

    def get_list_urls(self, category='xuanhuan', pages=5):
        urls = []
        cat_id = self.CATEGORY_PAGE_IDS.get(category, '1')
        for page in range(1, pages + 1):
            urls.append(f'https://www.17k.com/all/book/{cat_id}_0_0_0_0_2_0_0_{page}.html')
        logger.info(f"Generated {len(urls)} list URLs for category={category}")
        return urls

    def get_category_name(self, category):
        return self.CATEGORY_NAMES.get(category, '玄幻')

    def fetch_list_page(self, url):
        logger.info(f"Fetching list page: {url}")
        html = self.client.get(url)

        debug_path = os.path.join(os.path.dirname(__file__), 'html_debug', 'list_page.html')
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return html

    def parse_list_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        items = []
        seen = set()

        # Target book title links inside strong tags within search-list container
        search_list = soup.find('div', class_='search-list')
        if search_list:
            for a in search_list.select('strong a[href]'):
                href = a.get('href', '').strip()

                if not href.startswith('//www.17k.com/book/') and not href.startswith('/book/'):
                    continue

                if '/all/book/' in href:
                    continue

                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    href = self.BASE_URL + href

                if href in seen:
                    continue
                seen.add(href)

                title = a.get_text(strip=True)
                if not title or len(title) < 2:
                    continue

                if title.startswith('[') and title.endswith(']'):
                    continue

                items.append({
                    'novel_name_raw': title,
                    'author_name_raw': None,
                    'category_name_raw': None,
                    'status_raw': '连载中',
                    'word_count_raw': None,
                    'intro_raw': None,
                    'update_time_raw': None,
                    'source_url': href,
                    'detail_url': href,
                })

        logger.info(f"Parsed {len(items)} novels")
        return items[:100]

    def fetch_detail_page(self, url):
        if not url:
            return ''
        logger.info(f"Fetching detail: {url}")
        try:
            html = self.client.get(url)
            return html
        except Exception as e:
            logger.error(f"Fetch detail failed: {e}")
            return ''

    def parse_detail_page(self, html):
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')
        data = {
            'novel_name_raw': None,
            'author_name_raw': None,
            'category_name_raw': None,
            'status_raw': None,
            'word_count_raw': None,
            'intro_raw': None,
            'update_time_raw': None,
        }

        try:
            # 1. Title: from BookInfo h1 > a, or fallback to h1 title, or meta title
            book_info = soup.find('div', class_='BookInfo')
            if book_info:
                h1 = book_info.find('h1')
                if h1:
                    a = h1.find('a')
                    if a:
                        data['novel_name_raw'] = a.get_text(strip=True)
                    else:
                        data['novel_name_raw'] = h1.get_text(strip=True)

                # 2. Category: from div.label > a, or first category-like link
                label = book_info.find('div', class_='label')
                if label:
                    cat_a = label.find('a')
                    if cat_a:
                        cat_text = cat_a.get_text(strip=True)
                        data['category_name_raw'] = self._normalize_category(cat_text)

                # Fallback: search for any link with category text
                if not data['category_name_raw']:
                    for a in book_info.find_all('a', href=True):
                        txt = a.get_text(strip=True)
                        normalized = self._normalize_category(txt)
                        if normalized:
                            data['category_name_raw'] = normalized
                            break

                # 3. Intro: p.intro > a, or div.BookIntro, or meta description
                intro_p = book_info.find('p', class_='intro')
                if intro_p:
                    intro_a = intro_p.find('a')
                    if intro_a:
                        intro_text = intro_a.get_text(strip=True)
                        data['intro_raw'] = re.sub(r'\s+', ' ', intro_text).strip()[:500]

            # Fallback intro from meta description
            if not data['intro_raw']:
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    content = meta_desc.get('content', '')
                    if content:
                        data['intro_raw'] = content.strip()[:500]

            # 4. Author: div.AuthorInfo > a.name, or fallback to author link
            author_info = soup.find('div', class_='AuthorInfo')
            if author_info:
                author_a = author_info.find('a', class_='name')
                if author_a:
                    data['author_name_raw'] = author_a.get_text(strip=True)

            # Fallback: look for author link in page
            if not data['author_name_raw']:
                for a in soup.find_all('a', href=True):
                    href = a.get('href', '')
                    if '/author/' in href:
                        name = a.get_text(strip=True)
                        if name and len(name) > 1:
                            data['author_name_raw'] = name
                            break

            # 5. Status: look for 连载/完结 in page text
            full_text = soup.get_text()
            if '已完结' in full_text or '完本' in full_text:
                data['status_raw'] = '已完结'
            elif '连载中' in full_text:
                data['status_raw'] = '连载中'

            # 6. Word count: look for span with 万字 pattern
            for span in soup.find_all('span'):
                txt = span.get_text(strip=True)
                if txt and '万' in txt and any(c.isdigit() for c in txt):
                    match = re.search(r'(\d+\.?\d*)\s*万', txt)
                    if match:
                        num = float(match.group(1))
                        data['word_count_raw'] = int(num * 10000)
                        break

            # Fallback: check for word count in text pattern like "XXX万字"
            if not data['word_count_raw']:
                wc_match = re.search(r'(\d+\.?\d*)\s*万字', full_text)
                if wc_match:
                    num = float(wc_match.group(1))
                    data['word_count_raw'] = int(num * 10000)

            # 7. Update time: dt.tit > em, or from text pattern
            if book_info:
                dt_tit = book_info.find('dt', class_='tit')
                if dt_tit:
                    em = dt_tit.find('em')
                    if em:
                        em_text = em.get_text(strip=True)
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', em_text)
                        if date_match:
                            data['update_time_raw'] = date_match.group(1)

            # Fallback: search for date pattern in full text
            if not data['update_time_raw']:
                date_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', full_text)
                if date_match:
                    data['update_time_raw'] = date_match.group(1)

        except Exception as e:
            logger.warning(f"Detail parse error: {e}")

        return data

    def _normalize_category(self, category):
        if not category:
            return None
        for key, value in CATEGORY_MAP.items():
            if key in category:
                return value
        if category in VALID_GENRES:
            return category
        return None

    def _normalize_status(self, status):
        if not status:
            return '未知'
        status = str(status).lower()
        if any(kw in status for kw in ['连载', 'ing', '连载中']):
            return '连载中'
        elif any(kw in status for kw in ['完结', 'completed', '已完结']):
            return '已完结'
        return '未知'

    def _parse_word_count(self, text):
        if not text:
            return None
        match = re.search(r'[\d,]+', text.replace(',', ''))
        if match:
            try:
                return int(match.group().replace(',', ''))
            except:
                pass
        return None
