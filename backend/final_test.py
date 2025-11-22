"""
Test final : Envoyer un message de test à votre page
"""

import requests
import json

# Configuration - VOS VRAIES VALEURS
PAGE_ACCESS_TOKEN = "EAAiKkwNFIDgBQJEmbks..."  # Votre nouveau token
PAGE_ID = "847215158480695"
CONVERSATION_ID = "t_122136152834955153"  # De vos résultats

GRAPH_API = "https://graph.facebook.com/v18.0"


def test_1_read_conversation():
    """Lire la conversation existante"""
    print("\n" + "="*60)
    print("TEST 1 : Lire la conversation existante")
    print("="*60)
    
    url = f"{GRAPH_API}/{CONVERSATION_ID}/messages"
    params = {
        "access_token": PAGE_ACCESS_TOKEN,
        "fields": "id,from,to,message,created_time"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code == 200:
        messages = data.get('data', [])
        print(f"✅ {len(messages)} messages trouvés dans la conversation\n")
        
        for msg in messages:
            sender_id = msg.get('from', {}).get('id', 'N/A')
            message_text = msg.get('message', 'N/A')
            timestamp = msg.get('created_time', 'N/A')
            
            print(f"📩 Message de {sender_id}")
            print(f"   Contenu: {message_text}")
            print(f"   Date: {timestamp}\n")
        
        # Récupérer l'ID de l'expéditeur pour le test suivant
        if messages:
            for msg in messages:
                sender_id = msg.get('from', {}).get('id')
                if sender_id != PAGE_ID:  # Si ce n'est pas la page
                    return sender_id
        return None
    else:
        print(f"❌ Erreur: {data}")
        return None


def test_2_send_test_message(recipient_id):
    """Envoyer un message de test"""
    print("\n" + "="*60)
    print("TEST 2 : Envoyer un message de test")
    print("="*60)
    
    if not recipient_id:
        print("⚠️  Pas d'ID destinataire trouvé")
        print("   Solution: Quelqu'un doit d'abord envoyer un message à votre page")
        return False
    
    url = f"{GRAPH_API}/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": "🤖 Test automatique : Votre chatbot fonctionne !"},
        "access_token": PAGE_ACCESS_TOKEN
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    if response.status_code == 200:
        print(f"✅ Message envoyé avec succès!")
        print(f"   Message ID: {data.get('message_id', 'N/A')}")
        print(f"   Destinataire: {data.get('recipient_id', 'N/A')}")
        return True
    else:
        print(f"❌ Erreur: {data}")
        return False


def test_3_check_auto_responses():
    """Vérifier les réponses automatiques configurées"""
    print("\n" + "="*60)
    print("TEST 3 : Réponses automatiques disponibles")
    print("="*60)
    
    # Utiliser le contexte Flask
    try:
        from app import create_app
        from services.response_service import ResponseService
        
        app = create_app()
        
        # Simuler des messages pour voir quelles réponses seraient envoyées
        test_messages = [
            "Bonjour",
            "Quel est le prix ?",
            "C'est disponible ?",
            "Comment commander ?",
            "Merci"
        ]
        
        print("📝 Messages de test pour le NLP:\n")
        
        with app.app_context():
            for msg in test_messages:
                response = ResponseService.find_matching_response(msg, 'message')
                
                if response:
                    print(f"✅ '{msg}'")
                    print(f"   → {response[:80]}...")
                else:
                    print(f"⚠️  '{msg}'")
                    print(f"   → Aucune réponse configurée (réponse par défaut)")
                print()
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_4_verify_database():
    """Vérifier la configuration de la base de données"""
    print("\n" + "="*60)
    print("TEST 4 : Vérification Base de Données")
    print("="*60)
    
    try:
        from models import db, FacebookPage, AutoResponse, Message
        from app import create_app
        
        app = create_app()
        with app.app_context():
            # Vérifier la page
            page = FacebookPage.query.filter_by(page_id=PAGE_ID).first()
            
            if page:
                print(f"✅ Page enregistrée dans la DB")
                print(f"   Nom: {page.page_name}")
                print(f"   Active: {page.is_active}")
            else:
                print(f"⚠️  Page non enregistrée dans la DB")
                print(f"   Solution: Enregistrez-la via l'API")
                print(f"\n   Commande curl:")
                print(f"""
   curl -X POST https://facebook-auto-replay.onrender.com/api/facebook/pages \\
     -H "Content-Type: application/json" \\
     -d '{{
       "page_id": "{PAGE_ID}",
       "page_name": "Message auto replay",
       "access_token": "{PAGE_ACCESS_TOKEN[:20]}..."
     }}'
                """)
            
            # Vérifier les réponses auto
            responses = AutoResponse.query.filter_by(is_active=True).all()
            print(f"\n✅ {len(responses)} réponse(s) automatique(s) active(s)")
            
            if responses:
                for resp in responses[:5]:
                    print(f"   • '{resp.trigger_keyword}' → {resp.response_text[:50]}...")
            else:
                print("   ⚠️  Aucune réponse automatique configurée!")
                print("   Ajoutez des réponses via l'API:")
                print("""
   curl -X POST https://facebook-auto-replay.onrender.com/api/responses \\
     -H "Content-Type: application/json" \\
     -d '{
       "trigger_keyword": "bonjour,salut,hello",
       "response_text": "Bonjour ! Comment puis-je vous aider ?",
       "response_type": "both",
       "priority": 10
     }'
                """)
            
            # Vérifier les messages
            messages = Message.query.count()
            print(f"\n✅ {messages} message(s) enregistré(s) dans l'historique")
            
            # Afficher les derniers messages
            if messages > 0:
                recent_messages = Message.query.order_by(
                    Message.timestamp.desc()
                ).limit(3).all()
                
                print("\n📨 Derniers messages:")
                for msg in recent_messages:
                    print(f"   • {msg.sender_name}: {msg.message_text[:40]}...")
                    if msg.response_sent:
                        print(f"     → Bot: {msg.response_sent[:40]}...")
            
            return True
    
    except Exception as e:
        print(f"❌ Erreur DB: {e}")
        return False


