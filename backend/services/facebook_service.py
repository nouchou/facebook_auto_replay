import requests
from models import db, Message, Comment, AutoResponse
from datetime import datetime

class FacebookService:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def _make_request(self, method, url, **kwargs):
        """Méthode helper pour gérer les requêtes avec erreurs"""
        try:
            if method.upper() == 'GET':
                response = requests.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, **kwargs)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            result = response.json()
            
            # Vérifier les erreurs Facebook
            if 'error' in result:
                error = result['error']
                print(f"❌ Erreur Facebook API: {error.get('message')}")
                print(f"   Code: {error.get('code')}, Type: {error.get('type')}")
                
                # Erreurs spécifiques
                if error.get('code') == 200:
                    print("   ⚠️ PERMISSIONS MANQUANTES!")
                    print("   Solution: Régénérez le token avec pages_manage_metadata")
                elif error.get('code') == 190:
                    print("   ⚠️ TOKEN INVALIDE OU EXPIRÉ!")
                    print("   Solution: Générez un nouveau token")
            
            return result
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {str(e)}")
            return {'error': {'message': str(e)}}
        except Exception as e:
            print(f"❌ Erreur inattendue: {str(e)}")
            return {'error': {'message': str(e)}}
    
    def send_message(self, recipient_id, message_text):
        """Envoyer un message privé"""
        url = f"{self.base_url}/me/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text},
            "access_token": self.access_token
        }
        
        print(f"📤 Envoi message à {recipient_id}")
        result = self._make_request('POST', url, json=payload)
        
        if 'error' not in result:
            print(f"✅ Message envoyé!")
        
        return result
    
    def reply_to_comment(self, comment_id, message_text):
        """Répondre à un commentaire"""
        url = f"{self.base_url}/{comment_id}/comments"
        payload = {
            "message": message_text,
            "access_token": self.access_token
        }
        
        print(f"📤 Réponse au commentaire {comment_id}")
        result = self._make_request('POST', url, json=payload)
        
        if 'error' not in result:
            print(f"✅ Réponse envoyée!")
        else:
            print(f"❌ Échec réponse commentaire")
        
        return result
    
    def get_user_info(self, user_id):
        """Obtenir les informations d'un utilisateur"""
        url = f"{self.base_url}/{user_id}"
        params = {
            "fields": "name,first_name,last_name",
            "access_token": self.access_token
        }
        
        return self._make_request('GET', url, params=params)
    
    def test_permissions(self):
        """Tester les permissions du token"""
        url = f"{self.base_url}/me/permissions"
        params = {"access_token": self.access_token}
        
        result = self._make_request('GET', url, params=params)
        
        if 'data' in result:
            permissions = result['data']
            granted = [p['permission'] for p in permissions if p['status'] == 'granted']
            
            print("🔑 Permissions accordées:")
            for perm in granted:
                print(f"   ✅ {perm}")
            
            # Vérifier les permissions critiques
            critical_perms = [
                'pages_messaging',
                'pages_manage_metadata',
                'pages_read_engagement',
                'pages_manage_posts'
            ]
            
            missing = [p for p in critical_perms if p not in granted]
            if missing:
                print("⚠️ Permissions manquantes:")
                for perm in missing:
                    print(f"   ❌ {perm}")
            else:
                print("✅ Toutes les permissions OK!")
            
            return {
                'granted': granted,
                'missing': missing,
                'all_ok': len(missing) == 0
            }
        
        return result