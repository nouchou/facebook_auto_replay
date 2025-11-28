"""
Script pour vérifier la configuration Facebook de votre application
À exécuter localement pour diagnostiquer les problèmes
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Vos tokens
PAGE_ACCESS_TOKEN = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
APP_ID = os.getenv('FACEBOOK_APP_ID')

def check_page_info():
    """Vérifier les informations de la page"""
    print("\n" + "="*60)
    print("1️⃣  VÉRIFICATION DES INFORMATIONS DE LA PAGE")
    print("="*60)
    
    url = "https://graph.facebook.com/v18.0/me"
    params = {
        'access_token': PAGE_ACCESS_TOKEN,
        'fields': 'id,name,access_token'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ Erreur: {data['error']['message']}")
            return None
        
        print(f"✅ Page ID: {data.get('id')}")
        print(f"✅ Page Name: {data.get('name')}")
        return data.get('id')
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def check_page_permissions():
    """Vérifier les permissions de la page"""
    print("\n" + "="*60)
    print("2️⃣  VÉRIFICATION DES PERMISSIONS")
    print("="*60)
    
    url = "https://graph.facebook.com/v18.0/me/permissions"
    params = {'access_token': PAGE_ACCESS_TOKEN}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ Erreur: {data['error']['message']}")
            return
        
        permissions = data.get('data', [])
        
        required_permissions = [
            'pages_manage_metadata',
            'pages_read_engagement',
            'pages_manage_posts',
            'pages_manage_engagement'  # CRITIQUE pour les commentaires
        ]
        
        print("\n📋 Permissions actuelles:")
        for perm in permissions:
            status = "✅" if perm['status'] == 'granted' else "❌"
            print(f"   {status} {perm['permission']}: {perm['status']}")
        
        print("\n📋 Permissions requises pour les commentaires:")
        for req_perm in required_permissions:
            found = any(p['permission'] == req_perm and p['status'] == 'granted' 
                       for p in permissions)
            status = "✅" if found else "❌ MANQUANTE"
            print(f"   {status} {req_perm}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def check_subscribed_fields(page_id):
    """Vérifier les champs webhook auxquels on est abonné"""
    print("\n" + "="*60)
    print("3️⃣  VÉRIFICATION DES WEBHOOKS ABONNÉS")
    print("="*60)
    
    url = f"https://graph.facebook.com/v18.0/{page_id}/subscribed_apps"
    params = {'access_token': PAGE_ACCESS_TOKEN}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ Erreur: {data['error']['message']}")
            return
        
        if not data.get('data'):
            print("❌ Aucune application abonnée aux webhooks de cette page!")
            print("   👉 Vous devez abonner votre app dans Facebook Developers")
            return
        
        print("\n📱 Applications abonnées:")
        for app in data.get('data', []):
            print(f"\n   App ID: {app.get('id')}")
            subscribed_fields = app.get('subscribed_fields', [])
            
            if not subscribed_fields:
                print("   ❌ Aucun champ webhook abonné!")
            else:
                print("   📋 Champs abonnés:")
                for field in subscribed_fields:
                    print(f"      ✅ {field}")
            
            # Vérifier les champs critiques pour les commentaires
            critical_fields = ['feed', 'comments', 'mention']
            print("\n   📋 Champs requis pour les commentaires:")
            for field in critical_fields:
                if field in subscribed_fields:
                    print(f"      ✅ {field}")
                else:
                    print(f"      ❌ {field} - NON ABONNÉ!")
                    
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_comment_api(page_id):
    """Tester si on peut lire/écrire des commentaires"""
    print("\n" + "="*60)
    print("4️⃣  TEST D'ACCÈS AUX COMMENTAIRES")
    print("="*60)
    
    # Récupérer les posts récents
    url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
    params = {
        'access_token': PAGE_ACCESS_TOKEN,
        'limit': 5,
        'fields': 'id,message,comments{id,message,from}'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ Erreur: {data['error']['message']}")
            return
        
        posts = data.get('data', [])
        
        if not posts:
            print("ℹ️  Aucun post récent trouvé")
            return
        
        print(f"\n✅ {len(posts)} posts récents trouvés")
        
        for post in posts[:2]:  # 2 premiers posts
            post_id = post.get('id')
            message = post.get('message', 'Sans texte')[:50]
            comments = post.get('comments', {}).get('data', [])
            
            print(f"\n📄 Post {post_id}")
            print(f"   Message: {message}...")
            print(f"   💬 {len(comments)} commentaire(s)")
            
            if comments:
                for comment in comments[:2]:  # 2 premiers commentaires
                    print(f"      - {comment.get('from', {}).get('name')}: {comment.get('message', '')[:50]}...")
        
        print("\n✅ L'accès aux commentaires fonctionne!")
                    
    except Exception as e:
        print(f"❌ Erreur: {e}")

def check_webhook_subscription():
    """Vérifier l'abonnement webhook au niveau de l'app"""
    print("\n" + "="*60)
    print("5️⃣  VÉRIFICATION ABONNEMENT WEBHOOK APP")
    print("="*60)
    
    print("\n⚠️  Cette vérification nécessite un App Access Token")
    print("📖 Pour vérifier manuellement:")
    print("   1. Allez sur https://developers.facebook.com/apps/")
    print(f"   2. Sélectionnez votre app (ID: {APP_ID})")
    print("   3. Allez dans 'Webhooks' dans le menu gauche")
    print("   4. Vérifiez que les champs suivants sont cochés:")
    print("      ✓ feed")
    print("      ✓ comments")
    print("      ✓ mention")
    print("      ✓ messages (pour les messages privés)")

def show_setup_instructions():
    """Afficher les instructions de configuration"""
    print("\n" + "="*60)
    print("🔧 INSTRUCTIONS DE CONFIGURATION")
    print("="*60)
    
    print("""
