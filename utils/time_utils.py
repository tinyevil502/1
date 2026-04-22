from datetime import datetime, timedelta
import re


def parse_datetime(text):
    if not text:
        return None

    text = str(text).strip()
    patterns = [
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
        (r'(\d{4})/(\d{1,2})/(\d{1,2})', '%Y/%m/%d'),
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '%Y年%m月%d日'),
        (r'(\d{1,2})-(\d{1,2})', '%m-%d'),
    ]

    for pattern, fmt in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                if '%Y' in fmt:
                    return datetime.strptime(text[:10], fmt).strftime('%Y-%m-%d')
                else:
                    year = datetime.now().year
                    return datetime.strptime(f"{year}-{text}", '%Y-%m-%d').strftime('%Y-%m-%d')
            except:
                pass

    return text


def format_datetime(dt, fmt='%Y-%m-%d %H:%M:%S'):
    if not dt:
        return ''
    if isinstance(dt, str):
        return dt
    try:
        return dt.strftime(fmt)
    except:
        return ''


def get_current_date():
    return datetime.now().strftime('%Y-%m-%d')


def get_current_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_date_range(days=30):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')