def test_5_api_endpoints():
    """Tester les endpoints de l'API"""
    print("\n" + "="*60)
    print("TEST 5 : Endpoints API")
    print("="*60)
    
    base_url = "https://facebook-auto-replay.onrender.com"
    
    # Test health endpoint
    print("1. Test /health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ API opérationnelle: {response.json()}")
        else:
            print(f"   ❌ Erreur {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test webhook endpoint
    print("\n2. Test /webhook (verification)...")
    try:
        params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'my_verify_token_123',
            'hub.challenge': 'test123'
        }
        response = requests.get(f"{base_url}/webhook", params=params, timeout=5)
        if response.status_code == 200 and response.text == 'test123':
            print(f"   ✅ Webhook vérifié")
        else:
            print(f"   ❌ Webhook invalide")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test responses endpoint
    print("\n3. Test /api/responses...")
    try:
        response = requests.get(f"{base_url}/api/responses", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data)} réponses configurées")
        else:
            print(f"   ❌ Erreur {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")


def run_all_tests():
    """Exécuter tous les tests"""
    print("\n" + "🎯 TESTS FINAUX DU CHATBOT ".center(60, "="))
    
    results = {}
    
    # Test 1
    recipient_id = test_1_read_conversation()
    results['Conversation'] = recipient_id is not None
    
    # Test 2
    if recipient_id:
        results['Envoi message'] = test_2_send_test_message(recipient_id)
    else:
        print("\n⚠️  Test 2 ignoré (pas de destinataire)")
        results['Envoi message'] = None
    
    # Test 3
    results['Réponses auto'] = test_3_check_auto_responses()
    
    # Test 4
    results['Base de données'] = test_4_verify_database()
    
    # Test 5
    test_5_api_endpoints()
    
    # Résumé final
    print("\n" + "="*60)
    print("📋 RÉSUMÉ DES TESTS")
    print("="*60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    print("📱 ÉTAPES SUIVANTES")
    print("="*60)
    
    print("""
✅ VOTRE CHATBOT EST OPÉRATIONNEL !

🧪 Pour tester en conditions réelles:

1. Envoyez un message à votre page Facebook "Message auto replay"
   Depuis votre compte personnel Facebook, recherchez la page
   et envoyez un message comme:
   • "Bonjour"
   • "Quel est le prix ?"
   • "C'est disponible ?"

2. Le bot devrait répondre automatiquement ! 🤖

3. Vérifiez les logs Render pour voir le traitement:
   https://dashboard.render.com → Votre service → Logs
   
   Vous devriez voir:
   Message traité de [Votre nom]: bonjour
   Réponse envoyée: ...

4. Consultez votre base de données pour voir les messages:
   • GET /api/responses/messages
   • GET /api/responses/stats

📊 Endpoints utiles:
   • GET  /api/responses          - Liste des réponses
   • POST /api/responses          - Ajouter une réponse
   • GET  /api/responses/messages - Historique messages
   • GET  /api/nlp/sentiment-stats - Stats sentiment
   • GET  /api/nlp/intents-stats   - Stats intentions

💡 Si le bot ne répond pas:
   • Vérifiez que la page est enregistrée dans la DB (Test 4)
   • Ajoutez des réponses automatiques (POST /api/responses)
   • Consultez les logs Render pour les erreurs
    """)


if __name__ == "__main__":
    run_all_tests()