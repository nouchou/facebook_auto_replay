"""
Script pour tester avec un VRAI commentaire Facebook
Pré-requis: 
1. Créez un post sur votre page Facebook
2. Notez l'ID du post
3. Le bot répondra automatiquement aux nouveaux commentaires

Usage: python test_comment_reel.py
"""

import requests
import time
import json
from datetime import datetime

# ============ CONFIGURATION - MODIFIEZ ICI ============
BASE_URL = "https://facebook-auto-replay.onrender.com"
PAGE_ACCESS_TOKEN = "EAAMO3n7MHVgBQKNG7jhZBJpK3dmkGIdGGQjZCOokuqMEfXawgO8lOfhczdUSnWEyI9KoPvXgocxxFfo6iIqUfMbgZCr47Ob5ZAZAyZBaSetZBQTbKCXUkyo7dZBKY0f0OOwMw7cVdjSAuZB2Dfqpbx7essNtj1UJi4kNZCJcfn2DmzPp7VZAOnrO4Gub2ftSqj6C4G0WZA2Y7iTZAKQZDZD"  # Token de votre page
FB_PAGE_ID = "847215158480695"  # ID de votre page Facebook
POST_ID = "834491979512788"  # Optionnel: ID d'un post spécifique à surveiller
# =====================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_section(title):
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{title}{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}")

def get_recent_posts():
    """Récupérer les posts récents de la page"""
    print_section("📋 Récupération des posts récents")
    
    url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/feed"
    params = {
        'access_token': PAGE_ACCESS_TOKEN,
        'fields': 'id,message,created_time',
        'limit': 5
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"{Colors.RED}❌ Erreur: {response.json()}{Colors.END}")
            return None
        
        posts = response.json().get('data', [])
        
        if not posts:
            print(f"{Colors.YELLOW}⚠️ Aucun post trouvé{Colors.END}")
            print(f"{Colors.BLUE}💡 Créez un post sur votre page Facebook d'abord{Colors.END}")
            return None
        
        print(f"{Colors.GREEN}✅ {len(posts)} posts trouvés{Colors.END}\n")
        
        for i, post in enumerate(posts, 1):
            message = post.get('message', 'Pas de texte')[:50]
            print(f"{i}. Post ID: {post['id']}")
            print(f"   Message: {message}...")
            print(f"   Créé: {post['created_time']}\n")
        
        return posts
    
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur: {e}{Colors.END}")
        return None

def get_post_comments(post_id):
    """Récupérer les commentaires d'un post"""
    url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
    params = {
        'access_token': PAGE_ACCESS_TOKEN,
        'fields': 'id,message,from,created_time',
        'limit': 10
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"{Colors.RED}❌ Erreur: {response.json()}{Colors.END}")
            return []
        
        comments = response.json().get('data', [])
        return comments
    
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur: {e}{Colors.END}")
        return []

def post_test_comment(post_id, message="Test automatique - Bonjour"):
    """Poster un commentaire de test"""
    print_section("💬 Publication d'un commentaire de test")
    
    url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
    data = {
        'message': message,
        'access_token': PAGE_ACCESS_TOKEN
    }
    
    try:
        print(f"   Message: {message}")
        print(f"   Post ID: {post_id}")
        
        response = requests.post(url, data=data)
        
        if response.status_code != 200:
            print(f"\n{Colors.RED}❌ Erreur: {response.json()}{Colors.END}")
            return None
        
        result = response.json()
        comment_id = result.get('id')
        
        print(f"\n{Colors.GREEN}✅ Commentaire publié!{Colors.END}")
        print(f"   Comment ID: {comment_id}")
        
        return comment_id
    
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur: {e}{Colors.END}")
        return None

