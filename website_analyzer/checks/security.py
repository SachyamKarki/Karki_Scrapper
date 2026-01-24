import re
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def analyze_security(url, response, soup):
    """Analyze security measures"""
    score = 100
    checks = {}
    recommendations = []
    
    # HTTPS
    parsed_url = urlparse(url)
    checks['https'] = parsed_url.scheme == 'https'
    
    if not checks['https']:
        score -= 30
        recommendations.append({
            'title': 'Enable HTTPS',
            'description': 'Critical: HTTPS is essential for security and SEO. Install an SSL certificate.'
        })
    
    # Security headers
    headers = response.headers
    
    # Content-Security-Policy
    checks['csp'] = 'Content-Security-Policy' in headers
    if not checks['csp']:
        score -= 10
        recommendations.append({
            'title': 'Add Content Security Policy',
            'description': 'CSP headers protect against XSS and injection attacks.'
        })
    
    # Strict-Transport-Security (HSTS)
    checks['hsts'] = 'Strict-Transport-Security' in headers
    if not checks['hsts'] and checks['https']:
        score -= 10
        recommendations.append({
            'title': 'Enable HSTS',
            'description': 'HSTS forces browsers to always use HTTPS connections.'
        })
    
    # X-Frame-Options
    checks['x_frame_options'] = 'X-Frame-Options' in headers
    if not checks['x_frame_options']:
        score -= 8
        recommendations.append({
            'title': 'Add X-Frame-Options',
            'description': 'Protects against clickjacking attacks.'
        })
    
    # X-Content-Type-Options
    checks['x_content_type'] = 'X-Content-Type-Options' in headers
    if not checks['x_content_type']:
        score -= 5
    
    # Referrer-Policy
    checks['referrer_policy'] = 'Referrer-Policy' in headers
    
    # Mixed content (HTTP resources on HTTPS page)
    if checks['https']:
        http_resources = []
        for tag in soup.find_all(['img', 'script', 'link'], src=True):
            src = tag.get('src', '')
            if src.startswith('http://'):
                http_resources.append(src)
        
        checks['mixed_content'] = len(http_resources) > 0
        if checks['mixed_content']:
            score -= 15
            recommendations.append({
                'title': 'Fix Mixed Content',
                'description': f'Found {len(http_resources)} HTTP resources on HTTPS page. Update to HTTPS.'
            })
    
    return {
        'score': max(0, score),
        'status': self.get_status(score),
        'checks': checks,
        'recommendations': recommendations[:5]
    }

# ========== CATEGORY 6: ACCESSIBILITY ==========
