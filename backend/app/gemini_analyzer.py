"""
Gemini-powered website analysis: bugs, glitches, improvements, and keyword ranking insights.
Requires GEMINI_API_KEY in .env
"""
import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

GEMINI_PROMPT = """You are an expert website analyst and SEO specialist. Analyze the following website content and provide a comprehensive report for cold-email outreach and sales prospecting.

**Website URL:** {url}
**Business/Page Context:** {business_context}

**Website HTML/Text Content (first ~15000 chars):**
```
{content}
```

IMPORTANT: Respond with ONLY a valid JSON object. No markdown, no code blocks, no explanation before or after. Use snake_case for all keys.

{{
  "business_content_summary": {{
    "what_they_do": "2-3 sentence description of what this business does, their industry, and core offering",
    "key_products_services": ["Product/service 1", "Product/service 2", "..."],
    "target_audience": "Who they serve (B2B/B2C, demographics, industries)",
    "value_proposition": "Their main differentiator or unique selling point",
    "key_content_on_site": ["Main page/section 1", "Main page/section 2", "..."],
    "location_market": "Geographic focus, local vs national, if evident",
    "crucial_details": ["Important detail 1 (e.g. contact methods)", "Important detail 2 (e.g. pricing model)", "..."]
  }},
  "website_quality_red_flags": [
    {{ "flag": "e.g. No SSL (http not https)", "present": true|false, "cold_email_angle": "I noticed your site isn't optimized for mobile users, which may be costing you leads..." }}
  ],
  "tech_stack_signals": [
    {{ "signal": "e.g. Old WordPress 4.x", "present": true|false, "cold_email_angle": "You're running WordPress without a CDN — that usually impacts speed and SEO." }}
  ],
  "business_growth_indicators": [
    {{ "indicator": "e.g. Recently launched site but half-done", "present": true|false, "cold_email_angle": "Since you're expanding, improving conversion on your site could directly impact ROI." }}
  ],
  "conversion_problems": [
    {{ "problem": "e.g. No lead capture forms", "present": true|false, "cold_email_angle": "Small UX changes here typically increase conversions by 20-30%." }}
  ],
  "seo_visibility_issues": [
    {{ "issue": "e.g. No meta titles", "present": true|false, "cold_email_angle": "Your site isn't ranking for branded searches — that's usually an easy fix." }}
  ],
  "bugs_and_glitches": [
    {{ "title": "Brief issue title", "description": "Detailed description", "severity": "critical|high|medium|low", "cold_email_angle": "Pitch angle for outreach" }}
  ],
  "errors_and_loading_issues": [
    {{ "issue": "Description of error or loading problem", "likely_cause": "What might cause it", "cold_email_angle": "Pitch angle for outreach" }}
  ],
  "developer_technical_issues": [
    {{ "category": "vulnerability|security|functionality|glitch", "title": "Brief title", "description": "Detailed description", "severity": "critical|high|medium|low", "cold_email_angle": "Pitch angle for outreach" }}
  ],
  "overall_analysis": {{
    "summary": "2-3 sentence overall assessment of the website",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "critical_issues": ["Most urgent issues to fix"]
  }},
  "improvement_recommendations": [
    {{ "category": "e.g. Performance, UX, SEO", "recommendation": "Specific actionable recommendation", "priority": "high|medium|low", "cold_email_angle": "Pitch angle for cold outreach" }}
  ],
  "keyword_analysis": [
    {{
      "keyword": "exact keyword phrase to search in Google",
      "relevance_score": 1-10,
      "current_content_strength": "weak|moderate|strong",
      "estimated_ranking_potential": "low|medium|high",
      "estimated_current_rank": "1-3|4-10|11-20|21-30|31-50|Not in top 50|Not ranking",
      "landing_page_suggestion": "Which page/section should target this",
      "improvement_tips": "How to improve ranking for this keyword",
      "cold_email_angle": "Pitch angle for cold outreach about this keyword opportunity"
    }}
  ],
  "feature_and_growth_suggestions": [
    {{ "type": "ai_agent|feature|growth", "suggestion": "Specific suggestion for this company", "practical_impact": "How it grows their business", "cold_email_angle": "Pitch angle" }}
  ]
}}

**Requirements:**
- business_content_summary: A concise overview for a consultant to quickly understand the business. Extract from the website content: what they do, key offerings, who they serve, their value prop, main site sections, location/market, and any crucial details (contact info, pricing hints, certifications, etc.). Be specific and factual based on the content.
- website_quality_red_flags: Check for: No SSL (http), not mobile-friendly, very slow load, broken links/404s, outdated design, no clear CTA, no analytics/tracking, no accessibility (alt tags, contrast). For each, set present true/false and provide a cold_email_angle.
- tech_stack_signals: Infer from content: old CMS (WordPress 4.x, old PHP), no CDN (Cloudflare/Fastly), no performance tools (Lighthouse, GTM), no marketing tools (HubSpot, GA4, Meta Pixel).
- business_growth_indicators: Recently launched site, active on social, running paid ads with weak landing page, hiring, press/funding.
- conversion_problems: No lead forms, forms but no thank-you, no booking, no chat, long checkout, no trust signals.
- seo_visibility_issues: No meta titles/descriptions, duplicate titles, no local SEO/schema, not ranking for brand, abandoned blog.
- bugs_and_glitches: Include cold_email_angle. Cover: UI glitches, layout breaks, responsive issues, broken elements.
- errors_and_loading_issues: Include cold_email_angle. Cover: forms not submitting, links broken, JS errors, slow load, timeouts.
- developer_technical_issues (CRITICAL — MUST provide 5-10 items): Developer-focused findings. MUST include at least one from EACH category: (1) vulnerability — XSS, SQL injection risk, outdated libraries, exposed endpoints, CORS misconfig; (2) security — no HTTPS, weak auth, exposed data, missing security headers, mixed content; (3) functionality — broken forms, broken buttons, broken links, 404s, JS errors, features not working; (4) glitch — layout breaks, responsive issues, UI bugs, visual glitches. For each: category (vulnerability|security|functionality|glitch), title, description, severity, cold_email_angle.
- keyword_analysis: Provide exactly 10 keywords that are real Google search phrases (2-5 words, e.g. "cafe pokhara", "best restaurant lakeside") - these will be checked against live Google results. For EACH keyword you MUST include: estimated_current_rank (REQUIRED) with one of "1-3", "4-10", "11-20", "21-30", "31-50", "Not in top 50", or "Not ranking"; improvement_tips; and cold_email_angle (a 1-2 sentence pitch for cold outreach about this keyword opportunity). Use narrow bands (e.g. 21-30 not 21-50). Never omit estimated_current_rank.
- improvement_recommendations: Include cold_email_angle for each recommendation (pitch angle for outreach).
- feature_and_growth_suggestions: Provide 5-8 suggestions tailored to THIS company. Mix of: (1) AI agent ideas (e.g. chatbot, AI booking, automated follow-ups) — how AI can help them specifically; (2) Feature suggestions (e.g. online ordering, live chat, booking system) — based on their business type; (3) Practical growth tips (e.g. local SEO, email marketing, retargeting) — how it practically grows revenue/leads. For each: type (ai_agent|feature|growth), suggestion, practical_impact (concrete outcome), cold_email_angle.
- Use only valid JSON with snake_case keys. Output ONLY the JSON object, nothing else."""

