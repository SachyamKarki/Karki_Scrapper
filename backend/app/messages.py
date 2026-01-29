from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
from bson.objectid import ObjectId
from .database import get_db_connection, get_users_collection
from .models import User

messages = Blueprint('messages', __name__)

def get_messages_collection():
    """Get the messages collection from MongoDB"""
    db = get_db_connection().database
    return db['messages']

def get_dm_room_name(user1_id, user2_id):
    """Generate consistent room name for DM between two users"""
    ids = sorted([str(user1_id), str(user2_id)])
    return f"dm_{ids[0]}_{ids[1]}"

# ===== TEAM CHAT ENDPOINTS =====

@messages.route('/history')
@login_required
def get_history():
    """Get recent team chat message history"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        collection = get_messages_collection()
        # Get last 100 team chat messages
        messages_list = list(collection.find({'conversation_type': 'team'}).sort('timestamp', -1).limit(100))
        
        # Reverse to show oldest first
        messages_list.reverse()
        
        # Convert ObjectId to string
        for msg in messages_list:
            msg['_id'] = str(msg['_id'])
            
        return jsonify({'messages': messages_list})
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return jsonify({'error': str(e)}), 500

@messages.route('/admins')
@login_required
def get_admins():
    """Get all registered admins for team chat - visible to admins even if no messages exchanged"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        users_collection = get_users_collection()
        admins = list(users_collection.find({'role': {'$in': ['admin', 'superadmin']}}, {'email': 1, 'role': 1}).sort('email', 1))
        formatted = [{'id': str(u['_id']), 'email': ((u.get('email') or '').strip() or 'Unknown'), 'role': u.get('role') or 'user', 'is_you': str(u['_id']) == str(current_user.id)} for u in admins]
        return jsonify({'admins': formatted})
    except Exception as e:
        print(f"Error fetching admins: {e}")
        return jsonify({'error': str(e)}), 500

# ===== DIRECT MESSAGE ENDPOINTS =====

