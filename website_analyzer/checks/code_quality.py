import re
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def analyze_code_quality(soup):
    """Analyze code quality and maintainability"""
    score = 100
    checks = {}
    recommendations = []
    
    # Semantic HTML5 tags
    semantic_tags = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']
    found_semantic = [tag for tag in semantic_tags if soup.find(tag)]
    checks['semantic_html'] = len(found_semantic)
    
    if len(found_semantic) < 3:
        score -= 15
        recommendations.append({
            'title': 'Use Semantic HTML',
            'description': 'Replace generic <div> tags with semantic HTML5 elements (header, nav, main, etc.).'
        })
    
    # Inline styles
    inline_styles = soup.find_all(style=True)
    checks['inline_styles'] = len(inline_styles)
    
    if len(inline_styles) > 20:
        score -= 15
        recommendations.append({
            'title': 'Remove Inline Styles',
            'description': f'Found {len(inline_styles)} inline styles. Move to external CSS for maintainability.'
        })
    elif len(inline_styles) > 10:
        score -= 8
    
    # Inline scripts
    inline_scripts = soup.find_all('script', src=False)
    checks['inline_scripts'] = len(inline_scripts)
    
    if len(inline_scripts) > 5:
        score -= 10
        recommendations.append({
            'title': 'Externalize JavaScript',
            'description': 'Move inline scripts to external files for better caching and maintenance.'
        })
    
    # Deprecated HTML tags
    deprecated = soup.find_all(['center', 'font', 'marquee', 'blink', 'big', 'strike'])
    checks['deprecated_tags'] = len(deprecated)
    
    if len(deprecated) > 0:
        score -= 20
        recommendations.append({
            'title': 'Remove Deprecated Tags',
            'description': f'Found {len(deprecated)} deprecated HTML tags. Update to modern HTML5.'
        })
    
    # CSS and JS file count
    css_files = soup.find_all('link', rel='stylesheet')
    js_files = soup.find_all('script', src=True)
    checks['css_files'] = len(css_files)
    checks['js_files'] = len(js_files)
    
    if len(css_files) > 10:
        score -= 5
        recommendations.append({
            'title': 'Combine CSS Files',
            'description': f'{len(css_files)} CSS files detected. Combine to reduce HTTP requests.'
        })
    
    return {
        'score': max(0, score),
        'status': self.get_status(score),
        'checks': checks,
        'recommendations': recommendations[:5]
    }

# ========== CATEGORY 8: ANALYTICS & TRACKING ==========
