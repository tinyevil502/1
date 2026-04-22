import requests
from bs4 import BeautifulSoup


def discover_categories(base_url: str = 'https://www.17k.com/all/'):
    """Dynamically discover categories from 17K All page.
    This is a light-weight discovery that returns a list of (name, url) pairs.
    """
    try:
        resp = requests.get(base_url, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        # heuristic: links that resemble category pages
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if not href or not text:
                continue
            if '/all/book/' in href:
                # skip deep book links
                continue
            if href.startswith('//'):
                href = 'https:' + href
            if href.startswith('/'):
                href = 'https://www.17k.com' + href
            if text in ('玄幻', '历史', '仙侠', '都市', '军事', '游戏', '科幻', '悬疑', '轻小说'):
                results.append({'name': text, 'url': href})
        # de-duplicate while preserving order
        seen = set()
        dedup = []
        for it in results:
            key = (it['name'], it['url'])
            if key in seen:
                continue
            seen.add(key)
            dedup.append(it)
        return dedup
    except Exception:
        return []
