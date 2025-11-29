from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class FacebookPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.String(100), unique=True, nullable=False)
    page_name = db.Column(db.String(200))
    access_token = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AutoResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trigger_keyword = db.Column(db.String(200), nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    response_type = db.Column(db.String(50))  # message, comment, both
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(100), unique=True)
    sender_id = db.Column(db.String(100))
    sender_name = db.Column(db.String(200))
    message_text = db.Column(db.Text)
    response_sent = db.Column(db.Text)
    is_automated = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    page_id = db.Column(db.Integer, db.ForeignKey('facebook_page.id'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.String(100), unique=True)
    post_id = db.Column(db.String(100))
    user_id = db.Column(db.String(100))
    user_name = db.Column(db.String(200))
    comment_text = db.Column(db.Text)
    response_sent = db.Column(db.Text)
    is_automated = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    page_id = db.Column(db.Integer, db.ForeignKey('facebook_page.id'))