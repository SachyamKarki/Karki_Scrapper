import re
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def analyze_mobile_responsiveness(soup, response):
    """Analyze mobile responsiveness"""
    score = 100
    checks = {}
    recommendations = []
    
    # Viewport meta tag
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport and viewport.get('content'):
        checks['viewport_tag'] = True
        content = viewport.get('content', '')
        if 'width=device-width' in content:
            checks['viewport_width'] = True
        else:
            checks['viewport_width'] = False
            score -= 10
            recommendations.append({
                'title': 'Fix Viewport Configuration',
                'description': 'Viewport should include width=device-width for proper mobile rendering.'
            })
    else:
        checks['viewport_tag'] = False
        checks['viewport_width'] = False
        score -= 25
        recommendations.append({
            'title': 'Add Viewport Meta Tag',
            'description': 'Critical for mobile responsiveness. Add: <meta name="viewport" content="width=device-width, initial-scale=1">'
        })
    
    # Check for responsive CSS (media queries)
    style_tags = soup.find_all('style')
    has_media_queries = False
    for style in style_tags:
        if '@media' in str(style.string):
            has_media_queries = True
            break
    
    checks['media_queries'] = has_media_queries
    if not has_media_queries:
        score -= 15
        recommendations.append({
            'title': 'Add Responsive CSS',
            'description': 'No media queries detected. Implement responsive design with CSS media queries.'
        })
    
    # Font size check (basic)
    body = soup.find('body')
    if body:
        style = body.get('style', '')
        if 'font-size' in style and 'px' in style:
            # Check if font size is too small
            match = re.search(r'font-size:\s*(\d+)px', style)
            if match and int(match.group(1)) < 14:
                score -= 5
                recommendations.append({
                    'title': 'Increase Font Size',
                    'description': 'Font size appears small for mobile. Use at least 14px for body text.'
                })
    
    # Touch-friendly elements (buttons/links)
    buttons = soup.find_all(['button', 'a'])
    checks['interactive_elements'] = len(buttons)
    
    return {
        'score': max(0, score),
        'status': self.get_status(score),
        'checks': checks,
        'recommendations': recommendations[:5]
    }

# ========== CATEGORY 3: TECHNICAL SEO ==========
