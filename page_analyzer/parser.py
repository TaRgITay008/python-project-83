"""Parser utilities for extracting SEO tags from HTML."""

from bs4 import BeautifulSoup


def parse_seo_tags(html_content):
    """Parse HTML and extract h1, title, and meta description."""
    soup = BeautifulSoup(html_content, 'html.parser')

    h1_tag = soup.find('h1')
    h1 = h1_tag.get_text(strip=True) if h1_tag else None

    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else None

    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description = meta_desc.get('content', '').strip() if meta_desc else None

    return h1, title, description


def truncate(text, length=200):
    """Truncate text to specified length with ellipsis."""
    if not text:
        return ''
    if len(text) <= length:
        return text
    return text[:length] + '...'
