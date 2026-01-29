import re
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def analyze_analytics(soup):
    """Analyze analytics and tracking implementation"""
    score = 100
    checks = {}
    recommendations = []
    
    html_content = str(soup)
    
    # Google Analytics (UA)
    checks['google_analytics_ua'] = 'google-analytics.com/analytics.js' in html_content or 'UA-' in html_content
    
    # Google Analytics 4 (GA4)
    checks['google_analytics_ga4'] = 'googletagmanager.com/gtag/js' in html_content or 'G-' in html_content
    
    # Google Tag Manager
    checks['google_tag_manager'] = 'googletagmanager.com/gtm.js' in html_content or 'GTM-' in html_content
    
    # Facebook Pixel
    checks['facebook_pixel'] = 'connect.facebook.net' in html_content or 'fbq(' in html_content
    
    # Other analytics
    checks['hotjar'] = 'hotjar.com' in html_content
    checks['mixpanel'] = 'mixpanel.com' in html_content
    
    # Check if any analytics is present
    has_analytics = any([
        checks['google_analytics_ua'],
        checks['google_analytics_ga4'],
        checks['google_tag_manager']
    ])
    
    if not has_analytics:
        score -= 30
        recommendations.append({
            'title': 'Install Analytics',
            'description': 'No analytics detected. Install Google Analytics 4 to track visitor behavior.'
        })
    
    # Check for duplicate tracking
    ga_count = html_content.count('google-analytics.com')
    if ga_count > 2:
        score -= 10
        recommendations.append({
            'title': 'Remove Duplicate Tracking',
            'description': 'Multiple analytics scripts detected. This can cause inaccurate data.'
        })
    
    # Recommend GTM if not using it
    if has_analytics and not checks['google_tag_manager']:
        recommendations.append({
            'title': 'Consider Google Tag Manager',
            'description': 'GTM simplifies managing multiple tracking scripts and tags.'
        })
    
    return {
        'score': max(0, score),
        'status': self.get_status(score),
        'checks': checks,
        'recommendations': recommendations[:5]
    }

# ========== CATEGORY 9: SERVER & INFRASTRUCTURE ==========
