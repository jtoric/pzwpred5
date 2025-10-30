from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from bson import ObjectId

class User(UserMixin):
    """User model za Flask-Login i MongoDB"""
    
    def __init__(self, user_data):
        """Inicijalizira User objekt iz MongoDB dokumenta"""
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data.get('email', '')
        self.password_hash = user_data['password_hash']
        self.email_verified = user_data.get('email_verified', False)
    
    @staticmethod
    def _get_collection():
        """Dohvaća users kolekciju iz current_app.config"""
        return current_app.config['USERS_COLLECTION']
    
    @staticmethod
    def _get_serializer():
        """Dohvaća URLSafeTimedSerializer za generiranje i verifikaciju tokena"""
        secret_key = current_app.config['SECRET_KEY']
        return URLSafeTimedSerializer(secret_key)
    
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
            'password_hash': password_hash,
            'email_verified': False
        }
        
        result = users_collection.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)
    
    @staticmethod
    def verify_email(token):
        """Verificira email adresu koristeći token (token traje 1 sat)"""
        serializer = User._get_serializer()
        users_collection = User._get_collection()
        
        try:
            # Dekodiraj token i dobij user_id (automatski provjerava isteak)
            user_id = serializer.loads(token, max_age=3600)  # 3600 sekundi = 1 sat
        except SignatureExpired:
            return None, 'Verifikacijski token je istekao. Molimo zatražite novi verifikacijski email.'
        except BadSignature:
            return None, 'Nevažeći verifikacijski token'
        
        # Dohvati korisnika
        try:
            user_data = users_collection.find_one({'_id': ObjectId(user_id)})
        except:
            return None, 'Nevažeći verifikacijski token'
        
        if not user_data:
            return None, 'Nevažeći verifikacijski token'
        
        if user_data.get('email_verified', False):
            return None, 'Email adresa je već verificirana'
        
        # Ažuriraj korisnika kao verificiranog
        users_collection.update_one(
            {'_id': user_data['_id']},
            {'$set': {'email_verified': True}}
        )
        
        # Dohvati ažurirani dokument
        updated_user_data = users_collection.find_one({'_id': user_data['_id']})
        return User(updated_user_data), None
    
    def generate_verification_token(self):
        """Generira verifikacijski token koji traje 1 sat"""
        serializer = User._get_serializer()
        # Token sadrži user_id i automatski ističe za 1 sat
        return serializer.dumps(self.id)
    
    def check_password(self, password):
        """Provjeri lozinku"""
        return check_password_hash(self.password_hash, password)