# Same schema as GEMINI_PROMPT but tailored for Facebook pages (posts, about, engagement, etc.)
GEMINI_PROMPT_FACEBOOK = """You are an expert social media and business analyst. Analyze the following Facebook page content and provide a comprehensive report for cold-email outreach and sales prospecting. Use the SAME JSON structure as website analysis.

**Facebook Page URL:** {url}
**Business/Page Context:** {business_context}

**Facebook Page Text Content (first ~15000 chars):**
```
{content}
```

IMPORTANT: Respond with ONLY a valid JSON object. No markdown, no code blocks, no explanation before or after. Use snake_case for all keys. Use the EXACT same schema as website analysis.

{{
  "business_content_summary": {{
    "what_they_do": "2-3 sentence description of what this business does, their industry, and core offering",
    "key_products_services": ["Product/service 1", "Product/service 2", "..."],
    "target_audience": "Who they serve (B2B/B2C, demographics, industries)",
    "value_proposition": "Their main differentiator or unique selling point",
    "key_content_on_site": ["Main content/section 1 (e.g. About, posts, services)", "..."],
    "location_market": "Geographic focus, local vs national, if evident",
    "crucial_details": ["Important detail 1 (e.g. contact methods)", "Important detail 2", "..."]
  }},
  "website_quality_red_flags": [
    {{ "flag": "e.g. Incomplete About section, no contact info", "present": true|false, "cold_email_angle": "..." }}
  ],
  "tech_stack_signals": [
    {{ "signal": "e.g. No linked website, no shop", "present": true|false, "cold_email_angle": "..." }}
  ],
  "business_growth_indicators": [
    {{ "indicator": "e.g. Active posting, recent reviews", "present": true|false, "cold_email_angle": "..." }}
  ],
  "conversion_problems": [
    {{ "problem": "e.g. No CTA, no contact button", "present": true|false, "cold_email_angle": "..." }}
  ],
  "seo_visibility_issues": [
    {{ "issue": "e.g. No website link, weak bio", "present": true|false, "cold_email_angle": "..." }}
  ],
  "bugs_and_glitches": [
    {{ "title": "Brief issue title", "description": "Detailed description", "severity": "critical|high|medium|low", "cold_email_angle": "Pitch angle for outreach" }}
  ],
  "errors_and_loading_issues": [
    {{ "issue": "Description of error or loading problem", "likely_cause": "What might cause it", "cold_email_angle": "Pitch angle for outreach" }}
  ],
  "developer_technical_issues": [
    {{ "category": "vulnerability|security|functionality|glitch", "title": "Brief title", "description": "Detailed description", "severity": "critical|high|medium|low", "cold_email_angle": "Pitch angle for outreach" }}
  ],
  "overall_analysis": {{
    "summary": "2-3 sentence overall assessment of the Facebook page",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "critical_issues": ["Most urgent issues to fix"]
  }},
  "improvement_recommendations": [
    {{ "category": "e.g. Profile, Engagement, Conversion", "recommendation": "Specific actionable recommendation", "priority": "high|medium|low", "cold_email_angle": "Pitch angle for cold outreach" }}
  ],
  "keyword_analysis": [
    {{
      "keyword": "exact keyword phrase to search in Google",
      "relevance_score": 1-10,
      "current_content_strength": "weak|moderate|strong",
      "estimated_ranking_potential": "low|medium|high",
      "estimated_current_rank": "1-3|4-10|11-20|21-30|31-50|Not in top 50|Not ranking",
      "landing_page_suggestion": "Which page/section should target this",
      "improvement_tips": "How to improve ranking for this keyword",
      "cold_email_angle": "Pitch angle for cold outreach about this keyword opportunity"
    }}
  ],
  "feature_and_growth_suggestions": [
    {{
      "type": "ai_agent|feature|growth",
      "suggestion": "Specific suggestion tailored to this company",
      "practical_impact": "How it practically grows their business",
      "cold_email_angle": "Pitch angle for cold outreach"
    }}
  ]
}}

**Requirements:**
- bugs_and_glitches, errors_and_loading_issues: Include cold_email_angle. Cover: UI glitches, layout breaks, forms not submitting, links broken, JS errors, slow load.
- developer_technical_issues (CRITICAL — MUST provide 5-10 items): Developer-focused findings. MUST include at least one from EACH: (1) vulnerability — XSS, SQL injection risk, outdated libraries, exposed endpoints; (2) security — no HTTPS, weak auth, exposed data, missing headers; (3) functionality — broken forms, broken buttons, broken links, 404s, JS errors; (4) glitch — layout breaks, responsive issues, UI bugs. For each: category, title, description, severity, cold_email_angle.
- keyword_analysis: Provide exactly 10 keywords that are real Google search phrases (2-5 words) - these will be checked against live Google results for the business's website. For EACH keyword you MUST include: estimated_current_rank (REQUIRED); improvement_tips; and cold_email_angle.
- feature_and_growth_suggestions: Provide 5-8 suggestions tailored to THIS company. Mix of: AI agent ideas (chatbot, AI booking), feature suggestions (online ordering, live chat), practical growth tips (local SEO, email marketing). For each: type, suggestion, practical_impact, cold_email_angle.
- Use only valid JSON with snake_case keys. Output ONLY the JSON object, nothing else. Same structure as website analysis."""

