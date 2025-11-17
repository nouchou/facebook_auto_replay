from flask import Blueprint

# Créer les blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
facebook_bp = Blueprint('facebook', __name__, url_prefix='/api/facebook')
responses_bp = Blueprint('responses', __name__, url_prefix='/api/responses')

def register_routes(app):
    """Enregistrer tous les blueprints"""
    from routes import auth, facebook, responses
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(facebook_bp)
    app.register_blueprint(responses_bp)