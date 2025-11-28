"""
Test de Configuration Webhook Facebook
"""
import requests
import json

BACKEND_URL = "https://facebook-auto-replay.onrender.com"
VERIFY_TOKEN = "my_verify_token_123"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_1_webhook_verification():
    """Test 1: Le webhook répond-il à la vérification Facebook ?"""
    print_section("TEST 1 : Vérification Webhook")
    
    print("📡 Simulation de la vérification Facebook...")
    
    # Simuler la requête que Facebook envoie
    params = {
        'hub.mode': 'subscribe',
        'hub.verify_token': VERIFY_TOKEN,
        'hub.challenge': 'test_challenge_12345'
    }
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/webhook",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200 and response.text == 'test_challenge_12345':
            print("✅ Webhook vérifié avec succès !")
            print(f"   Status: {response.status_code}")
            print(f"   Réponse: {response.text}")
            print("\n✨ Facebook peut maintenant envoyer des webhooks à votre serveur !")
            return True
        
        elif response.status_code == 403:
            print("❌ Erreur 403 - Token de vérification incorrect")
            print(f"   Le serveur a reçu: {params['hub.verify_token']}")
            print(f"   Vérifiez FACEBOOK_VERIFY_TOKEN dans Render")
            return False
        
        else:
            print(f"❌ Réponse inattendue")
            print(f"   Status: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_2_webhook_post():
    """Test 2: Le webhook accepte-t-il les POSTs ?"""
    print_section("TEST 2 : Webhook POST")
    
    print("📨 Envoi d'un webhook test simulé...")
    
    # Simuler un webhook Facebook
    fake_webhook = {
        "object": "page",
        "entry": [
            {
                "id": "847215158480695",
                "time": 1234567890,
                "messaging": [
                    {
                        "sender": {"id": "123456789"},
                        "recipient": {"id": "847215158480695"},
                        "timestamp": 1234567890,
                        "message": {
                            "mid": "test_message_id",
                            "text": "test webhook"
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/webhook",
            json=fake_webhook,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200 and response.text == 'OK':
            print("✅ Webhook POST accepté !")
            print(f"   Status: {response.status_code}")
            print(f"   Réponse: {response.text}")
            print("\n⚠️  Note: Le message ne sera pas traité car c'est un test simulé")
            print("   Pour un vrai test, envoyez un message depuis Facebook Messenger")
            return True
        else:
            print(f"❌ Réponse inattendue")
            print(f"   Status: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_3_check_page_registered():
    """Test 3: La page est-elle bien enregistrée ?"""
    print_section("TEST 3 : Page Enregistrée")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/facebook/pages", timeout=10)
        
        if response.status_code == 200:
            pages = response.json()
            
            if len(pages) > 0:
                print(f"✅ {len(pages)} page(s) enregistrée(s)\n")
                
                for page in pages:
                    status = "✅ Active" if page['is_active'] else "❌ Inactive"
                    print(f"{status} {page['page_name']}")
                    print(f"   Page ID: {page['page_id']}")
                    print(f"   Token présent: {'Oui' if page.get('access_token') else 'Non'}")
                
                return True
            else:
                print("❌ Aucune page enregistrée")
                return False
        else:
            print(f"❌ Erreur {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_4_check_responses():
    """Test 4: Des réponses automatiques sont-elles configurées ?"""
    print_section("TEST 4 : Réponses Automatiques")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/responses", timeout=10)
        
        if response.status_code == 200:
            responses = response.json()
            
            print(f"✅ {len(responses)} réponse(s) configurée(s)\n")
            
            if len(responses) > 0:
                print("📋 Liste des réponses:")
                for resp in responses[:5]:
                    status = "✅" if resp['is_active'] else "❌"
                    print(f"{status} '{resp['trigger_keyword']}'")
                    print(f"   → {resp['response_text'][:60]}...")
                    print()
                
                return True
            else:
                print("⚠️  Aucune réponse configurée")
                print("   Le bot utilisera la réponse par défaut")
                return True  # Pas critique
        else:
            print(f"❌ Erreur {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def check_facebook_dashboard():
    """Instructions pour vérifier le Dashboard Facebook"""
    print_section("VÉRIFICATION : Dashboard Facebook")
    
    print("🔍 Vérifiez manuellement sur Facebook Developers:\n")
    
    print("1️⃣ Aller sur:")
    print("   https://developers.facebook.com/apps/860773702966616/webhooks/\n")
    
    print("2️⃣ Vérifier que vous voyez:")
    print("   ✅ Callback URL: https://facebook-auto-replay.onrender.com/webhook")
    print("   ✅ Verify Token: (masqué)")
    print("   ✅ Page 'Message auto replay' abonnée")
    print("   ✅ Événements cochés: messages, feed\n")
    
    print("3️⃣ Si ce n'est PAS le cas:")
    print("   • Cliquez 'Edit Subscription'")
    print("   • Entrez l'URL et le verify token")
    print("   • Cliquez 'Verify and Save'")
    print("   • Sélectionnez votre page")
    print("   • Cochez 'messages' et 'feed'")
    print("   • Cliquez 'Subscribe'\n")


def run_all_tests():
    """Exécuter tous les tests"""
    print("\n" + "🧪 TEST CONFIGURATION WEBHOOK FACEBOOK ".center(60, "="))
    print(f"Backend: {BACKEND_URL}")
    
    results = {}
    
    # Test 1
    results['Vérification Webhook'] = test_1_webhook_verification()
    
    # Test 2
    results['Webhook POST'] = test_2_webhook_post()
    
    # Test 3
    results['Page Enregistrée'] = test_3_check_page_registered()
    
    # Test 4
    results['Réponses Configurées'] = test_4_check_responses()
    
    # Instructions Dashboard
    check_facebook_dashboard()
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📈 Score: {passed}/{total} tests réussis ({int(passed/total*100)}%)")
    
    # Diagnostic final
    print("\n" + "="*60)
    print("🎯 PROCHAINES ÉTAPES")
    print("="*60)
    
    if results['Vérification Webhook'] and results['Page Enregistrée']:
        print("\n✅ Votre webhook est PRÊT !\n")
        
        print("🧪 TEST FINAL - Envoyez un VRAI message:")
        print("\n1. Ouvrez Facebook Messenger")
        print("2. Recherchez 'Message auto replay'")
        print("3. Envoyez: 'test'")
        print("4. Le bot devrait répondre automatiquement !\n")
        
        print("📊 Surveillez les logs Render:")
        print("   https://dashboard.render.com → Votre service → Logs")
        print("\n   Vous devriez voir:")
        print("   'Message traité de [Votre Nom]: test'")
        print("   'Réponse envoyée: ...'")
    
    else:
        print("\n⚠️  Configuration incomplète\n")
        
        if not results['Vérification Webhook']:
            print("❌ Problème: Webhook ne répond pas")
            print("   Solution: Vérifiez FACEBOOK_VERIFY_TOKEN dans Render")
        
        if not results['Page Enregistrée']:
            print("❌ Problème: Page non enregistrée")
            print("   Solution: POST /api/facebook/pages (déjà fait normalement)")
        
        print("\n📋 Checklist complète:")
        print("   [ ] Webhook vérifié")
        print("   [ ] Page enregistrée")
        print("   [ ] Dashboard Facebook configuré")
        print("   [ ] Page abonnée aux événements")


if __name__ == "__main__":
    run_all_tests()
    
    print("\n" + "="*60)
    print("✅ Tests terminés!")
    print("="*60 + "\n")