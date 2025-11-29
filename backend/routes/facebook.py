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
    
    required_fields = ['page_id', 'access_token']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Champ requis: {field}'}), 400
    
    # Vérifier si la page existe déjà
    page = FacebookPage.query.filter_by(page_id=data['page_id']).first()
    
    if page:
        # Mettre à jour
        page.access_token = data['access_token']
        page.page_name = data.get('page_name', page.page_name)
        page.is_active = True
        message = 'Page mise à jour avec succès'
    else:
        # Créer nouvelle page
        page = FacebookPage(
            page_id=data['page_id'],
            page_name=data.get('page_name', 'Ma Page'),
            access_token=data['access_token'],
            is_active=True
        )
        db.session.add(page)
        message = 'Page connectée avec succès'
    
    db.session.commit()
    
    return jsonify({
        'message': message,
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
    """Tester la connexion Facebook avec diagnostic complet"""
    data = request.get_json()
    access_token = data.get('access_token')
    
    if not access_token:
        return jsonify({'error': 'Token requis'}), 400
    
    try:
        fb_service = FacebookService(access_token)
        
        # Test 1: Récupérer les infos de la page
        response = requests.get(
            f'https://graph.facebook.com/v18.0/me',
            params={'access_token': access_token, 'fields': 'id,name'}
        )
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'Token invalide',
                'details': response.json()
            }), 400
        
        page_info = response.json()
        
        # Test 2: Vérifier les permissions
        perms = fb_service.test_permissions()
        
        return jsonify({
            'success': True,
            'page_info': page_info,
            'permissions': perms,
            'warnings': [] if perms.get('all_ok') else [
                'Certaines permissions sont manquantes',
                'Les commentaires pourraient ne pas fonctionner'
            ]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== WEBHOOKS ====================

@facebook_bp.route('/pages/<int:page_id>/subscribe-webhooks', methods=['POST'])
def subscribe_webhooks(page_id):
    """
    🔥 CRITIQUE: Abonner la page aux événements webhook
    SANS CECI, LES COMMENTAIRES NE FONCTIONNENT PAS!
    """
    try:
        page = FacebookPage.query.get_or_404(page_id)
        
        print("\n" + "="*60)
        print("📡 ABONNEMENT AUX WEBHOOKS")
        print("="*60)
        print(f"Page: {page.page_name}")
        print(f"Page ID: {page.page_id}")
        print("="*60)
        
        url = f'https://graph.facebook.com/v18.0/{page.page_id}/subscribed_apps'
        
        # ✅ CHAMPS VALIDES - SANS message_echoes pour éviter doublons
        subscribed_fields = [
            'messages',              # Messages Messenger
            'messaging_postbacks',   # Boutons Messenger
            'message_deliveries',    # Livraison messages
            'message_reads',         # Messages lus
            'feed',                  # 🔥 Posts ET commentaires (CRITIQUE!)
            'mention',               # Mentions de la page
            'messaging_referrals'    # Références
            # ❌ 'message_echoes' retiré pour éviter les doublons
        ]
        
        payload = {
            'subscribed_fields': ','.join(subscribed_fields),
            'access_token': page.access_token
        }
        
        print(f"\nChamps d'abonnement: {subscribed_fields}")
        print(f"\nEnvoi requête POST vers: {url}")
        print(f"Payload: {payload}")
        
        response = requests.post(url, data=payload)
        result = response.json()
        
        print(f"\nStatut: {response.status_code}")
        print(f"Réponse: {result}")
        print("="*60 + "\n")
        
        if response.status_code == 200 and result.get('success'):
            return jsonify({
                'success': True,
                'message': '✅ Page abonnée aux webhooks avec succès!',
                'subscribed_fields': subscribed_fields,
                'page_name': page.page_name
            }), 200
        else:
            error = result.get('error', {})
            return jsonify({
                'success': False,
                'error': error.get('message', 'Erreur inconnue'),
                'error_code': error.get('code'),
                'details': result
            }), 400
    
    except Exception as e:
        print(f"\n❌ Erreur abonnement webhooks: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@facebook_bp.route('/pages/<int:page_id>/webhook-status', methods=['GET'])
def check_webhook_status(page_id):
    """Vérifier le statut d'abonnement webhook avec diagnostic"""
    try:
        page = FacebookPage.query.get_or_404(page_id)
        
        url = f'https://graph.facebook.com/v18.0/{page.page_id}/subscribed_apps'
        
        response = requests.get(url, params={
            'access_token': page.access_token
        })
        
        result = response.json()
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': result.get('error', {}).get('message', 'Erreur'),
                'details': result
            }), 400
        
        subscribed_data = result.get('data', [])
        
        if subscribed_data:
            app_data = subscribed_data[0]
            subscribed_fields = app_data.get('subscribed_fields', [])
            
            # Champs critiques pour les commentaires
            critical_fields = {
                'feed': '🔥 Posts et commentaires',
                'comments': '🔥 Commentaires',
                'messages': '💬 Messages Messenger'
            }
            
            missing_fields = [
                field for field in critical_fields.keys() 
                if field not in subscribed_fields
            ]
            
            status = {
                'success': True,
                'is_subscribed': True,
                'subscribed_fields': subscribed_fields,
                'critical_fields': {},
                'missing_critical_fields': missing_fields,
                'all_ok': len(missing_fields) == 0
            }
            
            # Détailler les champs critiques
            for field, description in critical_fields.items():
                status['critical_fields'][field] = {
                    'subscribed': field in subscribed_fields,
                    'description': description
                }
            
            if missing_fields:
                status['warning'] = (
                    f"⚠️ {len(missing_fields)} champs critiques manquants. "
                    "Les commentaires pourraient ne pas fonctionner!"
                )
                status['action_required'] = (
                    f"Abonnez la page avec: POST /api/facebook/pages/{page_id}/subscribe-webhooks"
                )
            else:
                status['message'] = "✅ Tous les champs critiques sont abonnés!"
            
            return jsonify(status), 200
        else:
            return jsonify({
                'success': True,
                'is_subscribed': False,
                'message': '❌ Page NON abonnée aux webhooks',
                'action_required': (
                    f"Abonnez la page avec: POST /api/facebook/pages/{page_id}/subscribe-webhooks"
                )
            }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@facebook_bp.route('/pages/<int:page_id>/test-comment-reply', methods=['POST'])
def test_comment_reply(page_id):
    """
    Tester la capacité de répondre aux commentaires
    Body: {"comment_id": "123456_789"}
    """
    try:
        data = request.get_json()
        comment_id = data.get('comment_id')
        
        if not comment_id:
            return jsonify({
                'error': 'comment_id requis'
            }), 400
        
        page = FacebookPage.query.get_or_404(page_id)
        fb_service = FacebookService(page.access_token)
        
        # Test complet
        success = fb_service.test_comment_reply(comment_id, test_mode=False)
        
        if success:
            return jsonify({
                'success': True,
                'message': '✅ Test réussi! La réponse aux commentaires fonctionne.'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '❌ Test échoué. Vérifiez les logs pour plus de détails.'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500