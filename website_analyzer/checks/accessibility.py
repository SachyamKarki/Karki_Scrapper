import re
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def analyze_accessibility(soup):
    """Analyze accessibility"""
    score = 100
    checks = {}
    recommendations = []
    
    # Images with alt text
    images = soup.find_all('img')
    images_with_alt = [img for img in images if img.get('alt') is not None]
    
    if images:
        alt_ratio = len(images_with_alt) / len(images)
        checks['alt_text_coverage'] = round(alt_ratio * 100, 1)
        
        if alt_ratio < 0.5:
            score -= 25
            recommendations.append({
                'title': 'Add Alt Text to Images',
                'description': f'Only {checks["alt_text_coverage"]}% of images have alt text. Aim for 100%.'
            })
        elif alt_ratio < 0.9:
            score -= 10
            recommendations.append({
                'title': 'Improve Alt Text Coverage',
                'description': f'{checks["alt_text_coverage"]}% coverage. Add alt text to remaining images.'
            })
    else:
        checks['alt_text_coverage'] = 100
    
    # Form labels
    inputs = soup.find_all('input', type=lambda x: x != 'hidden')
    labels = soup.find_all('label')
    
    if inputs:
        label_ratio = len(labels) / len(inputs)
        checks['form_labels'] = len(labels) >= len(inputs) * 0.8
        
        if label_ratio < 0.5:
            score -= 15
            recommendations.append({
                'title': 'Add Form Labels',
                'description': 'Most form inputs lack labels. Add <label> tags for accessibility.'
            })
    else:
        checks['form_labels'] = True
    
    # ARIA landmarks
    landmarks = soup.find_all(attrs={'role': True})
    checks['aria_landmarks'] = len(landmarks)
    
    if len(landmarks) == 0:
        score -= 10
        recommendations.append({
            'title': 'Add ARIA Landmarks',
            'description': 'Use ARIA roles (navigation, main, complementary) to improve screen reader navigation.'
        })
    
    # Language attribute
    html_tag = soup.find('html')
    checks['lang_attribute'] = bool(html_tag and html_tag.get('lang'))
    
    if not checks['lang_attribute']:
        score -= 10
        recommendations.append({
            'title': 'Add Language Declaration',
            'description': 'Add lang attribute to <html> tag (e.g., <html lang="en">).'
        })
    
    # Skip navigation link
    skip_link = soup.find('a', href='#main') or soup.find('a', href='#content')
    checks['skip_navigation'] = bool(skip_link)
    
    if not checks['skip_navigation']:
        score -= 5
    
    return {
        'score': max(0, score),
        'status': self.get_status(score),
        'checks': checks,
        'recommendations': recommendations[:5]
    }

# ========== CATEGORY 7: CODE QUALITY ==========
