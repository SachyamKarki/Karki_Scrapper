from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from bson.objectid import ObjectId
import json
import os
import subprocess
import uuid
from website_analyzer import analyzer
from .database import get_db_connection, get_sent_emails_collection

# Create Blueprint
main = Blueprint('main', __name__)

# Global to store current session
CURRENT_BATCH_ID = None

@main.route('/health')
def health():
    """Public health check - no auth required (for Render, load balancers)."""
    return jsonify({'status': 'ok'}), 200

@main.route('/db_check')
def db_check():
    """Diagnostic: test MongoDB connection (no auth required)."""
    try:
        coll = get_db_connection()
        count = coll.count_documents({})
        return jsonify({'status': 'ok', 'connected': True, 'places_count': count}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'connected': False, 'error': str(e)}), 500

def render_dashboard(places, title="Dashboard", show_join=False, is_scrappy=False, pagination=None):
    # Render the template from file instead of string
    return render_template('dashboard.html', places=places, title=title, show_join=show_join, is_scrappy=is_scrappy, batch_id=CURRENT_BATCH_ID, pagination=pagination, user=current_user)

@main.route('/')
@login_required
def index():
    # Redirect administrative roles to the panel IF they are landing on root directly via browser
    # We check if it's NOT an API call (no application/json in Accept or request is not JSON)
    is_api_request = (
        request.is_json or 
        'application/json' in request.headers.get('Accept', '') or
        request.args.get('format') == 'json'
    )
    
    if current_user.is_admin and not is_api_request:
        return redirect(url_for('admin.dashboard'))
        
    page = int(request.args.get('page', 1))
    per_page = 50 
    
    # Filtering Logic - search by name, address, phone, website, email; status filter
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip().lower()
    
    mongo_query = {}
    status_clause = None
    search_clause = None

    if status_filter and status_filter != 'all':
        if status_filter == 'pending':
            status_clause = {'$or': [{'status': None}, {'status': {'$exists': False}}, {'status': 'pending'}]}
        else:
            status_clause = {'status': status_filter}

    if search_query:
        search_clause = {'$or': [
            {'name': {'$regex': search_query, '$options': 'i'}},
            {'address': {'$regex': search_query, '$options': 'i'}},
            {'phone': {'$regex': search_query, '$options': 'i'}},
            {'website': {'$regex': search_query, '$options': 'i'}},
            {'email': {'$regex': search_query, '$options': 'i'}},
            {'social_links': {'$regex': search_query, '$options': 'i'}}
        ]}

    if status_clause and search_clause:
        mongo_query['$and'] = [status_clause, search_clause]
    elif status_clause:
        mongo_query = status_clause
    elif search_clause:
        mongo_query = search_clause
    
    skip = (page - 1) * per_page
    
    collection = get_db_connection()
    total_count = collection.count_documents(mongo_query)
    
    # Fetch slice
    places = list(collection.find(mongo_query).sort('_id', -1).skip(skip).limit(per_page))
    
    # Convert _id to string for JSON
    for place in places:
        place['_id'] = str(place['_id'])
        
    total_pages = (total_count + per_page - 1) // per_page
    
    if request.accept_mimetypes.accept_json:
        return jsonify({
            'places': places,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_items': total_count,
            }
        })
    
    # Windowed Pagination Logic (legacy) -> still returned for template rendering safety
    # ... (rest of legacy pagination logic if needed, but we mostly use API now)
    
    pagination = {
        'current_page': page,
        'per_page': per_page,
        'total_pages': total_pages, 
        'total_items': total_count,
        'has_next': page < total_pages,
        'has_prev': page > 1,
        'next_page': page + 1,
        'prev_page': page - 1,
        'display_pages': []
    }
    
    return render_dashboard(places, title="Dashboard", show_join=False, is_scrappy=False, pagination=pagination)