def _link_matches_domain(link, domain):
    """Check if link URL belongs to the given domain (handles subdomains, www, paths)."""
    if not link or not domain:
        return False
    link = link.lower().strip()
    domain = domain.lower().replace('www.', '')
    try:
        from urllib.parse import urlparse
        parsed = urlparse(link if link.startswith('http') else 'https://' + link)
        host = (parsed.netloc or parsed.path).split(':')[0].replace('www.', '')
        return host == domain or host.endswith('.' + domain)
    except Exception:
        return domain in link or link.endswith(domain)


def fetch_serper_ranking(keyword, website_domain, api_key):
    """Fetch exact Google ranking for a keyword via Serper API. Returns position (1-based) or None if not found."""
    if not api_key or not keyword or not website_domain:
        return None
    domain_clean = website_domain.lower().replace('www.', '').split(':')[0]
    endpoints = ['https://google.serper.dev/search', 'https://serper.dev/search']
    for endpoint in endpoints:
        try:
            resp = requests.post(
                endpoint,
                headers={
                    'X-API-KEY': api_key,
                    'Content-Type': 'application/json',
                },
                json={'q': keyword, 'num': 100},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            organic = data.get('organic') or []
            for item in organic:
                link = item.get('link') or ''
                position = item.get('position')
                if _link_matches_domain(link, domain_clean):
                    if isinstance(position, (int, float)) and position > 0:
                        return int(position)
                    return None
            return None
        except Exception as e:
            import logging
            logging.getLogger(__name__).debug(f"Serper {endpoint} failed for '{keyword}': {e}")
            continue
    return None


def extract_domain_from_url(url):
    """Extract domain (e.g. example.com) from URL for ranking lookup."""
    if not url:
        return ''
    url = str(url).strip().lower()
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.netloc or parsed.path
        return host.replace('www.', '').split(':')[0] or ''
    except Exception:
        return ''


def fetch_website_content(url, timeout=25):
    """Fetch website and extract text content for Gemini."""
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout, verify=False)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Remove scripts and styles
        for tag in soup(['script', 'style']):
            tag.decompose()
        text = soup.get_text(separator='\n', strip=True)
        # Limit size for API
        return text[:15000] if len(text) > 15000 else text
    except Exception as e:
        raise ValueError(f"Failed to fetch website: {str(e)}")


def fetch_facebook_content(url, timeout=30):
    """Fetch Facebook page content using Playwright (same approach as website - extract visible text)."""
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=DEFAULT_HEADERS.get('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'),
                viewport={'width': 1280, 'height': 800}
            )
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=timeout * 1000)
            page.wait_for_timeout(3000)  # Allow JS to render
            text = page.evaluate('''() => {
                const body = document.body;
                if (!body) return '';
                const clone = body.cloneNode(true);
                [].forEach.call(clone.querySelectorAll('script, style, noscript'), el => el.remove());
                return clone.innerText || clone.textContent || '';
            }''')
            browser.close()
            text = (text or '').strip().replace('\r\n', '\n').replace('\r', '\n')
            # Limit size for API (same as website)
            return text[:15000] if len(text) > 15000 else text
    except ImportError:
        raise ValueError('Playwright not installed. Run: pip install playwright && playwright install chromium')
    except Exception as e:
        raise ValueError(f"Failed to fetch Facebook page: {str(e)}")

