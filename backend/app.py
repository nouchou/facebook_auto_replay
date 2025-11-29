from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models import db, FacebookPage, Message, Comment
from services.facebook_service import FacebookService
from services.response_service import ResponseService
from config import Config
import os
import requests

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configuration CORS
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
        from routes.auth import auth_bp
        from routes.facebook import facebook_bp
        from routes.responses import responses_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(facebook_bp, url_prefix='/api/facebook')
        app.register_blueprint(responses_bp, url_prefix='/api/responses')
    
    # Enregistrer le blueprint NLP
    try:
        from routes.nlp import nlp_bp
        app.register_blueprint(nlp_bp, url_prefix='/api/nlp')
        print('✅ Blueprint NLP enregistré avec succès')
    except ImportError as e:
        print(f'⚠️ Impossible d\'importer le blueprint NLP: {e}')
    
    # ==================== WEBHOOKS FACEBOOK ====================
    
    @app.route('/webhook', methods=['GET'])
    def verify_webhook():
        """Vérification du webhook Facebook"""
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        print(f"🔍 Vérification webhook: mode={mode}, token={token}")
        
        if mode == 'subscribe' and token == Config.FACEBOOK_VERIFY_TOKEN:
            print('✅ Webhook vérifié avec succès!')
            return challenge, 200
        
        print('❌ Échec de la vérification du webhook')
        return 'Forbidden', 403
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Recevoir les notifications de Facebook"""
        data = request.get_json()
        
        print("=" * 60)
        print(f"📨 WEBHOOK REÇU")
        print("=" * 60)
        print(f"Data: {data}")
        print("=" * 60)
        
        if not data or data.get('object') != 'page':
            print("⚠️ Objet non-page, ignoré")
            return 'OK', 200
        
        for entry in data.get('entry', []):
            # Traiter les messages privés
            if 'messaging' in entry:
                print("💬 Événement messaging détecté")
                for messaging_event in entry['messaging']:
                    handle_message(messaging_event)
            
            # Traiter les commentaires
            if 'changes' in entry:
                print("💭 Événement changes détecté")
                for change in entry['changes']:
                    field = change.get('field')
                    print(f"   Field: {field}")
                    
                    if field == 'feed':
                        value = change.get('value', {})
                        print(f"   Value: {value}")
                        handle_comment(value)
        
        return 'OK', 200
    
    @app.route('/privacy-policy', methods=['GET'])
    def privacy_policy():
        return render_template('privacy-policy.html')
    
    # ==================== HANDLERS ====================
    
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
            
            fb_service = FacebookService(page.access_token)
            
            # Obtenir les infos de l'utilisateur
            try:
                user_info = fb_service.get_user_info(sender_id)
                sender_name = user_info.get('name', 'Utilisateur')
            except:
                sender_name = 'Utilisateur'
            
            # Trouver une réponse appropriée
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
        """
        Traiter un commentaire reçu - VERSION FINALE ROBUSTE
        """
        try:
            print("\n" + "=" * 60)
            print("💭 TRAITEMENT COMMENTAIRE")
            print("=" * 60)
            print(f"Données brutes: {comment_data}")
            print("=" * 60)
            
            # ÉTAPE 1: Vérifier le type d'item
            item_type = comment_data.get('item')
            print(f"1️⃣ Type d'item: {item_type}")
            
            if item_type not in ['comment', 'post', 'status']:
                print(f"   ❌ Type '{item_type}' ignoré")
                return
            
            # ÉTAPE 2: Vérifier le verbe (action)
            verb = comment_data.get('verb', 'add')
            print(f"2️⃣ Verbe: {verb}")
            
            if verb == 'remove':
                print("   ❌ Commentaire supprimé, ignoré")
                return
            
            # ÉTAPE 3: Extraire les données du commentaire
            comment_id = comment_data.get('comment_id')
            post_id = comment_data.get('post_id')
            
            # Essayer plusieurs structures pour l'utilisateur
            user_data = comment_data.get('from', {})
            if not user_data:
                user_data = comment_data.get('sender', {})
            
            user_id = user_data.get('id')
            user_name = user_data.get('name', 'Utilisateur')
            comment_text = comment_data.get('message', '')
            
            print(f"3️⃣ Données extraites:")
            print(f"   - Comment ID: {comment_id}")
            print(f"   - Post ID: {post_id}")
            print(f"   - User ID: {user_id}")
            print(f"   - User Name: {user_name}")
            print(f"   - Texte: {comment_text[:100]}...")
            
            # ÉTAPE 4: Validations
            if not comment_id:
                print("   ❌ Pas de comment_id, abandon")
                return
            
            if not comment_text or comment_text.strip() == '':
                print("   ❌ Commentaire vide, abandon")
                return
            
            # ÉTAPE 5: Récupérer la page active
            page = FacebookPage.query.filter_by(is_active=True).first()
            if not page:
                print('   ❌ Aucune page active trouvée')
                return
            
            print(f"4️⃣ Page active: {page.page_name} (ID: {page.page_id})")
            
            # ÉTAPE 6: Vérifier si c'est notre propre commentaire
            try:
                page_info_url = f"https://graph.facebook.com/v18.0/me"
                page_info_response = requests.get(page_info_url, params={
                    'access_token': page.access_token
                })
                
                if page_info_response.status_code == 200:
                    page_fb_id = page_info_response.json().get('id')
                    
                    if str(user_id) == str(page_fb_id):
                        print(f"   ⚠️ C'est notre propre commentaire ({user_id}), ignoré")
                        return
            except Exception as e:
                print(f"   ⚠️ Erreur vérification page ID: {e}")
            
            # ÉTAPE 7: Vérifier si déjà traité (éviter doublons)
            existing = Comment.query.filter_by(comment_id=comment_id).first()
            if existing:
                print(f"   ⚠️ Commentaire {comment_id} déjà traité, ignoré")
                return
            
            print(f"5️⃣ Commentaire valide, recherche de réponse...")
            
            # ÉTAPE 8: Chercher une réponse appropriée
            fb_service = FacebookService(page.access_token)
            response_text = ResponseService.find_matching_response(comment_text, 'comment')
            
            if not response_text:
                print("   ⚠️ Aucune réponse automatique trouvée")
                
                # Enregistrer quand même sans réponse
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
                print("   ℹ️ Commentaire enregistré sans réponse")
                return
            
            print(f"6️⃣ Réponse trouvée: {response_text[:50]}...")
            
            # ÉTAPE 9: Envoyer la réponse
            print(f"7️⃣ Envoi de la réponse au commentaire {comment_id}...")
            result = fb_service.reply_to_comment(comment_id, response_text)
            
            print(f"   Résultat API: {result}")
            
            # ÉTAPE 10: Vérifier le résultat
            if 'error' in result:
                error_msg = result['error'].get('message', 'Erreur inconnue')
                error_code = result['error'].get('code', 'N/A')
                error_type = result['error'].get('type', 'N/A')
                
                print(f"   ❌ ERREUR API:")
                print(f"      Code: {error_code}")
                print(f"      Type: {error_type}")
                print(f"      Message: {error_msg}")
                
                # Messages d'aide
                if error_code == 200:
                    print("      💡 Solution: Vérifiez la permission 'pages_manage_posts'")
                elif error_code == 190:
                    print("      💡 Solution: Token expiré, régénérez-le")
                elif error_code == 100:
                    print("      💡 Solution: Comment ID invalide")
                
                return
            
            print("   ✅ Réponse envoyée avec succès!")
            
            # ÉTAPE 11: Enregistrer dans la base de données
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
            
            print(f"8️⃣ ✅ SUCCÈS COMPLET - Commentaire de {user_name} traité")
            print("=" * 60 + "\n")
        
        except Exception as e:
            print(f'❌ ERREUR CRITIQUE traitement commentaire: {str(e)}')
            import traceback
            traceback.print_exc()
            db.session.rollback()
            print("=" * 60 + "\n")
    
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