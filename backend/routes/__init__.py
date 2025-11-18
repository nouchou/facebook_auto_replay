from flask import Blueprint

# Créer les blueprints SANS préfixe
auth_bp = Blueprint('auth', __name__)
facebook_bp = Blueprint('facebook', __name__)
responses_bp = Blueprint('responses', __name__)

def register_routes(app):
    """Enregistrer tous les blueprints avec le préfixe /api"""
    from routes import auth, facebook, responses
    
    # Enregistrer avec le préfixe /api
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(facebook_bp, url_prefix='/api/facebook')
    app.register_blueprint(responses_bp, url_prefix='/api/responses')
    
    print("✅ Routes enregistrées:")
    print("   - /api/auth/*")
    print("   - /api/facebook/*")
    print("   - /api/responses/*")