def parse_gemini_json(response_text):
    """Extract JSON from Gemini response (handles markdown code blocks)."""
    if not response_text or not isinstance(response_text, str):
        raise json.JSONDecodeError("Empty or invalid response", "", 0)
    text = response_text.strip()
    # Remove markdown code blocks if present
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0].strip()
    elif '```' in text:
        parts = text.split('```')
        if len(parts) >= 2:
            text = parts[1].strip()
            if text.startswith('json'):
                text = text[4:].strip()
    # Find JSON object boundaries (handle extra text before/after)
    start = text.find('{')
    end = text.rfind('}')
    if start >= 0 and end > start:
        text = text[start:end + 1]
    return json.loads(text)

def analyze_with_gemini(url, business_name='', business_category='', url_type='website', website_url_for_serper=None):
    """
    Run Gemini-powered analysis for website, Facebook, or Instagram.
    Returns structured dict with bugs, glitches, improvements, keyword analysis.
    url_type: 'website' | 'facebook' | 'instagram'
    website_url_for_serper: For Facebook/Instagram analysis, pass business website URL for 10 SEO keyword ranking lookup.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return {'status': 'failed', 'error': 'GEMINI_API_KEY not configured'}

    url_type = (url_type or 'website').strip().lower()

    # Fetch content: website uses requests+BeautifulSoup, Facebook uses Playwright (same structured output)
    try:
        if url_type == 'facebook':
            content = fetch_facebook_content(url)
        else:
            content = fetch_website_content(url)
    except ValueError as e:
        return {'status': 'failed', 'error': str(e)}

    source_label = {'website': 'website', 'facebook': 'Facebook page', 'instagram': 'Instagram profile'}.get(url_type, 'page')
    business_context = f"{business_name} - {business_category}" if (business_name or business_category) else f"General business {source_label}"

    # Same JSON schema for website and Facebook - identical report structure in AnalysisModal
    prompt_template = GEMINI_PROMPT_FACEBOOK if url_type == 'facebook' else GEMINI_PROMPT
    prompt = prompt_template.format(
        url=url,
        business_context=business_context,
        content=content
    )

    # Try newest models first: gemini-3-flash-preview, then gemini-2.5-flash, then gemini-2.0-flash
    MODELS_TO_TRY = ['gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-2.0-flash']
    raw_text = None
    last_error = None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        for model_name in MODELS_TO_TRY:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw_text = getattr(response, 'text', None)
                if raw_text and isinstance(raw_text, str) and len(raw_text.strip()) > 10:
                    break
            except Exception as e:
                last_error = e
                continue
        if not raw_text or not isinstance(raw_text, str):
            return {'status': 'failed', 'error': f'Gemini returned empty response. Last error: {last_error}'}
    except ImportError:
        return {'status': 'failed', 'error': 'google-generativeai package not installed. Run: pip install google-generativeai'}
    except Exception as e:
        return {'status': 'failed', 'error': f'Gemini API error: {str(e)}'}

    try:
        data = parse_gemini_json(raw_text)
    except json.JSONDecodeError as e:
        return {'status': 'failed', 'error': f'Failed to parse Gemini response: {str(e)}', 'raw': (raw_text or '')[:500]}

    if not isinstance(data, dict):
        return {'status': 'failed', 'error': 'Gemini returned invalid format'}

    # Support both snake_case and camelCase from Gemini
    def get_key(d, *keys):
        for k in keys:
            if k in d:
                return d[k]
        return None

    def safe_list(val, default=None):
        return val if isinstance(val, list) else (default or [])

    def safe_dict(val, default=None):
        return val if isinstance(val, dict) else (default or {})

    def safe_str(val):
        return str(val) if val is not None else ''

    # Serper API: fetch exact Google rankings for 10 SEO keywords (website: use url; Facebook/Instagram: use business website)
    serper_key = os.getenv('SERPER_API_KEY')
    domain = extract_domain_from_url(url) if url_type == 'website' else extract_domain_from_url(website_url_for_serper or '')

    # Sanitize keyword_analysis - ensure relevance_score is int, strings are safe
    keyword_data = (get_key(data, 'keyword_analysis', 'keywordAnalysis') or
                    get_key(data, 'keywords', 'keywordAnalysis') or [])
    keywords = []
    for kw in safe_list(keyword_data):
        if isinstance(kw, dict):
            score = kw.get('relevance_score') or kw.get('relevanceScore')
            if isinstance(score, str) and score.isdigit():
                score = int(score)
            elif not isinstance(score, (int, float)):
                score = 5
            strength = kw.get('current_content_strength') or kw.get('currentContentStrength')
            potential = kw.get('estimated_ranking_potential') or kw.get('estimatedRankingPotential')
            tips = kw.get('improvement_tips') or kw.get('improvementTips')
            # Try multiple key names Gemini might use for ranking
            est_rank = (kw.get('estimated_current_rank') or kw.get('estimatedCurrentRank') or
                        kw.get('current_rank') or kw.get('currentRank') or
                        kw.get('ranking') or kw.get('rank') or kw.get('estimated_rank') or
                        kw.get('google_rank') or kw.get('googleRank'))
            kw_text = safe_str(kw.get('keyword', ''))
            # Fetch exact Google rank via Serper if API key is set
            google_rank = None
            if serper_key and kw_text and domain:
                google_rank = fetch_serper_ranking(kw_text, domain, serper_key)
            # Normalize est_rank: can be string or number from Gemini
            est_rank_str = None
            if est_rank is not None:
                if isinstance(est_rank, (int, float)) and est_rank > 0:
                    est_rank_str = str(int(est_rank))
                else:
                    est_rank_str = safe_str(est_rank).strip() or None
            # Use Serper exact rank when available; otherwise Gemini's estimated rank; else derive from potential
            display_rank = str(google_rank) if google_rank is not None else est_rank_str
            if display_rank is None and potential:
                pot = safe_str(potential).lower()
                if pot == 'high': display_rank = '1-10'
                elif pot == 'medium': display_rank = '11-30'
                elif pot == 'low': display_rank = 'Not in top 50'
            if display_rank is None:
                display_rank = 'Unknown'
            kw_angle = safe_str(kw.get('cold_email_angle') or kw.get('coldEmailAngle', ''))
            keywords.append({
                'keyword': kw_text,
                'relevance_score': min(10, max(1, int(score))) if score is not None else 5,
                'current_content_strength': safe_str(strength).lower() or 'moderate',
                'estimated_ranking_potential': safe_str(potential).lower() or 'medium',
                'improvement_tips': safe_str(tips),
                'cold_email_angle': kw_angle,
                'google_rank': google_rank,
                'estimated_current_rank': est_rank_str,
                'display_rank': display_rank,
            })
        elif isinstance(kw, (str, int, float)):
            keywords.append({'keyword': str(kw), 'relevance_score': 5, 'current_content_strength': 'moderate', 'estimated_ranking_potential': 'medium', 'improvement_tips': '', 'cold_email_angle': '', 'google_rank': None, 'estimated_current_rank': None, 'display_rank': 'Unknown'})

    # Sanitize bugs_and_glitches
    bugs_data = get_key(data, 'bugs_and_glitches', 'bugsAndGlitches') or []
    bugs = []
    for b in safe_list(bugs_data):
        if isinstance(b, dict):
            bugs.append({
                'title': safe_str(b.get('title', '')),
                'description': safe_str(b.get('description', '')),
                'severity': (safe_str(b.get('severity', '')).lower() or 'medium')[:10],
                'cold_email_angle': safe_str(b.get('cold_email_angle') or b.get('coldEmailAngle', '')),
            })
        elif isinstance(b, str):
            bugs.append({'title': b[:100], 'description': b, 'severity': 'medium', 'cold_email_angle': ''})

    # Sanitize errors_and_loading_issues
    errors_data = get_key(data, 'errors_and_loading_issues', 'errorsAndLoadingIssues') or []
    errors = []
    for e in safe_list(errors_data):
        if isinstance(e, dict):
            issue = e.get('issue', '')
            cause = e.get('likely_cause') or e.get('likelyCause', '')
            angle = e.get('cold_email_angle') or e.get('coldEmailAngle', '')
            errors.append({'issue': safe_str(issue), 'likely_cause': safe_str(cause), 'cold_email_angle': safe_str(angle)})
        elif isinstance(e, str):
            errors.append({'issue': e, 'likely_cause': '', 'cold_email_angle': ''})

    # Sanitize developer_technical_issues (vulnerabilities, security, functionality, glitches)
    dev_issues_data = get_key(data, 'developer_technical_issues', 'developerTechnicalIssues') or []
    dev_issues = []
    for d in safe_list(dev_issues_data):
        if isinstance(d, dict):
            dev_issues.append({
                'category': (safe_str(d.get('category', '')).lower() or 'glitch')[:20],
                'title': safe_str(d.get('title', '')),
                'description': safe_str(d.get('description', '')),
                'severity': (safe_str(d.get('severity', '')).lower() or 'medium')[:10],
                'cold_email_angle': safe_str(d.get('cold_email_angle') or d.get('coldEmailAngle', '')),
            })
        elif isinstance(d, str):
            dev_issues.append({'category': 'glitch', 'title': d[:100], 'description': d, 'severity': 'medium', 'cold_email_angle': ''})

    # Sanitize improvement_recommendations
    recs_data = get_key(data, 'improvement_recommendations', 'improvementRecommendations') or []
    recs = []
    for r in safe_list(recs_data):
        if isinstance(r, dict):
            recs.append({
                'category': safe_str(r.get('category', '')),
                'recommendation': safe_str(r.get('recommendation', '')),
                'priority': (safe_str(r.get('priority', '')).lower() or 'medium')[:10],
                'cold_email_angle': safe_str(r.get('cold_email_angle') or r.get('coldEmailAngle', '')),
            })
        elif isinstance(r, str):
            recs.append({'category': 'General', 'recommendation': r, 'priority': 'medium'})

    overall = safe_dict(get_key(data, 'overall_analysis', 'overallAnalysis') or {})
    overall['summary'] = safe_str(overall.get('summary', ''))
    overall['strengths'] = [safe_str(x) for x in safe_list(overall.get('strengths')) if x]
    overall['critical_issues'] = [safe_str(x) for x in safe_list(overall.get('critical_issues')) if x]

    # Ensure we always have at least a basic summary (prevents blank report)
    if not overall['summary'] and (bugs or errors or recs or keywords):
        overall['summary'] = f"Analysis of {url}. Found {len(bugs)} potential issues, {len(recs)} improvement recommendations, and {len(keywords)} keyword insights."

    # Sanitize business_content_summary
    biz_summary_raw = safe_dict(get_key(data, 'business_content_summary', 'businessContentSummary') or {})
    business_summary = {
        'what_they_do': safe_str(biz_summary_raw.get('what_they_do') or biz_summary_raw.get('whatTheyDo', '')),
        'key_products_services': [safe_str(x) for x in safe_list(biz_summary_raw.get('key_products_services') or biz_summary_raw.get('keyProductsServices')) if x],
        'target_audience': safe_str(biz_summary_raw.get('target_audience') or biz_summary_raw.get('targetAudience', '')),
        'value_proposition': safe_str(biz_summary_raw.get('value_proposition') or biz_summary_raw.get('valueProposition', '')),
        'key_content_on_site': [safe_str(x) for x in safe_list(biz_summary_raw.get('key_content_on_site') or biz_summary_raw.get('keyContentOnSite')) if x],
        'location_market': safe_str(biz_summary_raw.get('location_market') or biz_summary_raw.get('locationMarket', '')),
        'crucial_details': [safe_str(x) for x in safe_list(biz_summary_raw.get('crucial_details') or biz_summary_raw.get('crucialDetails')) if x],
    }

    # Sanitize new sections: website_quality_red_flags, tech_stack_signals, etc.
    red_flags = []
    for item in safe_list(get_key(data, 'website_quality_red_flags', 'websiteQualityRedFlags')):
        if isinstance(item, dict):
            red_flags.append({
                'flag': safe_str(item.get('flag', '')),
                'present': item.get('present', False) if isinstance(item.get('present'), bool) else str(item.get('present', '')).lower() in ('true', '1', 'yes'),
                'cold_email_angle': safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle', '')),
            })
        elif isinstance(item, str):
            red_flags.append({'flag': item[:200], 'present': True, 'cold_email_angle': ''})

    tech_stack = []
    for item in safe_list(get_key(data, 'tech_stack_signals', 'techStackSignals')):
        if isinstance(item, dict):
            tech_stack.append({
                'signal': safe_str(item.get('signal', '')),
                'present': item.get('present', False) if isinstance(item.get('present'), bool) else str(item.get('present', '')).lower() in ('true', '1', 'yes'),
                'cold_email_angle': safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle', '')),
            })
        elif isinstance(item, str):
            tech_stack.append({'signal': item[:200], 'present': True, 'cold_email_angle': ''})

    growth_indicators = []
    for item in safe_list(get_key(data, 'business_growth_indicators', 'businessGrowthIndicators')):
        if isinstance(item, dict):
            growth_indicators.append({
                'indicator': safe_str(item.get('indicator', '')),
                'present': item.get('present', False) if isinstance(item.get('present'), bool) else str(item.get('present', '')).lower() in ('true', '1', 'yes'),
                'cold_email_angle': safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle', '')),
            })
        elif isinstance(item, str):
            growth_indicators.append({'indicator': item[:200], 'present': True, 'cold_email_angle': ''})

    conversion_problems = []
    for item in safe_list(get_key(data, 'conversion_problems', 'conversionProblems')):
        if isinstance(item, dict):
            conversion_problems.append({
                'problem': safe_str(item.get('problem', '')),
                'present': item.get('present', False) if isinstance(item.get('present'), bool) else str(item.get('present', '')).lower() in ('true', '1', 'yes'),
                'cold_email_angle': safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle', '')),
            })
        elif isinstance(item, str):
            conversion_problems.append({'problem': item[:200], 'present': True, 'cold_email_angle': ''})

    seo_issues = []
    for item in safe_list(get_key(data, 'seo_visibility_issues', 'seoVisibilityIssues')):
        if isinstance(item, dict):
            seo_issues.append({
                'issue': safe_str(item.get('issue', '')),
                'present': item.get('present', False) if isinstance(item.get('present'), bool) else str(item.get('present', '')).lower() in ('true', '1', 'yes'),
                'cold_email_angle': safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle', '')),
            })
        elif isinstance(item, str):
            seo_issues.append({'issue': item[:200], 'present': True, 'cold_email_angle': ''})

    feature_suggestions = []
    for item in safe_list(get_key(data, 'feature_and_growth_suggestions', 'featureAndGrowthSuggestions')):
        if isinstance(item, dict):
            feature_suggestions.append({
                'type': safe_str(item.get('type', '')).lower() or 'feature',
                'suggestion': safe_str(item.get('suggestion', '')),
                'practical_impact': safe_str(item.get('practical_impact') or item.get('practicalImpact', '')),
                'cold_email_angle': safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle', '')),
            })
        elif isinstance(item, str):
            feature_suggestions.append({'type': 'feature', 'suggestion': item[:200], 'practical_impact': '', 'cold_email_angle': ''})

    return {
        'status': 'completed',
        'source': 'gemini',
        'url_type': url_type,
        'url': url,
        'analyzed_at': datetime.utcnow().isoformat(),
        'business_content_summary': business_summary,
        'website_quality_red_flags': red_flags,
        'tech_stack_signals': tech_stack,
        'business_growth_indicators': growth_indicators,
        'conversion_problems': conversion_problems,
        'seo_visibility_issues': seo_issues,
        'bugs_and_glitches': bugs,
        'errors_and_loading_issues': errors,
        'developer_technical_issues': dev_issues,
        'overall_analysis': overall,
        'improvement_recommendations': recs,
        'keyword_analysis': keywords,
        'feature_and_growth_suggestions': feature_suggestions,
    }


def _build_must_include_checklist(analysis):
    """Extract every finding from analysis into a flat checklist so the model cannot ignore any line."""
    def safe_list(v):
        return v if isinstance(v, list) else []
    def safe_str(v):
        return str(v).strip() if v is not None else ''
    lines = []
    # Red flags (present=true)
    for item in safe_list(analysis.get('website_quality_red_flags') or analysis.get('websiteQualityRedFlags')):
        if isinstance(item, dict) and item.get('present'):
            angle = safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle'))
            flag = safe_str(item.get('flag'))
            if angle or flag:
                lines.append(f"[Red flag] {flag or angle} → {angle or flag}")
    # Tech stack
    for item in safe_list(analysis.get('tech_stack_signals') or analysis.get('techStackSignals')):
        if isinstance(item, dict) and item.get('present'):
            angle = safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle'))
            sig = safe_str(item.get('signal'))
            if angle or sig:
                lines.append(f"[Tech] {sig or angle} → {angle or sig}")
    # Growth indicators
    for item in safe_list(analysis.get('business_growth_indicators') or analysis.get('businessGrowthIndicators')):
        if isinstance(item, dict) and item.get('present'):
            angle = safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle'))
            ind = safe_str(item.get('indicator'))
            if angle or ind:
                lines.append(f"[Growth] {ind or angle} → {angle or ind}")
    # Conversion problems
    for item in safe_list(analysis.get('conversion_problems') or analysis.get('conversionProblems')):
        if isinstance(item, dict) and item.get('present'):
            angle = safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle'))
            prob = safe_str(item.get('problem'))
            if angle or prob:
                lines.append(f"[Conversion] {prob or angle} → {angle or prob}")
    # SEO issues
    for item in safe_list(analysis.get('seo_visibility_issues') or analysis.get('seoVisibilityIssues')):
        if isinstance(item, dict) and item.get('present'):
            angle = safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle'))
            iss = safe_str(item.get('issue'))
            if angle or iss:
                lines.append(f"[SEO] {iss or angle} → {angle or iss}")
    # Bugs & glitches
    for item in safe_list(analysis.get('bugs_and_glitches') or analysis.get('bugsAndGlitches')):
        if isinstance(item, dict):
            angle = safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle'))
            title = safe_str(item.get('title'))
            desc = safe_str(item.get('description'))
            if angle or title or desc:
                lines.append(f"[Bug] {title or desc} → {angle or desc or title}")
    # Errors & loading
    for item in safe_list(analysis.get('errors_and_loading_issues') or analysis.get('errorsAndLoadingIssues')):
        if isinstance(item, dict):
            angle = safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle'))
            iss = safe_str(item.get('issue'))
            if angle or iss:
                lines.append(f"[Error] {iss} → {angle or iss}")
    # Developer technical issues
    for item in safe_list(analysis.get('developer_technical_issues') or analysis.get('developerTechnicalIssues')):
        if isinstance(item, dict):
            angle = safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle'))
            title = safe_str(item.get('title'))
            cat = safe_str(item.get('category'))
            if angle or title:
                lines.append(f"[Dev/{cat or 'tech'}] {title} → {angle or title}")
    # Improvement recommendations
    for item in safe_list(analysis.get('improvement_recommendations') or analysis.get('improvementRecommendations')):
        if isinstance(item, dict):
            angle = safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle'))
            rec = safe_str(item.get('recommendation'))
            if angle or rec:
                lines.append(f"[Rec] {rec} → {angle or rec}")
    # Keywords
    for item in safe_list(analysis.get('keyword_analysis') or analysis.get('keywordAnalysis')):
        if isinstance(item, dict):
            kw = safe_str(item.get('keyword'))
            rank = item.get('display_rank') or item.get('google_rank') or item.get('estimated_current_rank')
            angle = safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle'))
            if kw and (angle or rank):
                lines.append(f"[Keyword] {kw} (rank: {rank or '?'}) → {angle or f'opportunity for {kw}'}")
    # Feature & growth suggestions
    for item in safe_list(analysis.get('feature_and_growth_suggestions') or analysis.get('featureAndGrowthSuggestions')):
        if isinstance(item, dict):
            angle = safe_str(item.get('cold_email_angle') or item.get('coldEmailAngle'))
            sug = safe_str(item.get('suggestion'))
            impact = safe_str(item.get('practical_impact') or item.get('practicalImpact'))
            if angle or sug:
                lines.append(f"[Feature] {sug} (impact: {impact}) → {angle or sug}")
    # Critical issues from overall
    for s in safe_list((analysis.get('overall_analysis') or analysis.get('overallAnalysis') or {}).get('critical_issues') or []):
        if s:
            lines.append(f"[Critical] {s}")
    return lines


def generate_email_with_gemini(place, analysis, note_text='', template_type=1, custom_prompt=''):
    """
    Generate a comprehensive cold email from analysis. Returns {subject, body} or {status: 'failed', error}.
    template_type: 1=Professional, 2=Friendly, 3=Direct, 4=Best (optimal — includes every finding, makes them feel they need help)
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return {'status': 'failed', 'error': 'GEMINI_API_KEY not configured'}

    if not analysis or not isinstance(analysis, dict):
        return {'status': 'failed', 'error': 'No analysis available. Run analysis first.'}
    if analysis.get('status') == 'failed':
        return {'status': 'failed', 'error': 'Analysis failed. Run analysis again.'}

    tone_map = {1: 'Professional', 2: 'Friendly', 3: 'Direct', 4: 'Best'}
    tone = tone_map.get(template_type, 'Professional')

    # Build explicit checklist so model cannot ignore findings
    must_include_lines = _build_must_include_checklist(analysis)
    checklist_text = '\n'.join(f'- {line}' for line in must_include_lines) if must_include_lines else '(No specific findings — use business summary and overall_analysis)'

    try:
        analysis_text = json.dumps(analysis, indent=2, default=str)
    except (TypeError, ValueError) as e:
        return {'status': 'failed', 'error': f'Invalid analysis format: {e}'}
    if len(analysis_text) > 35000:
        analysis_text = analysis_text[:35000] + '\n... [truncated]'

    business_name = str(place.get('name') or 'this business')
    business_category = str(place.get('category') or '')
    website_url = str(place.get('website') or analysis.get('url') or '')
    has_website = bool(website_url and website_url.strip())

    tone_desc = {
        'Professional': 'Formal, business-focused, value-driven.',
        'Friendly': 'Warm, conversational, personable.',
        'Direct': 'Short, punchy, clear call-to-action. No fluff.',
        'Best': 'OPTIMAL TONE — Best of all. See special instructions below.'
    }.get(tone, 'Professional')

    best_tone_instructions = """
**BEST TONE (template 4) — CRITICAL:**
- Include EACH AND EVERY line from the MUST-INCLUDE CHECKLIST below. Do NOT skip any. Weave the essence of each into the email.
- Make the company feel: "Yes, we have a lot to improve and we need your help." Create urgency and desire for improvement.
- **IF NO WEBSITE or weak/missing site:** Influence them on how critical a great website is — lost customers, no online presence, competitors ahead.
- **IF THEY HAVE A WEBSITE:** Show specific issues found — ranking gaps, broken elements, slow load, security, bugs, glitches. Make them feel their site needs care.
- 300-450 words allowed. Cohesive paragraphs, not bullet list. End with soft CTA. Sign as Shak.
""" if tone == 'Best' else ''

    prompt = f"""You are an expert cold email copywriter. Create a comprehensive cold email for sales outreach that demonstrates deep research.

**Business:** {business_name}
**Category:** {business_category}
**Website URL:** {website_url or 'Not provided'}
**Has website:** {has_website}
**Tone:** {tone} — {tone_desc}

**MUST-INCLUDE CHECKLIST — DO NOT SKIP ANY OF THESE. Each line is a finding from the analysis. Weave the essence of EACH into the email in the best way:**
```
{checklist_text}
```

**Full Analysis (reference for details):**
```
{analysis_text}
```

**Notes (if any):** {note_text or 'None'}
{best_tone_instructions}
**Requirements:**
- **CRITICAL:** Every line in the MUST-INCLUDE CHECKLIST above MUST appear in some form in your email. Do not ignore or skip any finding. Use the cold_email_angle or description from each.
- **Business summary:** Use what_they_do, target_audience, value_proposition from business_content_summary.
- **Domain/website:** If domain differs from company name or is hard to find, mention it.
- **Red flags, tech stack, growth, conversion, SEO:** Include cold_email_angle from each present item.
- **Bugs, errors, developer_technical_issues:** Include vulnerabilities, security concerns, functions not working, glitches — use cold_email_angle from each.
- **Keywords:** Mention specific keywords and rankings (e.g. "you're at #12 for 'cafe pokhara'").
- **Feature & growth suggestions:** Include AI agent ideas, feature suggestions, practical_impact.
- **Improvement recommendations:** Weave in cold_email_angle from each.
- **Critical issues:** Include from overall_analysis.critical_issues.
- **Greeting:** Start the email with exactly: "Greetings {{Business team}}" (keep this literal — it is a merge field).
- Write as cohesive paragraphs (not bullet list). 200-350 words (300-450 for Best tone).
- End with a clear, soft call-to-action.
- Plain text only: no markdown, no **, no asterisks.
- Sign as "Shak".
- Output ONLY valid JSON: {{"subject": "Email subject line", "body": "Full email body text"}}
- No markdown, no code blocks, no extra text."""

    MODELS_TO_TRY = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-3-flash-preview']
    raw = None
    last_error = None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        for model_name in MODELS_TO_TRY:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw = getattr(response, 'text', None)
                if raw and isinstance(raw, str) and len(raw.strip()) > 10:
                    break
            except Exception as e:
                last_error = e
                continue
        if not raw or not isinstance(raw, str):
            err_msg = str(last_error) if last_error else 'Empty response'
            return {'status': 'failed', 'error': f'Gemini error: {err_msg}'}
    except ImportError:
        return {'status': 'failed', 'error': 'google-generativeai not installed. Run: pip install google-generativeai'}
    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

    try:
        text = raw.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            parts = text.split('```')
            if len(parts) >= 2:
                text = parts[1].strip()
                if text.startswith('json'):
                    text = text[4:].strip()
        start, end = text.find('{'), text.rfind('}')
        if start >= 0 and end > start:
            text = text[start:end + 1]
        data = json.loads(text)
        subject = data.get('subject', '') or data.get('Subject', '')
        body = data.get('body', '') or data.get('Body', '')
        return {'subject': subject, 'body': body}
    except json.JSONDecodeError as e:
        return {'status': 'failed', 'error': f'Failed to parse Gemini response: {e}', 'raw': (raw or '')[:300]}
    except Exception as e:
        return {'status': 'failed', 'error': str(e)}
