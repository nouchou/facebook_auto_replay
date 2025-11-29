"""
Routes d'authentification
"""
from flask import request, jsonify
from routes import auth_bp  # ✅ Importer depuis __init__.py
from models import db
import jwt
import datetime
from config import Config

@auth_bp.route('/login', methods=['POST'])
def login():
    """Connexion utilisateur"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if username == 'admin' and password == 'admin':
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }, Config.SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': username
        }), 200
    
    return jsonify({'error': 'Identifiants invalides'}), 401

@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """Vérifier le token JWT"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return jsonify({'valid': True, 'user': payload['user']}), 200
    except:
        return jsonify({'valid': False}), 401