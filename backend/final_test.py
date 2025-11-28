"""
Script de diagnostic pour tester la configuration Facebook
Utilisation: python test_facebook.py
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
PAGE_ACCESS_TOKEN = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')  # Ajoutez à .env
GRAPH_VERSION = 'v18.0'
BASE_URL = f'https://graph.facebook.com/{GRAPH_VERSION}'

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_token():
    """Test 1: Token valide?"""
    print_header("TEST 1: Validité du token")
    
    url = f'{BASE_URL}/me'
    params = {'access_token': PAGE_ACCESS_TOKEN}
    
    try:
        response = requests.get(url, params=params)
        result = response.json()
        
        if 'error' in result:
            print(f"❌ ERREUR: {result['error']['message']}")
            return False
        else:
            print(f"✅ Token valide!")
            print(f"   Page: {result.get('name')}")
            print(f"   ID: {result.get('id')}")
            return True
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_permissions():
    """Test 2: Permissions OK?"""
    print_header("TEST 2: Permissions")
    
    url = f'{BASE_URL}/me/permissions'
    params = {'access_token': PAGE_ACCESS_TOKEN}
    
    try:
        response = requests.get(url, params=params)
        result = response.json()
        
        if 'data' in result:
            permissions = result['data']
            granted = [p['permission'] for p in permissions if p['status'] == 'granted']
            
            print("✅ Permissions accordées:")
            for perm in granted:
                print(f"   ✅ {perm}")
            
            # Critiques
            critical = [
                'pages_messaging',
                'pages_manage_metadata',
                'pages_read_engagement',
                'pages_manage_posts'
            ]
            
            missing = [p for p in critical if p not in granted]
            
            if missing:
                print("\n❌ PERMISSIONS MANQUANTES:")
                for perm in missing:
                    print(f"   ❌ {perm}")
                print("\n⚠️ SOLUTION:")
                print("   1. Allez sur developers.facebook.com/tools/explorer")
                print("   2. Générez un nouveau token")
                print("   3. Cochez toutes les permissions ci-dessus")
                return False
            else:
                print("\n✅ Toutes les permissions OK!")
                return True
        else:
            print(f"❌ ERREUR: {result.get('error', {}).get('message')}")
            return False
    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_webhook_subscription():
    """Test 3: Webhook abonné?"""
    print_header("TEST 3: Abonnement Webhook")
    
    if not PAGE_ID:
        print("⚠️ PAGE_ID manquant dans .env")
        print("   Ajoutez: FACEBOOK_PAGE_ID=votre_id")
        return False
    
    url = f'{BASE_URL}/{PAGE_ID}/subscribed_apps'
    params = {'access_token': PAGE_ACCESS_TOKEN}
    
    try:
        response = requests.get(url, params=params)
        result = response.json()
        
        if 'data' in result and result['data']:
            app_data = result['data'][0]
            subscribed_fields = app_data.get('subscribed_fields', [])
            
            print("✅ Page abonnée!")
            print("\n📡 Champs abonnés:")
            for field in subscribed_fields:
                print(f"   ✅ {field}")
            
            critical_fields = ['feed', 'comments', 'messages']
            missing = [f for f in critical_fields if f not in subscribed_fields]
            
            if missing:
                print("\n❌ CHAMPS MANQUANTS:")
                for field in missing:
                    print(f"   ❌ {field}")
                print("\n⚠️ SOLUTION: Tapez 'o' pour abonner")
                return False
            else:
                print("\n✅ Tous les champs OK!")
                return True
        else:
            print("❌ Page NON abonnée")
            print("\n⚠️ SOLUTION: Tapez 'o' pour abonner")
            return False
    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def subscribe_webhooks():
    """Abonner la page"""
    print_header("ABONNEMENT AUX WEBHOOKS")
    
    if not PAGE_ID:
        print("⚠️ PAGE_ID requis")
        return False
    
    url = f'{BASE_URL}/{PAGE_ID}/subscribed_apps'
    
    payload = {
        'subscribed_fields': [
            'messages',
            'messaging_postbacks',
            'message_deliveries',
            'message_reads',
            'feed',      # CRITIQUE pour commentaires!
            'comments',  # CRITIQUE pour commentaires!
            'mention'
        ],
        'access_token': PAGE_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        if result.get('success'):
            print("✅ Abonnement réussi!")
            print("\n📡 Champs abonnés:")
            for field in payload['subscribed_fields']:
                print(f"   ✅ {field}")
            return True
        else:
            print(f"❌ ERREUR: {result.get('error', {}).get('message')}")
            return False
    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def run_all_tests():
    """Exécuter tous les tests"""
    print("\n" + "🔍"*30)
    print("   DIAGNOSTIC FACEBOOK AUTO-REPLY")
    print("🔍"*30)
    
    if not PAGE_ACCESS_TOKEN:
        print("\n❌ ERREUR:")
        print("   FACEBOOK_PAGE_ACCESS_TOKEN manquant dans .env")
        return
    
    results = {}
    
    # Test 1
    results['token'] = test_token()
    if not results['token']:
        print("\n⛔ Token invalide - Arrêt")
        return
    
    # Test 2
    results['permissions'] = test_permissions()
    
    # Test 3
    results['webhook'] = test_webhook_subscription()
    
    # Abonner si nécessaire
    if not results['webhook']:
        print("\n" + "="*60)
        response = input("❓ Abonner la page maintenant? (o/n): ")
        if response.lower() == 'o':
            results['subscribe'] = subscribe_webhooks()
    
    # Résumé
    print("\n" + "="*60)
    print("   RÉSUMÉ")
    print("="*60)
    
    all_ok = True
    for test, passed in results.items():
        status = "✅ OK" if passed else "❌ FAIL"
        print(f"{test.upper():.<20} {status}")
        if not passed:
            all_ok = False
    
    print("="*60)
    
    if all_ok:
        print("\n🎉 CONFIGURATION COMPLÈTE!")
        print("   ✅ Messages Messenger")
        print("   ✅ Commentaires Facebook")
    else:
        print("\n⚠️ CONFIGURATION INCOMPLÈTE")
        print("   Corrigez les erreurs ci-dessus")

if __name__ == '__main__':
    run_all_tests()