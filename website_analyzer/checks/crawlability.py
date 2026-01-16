import re
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def analyze_crawlability(soup, url, response):
    """Analyze crawlability and indexing"""
    score = 100
    checks = {}
    recommendations = []
    
    # Check for robots.txt
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    
    try:
        robots_response = requests.get(robots_url, timeout=5, verify=False)
        if robots_response.status_code == 200:
            checks['robots_txt'] = True
            # Check if it's blocking important paths
            if 'Disallow: /' in robots_response.text:
                score -= 20
                recommendations.append({
                    'title': 'Review Robots.txt',
                    'description': 'Robots.txt may be blocking search engines from crawling your site.'
                })
        else:
            checks['robots_txt'] = False
            score -= 5
    except:
        checks['robots_txt'] = False
        score -= 5
    
    # Check for XML sitemap
    sitemap_link = soup.find('link', attrs={'rel': 'sitemap'})
    checks['sitemap_link'] = bool(sitemap_link)
    
    if not sitemap_link:
        score -= 10
        recommendations.append({
            'title': 'Add XML Sitemap',
            'description': 'Submit an XML sitemap to help search engines discover all your pages.'
        })
    
    # Internal links
    internal_links = []
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href.startswith('/') or parsed_url.netloc in href:
            internal_links.append(href)
    
    checks['internal_links'] = len(internal_links)
    
    if len(internal_links) < 5:
        score -= 10
        recommendations.append({
            'title': 'Improve Internal Linking',
            'description': 'Add more internal links to help search engines discover your content.'
        })
    
    # Check for nofollow links
    nofollow_links = soup.find_all('a', rel='nofollow')
    checks['nofollow_links'] = len(nofollow_links)
    
    # Meta robots
    meta_robots = soup.find('meta', attrs={'name': 'robots'})
    if meta_robots:
        content = meta_robots.get('content', '').lower()
        checks['noindex'] = 'noindex' in content
        checks['nofollow'] = 'nofollow' in content
    else:
        checks['noindex'] = False
        checks['nofollow'] = False
    
    return {
        'score': max(0, score),
        'status': self.get_status(score),
        'checks': checks,
        'recommendations': recommendations[:5]
    }

# ========== CATEGORY 5: SECURITY ==========
