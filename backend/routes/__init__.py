"""
Initialisation des blueprints pour les routes
"""
from flask import Blueprint

# Créer les blueprints UNE SEULE FOIS
auth_bp = Blueprint('auth', __name__)
facebook_bp = Blueprint('facebook', __name__)
responses_bp = Blueprint('responses', __name__)

def register_routes(app):
    """Enregistrer tous les blueprints dans l'application Flask"""
    
    # Importer les fichiers de routes (ceci charge les décorateurs @blueprint.route)
    from routes import auth, facebook, responses
    
    # Enregistrer les blueprints avec leurs préfixes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(facebook_bp, url_prefix='/api/facebook')
    app.register_blueprint(responses_bp, url_prefix='/api/responses')
    
    print("✅ Routes enregistrées:")
    print("   - /api/auth/*")
    print("   - /api/facebook/*")
    print("   - /api/responses/*")