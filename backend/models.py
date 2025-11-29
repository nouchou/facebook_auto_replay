"""
Modèles de base de données - MESSAGES UNIQUEMENT
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class FacebookPage(db.Model):
    """Pages Facebook connectées"""
    __tablename__ = 'facebook_pages'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.String(100), unique=True, nullable=False)
    page_name = db.Column(db.String(200))
    access_token = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    messages = db.relationship('Message', backref='page', lazy=True, cascade='all, delete-orphan')

class Message(db.Model):
    """Messages Messenger reçus et envoyés"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(100), unique=True)
    sender_id = db.Column(db.String(100))
    sender_name = db.Column(db.String(200))
    message_text = db.Column(db.Text)
    response_sent = db.Column(db.Text)
    is_automated = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Clé étrangère
    page_id = db.Column(db.Integer, db.ForeignKey('facebook_pages.id'), nullable=True)

class AutoResponse(db.Model):
    """Réponses automatiques configurées"""
    __tablename__ = 'auto_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    trigger_keyword = db.Column(db.String(200), nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    response_type = db.Column(db.String(20), default='message') 
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)