"""
Service Facebook - MESSAGES MESSENGER UNIQUEMENT
"""
import requests
from models import db, Message, AutoResponse
from datetime import datetime

class FacebookService:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def _make_request(self, method, url, **kwargs):
        """Méthode helper pour gérer les requêtes avec erreurs détaillées"""
        try:
            print(f"📡 Requête {method} vers: {url}")
            
            if method.upper() == 'GET':
                response = requests.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, **kwargs)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            print(f"   Status: {response.status_code}")
            
            result = response.json()
            print(f"   Réponse: {result}")
            
            # Vérifier les erreurs Facebook
            if 'error' in result:
                error = result['error']
                print(f"❌ Erreur Facebook API:")
                print(f"   Message: {error.get('message')}")
                print(f"   Code: {error.get('code')}")
                print(f"   Type: {error.get('type')}")
                
                # Messages d'aide spécifiques
                error_code = error.get('code')
                if error_code == 200:
                    print("\n   💡 PERMISSIONS MANQUANTES!")
                    print("   Solution:")
                    print("   1. Allez sur developers.facebook.com")
                    print("   2. Votre app → Outils de jetons d'accès")
                    print("   3. Générez un nouveau token avec:")
                    print("      - pages_messaging (CRITIQUE)")
                    print("      - pages_read_engagement")
                    print("      - pages_manage_metadata")
                    
                elif error_code == 190:
                    print("\n   💡 TOKEN INVALIDE OU EXPIRÉ!")
                    print("   Solution:")
                    print("   1. Générez un nouveau Page Access Token")
                    print("   2. Mettez-le à jour dans votre config")
            
            return result
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {str(e)}")
            return {'error': {'message': str(e), 'code': 'NETWORK_ERROR'}}
        except ValueError as e:
            print(f"❌ Erreur JSON: {str(e)}")
            return {'error': {'message': 'Invalid JSON response', 'code': 'JSON_ERROR'}}
        except Exception as e:
            print(f"❌ Erreur inattendue: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': {'message': str(e), 'code': 'UNKNOWN_ERROR'}}
    
    def send_message(self, recipient_id, message_text):
        """Envoyer un message privé Messenger"""
        url = f"{self.base_url}/me/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text},
            "access_token": self.access_token
        }
        
        print(f"\n📤 Envoi message à {recipient_id}")
        print(f"   Texte: {message_text[:50]}...")
        
        result = self._make_request('POST', url, json=payload)
        
        if 'error' not in result:
            print(f"   ✅ Message envoyé avec succès!")
        
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
        """Tester les permissions du token - VERSION MESSAGES"""
        print("\n" + "="*60)
        print("🔍 TEST DES PERMISSIONS - MESSAGES UNIQUEMENT")
        print("="*60)
        
        url = f"{self.base_url}/me/permissions"
        params = {"access_token": self.access_token}
        
        result = self._make_request('GET', url, params=params)
        
        if 'data' in result:
            permissions = result['data']
            granted = [p['permission'] for p in permissions if p['status'] == 'granted']
            declined = [p['permission'] for p in permissions if p['status'] == 'declined']
            
            print("\n✅ Permissions accordées:")
            for perm in sorted(granted):
                print(f"   ✅ {perm}")
            
            if declined:
                print("\n❌ Permissions refusées:")
                for perm in sorted(declined):
                    print(f"   ❌ {perm}")
            
            # Vérifier les permissions critiques pour les messages
            critical_perms = {
                'pages_messaging': '💬 Messages privés (CRITIQUE!)',
                'pages_manage_metadata': 'Gestion métadonnées',
                'pages_read_engagement': 'Lecture engagement'
            }
            
            print("\n🎯 Permissions critiques pour MESSAGES:")
            missing = []
            for perm, description in critical_perms.items():
                if perm in granted:
                    print(f"   ✅ {perm}: {description}")
                else:
                    print(f"   ❌ {perm}: {description}")
                    missing.append(perm)
            
            if missing:
                print("\n⚠️ ATTENTION: Permissions manquantes!")
                print("   Sans ces permissions, les messages NE FONCTIONNERONT PAS!")
                print("\n   🔧 Actions requises:")
                print("   1. Allez sur: https://developers.facebook.com/tools/explorer")
                print("   2. Sélectionnez votre app")
                print("   3. Cliquez sur 'Generate Access Token'")
                print("   4. Sélectionnez TOUTES ces permissions:")
                for perm in missing:
                    print(f"      - {perm}")
                print("   5. Copiez le nouveau token")
                print("   6. Mettez-le à jour dans votre application")
            else:
                print("\n✅ Toutes les permissions critiques sont OK!")
            
            print("="*60)
            
            return {
                'granted': granted,
                'declined': declined,
                'missing': missing,
                'all_ok': len(missing) == 0
            }
        
        print("="*60)
        return result