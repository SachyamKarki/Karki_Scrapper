from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from .database import get_users_collection

class User(UserMixin):
    def __init__(self, email, password_hash, role='user', _id=None):
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.id = str(_id) if _id else None

    @staticmethod
    def get_by_email(email):
        users = get_users_collection()
        user_data = users.find_one({'email': email})
        if user_data:
            return User(
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                role=user_data.get('role', 'user'),
                _id=user_data['_id']
            )
        return None

    @staticmethod
    def get_by_id(user_id):
        users = get_users_collection()
        try:
            user_data = users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    role=user_data.get('role', 'user'),
                    _id=user_data['_id']
                )
        except:
            return None
        return None

    @staticmethod
    def create(email, password, role='user'):
        users = get_users_collection()
        if users.find_one({'email': email}):
            return None # User exists
        
        password_hash = generate_password_hash(password)
        result = users.insert_one({
            'email': email,
            'password_hash': password_hash,
            'role': role
        })
        return User(email, password_hash, role, result.inserted_id)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        return self.role in ['admin', 'superadmin']
    
    @property
    def is_superadmin(self):
        return self.role == 'superadmin'