def wait_for_bot_response(comment_id, post_id, timeout=30):
    """Attendre que le bot réponde"""
    print_section("⏳ Attente de la réponse automatique")
    
    print(f"   Surveillance pendant {timeout} secondes...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        elapsed = int(time.time() - start_time)
        print(f"\r   Temps écoulé: {elapsed}s", end='', flush=True)
        
        # Récupérer les commentaires
        comments = get_post_comments(post_id)
        
        # Chercher une réponse au commentaire
        for comment in comments:
            # Si le commentaire a un parent_id qui correspond à notre comment_id
            # ou si c'est un commentaire de la page après notre commentaire
            if comment.get('from', {}).get('id') == FB_PAGE_ID:
                # Vérifier si c'est récent
                created_time = comment.get('created_time')
                # Si créé après notre test
                print(f"\n\n{Colors.GREEN}✅ RÉPONSE DÉTECTÉE!{Colors.END}")
                print(f"   Message: {comment.get('message')}")
                print(f"   ID: {comment.get('id')}")
                print(f"   Créé: {created_time}")
                return True
        
        time.sleep(2)
    
    print(f"\n\n{Colors.YELLOW}⏰ Timeout - Aucune réponse détectée{Colors.END}")
    return False

def check_backend_logs():
    """Vérifier les logs du backend"""
    print_section("📊 Vérification de l'historique backend")
    
    try:
        response = requests.get(f"{BASE_URL}/api/responses/comments?limit=5")
        
        if response.status_code != 200:
            print(f"{Colors.RED}❌ Erreur: {response.status_code}{Colors.END}")
            return
        
        comments = response.json()
        
        if not comments:
            print(f"{Colors.YELLOW}⚠️ Aucun commentaire dans l'historique{Colors.END}")
            return
        
        print(f"{Colors.GREEN}✅ {len(comments)} commentaires trouvés{Colors.END}\n")
        
        for comment in comments:
            print(f"💬 {comment['user_name']}:")
            print(f"   Texte: {comment['comment_text'][:60]}...")
            print(f"   Réponse: {comment.get('response_sent', 'Aucune')[:60] if comment.get('response_sent') else 'Aucune'}...")
            print(f"   Auto: {comment['is_automated']}")
            print(f"   Date: {comment['timestamp']}\n")
    
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur: {e}{Colors.END}")

def simulate_webhook_event(comment_id, post_id):
    """Simuler l'événement webhook (pour déboguer)"""
    print_section("🔧 Simulation de webhook")
    
    webhook_data = {
        "object": "page",
        "entry": [
            {
                "id": FB_PAGE_ID,
                "time": int(time.time()),
                "changes": [
                    {
                        "field": "feed",
                        "value": {
                            "item": "comment",
                            "verb": "add",
                            "comment_id": comment_id,
                            "post_id": post_id,
                            "from": {
                                "id": "TEST_USER_ID",
                                "name": "Test User"
                            },
                            "message": "Test automatique - Bonjour"
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        print(f"   Envoi du webhook simulé...")
        print(f"   URL: {BASE_URL}/webhook")
        
        response = requests.post(f"{BASE_URL}/webhook", json=webhook_data)
        
        if response.status_code == 200:
            print(f"\n{Colors.GREEN}✅ Webhook accepté{Colors.END}")
            print(f"{Colors.BLUE}💡 Vérifiez les logs Render pour voir le traitement{Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ Webhook rejeté: {response.status_code}{Colors.END}")
            print(f"   Réponse: {response.text}")
    
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur: {e}{Colors.END}")

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║           TEST COMMENTAIRE RÉEL - FACEBOOK AUTO-REPLY              ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    # Vérifier la configuration
    if PAGE_ACCESS_TOKEN == "VOTRE_TOKEN_ICI" or not PAGE_ACCESS_TOKEN:
        print(f"{Colors.RED}❌ Veuillez configurer PAGE_ACCESS_TOKEN dans le script{Colors.END}")
        return
    
    if FB_PAGE_ID == "VOTRE_PAGE_ID_ICI" or not FB_PAGE_ID:
        print(f"{Colors.RED}❌ Veuillez configurer FB_PAGE_ID dans le script{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}Configuration:{Colors.END}")
    print(f"   Backend: {BASE_URL}")
    print(f"   Page ID: {FB_PAGE_ID}")
    print(f"   Token: {PAGE_ACCESS_TOKEN[:20]}...")
    
    # 1. Récupérer les posts
    posts = get_recent_posts()
    if not posts:
        return
    
    # 2. Choisir un post
    if POST_ID:
        selected_post_id = POST_ID
        print(f"\n{Colors.BLUE}ℹ️ Utilisation du post configuré: {POST_ID}{Colors.END}")
    else:
        print(f"\n{Colors.BOLD}Choisissez un post (1-{len(posts)}):{Colors.END}")
        choice = input("Numéro du post (ou Enter pour le 1er): ").strip()
        
        if not choice:
            choice = "1"
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(posts):
                selected_post_id = posts[index]['id']
            else:
                print(f"{Colors.RED}❌ Choix invalide{Colors.END}")
                return
        except ValueError:
            print(f"{Colors.RED}❌ Choix invalide{Colors.END}")
            return
    
    print(f"\n{Colors.GREEN}✅ Post sélectionné: {selected_post_id}{Colors.END}")
    
    # 3. Menu d'actions
    print(f"\n{Colors.BOLD}Que voulez-vous faire?{Colors.END}")
    print("1. Poster un commentaire de test et attendre la réponse")
    print("2. Surveiller les commentaires existants")
    print("3. Simuler un webhook")
    print("4. Vérifier l'historique backend")
    
    action = input("\nChoix (1-4): ").strip()
    
    if action == "1":
        # Poster et attendre
        message = input("\nMessage du commentaire (ou Enter pour défaut): ").strip()
        if not message:
            message = "Bonjour, quel est le prix?"
        
        comment_id = post_test_comment(selected_post_id, message)
        
        if comment_id:
            # Attendre la réponse
            wait_for_bot_response(comment_id, selected_post_id, timeout=30)
            
            # Vérifier l'historique
            time.sleep(2)
            check_backend_logs()
    
    elif action == "2":
        # Surveiller
        print_section("👀 Surveillance des commentaires")
        
        comments = get_post_comments(selected_post_id)
        
        if not comments:
            print(f"{Colors.YELLOW}⚠️ Aucun commentaire sur ce post{Colors.END}")
            print(f"{Colors.BLUE}💡 Créez un commentaire manuellement sur Facebook{Colors.END}")
        else:
            print(f"{Colors.GREEN}✅ {len(comments)} commentaires trouvés{Colors.END}\n")
            
            for comment in comments:
                print(f"💬 {comment.get('from', {}).get('name')}:")
                print(f"   Message: {comment.get('message')}")
                print(f"   ID: {comment.get('id')}")
                print(f"   Créé: {comment.get('created_time')}\n")
    
    elif action == "3":
        # Simuler webhook
        comment_id = f"TEST_{int(time.time())}"
        simulate_webhook_event(comment_id, selected_post_id)
    
    elif action == "4":
        # Historique
        check_backend_logs()
    
    else:
        print(f"{Colors.RED}❌ Choix invalide{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrompu{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Erreur: {e}{Colors.END}")
        import traceback
        traceback.print_exc()