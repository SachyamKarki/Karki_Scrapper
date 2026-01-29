from flask import Blueprint, render_template, abort, request, jsonify
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from .database import get_users_collection

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@login_required
def dashboard():
    if not current_user.is_admin:
        abort(403) # Forbidden
    
    data = {
        'users': [],
        'stats': {},
        'moderation_items': []
    }
    
    if current_user.is_superadmin:
        # Superadmin: User Management + Stats
        users_collection = get_users_collection()
        users = list(users_collection.find())
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
            if 'password_hash' in user:
                del user['password_hash']
        data['users'] = users
        
        from .database import get_db_connection
        places_collection = get_db_connection()
        data['stats'] = {
            'total_users': len(data['users']),
            'total_places': places_collection.count_documents({}),
            'approved_places': places_collection.count_documents({'status': 'approved'})
        }
    else:
        # Regular Admin: Data Moderation
        from .database import get_db_connection
        places_collection = get_db_connection()
        # Show last 100 items for moderation
        moderation_items = list(places_collection.find().sort('_id', -1).limit(100))
        for item in moderation_items:
            item['_id'] = str(item['_id'])
        data['moderation_items'] = moderation_items
    
    if request.accept_mimetypes.accept_json:
        return jsonify(data)
        
    return render_template('admin_dashboard.html', **data)

@admin.route('/delete_user/<user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_superadmin:
        abort(403)
    
    users_collection = get_users_collection()
    users_collection.delete_one({'_id': ObjectId(user_id)})
    return jsonify({'success': True})

@admin.route('/update_role/<user_id>', methods=['POST'])
@login_required
def update_role(user_id):
    if not current_user.is_superadmin:
        abort(403)
    
    new_role = request.json.get('role')
    if new_role not in ['user', 'admin', 'superadmin']:
        return jsonify({'success': False, 'error': 'Invalid role'})
        
    users_collection = get_users_collection()
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'role': new_role}}
    )
    return jsonify({'success': True})
