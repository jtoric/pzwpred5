import markdown2
import bleach

# Markdown konfiguracija
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'hr'
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'code': ['class']
}

def markdown_to_html(text):
    """Pretvara Markdown u sanitizirani HTML"""
    if not text:
        return ""
    # Pretvori Markdown u HTML
    html = markdown2.markdown(text, extras=['fenced-code-blocks', 'tables', 'break-on-newline'])
    # Sanitiziraj HTML da spriječiš XSS
    clean_html = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    return clean_html

def get_pagination_info(page, per_page, total):
    """Izračunava paginacijske podatke"""
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page < total_pages else None
    }

def get_pagination_range(current_page, total_pages, delta=2):
    """Generira raspon stranica za prikaz u paginaciji"""
    start = max(1, current_page - delta)
    end = min(total_pages, current_page + delta)
    
    # Dodaj prvu i zadnju stranicu ako nisu u rasponu
    pages = []
    if start > 1:
        pages.append(1)
        if start > 2:
            pages.append('...')
    
    pages.extend(range(start, end + 1))
    
    if end < total_pages:
        if end < total_pages - 1:
            pages.append('...')
        pages.append(total_pages)
    
    return pages

