"""
Script de test pour vérifier la configuration Webhook et API Graph Facebook
Exécutez ce script pour diagnostiquer votre configuration
"""

import requests
import json
import os
from datetime import datetime

# ============================================
# CONFIGURATION - À REMPLIR
# ============================================

# Votre token d'accès (celui visible dans l'image)
PAGE_ACCESS_TOKEN = "EAAiKkwNFIDgBQJEmbksAybAi95Iphoaco4yZAUemYHCMrv27i51FZBw4XKmQ88tHqs5PkDTUZCy6DjQBiuOY3ZBaHvFNn3v8xg0ZC0qbaBKB8MttrZCAH2P6rduFw6rcILwBzASLyL9Mqt8Kq5hZBpoEoZARV7S6nQsbDRd0j7ROG5hq6LOyRdpWhOEl6tRrboeZB6vtBfC9YDwZDZD"

# L'ID de votre page (visible dans la réponse: "834491979512788")
PAGE_ID = "847215158480695"

# URL de votre webhook déployé sur Render
WEBHOOK_URL = "https://facebook-auto-replay.onrender.com/webhook"

# Token de vérification (doit correspondre à celui dans config.py)
VERIFY_TOKEN = "my_verify_token_123"

GRAPH_API_VERSION = "v18.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


# ============================================
# TESTS
# ============================================

def print_section(title):
    """Afficher une section"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_1_page_info():
    """Test 1: Vérifier les informations de la page"""
    print_section("TEST 1: Informations de la Page")
    
    url = f"{GRAPH_API_BASE}/{PAGE_ID}"
    params = {
        "fields": "id,name,access_token,category,fan_count",
        "access_token": PAGE_ACCESS_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Connexion réussie à l'API Graph!")
            print(f"📄 Nom de la page: {data.get('name', 'N/A')}")
            print(f"🆔 ID de la page: {data.get('id', 'N/A')}")
            print(f"📂 Catégorie: {data.get('category', 'N/A')}")
            print(f"👥 Fans: {data.get('fan_count', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Détails: {json.dumps(data, indent=2)}")
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_2_permissions():
    """Test 2: Vérifier les permissions du token"""
    print_section("TEST 2: Permissions du Token")
    
    url = f"{GRAPH_API_BASE}/me/permissions"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            permissions = data.get('data', [])
            granted = [p['permission'] for p in permissions if p['status'] == 'granted']
            
            required_perms = [
                'pages_messaging',
                'pages_manage_engagement',
                'pages_read_engagement',
                'pages_manage_posts'
            ]
            
            print("✅ Permissions accordées:")
            for perm in granted:
                print(f"   ✓ {perm}")
            
            print("\n🔍 Vérification des permissions requises:")
            all_ok = True
            for perm in required_perms:
                if perm in granted:
                    print(f"   ✅ {perm}")
                else:
                    print(f"   ❌ {perm} - MANQUANT!")
                    all_ok = False
            
            return all_ok
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Détails: {json.dumps(data, indent=2)}")
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_3_webhook_url():
    """Test 3: Vérifier que l'URL webhook est accessible"""
    print_section("TEST 3: Accessibilité du Webhook")
    
    # Test GET (vérification Facebook)
    print("📡 Test de vérification webhook (GET)...")
    params = {
        'hub.mode': 'subscribe',
        'hub.verify_token': VERIFY_TOKEN,
        'hub.challenge': 'test_challenge_12345'
    }
    
    try:
        response = requests.get(WEBHOOK_URL, params=params, timeout=10)
        
        if response.status_code == 200 and response.text == 'test_challenge_12345':
            print("✅ Webhook répond correctement à la vérification!")
            return True
        else:
            print(f"❌ Réponse incorrecte du webhook")
            print(f"   Status: {response.status_code}")
            print(f"   Réponse: {response.text[:100]}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Timeout - Le webhook ne répond pas (vérifiez Render)")
        return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_4_send_message():
    """Test 4: Tester l'envoi d'un message (optionnel - nécessite un user_id)"""
    print_section("TEST 4: Test d'envoi de message")
    
    print("⚠️  Ce test nécessite un User ID valide.")
    print("    Pour l'obtenir, quelqu'un doit d'abord vous envoyer un message.")
    print("    Test ignoré pour le moment.")
    return True


