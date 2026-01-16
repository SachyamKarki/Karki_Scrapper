import re
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def analyze_seo(soup, url, response):
    """Analyze Technical SEO with Enhanced Metrics"""
    score = 100
    checks = {}
    metrics = {}
    recommendations = []
    
    # Get page text content for analysis
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    text_content = soup.get_text()
    words = text_content.split()
    
    # ===== CONTENT ANALYSIS =====
    word_count = len(words)
    metrics['word_count'] = word_count
    
    # Word count scoring
    if word_count < 300:
        score -= 15
        recommendations.append({
            'title': 'Increase Content Length',
            'description': f'Only {word_count} words. Pages with 1,000+ words rank better. Add valuable content.'
        })
    elif word_count < 1000:
        score -= 5
        recommendations.append({
            'title': 'Add More Content',
            'description': f'{word_count} words is okay, but 1,500+ words rank best. Expand your content.'
        })
    
    # Content to HTML ratio
    html_size = len(str(soup))
    text_size = len(text_content)
    content_ratio = (text_size / html_size * 100) if html_size > 0 else 0
    metrics['content_to_html_ratio'] = f"{content_ratio:.1f}%"
    
    if content_ratio < 15:
        score -= 10
        recommendations.append({
            'title': 'Improve Content-to-Code Ratio',
            'description': f'Only {content_ratio:.1f}% of page is content. Reduce HTML bloat, add more text.'
        })
    
    # ===== KEYWORD ANALYSIS =====
    # Simple keyword density (top 5 words excluding common words)
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'}
    
    word_freq = {}
    for word in words:
        word_lower = word.lower().strip('.,!?;:()[]{}\"\'')
        if len(word_lower) > 3 and word_lower not in common_words:
            word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
    
    # Get top keywords
    top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    if top_keywords:
        top_word, top_count = top_keywords[0]
        keyword_density = (top_count / len(words) * 100) if words else 0
        metrics['top_keyword'] = f"{top_word} ({keyword_density:.1f}%)"
        
        if keyword_density > 5:
            recommendations.append({
                'title': 'Reduce Keyword Stuffing',
                'description': f'"{top_word}" appears {keyword_density:.1f}% of the time. Keep it under 3% for natural content.'
            })
    
    # ===== GOOGLE RANKING CHECK =====
    # Extract potential search keywords (combine top keywords with title)
    search_keywords = []
    
    # Add title as primary keyword phrase
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        title_text = title_tag.string.strip()
        # Clean title (remove brand name, special chars)
        clean_title = re.sub(r'[|•\-–—].*$', '', title_text).strip()
        if clean_title and len(clean_title) > 5:
            search_keywords.append(clean_title)
    
    # Add top 3 individual keywords
    for keyword, count in top_keywords[:3]:
        if keyword not in search_keywords:
            search_keywords.append(keyword)
    
    # Add H1 text as keyword phrase
    h1_tag = soup.find('h1')
    if h1_tag:
        h1_text = h1_tag.get_text().strip()
        if h1_text and len(h1_text) > 5 and h1_text not in search_keywords:
            search_keywords.append(h1_text)
    
    
    # Check Google rankings for these keywords
    # TEMPORARILY DISABLED - Testing if this causes timeout
    if False and search_keywords:
        try:
            rankings = self.check_google_rankings(url, search_keywords)
            
            # Add ranking data to metrics
            ranking_summary = []
            for keyword, data in rankings.items():
                if data['position']:
                    ranking_summary.append(f"{keyword}: #{data['position']}")
                else:
                    ranking_summary.append(f"{keyword}: Not in top 50")
            
            if ranking_summary:
                metrics['google_rankings'] = ranking_summary
                
                # Add recommendations based on rankings
                poor_rankings = [k for k, v in rankings.items() if not v['position'] or v['position'] > 20]
                if poor_rankings:
                    recommendations.append({
                        'title': 'Improve Keyword Rankings',
                        'description': f'Not ranking well for: {", ".join(poor_rankings[:2])}. Optimize content and build backlinks.'
                    })
        except Exception as e:
            # If ranking check fails, continue without it
            metrics['google_rankings'] = ['Ranking check unavailable']

    
    # ===== TITLE TAG =====
    title = soup.find('title')
    if title and title.string and len(title.string.strip()) > 0:
        title_text = title.string.strip()
        checks['title_tag'] = True
        metrics['title_length'] = len(title_text)
        
        # Title optimization score
        title_score = 100
        if len(title_text) < 30:
            title_score -= 40
            recommendations.append({
                'title': 'Lengthen Page Title',
                'description': f'Title is only {len(title_text)} characters. Aim for 50-60 characters for better visibility.'
            })
        elif len(title_text) > 60:
            title_score -= 20
            recommendations.append({
                'title': 'Shorten Page Title',
                'description': f'Title is {len(title_text)} characters. Keep it under 60 to avoid truncation in search results.'
            })
        
        # Check if title contains keywords
        if top_keywords and top_keywords[0][0] in title_text.lower():
            title_score += 10
        else:
            recommendations.append({
                'title': 'Add Keywords to Title',
                'description': 'Include your main keyword in the page title for better SEO.'
            })
        
        metrics['title_optimization'] = f"{title_score}%"
    else:
        checks['title_tag'] = False
        score -= 20
        recommendations.append({
            'title': 'Add Page Title',
            'description': 'Critical: Every page must have a unique, descriptive title tag with target keywords.'
        })
    
    # ===== META DESCRIPTION =====
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        desc_text = meta_desc.get('content', '')
        checks['meta_description'] = True
        metrics['meta_desc_length'] = len(desc_text)
        
        if len(desc_text) < 120:
            score -= 5
            recommendations.append({
                'title': 'Expand Meta Description',
                'description': f'Meta description is only {len(desc_text)} characters. Aim for 150-160 for better CTR.'
            })
        elif len(desc_text) > 160:
            score -= 3
            recommendations.append({
                'title': 'Shorten Meta Description',
                'description': f'Meta description is {len(desc_text)} characters. Keep under 160 to avoid truncation.'
            })
    else:
        checks['meta_description'] = False
        score -= 15
        recommendations.append({
            'title': 'Add Meta Description',
            'description': 'Meta descriptions improve click-through rates. Write a compelling 150-160 character summary.'
        })
    
    # ===== HEADING HIERARCHY =====
    h1_tags = soup.find_all('h1')
    h2_tags = soup.find_all('h2')
    h3_tags = soup.find_all('h3')
    
    metrics['h1_count'] = len(h1_tags)
    metrics['h2_count'] = len(h2_tags)
    metrics['h3_count'] = len(h3_tags)
    
    if len(h1_tags) == 0:
        score -= 15
        recommendations.append({
            'title': 'Add H1 Heading',
            'description': 'Every page needs exactly one H1 heading with your main keyword.'
        })
    elif len(h1_tags) > 1:
        score -= 10
        recommendations.append({
            'title': 'Fix H1 Structure',
            'description': f'Found {len(h1_tags)} H1 tags. Use only one H1 per page for proper hierarchy.'
        })
    else:
        checks['h1_proper'] = True
        # Check if H1 contains keywords
        h1_text = h1_tags[0].get_text().lower()
        if top_keywords and top_keywords[0][0] in h1_text:
            metrics['h1_has_keyword'] = True
        else:
            recommendations.append({
                'title': 'Optimize H1 Heading',
                'description': 'Include your main keyword in the H1 heading for better SEO.'
            })
    
    # Check heading structure
    if len(h2_tags) == 0 and word_count > 500:
        recommendations.append({
            'title': 'Add H2 Subheadings',
            'description': 'Break up content with H2 subheadings for better readability and SEO.'
        })
    
    # ===== LINK ANALYSIS =====
    all_links = soup.find_all('a', href=True)
    parsed_url = urlparse(url)
    
    internal_links = []
    external_links = []
    broken_links = []
    
    for link in all_links:
        href = link.get('href', '')
        if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
            continue
        
        if href.startswith('/') or parsed_url.netloc in href:
            internal_links.append(href)
        elif href.startswith('http'):
            external_links.append(href)
    
    metrics['internal_links'] = len(internal_links)
    metrics['external_links'] = len(external_links)
    metrics['total_links'] = len(all_links)
    
    if len(internal_links) < 3:
        score -= 10
        recommendations.append({
            'title': 'Add Internal Links',
            'description': f'Only {len(internal_links)} internal links. Add more to help users and search engines navigate.'
        })
    
    if len(external_links) > 20:
        recommendations.append({
            'title': 'Review External Links',
            'description': f'{len(external_links)} external links detected. Ensure they add value and use nofollow for untrusted sites.'
        })
    
    # ===== IMAGE SEO =====
    images = soup.find_all('img')
    images_with_alt = [img for img in images if img.get('alt')]
    
    if images:
        alt_coverage = len(images_with_alt) / len(images) * 100
        metrics['images_with_alt'] = f"{alt_coverage:.0f}%"
        
        if alt_coverage < 80:
            score -= 10
            recommendations.append({
                'title': 'Add Alt Text to Images',
                'description': f'Only {alt_coverage:.0f}% of images have alt text. Add descriptive alt text to all images.'
            })
    
    # ===== CANONICAL & SCHEMA =====
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    checks['canonical_tag'] = bool(canonical)
    if not canonical:
        score -= 5
        recommendations.append({
            'title': 'Add Canonical Tag',
            'description': 'Canonical tags prevent duplicate content issues and consolidate ranking signals.'
        })
    
    # Structured data (Schema.org)
    json_ld = soup.find_all('script', type='application/ld+json')
    microdata = soup.find_all(attrs={'itemtype': True})
    checks['structured_data'] = len(json_ld) > 0 or len(microdata) > 0
    
    if not checks['structured_data']:
        score -= 10
        recommendations.append({
            'title': 'Add Structured Data',
            'description': 'Schema markup helps search engines understand your content and can enable rich snippets.'
        })
    
    # Open Graph tags
    og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
    checks['open_graph'] = len(og_tags) >= 3
    
    if not checks['open_graph']:
        score -= 5
        recommendations.append({
            'title': 'Add Open Graph Tags',
            'description': 'OG tags control how your page appears when shared on social media.'
        })
    
    # Robots meta
    robots = soup.find('meta', attrs={'name': 'robots'})
    if robots and 'noindex' in str(robots.get('content', '')).lower():
        checks['indexable'] = False
        score -= 30
        recommendations.append({
            'title': 'Remove Noindex Tag',
            'description': 'WARNING: Page is blocked from search engines! Remove noindex to allow indexing.'
        })
    else:
        checks['indexable'] = True
    
    # ===== URL QUALITY =====
    url_path = parsed_url.path
    url_quality = 'good'
    
    if len(url_path) > 100:
        url_quality = 'too_long'
        recommendations.append({
            'title': 'Shorten URL',
            'description': 'URL is too long. Keep URLs under 100 characters for better usability.'
        })
    elif '_' in url_path or '%20' in url_path:
        url_quality = 'needs_improvement'
        recommendations.append({
            'title': 'Improve URL Structure',
            'description': 'Use hyphens instead of underscores in URLs. Avoid spaces and special characters.'
        })
    
    metrics['url_quality'] = url_quality
    
    # ===== SEO POTENTIAL SCORE =====
    # Calculate overall SEO potential (0-100)
    seo_potential = 0
    seo_potential += 15 if checks.get('title_tag') and 30 <= metrics.get('title_length', 0) <= 60 else 0
    seo_potential += 20 if word_count >= 1000 else (word_count / 1000 * 20)
    seo_potential += 15 if checks.get('meta_description') else 0
    seo_potential += 15 if checks.get('h1_proper') else 0
    seo_potential += 10 if checks.get('structured_data') else 0
    seo_potential += 10 if metrics.get('internal_links', 0) >= 5 else (metrics.get('internal_links', 0) * 2)
    seo_potential += 10 if checks.get('canonical_tag') else 0
    seo_potential += 5 if url_quality == 'good' else 0
    
    metrics['seo_potential_score'] = f"{int(seo_potential)}/100"
    
    return {
        'score': max(0, score),
        'status': self.get_status(score),
        'checks': checks,
        'metrics': metrics,
        'recommendations': recommendations[:8]  # More recommendations for SEO
    }


# ========== CATEGORY 4: CRAWLABILITY & INDEXING ==========
