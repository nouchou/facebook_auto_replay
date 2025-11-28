from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models import db, FacebookPage, Message, Comment
from services.facebook_service import FacebookService
from services.response_service import ResponseService

from config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configuration CORS simplifiée et permissive
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Initialiser la base de données
    db.init_app(app)
    
    # Créer les tables
    with app.app_context():
        db.create_all()
    
    # Enregistrer les blueprints
    try:
        from routes import register_routes
        register_routes(app)
    except ImportError as e:
        print(f"Erreur d'import des routes: {e}")
        # Import direct en cas d'échec
        from routes.auth import auth_bp
        from routes.facebook import facebook_bp
        from routes.responses import responses_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(facebook_bp, url_prefix='/api/facebook')
        app.register_blueprint(responses_bp, url_prefix='/api/responses')
    
    # 🆕 NOUVEAU : Enregistrer le blueprint NLP
    try:
        from routes.nlp import nlp_bp
        app.register_blueprint(nlp_bp, url_prefix='/api/nlp')
        print('✅ Blueprint NLP enregistré avec succès')
    except ImportError as e:
        print(f'⚠️ Impossible d\'importer le blueprint NLP: {e}')
        print('   Le système fonctionnera sans les fonctionnalités NLP avancées')
    
    # Webhook Facebook
    @app.route('/webhook', methods=['GET'])
    def verify_webhook():
        """Vérification du webhook Facebook"""
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == Config.FACEBOOK_VERIFY_TOKEN:
            print('✅ Webhook vérifié avec succès!')
            return challenge, 200
        
        print('❌ Échec de la vérification du webhook')
        return 'Forbidden', 403
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Recevoir les notifications de Facebook"""
        data = request.get_json()
        
        print(f"📨 Webhook reçu: {data}")
        
        if not data or data.get('object') != 'page':
            return 'OK', 200
        
        for entry in data.get('entry', []):
            # Traiter les messages privés
            if 'messaging' in entry:
                for messaging_event in entry['messaging']:
                    handle_message(messaging_event)
            
            # Traiter les commentaires
            if 'changes' in entry:
                for change in entry['changes']:
                    if change.get('field') == 'feed':
                        handle_comment(change.get('value', {}))
        
        return 'OK', 200
    
    @app.route('/privacy-policy', methods=['GET'])
    def privacy_policy():
        return render_template('privacy-policy.html')
    
    def handle_message(messaging_event):
        """Traiter un message reçu"""
        try:
            # Éviter les échos
            if 'is_echo' in messaging_event.get('message', {}):
                return
            
            sender_id = messaging_event.get('sender', {}).get('id')
            message = messaging_event.get('message', {})
            message_text = message.get('text', '')
            message_id = message.get('mid')
            
            if not message_text or not sender_id:
                return
            
            print(f"📩 Message reçu de {sender_id}: {message_text[:50]}...")
            
            # Récupérer la page active
            page = FacebookPage.query.filter_by(is_active=True).first()
            if not page:
                print('❌ Aucune page active trouvée')
                return
            
            print(f"✅ Page active: {page.page_name}")
            
            fb_service = FacebookService(page.access_token)
            
            # Obtenir les infos de l'utilisateur
            try:
                user_info = fb_service.get_user_info(sender_id)
                sender_name = user_info.get('name', 'Utilisateur')
            except:
                sender_name = 'Utilisateur'
            
            # 🆕 AMÉLIORÉ : Trouver une réponse appropriée avec NLP
            response_text = ResponseService.find_matching_response(message_text, 'message')
            if not response_text:
                response_text = ResponseService.get_default_response()
            
            print(f"💬 Réponse: {response_text[:50]}...")
            
            # Envoyer la réponse
            result = fb_service.send_message(sender_id, response_text)
            
            if 'error' in result:
                print(f"❌ Erreur envoi: {result['error']}")
                return
            
            # Enregistrer dans la base de données
            new_message = Message(
                message_id=message_id,
                sender_id=sender_id,
                sender_name=sender_name,
                message_text=message_text,
                response_sent=response_text,
                is_automated=True,
                page_id=page.id
            )
            db.session.add(new_message)
            db.session.commit()
            
            print(f'✅ Message traité de {sender_name}')
        
        except Exception as e:
            print(f'❌ Erreur traitement message: {str(e)}')
            import traceback
            traceback.print_exc()
            db.session.rollback()
    
def handle_comment(comment_data):
    """Traiter un commentaire reçu - VERSION CORRIGÉE ET ROBUSTE"""
    try:
        print(f"📦 Données brutes reçues: {comment_data}")
        
        # CHANGEMENT 1: Accepter plus de types d'événements
        item_type = comment_data.get('item')
        if item_type not in ['comment', 'post', 'status']:
            print(f"⚠️ Item non-commentaire ignoré: {item_type}")
            return
        
        # CHANGEMENT 2: Accepter tous les verbes sauf 'remove'
        verb = comment_data.get('verb', 'add')
        if verb == 'remove':
            print(f"❌ Commentaire supprimé, ignoré")
            return
        
        print(f"✅ Verbe accepté: {verb}")
        
        # CHANGEMENT 3: Gérer différentes structures de données
        comment_id = comment_data.get('comment_id')
        post_id = comment_data.get('post_id')
        
        # Essayer plusieurs chemins pour récupérer l'utilisateur
        user_data = comment_data.get('from', {})
        if not user_data:
            # Parfois dans 'sender'
            user_data = comment_data.get('sender', {})
        
        user_id = user_data.get('id')
        user_name = user_data.get('name', 'Utilisateur')
        
        # Message du commentaire
        comment_text = comment_data.get('message', '')
        
        # CHANGEMENT 4: Logs détaillés
        print(f"📝 Commentaire détecté:")
        print(f"   - ID: {comment_id}")
        print(f"   - Post: {post_id}")
        print(f"   - User: {user_name} ({user_id})")
        print(f"   - Texte: {comment_text[:100]}...")
        
        # Vérifications
        if not comment_id:
            print("❌ Pas de comment_id")
            return
        
        if not comment_text:
            print("❌ Commentaire vide")
            return
        
        # Récupérer la page active
        page = FacebookPage.query.filter_by(is_active=True).first()
        if not page:
            print('❌ Aucune page active trouvée')
            return
        
        print(f"✅ Page active: {page.page_name}")
        
        # CHANGEMENT 5: Vérifier si ce n'est pas notre propre commentaire
        fb_service = FacebookService(page.access_token)
        
        # Récupérer l'ID de la page pour éviter de répondre à soi-même
        try:
            page_info_url = f"https://graph.facebook.com/v18.0/{page.page_id}"
            page_info_response = requests.get(page_info_url, params={
                'access_token': page.access_token,
                'fields': 'id'
            })
            page_fb_id = page_info_response.json().get('id')
            
            if user_id == page_fb_id:
                print("⚠️ C'est notre propre commentaire, ignoré")
                return
        except:
            pass  # Si erreur, continuer quand même
        
        # Vérifier si déjà traité (éviter doublons)
        existing = Comment.query.filter_by(comment_id=comment_id).first()
        if existing:
            print(f"⚠️ Commentaire déjà traité: {comment_id}")
            return
        
        # Trouver une réponse appropriée avec NLP
        response_text = ResponseService.find_matching_response(comment_text, 'comment')
        
        if response_text:
            print(f"💬 Réponse trouvée: {response_text[:50]}...")
            
            # Répondre au commentaire
            result = fb_service.reply_to_comment(comment_id, response_text)
            print(f"📤 Résultat API: {result}")
            
            # Vérifier si erreur
            if 'error' in result:
                error_msg = result['error'].get('message', 'Erreur inconnue')
                error_code = result['error'].get('code', 'N/A')
                print(f"❌ ERREUR API ({error_code}): {error_msg}")
                
                # Messages d'aide selon l'erreur
                if error_code == 200:
                    print("   💡 Solution: Vérifiez les permissions 'pages_manage_posts'")
                elif error_code == 190:
                    print("   💡 Solution: Token expiré, régénérez-le")
                elif error_code == 100:
                    print("   💡 Solution: Vérifiez que le comment_id est correct")
                
                return
            
            # Enregistrer dans la base de données
            new_comment = Comment(
                comment_id=comment_id,
                post_id=post_id,
                user_id=user_id,
                user_name=user_name,
                comment_text=comment_text,
                response_sent=response_text,
                is_automated=True,
                page_id=page.id
            )
            db.session.add(new_comment)
            db.session.commit()
            
            print(f'✅ Commentaire traité de {user_name}')
        else:
            print(f"⚠️ Aucune réponse trouvée pour: {comment_text[:30]}...")
            
            # Optionnel: Enregistrer quand même sans réponse
            new_comment = Comment(
                comment_id=comment_id,
                post_id=post_id,
                user_id=user_id,
                user_name=user_name,
                comment_text=comment_text,
                response_sent=None,
                is_automated=False,
                page_id=page.id
            )
            db.session.add(new_comment)
            db.session.commit()
    
    except Exception as e:
        print(f'❌ Erreur traitement commentaire: {str(e)}')
        import traceback
        traceback.print_exc()
        db.session.rollback()
    
    # Route de santé
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'message': 'API is running'}), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    print('='*60)
    print('🚀 Démarrage de l\'application Facebook Auto-Reply')
    print('='*60)
    print(f'🔌 Port: {port}')
    print(f'🔧 Mode: {Config.DEBUG and "Development" or "Production"}')
    print(f'💾 Database: {Config.SQLALCHEMY_DATABASE_URI.split("://")[0]}')
    print('='*60)
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)