import re
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def analyze_infrastructure(response, load_time, url):
    """Analyze server and infrastructure"""
    score = 100
    metrics = {}
    recommendations = []
    
    headers = response.headers
    
    # Server response time (same as load time for now)
    metrics['response_time'] = round(load_time, 2)
    
    if load_time > 3:
        score -= 20
        recommendations.append({
            'title': 'Improve Server Response Time',
            'description': 'Server response is slow. Consider upgrading hosting or using a CDN.'
        })
    elif load_time > 1.5:
        score -= 10
    
    # Compression
    encoding = headers.get('Content-Encoding', '')
    metrics['compression'] = encoding
    
    if encoding in ['gzip', 'br', 'deflate']:
        metrics['compression_enabled'] = True
    else:
        metrics['compression_enabled'] = False
        score -= 15
        recommendations.append({
            'title': 'Enable Compression',
            'description': 'Enable GZIP or Brotli compression to reduce transfer sizes by 70%+.'
        })
    
    # Server header
    server = headers.get('Server', 'Unknown')
    metrics['server'] = server
    
    # Caching headers
    cache_control = headers.get('Cache-Control', '')
    metrics['cache_control'] = bool(cache_control)
    
    if not cache_control:
        score -= 10
        recommendations.append({
            'title': 'Add Caching Headers',
            'description': 'Implement Cache-Control headers to improve repeat visit performance.'
        })
    
    # Check for CDN (basic detection)
    cdn_indicators = ['cloudflare', 'cloudfront', 'fastly', 'akamai', 'cdn']
    uses_cdn = any(indicator in server.lower() for indicator in cdn_indicators)
    metrics['cdn_detected'] = uses_cdn
    
    # Redirect chain check
    if len(response.history) > 1:
        score -= 10
        recommendations.append({
            'title': 'Reduce Redirect Chain',
            'description': f'Found {len(response.history)} redirects. Each redirect adds latency.'
        })
    
    metrics['redirects'] = len(response.history)
    
    return {
        'score': max(0, score),
        'status': self.get_status(score),
        'metrics': metrics,
        'recommendations': recommendations[:5]
    }

# ========== HELPER METHODS ==========