@main.route('/scrape', methods=['POST'])
def scrape():
    global CURRENT_BATCH_ID
    
    # Handle both JSON and Form data
    if request.is_json:
        query = request.get_json().get('query')
    else:
        query = request.form.get('query')
        
    if query:
        # Generate new Batch ID (still useful for tracking origin)
        CURRENT_BATCH_ID = str(uuid.uuid4())
        
        try:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            run_sh = os.path.join(backend_dir, 'run.sh')
            if not os.path.isfile(run_sh):
                raise FileNotFoundError(f"run.sh not found at {run_sh}")
            log_path = os.path.join(backend_dir, 'data', 'scrape.log')
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            log_file = open(log_path, 'a')
            log_file.write(f"\n--- Scrape started: {query} ({CURRENT_BATCH_ID}) ---\n")
            log_file.flush()
            subprocess.Popen(
                ['bash', run_sh, str(query), CURRENT_BATCH_ID],
                cwd=backend_dir,
                env={**os.environ},
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
            
            if request.is_json or request.accept_mimetypes.accept_json:
                return jsonify({'success': True, 'batch_id': CURRENT_BATCH_ID, 'message': 'Scraping started. Results will appear shortly.'})
                
        except Exception as e:
            print(f"Scraper Error: {e}")
            if request.is_json or request.accept_mimetypes.accept_json:
                 return jsonify({'success': False, 'error': str(e)}), 500
            return f"Error running scraper: {e}", 500
            
    if request.is_json or request.accept_mimetypes.accept_json:
        return jsonify({'success': False, 'error': 'No query provided'}), 400
        
    return redirect(url_for('main.index'))

@main.route('/update_status', methods=['POST'])
def update_status():
    """Update the status of a place in MongoDB"""
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        new_status = data.get('status')
        
        if not item_id or not new_status:
            return jsonify({'success': False, 'error': 'Missing parameters'})
        
        if new_status not in ['pending', 'in_progress', 'approved', 'rejected']:
            return jsonify({'success': False, 'error': 'Invalid status'})
        
        collection = get_db_connection()
        result = collection.update_one(
            {'_id': ObjectId(item_id)},
            {'$set': {'status': new_status}}
        )
        
        return jsonify({'success': result.modified_count > 0})
    except Exception as e:
        print(f"Error updating status: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/updates')
def api_updates():
    # Return ANY new items added to the collection, regardless of batch
    last_id = request.args.get('last_id')
    collection = get_db_connection()
    
    query = {}
    
    # If we have a last_id, only get items NEWER than that
    if last_id and last_id != 'null':
        try:
            query['_id'] = {'$gt': ObjectId(last_id)}
        except:
            pass 
            
    # Fetch newest first so they are added to top correctly?
    new_items_cursor = collection.find(query).sort('_id', 1) 
    
    new_items = []
    for item in new_items_cursor:
        item['_id'] = str(item['_id']) 
        new_items.append(item)
        
    return jsonify({'new_items': new_items})

def _get_url_for_analysis(business, url_type):
    """Resolve URL from business based on url_type: website, facebook, instagram."""
    url_type = (url_type or 'website').strip().lower()
    if url_type == 'website':
        return business.get('website')
    if url_type in ('facebook', 'instagram'):
        sl = business.get('social_links')
        if sl:
            try:
                data = json.loads(sl) if isinstance(sl, str) else sl
                if isinstance(data, dict):
                    # Handle both 'facebook' and 'Facebook' keys
                    for k, v in data.items():
                        if k and v and str(k).lower() == url_type:
                            return v
            except (json.JSONDecodeError, TypeError):
                pass
    return None


@main.route('/analyze/<item_id>', methods=['POST'])
def analyze_website_endpoint(item_id):
    """Trigger analysis for a business (website, facebook, or instagram). Uses Gemini when GEMINI_API_KEY is set."""
    import os
    try:
        collection = get_db_connection()
        
        # Get the business data
        business = collection.find_one({'_id': ObjectId(item_id)})
        if not business:
            return jsonify({'success': False, 'error': 'Business not found'})
        
        # Accept url_type from POST body: website, facebook, instagram
        data = request.get_json(silent=True) or {}
        url_type = (data.get('url_type') or 'website').strip().lower()
        
        url = _get_url_for_analysis(business, url_type)
        if not url:
            type_label = {'website': 'Website', 'facebook': 'Facebook', 'instagram': 'Instagram'}.get(url_type, url_type)
            return jsonify({'success': False, 'error': f'No {type_label} URL available for this business'})
        
        # Use Gemini when API key is set, otherwise fallback to local analyzer (website only)
        if os.getenv('GEMINI_API_KEY'):
            from .gemini_analyzer import analyze_with_gemini
            # For Facebook/Instagram, pass website URL for Serper keyword ranking (10 SEO keywords)
            website_url = business.get('website') if url_type in ('facebook', 'instagram') else None
            analysis_result = analyze_with_gemini(
                url,
                business_name=business.get('name', ''),
                business_category=business.get('category', ''),
                url_type=url_type,
                website_url_for_serper=website_url
            )
        else:
            if url_type != 'website':
                return jsonify({'success': False, 'error': 'Facebook/Instagram analysis requires GEMINI_API_KEY'})
            analysis_result = analyzer.analyze_website(url)
        
        # Store analysis in MongoDB
        collection.update_one(
            {'_id': ObjectId(item_id)},
            {'$set': {'analysis': analysis_result}}
        )
        
        # Check if analysis failed
        if analysis_result.get('status') == 'failed':
            return jsonify({
                'success': True,
                'status': 'failed',
                'error': analysis_result.get('error', 'Analysis failed')
            })
        
        return jsonify({
            'success': True,
            'status': 'completed',  # Frontend expects 'completed' for success
            'summary': 'Analysis completed successfully'
        })

        
    except Exception as e:
        print(f"Error in analysis: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/analyze_link', methods=['POST'])
def analyze_link_endpoint():
    """Direct link analysis: paste any website or Facebook URL, get report. No DB storage."""
    import os
    try:
        data = request.get_json(silent=True) or {}
        url = (data.get('url') or '').strip()
        url_type = (data.get('url_type') or 'website').strip().lower()
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'})
        
        if url_type not in ('website', 'facebook'):
            return jsonify({'success': False, 'error': 'url_type must be website or facebook'})
        
        if not url.startswith('http'):
            url = 'https://' + url
        
        if not os.getenv('GEMINI_API_KEY'):
            return jsonify({'success': False, 'error': 'GEMINI_API_KEY not configured'})
        
        from .gemini_analyzer import analyze_with_gemini
        analysis_result = analyze_with_gemini(
            url,
            business_name='',
            business_category='',
            url_type=url_type,
            website_url_for_serper=url if url_type == 'website' else None  # Serper uses URL domain for website
        )
        
        if analysis_result.get('status') == 'failed':
            return jsonify({'success': False, 'error': analysis_result.get('error', 'Analysis failed')})
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'url': url,
            'url_type': url_type
        })
    except Exception as e:
        print(f"Error in analyze_link: {e}")
        return jsonify({'success': False, 'error': str(e)})


@main.route('/get_analysis/<item_id>')
def get_analysis_endpoint(item_id):
    """Retrieve stored analysis data"""
    try:
        collection = get_db_connection()
        business = collection.find_one({'_id': ObjectId(item_id)})
        
        if not business:
            return jsonify({'success': False, 'error': 'Business not found'})
        
        analysis = business.get('analysis')
        if not analysis:
            return jsonify({'success': False, 'error': 'No analysis data available'})
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'business_name': business.get('name'),
            'website': business.get('website')
        })
        
    except Exception as e:
        print(f"Error retrieving analysis: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/save_note/<item_id>', methods=['POST'])
def save_note(item_id):
    """Save a note for a business"""
    try:
        text = request.form.get('text', '')
        image_file = request.files.get('image')
        
        note_data = {'text': text}
        
        # Handle image upload
        if image_file:
            import base64
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            note_data['image'] = f"data:image/{image_file.filename.split('.')[-1]};base64,{image_data}"
        
        collection = get_db_connection()
        result = collection.update_one(
            {'_id': ObjectId(item_id)},
            {'$set': {'note': note_data}}
        )
        
        return jsonify({'success': result.modified_count > 0 or result.matched_count > 0})
    except Exception as e:
        print(f"Error saving note: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/generate_email_from_analysis', methods=['POST'])
def generate_email_from_analysis():
    """Generate cold email from analysis (for Link Analyzer - no item_id). Accepts analysis, url, template_type."""
    try:
        data = request.get_json() or {}
        analysis = data.get('analysis')
        url = (data.get('url') or '').strip()
        template_type = int(data.get('template_type', 1))
        if not analysis or not isinstance(analysis, dict):
            return jsonify({'success': False, 'error': 'analysis required'})
        place = {'name': '', 'category': '', 'website': url}
        from .gemini_analyzer import generate_email_with_gemini
        result = generate_email_with_gemini(
            place=place,
            analysis=analysis,
            note_text='',
            template_type=template_type,
            custom_prompt=''
        )
        if result.get('status') == 'failed':
            return jsonify({'success': False, 'error': result.get('error', 'Generation failed')})
        return jsonify({'success': True, 'subject': result.get('subject', ''), 'body': result.get('body', '')})
    except Exception as e:
        print(f"Error in generate_email_from_analysis: {e}")
        return jsonify({'success': False, 'error': str(e)})


@main.route('/generate_email', methods=['POST'])
def generate_email():
    """Generate cold email with Gemini using Analysis + Notes. Returns subject and body."""
    try:
        data = request.get_json() or {}
        item_id = data.get('item_id') or data.get('place_id')
        template_type = int(data.get('template_type', 1))
        custom_prompt = (data.get('custom_prompt') or '').strip()

        if not item_id:
            return jsonify({'success': False, 'error': 'item_id required'})

        collection = get_db_connection()
        business = collection.find_one({'_id': ObjectId(item_id)})
        if not business:
            return jsonify({'success': False, 'error': 'Business not found'})

        analysis = business.get('analysis')
        note_data = business.get('note') or {}
        note_text = note_data.get('text', '') if isinstance(note_data, dict) else ''

        from .gemini_analyzer import generate_email_with_gemini
        result = generate_email_with_gemini(
            place=business,
            analysis=analysis,
            note_text=note_text,
            template_type=template_type,
            custom_prompt=custom_prompt
        )

        if result.get('status') == 'failed':
            err = result.get('error', 'Generation failed')
            return jsonify({'success': False, 'error': err})

        return jsonify({
            'success': True,
            'subject': result.get('subject', ''),
            'body': result.get('body', '')
        })
    except Exception as e:
        print(f"Error generating email: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/get_note/<item_id>')
def get_note(item_id):
    """Retrieve a note for a business"""
    try:
        collection = get_db_connection()
        business = collection.find_one({'_id': ObjectId(item_id)})
        
        if not business:
            return jsonify({'success': False, 'error': 'Business not found'})
        
        note = business.get('note')
        return jsonify({
            'success': True,
            'note': note if note else None
        })
    except Exception as e:
        print(f"Error retrieving note: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/delete_items', methods=['POST'])
def delete_items():
    """Delete multiple items by their IDs. Only items with status 'pending' can be deleted."""
    try:
        data = request.get_json()
        ids = data.get('ids', [])
        
        if not ids:
            return jsonify({'success': False, 'error': 'No IDs provided'})
        
        collection = get_db_connection()
        object_ids = [ObjectId(id) for id in ids]
        # Only delete items with status 'pending' (or missing/null)
        result = collection.delete_many({
            '_id': {'$in': object_ids},
            '$or': [
                {'status': 'pending'},
                {'status': None},
                {'status': {'$exists': False}}
            ]
        })
        
        return jsonify({
            'success': True,
            'deleted_count': result.deleted_count
        })
    except Exception as e:
        print(f"Error deleting items: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/sent_email', methods=['POST'])
@login_required
def save_sent_email():
    """Save a sent email to the sent_emails collection"""
    try:
        data = request.get_json()
        to_email = data.get('to', '').strip()
        subject = data.get('subject', '').strip()
        body = data.get('body', '').strip()
        lead_name = data.get('lead_name', '')
        lead_id = data.get('lead_id', '')

        if not to_email or not subject:
            return jsonify({'success': False, 'error': 'To and Subject required'}), 400

        from datetime import datetime
        collection = get_sent_emails_collection()
        doc = {
            'user_id': str(current_user.id),
            'user_email': current_user.email,
            'to': to_email,
            'subject': subject,
            'body': body,
            'lead_name': lead_name,
            'lead_id': lead_id,
            'sent_at': datetime.utcnow(),
        }
        result = collection.insert_one(doc)
        doc['_id'] = str(result.inserted_id)
        doc['sent_at'] = doc['sent_at'].isoformat()
        return jsonify({'success': True, 'email': doc})
    except Exception as e:
        print(f"Error saving sent email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/sent_emails')
@login_required
def list_sent_emails():
    """List sent emails for current user"""
    try:
        collection = get_sent_emails_collection()
        user_id = str(current_user.id)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        skip = (page - 1) * per_page

        cursor = collection.find({'user_id': user_id}).sort('sent_at', -1).skip(skip).limit(per_page)
        emails = list(cursor)
        total = collection.count_documents({'user_id': user_id})

        for e in emails:
            e['_id'] = str(e['_id'])
            if hasattr(e.get('sent_at'), 'isoformat'):
                e['sent_at'] = e['sent_at'].isoformat()

        return jsonify({
            'emails': emails,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        print(f"Error listing sent emails: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/download_excel')
def download_excel():
    from flask import send_file
    try:
        # data/ is in project root, we are in app/routes.py (but running from project root)
        # Flask's send_file with relative path is relative to root_path of app.
        # run.py is in root. So 'data/...' should work.
        return send_file('data/consolidated_data.xlsx', as_attachment=True)
    except:
        return "Master file not found yet.", 404
