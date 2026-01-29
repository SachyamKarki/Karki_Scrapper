from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from bson.objectid import ObjectId
import subprocess
import uuid
from website_analyzer import analyzer
from .database import get_db_connection, get_sent_emails_collection

# Create Blueprint
main = Blueprint('main', __name__)

# Global to store current session
CURRENT_BATCH_ID = None

def render_dashboard(places, title="Dashboard", show_join=False, is_scrappy=False, pagination=None):
    # Render the template from file instead of string
    return render_template('dashboard.html', places=places, title=title, show_join=show_join, is_scrappy=is_scrappy, batch_id=CURRENT_BATCH_ID, pagination=pagination, user=current_user)

@main.route('/')
@login_required
def index():
    # Redirect administrative roles to the panel (only if NOT an API call)
    if current_user.is_admin and not request.accept_mimetypes.accept_json:
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
            # Pass Query and Batch ID to run.sh
            subprocess.run(["./run.sh", query, CURRENT_BATCH_ID], check=True)
            
            if request.is_json or request.accept_mimetypes.accept_json:
                return jsonify({'success': True, 'batch_id': CURRENT_BATCH_ID, 'message': 'Scraping started successfully'})
                
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

@main.route('/analyze/<item_id>', methods=['POST'])
def analyze_website_endpoint(item_id):
    """Trigger website analysis for a business. Uses Gemini when GEMINI_API_KEY is set."""
    import os
    try:
        collection = get_db_connection()
        
        # Get the business data
        business = collection.find_one({'_id': ObjectId(item_id)})
        if not business:
            return jsonify({'success': False, 'error': 'Business not found'})
        
        website = business.get('website')
        if not website:
            return jsonify({'success': False, 'error': 'No website URL available'})
        
        # Use Gemini when API key is set, otherwise fallback to local analyzer
        if os.getenv('GEMINI_API_KEY'):
            from .gemini_analyzer import analyze_with_gemini
            analysis_result = analyze_with_gemini(
                website,
                business_name=business.get('name', ''),
                business_category=business.get('category', '')
            )
        else:
            analysis_result = analyzer.analyze_website(website)
        
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