Si des champs webhook sont manquants, voici comment les ajouter:

1️⃣  Aller sur Facebook Developers:
   https://developers.facebook.com/apps/

2️⃣  Sélectionner votre application

3️⃣  Dans le menu gauche, cliquer sur "Webhooks"

4️⃣  Pour le produit "Pages", cliquer sur "Modifier"

5️⃣  Cocher ces champs (CRITIQUE):
   ✅ feed (pour les commentaires sur les posts)
   ✅ comments (pour les commentaires)
   ✅ mention (pour les mentions)
   ✅ messages (pour les messages privés)

6️⃣  Cliquer sur "Enregistrer"

7️⃣  Vérifier que votre URL webhook est bien:
   https://votre-app.onrender.com/webhook

8️⃣  Verify Token doit correspondre à FACEBOOK_VERIFY_TOKEN dans .env
""")

def main():
    print("="*60)
    print("🔍 DIAGNOSTIC CONFIGURATION FACEBOOK")
    print("="*60)
    
    if not PAGE_ACCESS_TOKEN:
        print("❌ FACEBOOK_PAGE_ACCESS_TOKEN non trouvé dans .env")
        return
    
    if not APP_ID:
        print("❌ FACEBOOK_APP_ID non trouvé dans .env")
        return
    
    # Exécuter tous les checks
    page_id = check_page_info()
    
    if page_id:
        check_page_permissions()
        check_subscribed_fields(page_id)
        test_comment_api(page_id)
    
    check_webhook_subscription()
    show_setup_instructions()
    
    print("\n" + "="*60)
    print("✅ DIAGNOSTIC TERMINÉ")
    print("="*60)
    print("\n💡 Prochaines étapes:")
    print("   1. Corriger les problèmes identifiés ci-dessus")
    print("   2. Redémarrer votre app sur Render")
    print("   3. Tester avec un vrai commentaire")
    print("   4. Surveiller les logs Render")

if __name__ == "__main__":
    main()