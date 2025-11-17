import requests
from models import db, Message, Comment, AutoResponse
from datetime import datetime

class FacebookService:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def send_message(self, recipient_id, message_text):
        """Envoyer un message privé"""
        url = f"{self.base_url}/me/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text},
            "access_token": self.access_token
        }
        response = requests.post(url, json=payload)
        return response.json()
    
    def reply_to_comment(self, comment_id, message_text):
        """Répondre à un commentaire"""
        url = f"{self.base_url}/{comment_id}/comments"
        payload = {
            "message": message_text,
            "access_token": self.access_token
        }
        response = requests.post(url, json=payload)
        return response.json()
    
    def get_user_info(self, user_id):
        """Obtenir les informations d'un utilisateur"""
        url = f"{self.base_url}/{user_id}"
        params = {
            "fields": "name,first_name,last_name",
            "access_token": self.access_token
        }
        response = requests.get(url, params=params)
        return response.json()