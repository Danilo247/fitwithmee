from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

# Role constants
ROLE_ADMIN = 'admin'
ROLE_CUSTOMER = 'customer'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_CUSTOMER)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'verified': self.verified,
            'role': self.role
        }
    
    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN
    
    @property
    def is_customer(self):
        return self.role == ROLE_CUSTOMER

class VerificationToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, token, email):
        self.token = token
        self.email = email
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(hours=24)  # Token expires in 24 hours
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at 