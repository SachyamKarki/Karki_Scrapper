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
    {{ "title": "Brief issue title", "description": "Detailed description", "severity": "critical|high|medium|low" }}
  ],
  "errors_and_loading_issues": [
    {{ "issue": "Description of error or loading problem", "likely_cause": "What might cause it" }}
  ],
  "overall_analysis": {{
    "summary": "2-3 sentence overall assessment of the website",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "critical_issues": ["Most urgent issues to fix"]
  }},
  "improvement_recommendations": [
    {{ "category": "e.g. Performance, UX, SEO", "recommendation": "Specific actionable recommendation", "priority": "high|medium|low" }}
  ],
  "keyword_analysis": [
    {{
      "keyword": "exact keyword phrase to search in Google",
      "relevance_score": 1-10,
      "current_content_strength": "weak|moderate|strong",
      "estimated_ranking_potential": "low|medium|high",
      "estimated_current_rank": "1-3|4-10|11-20|21-30|31-50|Not in top 50|Not ranking",
      "landing_page_suggestion": "Which page/section should target this",
      "improvement_tips": "How to improve ranking for this keyword"
    }}
  ]
}}

**Requirements:**
- business_content_summary: A concise overview for a consultant to quickly understand the business. Extract from the website content: what they do, key offerings, who they serve, their value prop, main site sections, location/market, and any crucial details (contact info, pricing hints, certifications, etc.). Be specific and factual based on the content.
- website_quality_red_flags: Check for: No SSL (http), not mobile-friendly, very slow load, broken links/404s, outdated design, no clear CTA, no analytics/tracking, no accessibility (alt tags, contrast). For each, set present true/false and provide a cold_email_angle.
- tech_stack_signals: Infer from content: old CMS (WordPress 4.x, old PHP), no CDN (Cloudflare/Fastly), no performance tools (Lighthouse, GTM), no marketing tools (HubSpot, GA4, Meta Pixel).
- business_growth_indicators: Recently launched site, active on social, running paid ads with weak landing page, hiring, press/funding.
- conversion_problems: No lead forms, forms but no thank-you, no booking, no chat, long checkout, no trust signals.
- seo_visibility_issues: No meta titles/descriptions, duplicate titles, no local SEO/schema, not ranking for brand, abandoned blog.
- keyword_analysis: Provide exactly 10 keywords. For EACH keyword you MUST include estimated_current_rank (REQUIRED) with one of: "1-3", "4-10", "11-20", "21-30", "31-50", "Not in top 50", or "Not ranking". Use narrow bands (e.g. 21-30 not 21-50). Never omit estimated_current_rank.
- Use only valid JSON with snake_case keys. Output ONLY the JSON object, nothing else."""

def fetch_serper_ranking(keyword, website_domain, api_key):
    """Fetch exact Google ranking for a keyword via Serper API. Returns position (1-based) or None if not found."""
    if not api_key or not keyword or not website_domain:
        return None
    try:
        resp = requests.post(
            'https://google.serper.dev/search',
            headers={
                'X-API-KEY': api_key,
                'Content-Type': 'application/json',
            },
            json={'q': keyword},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        organic = data.get('organic') or []
        domain_lower = website_domain.lower().replace('www.', '')
        for item in organic:
            link = (item.get('link') or '').lower()
            position = item.get('position')
            if domain_lower in link or link.endswith(domain_lower):
                return int(position) if isinstance(position, (int, float)) and position > 0 else None
        return None
    except Exception:
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

def analyze_with_gemini(url, business_name='', business_category=''):
    """
    Run Gemini-powered website analysis.
    Returns structured dict with bugs, glitches, improvements, keyword analysis.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return {'status': 'failed', 'error': 'GEMINI_API_KEY not configured'}

    try:
        content = fetch_website_content(url)
    except ValueError as e:
        return {'status': 'failed', 'error': str(e)}

    business_context = f"{business_name} - {business_category}" if (business_name or business_category) else "General business website"

    prompt = GEMINI_PROMPT.format(
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

    # Serper API: fetch exact Google rankings for each keyword (optional)
    serper_key = os.getenv('SERPER_API_KEY')
    domain = extract_domain_from_url(url)

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
            display_rank = google_rank if google_rank is not None else est_rank_str
            if display_rank is None and potential:
                pot = safe_str(potential).lower()
                if pot == 'high': display_rank = '1-10'
                elif pot == 'medium': display_rank = '11-30'
                elif pot == 'low': display_rank = 'Not in top 50'
            if display_rank is None:
                display_rank = 'Unknown'
            keywords.append({
                'keyword': kw_text,
                'relevance_score': min(10, max(1, int(score))) if score is not None else 5,
                'current_content_strength': safe_str(strength).lower() or 'moderate',
                'estimated_ranking_potential': safe_str(potential).lower() or 'medium',
                'improvement_tips': safe_str(tips),
                'google_rank': google_rank,
                'estimated_current_rank': est_rank_str,
                'display_rank': display_rank,
            })
        elif isinstance(kw, (str, int, float)):
            keywords.append({'keyword': str(kw), 'relevance_score': 5, 'current_content_strength': 'moderate', 'estimated_ranking_potential': 'medium', 'improvement_tips': '', 'google_rank': None, 'estimated_current_rank': None, 'display_rank': 'Unknown'})

    # Sanitize bugs_and_glitches
    bugs_data = get_key(data, 'bugs_and_glitches', 'bugsAndGlitches') or []
    bugs = []
    for b in safe_list(bugs_data):
        if isinstance(b, dict):
            bugs.append({
                'title': safe_str(b.get('title', '')),
                'description': safe_str(b.get('description', '')),
                'severity': (safe_str(b.get('severity', '')).lower() or 'medium')[:10],
            })
        elif isinstance(b, str):
            bugs.append({'title': b[:100], 'description': b, 'severity': 'medium'})

    # Sanitize errors_and_loading_issues
    errors_data = get_key(data, 'errors_and_loading_issues', 'errorsAndLoadingIssues') or []
    errors = []
    for e in safe_list(errors_data):
        if isinstance(e, dict):
            issue = e.get('issue', '')
            cause = e.get('likely_cause') or e.get('likelyCause', '')
            errors.append({'issue': safe_str(issue), 'likely_cause': safe_str(cause)})
        elif isinstance(e, str):
            errors.append({'issue': e, 'likely_cause': ''})

    # Sanitize improvement_recommendations
    recs_data = get_key(data, 'improvement_recommendations', 'improvementRecommendations') or []
    recs = []
    for r in safe_list(recs_data):
        if isinstance(r, dict):
            recs.append({
                'category': safe_str(r.get('category', '')),
                'recommendation': safe_str(r.get('recommendation', '')),
                'priority': (safe_str(r.get('priority', '')).lower() or 'medium')[:10],
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

    return {
        'status': 'completed',
        'source': 'gemini',
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
        'overall_analysis': overall,
        'improvement_recommendations': recs,
        'keyword_analysis': keywords,
    }
