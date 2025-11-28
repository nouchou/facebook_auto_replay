from flask import request, jsonify
from routes import facebook_bp
from models import db, FacebookPage
from services.facebook_service import FacebookService
import requests

@facebook_bp.route('/pages', methods=['GET'])
def get_pages():
    """Récupérer toutes les pages connectées"""
    pages = FacebookPage.query.all()
    return jsonify([{
        'id': p.id,
        'page_id': p.page_id,
        'page_name': p.page_name,
        'is_active': p.is_active,
        'created_at': p.created_at.isoformat()
    } for p in pages])

@facebook_bp.route('/pages', methods=['POST'])
def connect_page():
    """Connecter une nouvelle page Facebook"""
    data = request.get_json()
    
    # Vérifier si la page existe déjà
    page = FacebookPage.query.filter_by(page_id=data['page_id']).first()
    
    if page:
        # Mettre à jour
        page.access_token = data['access_token']
        page.page_name = data.get('page_name', page.page_name)
        page.is_active = True
    else:
        # Créer nouvelle page
        page = FacebookPage(
            page_id=data['page_id'],
            page_name=data.get('page_name', 'Ma Page'),
            access_token=data['access_token'],
            is_active=True
        )
        db.session.add(page)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Page connectée avec succès',
        'page': {
            'id': page.id,
            'page_id': page.page_id,
            'page_name': page.page_name
        }
    }), 201

@facebook_bp.route('/pages/<int:page_id>', methods=['DELETE'])
def disconnect_page(page_id):
    """Déconnecter une page"""
    page = FacebookPage.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    return jsonify({'message': 'Page déconnectée'}), 200

@facebook_bp.route('/pages/<int:page_id>/toggle', methods=['PUT'])
def toggle_page(page_id):
    """Activer/désactiver une page"""
    page = FacebookPage.query.get_or_404(page_id)
    page.is_active = not page.is_active
    db.session.commit()
    return jsonify({
        'message': 'Statut modifié',
        'is_active': page.is_active
    }), 200

@facebook_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """Tester la connexion Facebook"""
    data = request.get_json()
    access_token = data.get('access_token')
    
    try:
        fb_service = FacebookService(access_token)
        # Tester en récupérant les infos de la page
        response = requests.get(
            f'https://graph.facebook.com/v18.0/me',
            params={'access_token': access_token}
        )
        
        if response.status_code == 200:
            page_info = response.json()
            
            # Tester aussi les permissions
            perms = fb_service.test_permissions()
            
            return jsonify({
                'success': True,
                'page_info': page_info,
                'permissions': perms
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Token invalide'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 🆕 NOUVELLES ROUTES POUR WEBHOOKS

@facebook_bp.route('/pages/<int:page_id>/subscribe-webhooks', methods=['POST'])
def subscribe_webhooks(page_id):
    """
    CRITIQUE: Abonner la page aux événements webhook
    Sans ceci, les commentaires ne fonctionnent PAS!
    """
    try:
        page = FacebookPage.query.get_or_404(page_id)
        
        url = f'https://graph.facebook.com/v18.0/{page.page_id}/subscribed_apps'
        
        payload = {
            'subscribed_fields': [
                'messages',           # Messages Messenger
                'messaging_postbacks',# Boutons
                'message_deliveries', # Livraison
                'message_reads',      # Lu
                'feed',              # Posts et commentaires (CRITIQUE!)
                'comments',          # Commentaires
                'mention'            # Mentions
            ],
            'access_token': page.access_token
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        print(f"📡 Abonnement webhook: {result}")
        
        if response.status_code == 200 and result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Page abonnée aux webhooks!',
                'subscribed_fields': payload['subscribed_fields']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', {}).get('message', 'Erreur'),
                'details': result
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@facebook_bp.route('/pages/<int:page_id>/webhook-status', methods=['GET'])
def check_webhook_status(page_id):
    """Vérifier le statut d'abonnement webhook"""
    try:
        page = FacebookPage.query.get_or_404(page_id)
        
        url = f'https://graph.facebook.com/v18.0/{page.page_id}/subscribed_apps'
        
        response = requests.get(url, params={
            'access_token': page.access_token
        })
        
        result = response.json()
        
        if response.status_code == 200:
            subscribed_data = result.get('data', [])
            
            if subscribed_data:
                app_data = subscribed_data[0]
                subscribed_fields = app_data.get('subscribed_fields', [])
                
                critical_fields = ['feed', 'comments', 'messages']
                missing_fields = [f for f in critical_fields if f not in subscribed_fields]
                
                return jsonify({
                    'success': True,
                    'is_subscribed': True,
                    'subscribed_fields': subscribed_fields,
                    'missing_critical_fields': missing_fields,
                    'all_ok': len(missing_fields) == 0
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'is_subscribed': False,
                    'message': 'Page non abonnée'
                }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', {}).get('message')
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500