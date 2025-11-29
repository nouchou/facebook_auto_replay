"""
Script pour connecter une page Facebook à votre base de données
Usage: python connect_page.py
"""

import requests

# ============ CONFIGURATION ============
BASE_URL = "https://facebook-auto-replay.onrender.com"

# Vos informations Facebook
PAGE_ID = "847215158480695"  # Votre Page ID Facebook
PAGE_NAME = "Message auto replay"
ACCESS_TOKEN = "EAAMO3n7MHVgBQKNG7jhZBJpK3dmkGIdGGQjZCOokuqMEfXawgO8lOfhczdUSnWEyI9KoPvXgocxxFfo6iIqUfMbgZCr47Ob5ZAZAyZBaSetZBQTbKCXUkyo7dZBKY0f0OOwMw7cVdjSAuZB2Dfqpbx7essNtj1UJi4kNZCJcfn2DmzPp7VZAOnrO4Gub2ftSqj6C4G0WZA2Y7iTZAKQZDZD"  # Mettez votre token complet ici
# ========================================

def connect_page():
    """Connecter la page à la base de données"""
    
    print("\n" + "="*70)
    print("CONNEXION DE LA PAGE FACEBOOK")
    print("="*70)
    
    print(f"\n📋 Informations:")
    print(f"   - Page ID: {PAGE_ID}")
    print(f"   - Nom: {PAGE_NAME}")
    print(f"   - Token: {ACCESS_TOKEN[:30]}...")
    
    # Données à envoyer
    data = {
        "page_id": PAGE_ID,
        "page_name": PAGE_NAME,
        "access_token": ACCESS_TOKEN
    }
    
    print(f"\n📤 Envoi de la requête...")
    print(f"   URL: {BASE_URL}/api/facebook/pages")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/facebook/pages",
            json=data,
            timeout=15
        )
        
        print(f"\n📥 Réponse reçue:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"\n✅ SUCCÈS!")
            print(f"   Message: {result.get('message')}")
            
            if 'page' in result:
                page_info = result['page']
                print(f"\n📄 Page connectée:")
                print(f"   - ID base de données: {page_info.get('id')}")
                print(f"   - Page ID Facebook: {page_info.get('page_id')}")
                print(f"   - Nom: {page_info.get('page_name')}")
            
            return True
        else:
            print(f"\n❌ ERREUR:")
            try:
                error = response.json()
                print(f"   {error}")
            except:
                print(f"   {response.text}")
            
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Impossible de se connecter à {BASE_URL}")
        print(f"   Vérifiez que l'URL est correcte")
        return False
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

def verify_connection():
    """Vérifier que la page est bien connectée"""
    
    print("\n" + "="*70)
    print("VÉRIFICATION DE LA CONNEXION")
    print("="*70)
    
    try:
        print(f"\n🔍 Récupération des pages...")
        response = requests.get(f"{BASE_URL}/api/facebook/pages", timeout=10)
        
        if response.status_code == 200:
            pages = response.json()
            
            if not pages:
                print(f"   ⚠️ Aucune page trouvée")
                return False
            
            print(f"\n✅ {len(pages)} page(s) connectée(s):\n")
            
            for page in pages:
                print(f"   📄 {page['page_name']}")
                print(f"      - ID BDD: {page['id']}")
                print(f"      - Page ID: {page['page_id']}")
                print(f"      - Active: {'✅' if page['is_active'] else '❌'}")
                print()
            
            return True
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def subscribe_webhooks(page_db_id=1):
    """Abonner la page aux webhooks"""
    
    print("\n" + "="*70)
    print("ABONNEMENT AUX WEBHOOKS")
    print("="*70)
    
    try:
        print(f"\n📡 Abonnement de la page (ID: {page_db_id})...")
        
        response = requests.post(
            f"{BASE_URL}/api/facebook/pages/{page_db_id}/subscribe-webhooks",
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"\n✅ SUCCÈS!")
                print(f"   {result.get('message')}")
                
                if 'subscribed_fields' in result:
                    print(f"\n   Champs abonnés:")
                    for field in result['subscribed_fields']:
                        print(f"   ✅ {field}")
                
                return True
            else:
                print(f"\n❌ Échec:")
                print(f"   {result.get('error')}")
                return False
        else:
            print(f"\n❌ Erreur HTTP {response.status_code}")
            try:
                print(f"   {response.json()}")
            except:
                print(f"   {response.text}")
            return False
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

def add_test_response():
    """Ajouter une réponse automatique de test"""
    
    print("\n" + "="*70)
    print("AJOUT D'UNE RÉPONSE AUTOMATIQUE")
    print("="*70)
    
    response_data = {
        "trigger_keyword": "bonjour, salut, hello, salama",
        "response_text": "Salama Tompoko oh! Inona no azoko atao anao? Merci!",
        "response_type": "both",
        "priority": 10,
        "is_active": True
    }
    
    try:
        print(f"\n📝 Création de la réponse...")
        print(f"   Mots-clés: {response_data['trigger_keyword']}")
        print(f"   Réponse: {response_data['response_text'][:50]}...")
        
        response = requests.post(
            f"{BASE_URL}/api/responses",
            json=response_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"\n✅ SUCCÈS!")
            print(f"   {result.get('message')}")
            return True
        else:
            print(f"\n⚠️ Status: {response.status_code}")
            print(f"   (La réponse existe peut-être déjà)")
            return False
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

def main():
    """Menu principal"""
    
    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║              CONFIGURATION FACEBOOK AUTO-REPLY                     ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    print(f"\n🌐 Backend: {BASE_URL}")
    print(f"📄 Page: {PAGE_NAME} ({PAGE_ID})")
    
    print("\n\nQue voulez-vous faire?")
    print("1. Connecter la page à la base de données")
    print("2. Vérifier les pages connectées")
    print("3. Abonner aux webhooks")
    print("4. Ajouter une réponse automatique de test")
    print("5. Configuration complète (1+2+3+4)")
    
    choice = input("\nChoix (1-5): ").strip()
    
    if choice == "1":
        connect_page()
    
    elif choice == "2":
        verify_connection()
    
    elif choice == "3":
        page_id = input("\nID de la page dans la BDD (défaut: 1): ").strip()
        if not page_id:
            page_id = 1
        else:
            page_id = int(page_id)
        
        subscribe_webhooks(page_id)
    
    elif choice == "4":
        add_test_response()
    
    elif choice == "5":
        print("\n🚀 CONFIGURATION COMPLÈTE\n")
        
        # Étape 1
        if not connect_page():
            print("\n⛔ Échec à l'étape 1. Abandon.")
            return
        
        input("\n⏸️  Appuyez sur Enter pour continuer...")
        
        # Étape 2
        if not verify_connection():
            print("\n⛔ Échec à l'étape 2. Abandon.")
            return
        
        input("\n⏸️  Appuyez sur Enter pour continuer...")
        
        # Étape 3
        if not subscribe_webhooks(1):
            print("\n⚠️ Échec à l'étape 3, mais on continue...")
        
        input("\n⏸️  Appuyez sur Enter pour continuer...")
        
        # Étape 4
        add_test_response()
        
        print("\n" + "="*70)
        print("✅ CONFIGURATION TERMINÉE!")
        print("="*70)
        print("\n📝 Prochaines étapes:")
        print("   1. Allez sur votre page Facebook")
        print("   2. Créez un post")
        print("   3. Commentez avec 'bonjour' ou 'salama'")
        print("   4. Le bot devrait répondre automatiquement!")
        print("\n📊 Surveillez les logs sur Render:")
        print("   https://dashboard.render.com > Votre service > Logs")
    
    else:
        print("\n❌ Choix invalide")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()