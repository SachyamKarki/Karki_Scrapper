import re
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def analyze_performance(response, load_time, soup, url):
    """Analyze performance metrics"""
    score = 100
    metrics = {}
    recommendations = []
    
    # Load time analysis (TTFB approximation)
    metrics['load_time'] = round(load_time, 2)
    if load_time < 1:
        metrics['load_time_status'] = 'excellent'
    elif load_time < 2:
        metrics['load_time_status'] = 'good'
        score -= 5
    elif load_time < 3:
        metrics['load_time_status'] = 'fair'
        score -= 15
        recommendations.append({
            'title': 'Improve Server Response Time',
            'description': 'Page load time is slow. Consider upgrading hosting or implementing caching.'
        })
    else:
        metrics['load_time_status'] = 'poor'
        score -= 25
        recommendations.append({
            'title': 'Critical: Optimize Page Load Speed',
            'description': f'Load time of {load_time:.1f}s is too slow. Users expect pages to load in under 2 seconds.'
        })
    
    # Page size
    page_size_kb = len(response.content) / 1024
    page_size_mb = page_size_kb / 1024
    metrics['page_size_kb'] = round(page_size_kb, 1)
    metrics['page_size_mb'] = round(page_size_mb, 2)
    
    if page_size_kb > 3000:  # > 3MB
        score -= 20
        recommendations.append({
            'title': 'Reduce Page Size',
            'description': f'Page is {page_size_mb:.1f}MB. Compress images and minify resources.'
        })
    elif page_size_kb > 1500:  # > 1.5MB
        score -= 10
    
    # Images analysis
    images = soup.find_all('img')
    metrics['total_images'] = len(images)
    
    # Check for lazy loading
    lazy_images = [img for img in images if img.get('loading') == 'lazy']
    metrics['lazy_loaded_images'] = len(lazy_images)
    
    if len(images) > 20 and len(lazy_images) < len(images) * 0.5:
        score -= 10
        recommendations.append({
            'title': 'Implement Lazy Loading',
            'description': 'Add loading="lazy" to images to improve initial page load.'
        })
    
    # Check for modern image formats
    webp_images = [img for img in images if img.get('src', '').endswith('.webp')]
    metrics['webp_images'] = len(webp_images)
    
    # External scripts
    scripts = soup.find_all('script', src=True)
    metrics['external_scripts'] = len(scripts)
    
    if len(scripts) > 15:
        score -= 10
        recommendations.append({
            'title': 'Reduce External Scripts',
            'description': f'{len(scripts)} external scripts detected. Combine and defer non-critical scripts.'
        })
    
    # CSS files
    css_files = soup.find_all('link', rel='stylesheet')
    metrics['css_files'] = len(css_files)
    
    if len(css_files) > 5:
        score -= 5
    
    # Check for minification (basic check)
    minified_css = any('.min.css' in str(css.get('href', '')) for css in css_files)
    minified_js = any('.min.js' in str(script.get('src', '')) for script in scripts)
    metrics['minified_css'] = minified_css
    metrics['minified_js'] = minified_js
    
    if not minified_css or not minified_js:
        score -= 5
        recommendations.append({
            'title': 'Minify CSS and JavaScript',
            'description': 'Minification reduces file sizes and improves load times.'
        })
    
    return {
        'score': max(0, score),
        'status': self.get_status(score),
        'metrics': metrics,
        'recommendations': recommendations[:5]
    }

# ========== CATEGORY 2: MOBILE RESPONSIVENESS ==========