def test_5_webhook_subscription():
    """Test 5: Vérifier les abonnements webhook"""
    print_section("TEST 5: Abonnements Webhook")
    
    url = f"{GRAPH_API_BASE}/{PAGE_ID}/subscribed_apps"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            subscriptions = data.get('data', [])
            
            if subscriptions:
                print("✅ Applications abonnées:")
                for sub in subscriptions:
                    print(f"   📱 {sub.get('name', 'N/A')} (ID: {sub.get('id', 'N/A')})")
                    if 'subscribed_fields' in sub:
                        print(f"      Champs: {', '.join(sub['subscribed_fields'])}")
                return True
            else:
                print("⚠️  Aucune application abonnée au webhook!")
                print("   Vous devez abonner votre app dans le Dashboard Facebook:")
                print("   1. Allez dans Paramètres > Webhooks")
                print("   2. Sélectionnez votre page")
                print("   3. Abonnez-vous aux événements: messages, messaging_postbacks, feed")
                return False
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Détails: {json.dumps(data, indent=2)}")
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_6_conversation_api():
    """Test 6: Tester l'API Conversations"""
    print_section("TEST 6: API Conversations")
    
    url = f"{GRAPH_API_BASE}/{PAGE_ID}/conversations"
    params = {
        "access_token": PAGE_ACCESS_TOKEN,
        "fields": "id,updated_time,message_count"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            conversations = data.get('data', [])
            print(f"✅ API Conversations accessible")
            print(f"   📊 {len(conversations)} conversation(s) trouvée(s)")
            
            if conversations:
                print("\n   Dernières conversations:")
                for conv in conversations[:3]:
                    print(f"   • ID: {conv.get('id')}")
                    print(f"     Messages: {conv.get('message_count', 0)}")
            
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            if 'error' in data:
                print(f"   Message: {data['error'].get('message', 'N/A')}")
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def run_all_tests():
    """Exécuter tous les tests"""
    print("\n" + "🤖 TEST DE CONFIGURATION CHATBOT FACEBOOK ".center(60, "="))
    print(f"⏰ Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "Infos Page": test_1_page_info(),
        "Permissions": test_2_permissions(),
        "Webhook URL": test_3_webhook_url(),
        "Envoi Message": test_4_send_message(),
        "Abonnements": test_5_webhook_subscription(),
        "API Conversations": test_6_conversation_api()
    }
    
    # Résumé
    print_section("RÉSUMÉ DES TESTS")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 Félicitations! Tout fonctionne correctement!")
        print("   Vous pouvez maintenant tester en envoyant un message à votre page.")
    else:
        print("\n⚠️  Certains tests ont échoué. Actions recommandées:")
        
        if not results["Permissions"]:
            print("   1. Vérifiez les permissions dans le Dashboard Facebook")
            print("      App > Paramètres de l'app > Autorisations et fonctionnalités")
        
        if not results["Webhook URL"]:
            print("   2. Vérifiez que votre application est déployée sur Render")
            print("      et que l'URL webhook est correcte")
        
        if not results["Abonnements"]:
            print("   3. Abonnez votre app aux webhooks de la page")
            print("      Dashboard > Webhooks > Sélectionner la page")


if __name__ == "__main__":
    print("\n🔧 Configuration:")
    print(f"   Page ID: {PAGE_ID}")
    print(f"   Webhook: {WEBHOOK_URL}")
    print(f"   Token: {PAGE_ACCESS_TOKEN[:20]}...")
    
    input("\nAppuyez sur Entrée pour commencer les tests...")
    
    run_all_tests()
    
    print("\n" + "="*60)
    print("Tests terminés!")
    print("="*60 + "\n")