@messages.route('/conversations')
@login_required
def get_conversations():
    """Get list of all DM conversations for current user. For admins, also include all other admin users even if no message sent yet."""
    try:
        collection = get_messages_collection()
        user_id = str(current_user.id)
        
        # Find all DM messages where user is participant
        pipeline = [
            {
                '$match': {
                    'conversation_type': 'dm',
                    'participants': user_id
                }
            },
            {
                '$sort': {'timestamp': -1}
            },
            {
                '$group': {
                    '_id': '$participants',
                    'last_message': {'$first': '$$ROOT'},
                    'unread_count': {
                        '$sum': {
                            '$cond': [
                                {
                                    '$and': [
                                        {'$ne': ['$sender_id', user_id]},
                                        {'$eq': ['$read', False]}
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    }
                }
            }
        ]
        
        conversations = list(collection.aggregate(pipeline))
        
        # Format conversations with user details
        formatted_conversations = []
        seen_user_ids = set()
        for conv in conversations:
            participants = conv['_id']
            other_user_id = [p for p in participants if p != user_id][0]
            other_user = User.get_by_id(other_user_id)
            
            if other_user:
                seen_user_ids.add(other_user_id)
                last_msg = conv['last_message']
                last_msg['_id'] = str(last_msg['_id'])
                
                formatted_conversations.append({
                    'user_id': other_user_id,
                    'user_email': (other_user.email or '').strip() or 'Unknown',
                    'user_role': other_user.role,
                    'last_message': last_msg,
                    'unread_count': conv.get('unread_count', 0),
                    'is_admin': other_user.role in ['admin', 'superadmin']
                })
        
        # Add other users who don't have a conversation yet - admins always see other admins, everyone sees all users
        users_collection = get_users_collection()
        try:
            current_id = ObjectId(current_user.id)
        except (TypeError, ValueError):
            current_id = None
        base_query = {'_id': {'$ne': current_id}} if current_id else {}
        placeholder_msg = {'message': 'No messages yet — click to start', 'timestamp': datetime.min}
        # For admins: ALWAYS add other admins first (even with zero messages exchanged)
        if current_user.is_admin:
            admin_query = {**base_query, 'role': {'$in': ['admin', 'superadmin']}}
            admin_users = list(users_collection.find(admin_query, {'email': 1, 'role': 1}))
            for u in admin_users:
                uid = str(u['_id'])
                if uid not in seen_user_ids:
                    seen_user_ids.add(uid)
                    formatted_conversations.append({
                        'user_id': uid,
                        'user_email': ((u.get('email') or '').strip() or 'Unknown'),
                        'user_role': u.get('role') or 'user',
                        'last_message': placeholder_msg,
                        'unread_count': 0,
                        'is_admin': True  # flag for sorting
                    })
        # Add ALL other users (everyone sees everyone, including admins for regular users)
        all_other_users = list(users_collection.find(base_query, {'email': 1, 'role': 1}))
        for u in all_other_users:
            uid = str(u['_id'])
            if uid not in seen_user_ids:
                seen_user_ids.add(uid)
                formatted_conversations.append({
                    'user_id': uid,
                    'user_email': ((u.get('email') or '').strip() or 'Unknown'),
                    'user_role': u.get('role') or 'user',
                    'last_message': placeholder_msg,
                    'unread_count': 0,
                    'is_admin': u.get('role') in ['admin', 'superadmin']
                })
        
        # Sort: existing conversations first (by last message time desc), then users with no messages
        # For admins: other admins first in no-messages section, then by email
        with_messages = [c for c in formatted_conversations if not c['last_message'].get('message', '').startswith('No messages yet')]
        no_messages = [c for c in formatted_conversations if c['last_message'].get('message', '').startswith('No messages yet')]
        with_messages.sort(key=lambda x: x['last_message'].get('timestamp', datetime.min), reverse=True)
        if current_user.is_admin:
            no_messages.sort(key=lambda x: (0 if x.get('is_admin') else 1, x['user_email'].lower()))
        else:
            no_messages.sort(key=lambda x: x['user_email'].lower())
        formatted_conversations = with_messages + no_messages
        
        return jsonify({'conversations': formatted_conversations})
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        return jsonify({'error': str(e)}), 500

@messages.route('/dm/<recipient_id>')
@login_required
def get_dm_history(recipient_id):
    """Get message history with a specific user"""
    try:
        collection = get_messages_collection()
        user_id = str(current_user.id)
        
        # Get messages between current user and recipient
        participants = sorted([user_id, recipient_id])
        messages_list = list(collection.find({
            'conversation_type': 'dm',
            'participants': {'$all': participants}
        }).sort('timestamp', 1).limit(100))
        
        # Mark messages as read
        collection.update_many(
            {
                'conversation_type': 'dm',
                'participants': {'$all': participants},
                'sender_id': recipient_id,
                'read': False
            },
            {'$set': {'read': True}}
        )
        
        # Convert ObjectId to string
        for msg in messages_list:
            msg['_id'] = str(msg['_id'])
        
        # Get recipient info
        recipient = User.get_by_id(recipient_id)
        recipient_info = {
            'id': recipient_id,
            'email': recipient.email if recipient else 'Unknown',
            'role': recipient.role if recipient else 'user'
        }
        
        return jsonify({
            'messages': messages_list,
            'recipient': recipient_info
        })
    except Exception as e:
        print(f"Error fetching DM history: {e}")
        return jsonify({'error': str(e)}), 500

@messages.route('/dm/send', methods=['POST'])
@login_required
def send_dm():
    """Send a direct message"""
    try:
        data = request.get_json()
        recipient_id = data.get('recipient_id')
        message_text = data.get('message', '').strip()
        
        if not recipient_id or not message_text:
            return jsonify({'error': 'Recipient and message required'}), 400
        
        collection = get_messages_collection()
        participants = sorted([str(current_user.id), recipient_id])
        
        message_doc = {
            'conversation_type': 'dm',
            'participants': participants,
            'sender_id': str(current_user.id),
            'sender_email': current_user.email,
            'recipient_id': recipient_id,
            'message': message_text,
            'timestamp': datetime.utcnow(),
            'read': False
        }
        
        result = collection.insert_one(message_doc)
        message_doc['_id'] = str(result.inserted_id)
        
        return jsonify({'success': True, 'message': message_doc})
    except Exception as e:
        print(f"Error sending DM: {e}")
        return jsonify({'error': str(e)}), 500

@messages.route('/users')
@login_required
def get_users():
    """Get all users for starting conversations"""
    try:
        users_collection = get_users_collection()
        try:
            current_id = ObjectId(current_user.id)
        except (TypeError, ValueError):
            current_id = None

        # Get all users except current user (use ObjectId for MongoDB _id)
        query = {}
        if current_id:
            query['_id'] = {'$ne': current_id}
        users = list(users_collection.find(query, {'email': 1, 'role': 1}))
        
        # Format users
        formatted_users = []
        for u in users:
            formatted_users.append({
                'id': str(u['_id']),
                'email': u.get('email', 'Unknown'),
                'role': u.get('role', 'user')
            })
        
        return jsonify({'users': formatted_users})
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({'error': str(e)}), 500

@messages.route('/conversations/delete', methods=['POST'])
@login_required
def delete_conversation():
    """Delete all messages in a conversation"""
    try:
        data = request.get_json()
        other_user_id = data.get('user_id')
        
        if not other_user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        collection = get_messages_collection()
        user_id = str(current_user.id)
        participants = sorted([user_id, other_user_id])
        
        # Delete all messages in this conversation
        result = collection.delete_many({
            'conversation_type': 'dm',
            'participants': {'$all': participants}
        })
        
        return jsonify({
            'success': True,
            'deleted_count': result.deleted_count
        })
    except Exception as e:
        print(f"Error deleting conversation: {e}")
        return jsonify({'error': str(e)}), 500

# ===== WEBSOCKET EVENT HANDLERS =====

def register_socketio_events(socketio):
    """Register Socket.IO event handlers"""
    
    # ===== TEAM CHAT EVENTS =====
    
    @socketio.on('join_chat')
    def handle_join(data):
        """Handle user joining the team chat room"""
        if not current_user.is_authenticated or not current_user.is_admin:
            return
        
        room = 'admin_chat'
        join_room(room)
        
        # Notify others that user joined
        emit('user_joined', {
            'email': current_user.email,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room, skip_sid=request.sid)
    
    @socketio.on('send_message')
    def handle_message(data):
        """Handle incoming team chat message"""
        if not current_user.is_authenticated or not current_user.is_admin:
            return
        
        message_text = data.get('message', '').strip()
        if not message_text:
            return
        
        # Save to database
        collection = get_messages_collection()
        message_doc = {
            'conversation_type': 'team',
            'sender_id': str(current_user.id),
            'sender_email': current_user.email,
            'message': message_text,
            'timestamp': datetime.utcnow(),
            'room': 'admin_chat'
        }
        
        result = collection.insert_one(message_doc)
        message_doc['_id'] = str(result.inserted_id)
        message_doc['timestamp'] = message_doc['timestamp'].isoformat()
        
        # Broadcast to all users in the room
        emit('new_message', message_doc, room='admin_chat')
    
    @socketio.on('typing')
    def handle_typing(data):
        """Handle typing indicator for team chat"""
        if not current_user.is_authenticated or not current_user.is_admin:
            return
        
        emit('user_typing', {
            'email': current_user.email,
            'is_typing': data.get('is_typing', False)
        }, room='admin_chat', skip_sid=request.sid)
    
    # ===== DIRECT MESSAGE EVENTS =====
    
    @socketio.on('join_dm')
    def handle_join_dm(data):
        """Handle user joining a DM room"""
        if not current_user.is_authenticated:
            return
        
        other_user_id = data.get('user_id')
        if not other_user_id:
            return
        
        room = get_dm_room_name(current_user.id, other_user_id)
        join_room(room)
        
        # Notify other user
        emit('dm_user_joined', {
            'user_id': str(current_user.id),
            'email': current_user.email
        }, room=room, skip_sid=request.sid)
    
    @socketio.on('leave_dm')
    def handle_leave_dm(data):
        """Handle user leaving a DM room"""
        if not current_user.is_authenticated:
            return
        
        other_user_id = data.get('user_id')
        if not other_user_id:
            return
        
        room = get_dm_room_name(current_user.id, other_user_id)
        leave_room(room)
    
    @socketio.on('send_dm')
    def handle_send_dm(data):
        """Handle sending a direct message"""
        if not current_user.is_authenticated:
            return
        
        recipient_id = data.get('recipient_id')
        message_text = data.get('message', '').strip()
        
        if not recipient_id or not message_text:
            return
        
        # Save to database
        collection = get_messages_collection()
        participants = sorted([str(current_user.id), recipient_id])
        
        message_doc = {
            'conversation_type': 'dm',
            'participants': participants,
            'sender_id': str(current_user.id),
            'sender_email': current_user.email,
            'recipient_id': recipient_id,
            'message': message_text,
            'timestamp': datetime.utcnow(),
            'read': False
        }
        
        result = collection.insert_one(message_doc)
        message_doc['_id'] = str(result.inserted_id)
        message_doc['timestamp'] = message_doc['timestamp'].isoformat()
        
        # Send to DM room
        room = get_dm_room_name(current_user.id, recipient_id)
        emit('new_dm', message_doc, room=room)
    
    @socketio.on('dm_typing')
    def handle_dm_typing(data):
        """Handle typing indicator for DM"""
        if not current_user.is_authenticated:
            return
        
        recipient_id = data.get('recipient_id')
        if not recipient_id:
            return
        
        room = get_dm_room_name(current_user.id, recipient_id)
        emit('dm_user_typing', {
            'user_id': str(current_user.id),
            'email': current_user.email,
            'is_typing': data.get('is_typing', False)
        }, room=room, skip_sid=request.sid)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle user disconnection"""
        if current_user.is_authenticated and current_user.is_admin:
            emit('user_left', {
                'email': current_user.email,
                'timestamp': datetime.utcnow().isoformat()
            }, room='admin_chat', skip_sid=request.sid)
