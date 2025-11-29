import requests
from models import db, Message, Comment, AutoResponse
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
                print(f"   Subcode: {error.get('error_subcode')}")
                
                # Messages d'aide spécifiques
                error_code = error.get('code')
                if error_code == 200:
                    print("\n   💡 PERMISSIONS MANQUANTES!")
                    print("   Solution:")
                    print("   1. Allez sur developers.facebook.com")
                    print("   2. Votre app > Outils de jetons d'accès")
                    print("   3. Générez un nouveau token avec:")
                    print("      - pages_manage_posts (CRITIQUE)")
                    print("      - pages_read_engagement")
                    print("      - pages_manage_metadata")
                    print("      - pages_messaging")
                    
                elif error_code == 190:
                    print("\n   💡 TOKEN INVALIDE OU EXPIRÉ!")
                    print("   Solution:")
                    print("   1. Générez un nouveau Page Access Token")
                    print("   2. Mettez-le à jour dans votre config")
                    
                elif error_code == 100:
                    print("\n   💡 PARAMÈTRE INVALIDE!")
                    print("   Solution:")
                    print("   1. Vérifiez que le comment_id est correct")
                    print("   2. Vérifiez que le commentaire existe toujours")
                    
                elif error_code == 10:
                    print("\n   💡 PERMISSION REFUSÉE!")
                    print("   Solution:")
                    print("   1. Vérifiez que vous êtes admin de la page")
                    print("   2. Vérifiez les permissions de l'app")
            
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
    
    def reply_to_comment(self, comment_id, message_text):
        """
        Répondre à un commentaire Facebook
        
        Args:
            comment_id: ID du commentaire (ex: "123456789_987654321")
            message_text: Texte de la réponse
        
        Returns:
            dict: Résultat de l'API ou erreur
        """
        url = f"{self.base_url}/{comment_id}/comments"
        
        payload = {
            "message": message_text,
            "access_token": self.access_token
        }
        
        print(f"\n💬 Réponse au commentaire")
        print(f"   Comment ID: {comment_id}")
        print(f"   URL: {url}")
        print(f"   Message: {message_text[:50]}...")
        
        result = self._make_request('POST', url, json=payload)
        
        if 'error' not in result:
            print(f"   ✅ Réponse au commentaire envoyée!")
            if 'id' in result:
                print(f"   ID de la réponse: {result['id']}")
        else:
            print(f"   ❌ Échec de la réponse au commentaire")
        
        return result
    
    def get_user_info(self, user_id):
        """Obtenir les informations d'un utilisateur"""
        url = f"{self.base_url}/{user_id}"
        params = {
            "fields": "name,first_name,last_name",
            "access_token": self.access_token
        }
        
        return self._make_request('GET', url, params=params)
    
    def get_comment_info(self, comment_id):
        """Obtenir les détails d'un commentaire"""
        url = f"{self.base_url}/{comment_id}"
        params = {
            "fields": "id,message,from,created_time,parent",
            "access_token": self.access_token
        }
        
        print(f"\n🔍 Récupération info commentaire {comment_id}")
        return self._make_request('GET', url, params=params)
    
    def test_permissions(self):
        """Tester les permissions du token - DÉTAILLÉ"""
        print("\n" + "="*60)
        print("🔐 TEST DES PERMISSIONS")
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
            
            # Vérifier les permissions critiques pour les commentaires
            critical_perms = {
                'pages_messaging': 'Messages privés',
                'pages_manage_metadata': 'Gestion métadonnées',
                'pages_read_engagement': 'Lecture engagement',
                'pages_manage_posts': '🔥 RÉPONDRE AUX COMMENTAIRES (CRITIQUE!)'
            }
            
            print("\n🎯 Permissions critiques:")
            missing = []
            for perm, description in critical_perms.items():
                if perm in granted:
                    print(f"   ✅ {perm}: {description}")
                else:
                    print(f"   ❌ {perm}: {description}")
                    missing.append(perm)
            
            if missing:
                print("\n⚠️ ATTENTION: Permissions manquantes!")
                print("   Sans ces permissions, les commentaires NE FONCTIONNERONT PAS!")
                print("\n   📝 Actions requises:")
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
    
    def test_comment_reply(self, comment_id, test_mode=True):
        """
        Tester la capacité de répondre à un commentaire
        
        Args:
            comment_id: ID du commentaire à tester
            test_mode: Si True, ne fait qu'une validation, n'envoie pas
        """
        print("\n" + "="*60)
        print("🧪 TEST DE RÉPONSE AUX COMMENTAIRES")
        print("="*60)
        
        # 1. Vérifier que le commentaire existe
        print("\n1️⃣ Vérification du commentaire...")
        comment_info = self.get_comment_info(comment_id)
        
        if 'error' in comment_info:
            print("   ❌ Commentaire introuvable ou inaccessible")
            return False
        
        print(f"   ✅ Commentaire trouvé: {comment_info.get('message', '')[:50]}...")
        
        # 2. Tester les permissions
        print("\n2️⃣ Vérification des permissions...")
        perms = self.test_permissions()
        
        if not perms.get('all_ok'):
            print("   ❌ Permissions insuffisantes")
            return False
        
        print("   ✅ Permissions OK")
        
        # 3. Test d'envoi (si pas en mode test)
        if not test_mode:
            print("\n3️⃣ Envoi d'une réponse de test...")
            result = self.reply_to_comment(comment_id, "Test automatique ✅")
            
            if 'error' in result:
                print("   ❌ Échec de l'envoi")
                return False
            
            print("   ✅ Réponse envoyée avec succès!")
        else:
            print("\n3️⃣ Mode test - pas d'envoi réel")
        
        print("\n" + "="*60)
        print("✅ TOUT FONCTIONNE CORRECTEMENT!")
        print("="*60)
        
        return True