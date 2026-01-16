from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from bson.objectid import ObjectId
import subprocess
import uuid
from website_analyzer import analyzer
from .database import get_db_connection

# Create Blueprint
main = Blueprint('main', __name__)

# Global to store current session
CURRENT_BATCH_ID = None

def render_dashboard(places, title="Dashboard", show_join=False, is_scrappy=False, pagination=None):
    # Render the template from file instead of string
    return render_template('dashboard.html', places=places, title=title, show_join=show_join, is_scrappy=is_scrappy, batch_id=CURRENT_BATCH_ID, pagination=pagination)

@main.route('/')
def index():
    page = int(request.args.get('page', 1))
    per_page = 50 
    
    skip = (page - 1) * per_page
    
    collection = get_db_connection()
    total_count = collection.count_documents({})
    
    # Fetch slice
    places = list(collection.find().sort('_id', -1).skip(skip).limit(per_page))
    
    total_pages = (total_count + per_page - 1) // per_page
    
    # Windowed Pagination Logic
    show_pages = set()
    show_pages.add(1)
    if total_pages > 0: show_pages.add(total_pages)
    
    # Show current +/- 2
    for p in range(max(1, page - 2), min(total_pages + 1, page + 3)):
        show_pages.add(p)
        
    ordered_pages = sorted(list(show_pages))
    display_pages = []
    
    for i, p in enumerate(ordered_pages):
        # If gap > 1, add None (ellipse)
        if i > 0 and p > ordered_pages[i-1] + 1:
            display_pages.append(None)
        display_pages.append(p)
    
    pagination = {
        'current_page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'total_items': total_count,
        'has_next': page < total_pages,
        'has_prev': page > 1,
        'next_page': page + 1,
        'prev_page': page - 1,
        'display_pages': display_pages
    }
    
    return render_dashboard(places, title="Dashboard", show_join=False, is_scrappy=False, pagination=pagination)

@main.route('/scrape', methods=['POST'])
def scrape():
    global CURRENT_BATCH_ID
    query = request.form.get('query')
    if query:
        # Generate new Batch ID (still useful for tracking origin)
        CURRENT_BATCH_ID = str(uuid.uuid4())
        print(f"Triggering scrape for: {query} (Batch: {CURRENT_BATCH_ID})")
        
        try:
            # Pass Query and Batch ID to run.sh
            subprocess.run(["./run.sh", query, CURRENT_BATCH_ID], check=True)
        except Exception as e:
            return f"Error running scraper: {e}", 500
    return redirect(url_for('main.index'))

@main.route('/api/update_status', methods=['POST'])
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

@main.route('/api/updates')
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

@main.route('/api/analyze/<item_id>', methods=['POST'])
def analyze_website_endpoint(item_id):
    """Trigger website analysis for a business"""
    try:
        collection = get_db_connection()
        
        # Get the business data
        business = collection.find_one({'_id': ObjectId(item_id)})
        if not business:
            return jsonify({'success': False, 'error': 'Business not found'})
        
        website = business.get('website')
        if not website:
            return jsonify({'success': False, 'error': 'No website URL available'})
        
        # Run analysis
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

@main.route('/api/get_analysis/<item_id>')
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

@main.route('/api/save_note/<item_id>', methods=['POST'])
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

@main.route('/api/get_note/<item_id>')
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

@main.route('/api/delete_items', methods=['POST'])
def delete_items():
    """Delete multiple items by their IDs"""
    try:
        data = request.get_json()
        ids = data.get('ids', [])
        
        if not ids:
            return jsonify({'success': False, 'error': 'No IDs provided'})
        
        collection = get_db_connection()
        object_ids = [ObjectId(id) for id in ids]
        result = collection.delete_many({'_id': {'$in': object_ids}})
        
        return jsonify({
            'success': True,
            'deleted_count': result.deleted_count
        })
    except Exception as e:
        print(f"Error deleting items: {e}")
        return jsonify({'success': False, 'error': str(e)})

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
