from models import db, AutoResponse
import re

class ResponseService:
    @staticmethod
    def find_matching_response(message_text, response_type='message'):
        """Trouver une réponse correspondante basée sur les mots-clés"""
        message_lower = message_text.lower()
        
        # Récupérer toutes les réponses actives triées par priorité
        responses = AutoResponse.query.filter_by(
            is_active=True
        ).filter(
            (AutoResponse.response_type == response_type) | 
            (AutoResponse.response_type == 'both')
        ).order_by(AutoResponse.priority.desc()).all()
        
        for response in responses:
            keywords = response.trigger_keyword.lower().split(',')
            for keyword in keywords:
                keyword = keyword.strip()
                # Recherche exacte ou partielle
                if keyword in message_lower or re.search(r'\b' + re.escape(keyword) + r'\b', message_lower):
                    return response.response_text
        
        return None
    
    @staticmethod
    def get_default_response():
        """Réponse par défaut si aucune correspondance"""
        return "Merci pour votre message. Notre équipe vous répondra dans les plus brefs délais."