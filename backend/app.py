from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, FacebookPage, Message, Comment
from services.facebook_service import FacebookService
from services.response_service import ResponseService
from config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialiser CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialiser la base de données
    db.init_app(app)
    
    # Créer les tables
    with app.app_context():
        db.create_all()
    
    # Enregistrer les blueprints - VERSION CORRIGÉE
    try:
        from routes import register_routes
        register_routes(app)
    except ImportError as e:
        print(f"Erreur d'import des routes: {e}")
        # Import direct en cas d'échec
        from routes.auth import auth_bp
        from routes.facebook import facebook_bp
        from routes.responses import responses_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(facebook_bp)
        app.register_blueprint(responses_bp)
    
    # Webhook Facebook
    @app.route('/webhook', methods=['GET'])
    def verify_webhook():
        """Vérification du webhook Facebook"""
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == Config.FACEBOOK_VERIFY_TOKEN:
            print('Webhook vérifié avec succès!')
            return challenge, 200
        
        print('Échec de la vérification du webhook')
        return 'Forbidden', 403
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Recevoir les notifications de Facebook"""
        data = request.get_json()
        
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
    
    def handle_message(messaging_event):
        """Traiter un message reçu"""
        try:
            # Éviter les échos
            if 'is_echo' in messaging_event.get('message', {}):
                return
            
            sender_id = messaging_event.get('sender', {}).get('id')
            message = messaging_event.get('message', {})
            message_text = message.get('text', '')
            message_id = message.get('id')
            
            if not message_text or not sender_id:
                return
            
            # Récupérer la page active
            page = FacebookPage.query.filter_by(is_active=True).first()
            if not page:
                print('Aucune page active trouvée')
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
            
            # Envoyer la réponse
            fb_service.send_message(sender_id, response_text)
            
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
            
            print(f'Message traité de {sender_name}: {message_text[:50]}...')
        
        except Exception as e:
            print(f'Erreur lors du traitement du message: {str(e)}')
            db.session.rollback()
    
    def handle_comment(comment_data):
        """Traiter un commentaire reçu"""
        try:
            if comment_data.get('item') != 'comment':
                return
            
            comment_id = comment_data.get('comment_id')
            post_id = comment_data.get('post_id')
            user_id = comment_data.get('from', {}).get('id')
            user_name = comment_data.get('from', {}).get('name', 'Utilisateur')
            comment_text = comment_data.get('message', '')
            
            if not comment_text:
                return
            
            # Récupérer la page active
            page = FacebookPage.query.filter_by(is_active=True).first()
            if not page:
                return
            
            fb_service = FacebookService(page.access_token)
            
            # Trouver une réponse appropriée
            response_text = ResponseService.find_matching_response(comment_text, 'comment')
            
            if response_text:
                # Répondre au commentaire
                fb_service.reply_to_comment(comment_id, response_text)
                
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
                
                print(f'Commentaire traité de {user_name}: {comment_text[:50]}...')
        
        except Exception as e:
            print(f'Erreur lors du traitement du commentaire: {str(e)}')
            db.session.rollback()
    
    # Route de santé
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'message': 'API is running'}), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)