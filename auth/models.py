from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from bson import ObjectId

class User(UserMixin):
    """User model za Flask-Login i MongoDB"""
    
    def __init__(self, user_data):
        """Inicijalizira User objekt iz MongoDB dokumenta"""
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data.get('email', '')
        self.password_hash = user_data['password_hash']
    
    @staticmethod
    def _get_collection():
        """Dohvaća users kolekciju iz current_app.config"""
        return current_app.config['USERS_COLLECTION']
    
    @staticmethod
    def get_by_id(user_id):
        """Dohvaća korisnika po ID-u"""
        try:
            users_collection = User._get_collection()
            user_data = users_collection.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            pass
        return None
    
    @staticmethod
    def get_by_username(username):
        """Dohvaća korisnika po korisničkom imenu"""
        users_collection = User._get_collection()
        user_data = users_collection.find_one({'username': username})
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_by_email(email):
        """Dohvaća korisnika po email adresi"""
        users_collection = User._get_collection()
        user_data = users_collection.find_one({'email': email})
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def create(username, email, password):
        """Kreira novog korisnika"""
        users_collection = User._get_collection()
        
        # Provjeri da li korisnik već postoji
        if users_collection.find_one({'username': username}):
            raise ValueError('Korisničko ime već postoji')
        
        if users_collection.find_one({'email': email}):
            raise ValueError('Email adresa već postoji')
        
        # Kreiraj novog korisnika
        password_hash = generate_password_hash(password)
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash
        }
        
        result = users_collection.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)
    
    def check_password(self, password):
        """Provjeri lozinku"""
        return check_password_hash(self.password_hash, password)

