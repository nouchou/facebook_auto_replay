"""
Script de test automatique - Connexion Backend + PostgreSQL
"""
import requests
import json
import time

# URL de votre backend
BACKEND_URL = "https://facebook-auto-replay.onrender.com"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_1_health_check():
    """Test 1: Backend est-il en ligne ?"""
    print_section("TEST 1 : Backend en ligne ?")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Backend en ligne")
            print(f"   Réponse: {response.json()}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Timeout - Le backend ne répond pas")
        print("   Vérifiez que Render est bien déployé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_2_database_read():
    """Test 2: Peut-on LIRE la base de données ?"""
    print_section("TEST 2 : Lecture Base de Données")
    
    print("📖 Test de lecture GET /api/responses...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/responses", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Lecture DB réussie !")
            print(f"📊 {len(data)} réponse(s) trouvée(s)")
            
            if len(data) > 0:
                print("\n   Exemples:")
                for resp in data[:2]:
                    print(f"   • {resp['trigger_keyword']} → {resp['response_text'][:40]}...")
            
            return True
        
        elif response.status_code == 500:
            print("❌ Erreur 500 - Problème de connexion à la DB")
            print(f"   Détails: {response.text[:200]}")
            return False
        
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"   Réponse: {response.text[:200]}")
            return False
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_3_database_write():
    """Test 3: Peut-on ÉCRIRE dans la base de données ?"""
    print_section("TEST 3 : Écriture Base de Données")
    
    print("✍️  Test d'écriture POST /api/responses...")
    
    test_data = {
        "trigger_keyword": f"test_db_connexion_{int(time.time())}",
        "response_text": "✅ Test d'écriture dans PostgreSQL réussi !",
        "response_type": "both",
        "priority": 1,
        "is_active": True
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/responses",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Écriture DB réussie !")
            print(f"   ID créé: {result.get('id', 'N/A')}")
            print(f"   Message: {result.get('message', '')}")
            return True
        
        elif response.status_code == 500:
            print("❌ Erreur 500 - Impossible d'écrire dans la DB")
            print(f"   Détails: {response.text[:200]}")
            return False
        
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"   Réponse: {response.text[:200]}")
            return False
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_4_stats():
    """Test 4: Les statistiques fonctionnent-elles ?"""
    print_section("TEST 4 : Statistiques")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/responses/stats", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Statistiques disponibles\n")
            print(f"📊 Statistiques:")
            print(f"   • Réponses automatiques: {stats.get('total_responses', 0)}")
            print(f"   • Réponses actives: {stats.get('active_responses', 0)}")
            print(f"   • Messages traités: {stats.get('total_messages', 0)}")
            print(f"   • Commentaires: {stats.get('total_comments', 0)}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_5_facebook_pages():
    """Test 5: Les pages Facebook sont-elles enregistrées ?"""
    print_section("TEST 5 : Pages Facebook")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/facebook/pages", timeout=10)
        
        if response.status_code == 200:
            pages = response.json()
            print(f"✅ {len(pages)} page(s) enregistrée(s)")
            
            if len(pages) > 0:
                print("\n📄 Pages:")
                for page in pages:
                    status = "✅ Active" if page['is_active'] else "❌ Inactive"
                    print(f"   {status} {page['page_name']} (ID: {page['page_id']})")
            else:
                print("\n⚠️  Aucune page enregistrée")
                print("   Action requise: POST /api/facebook/pages")
            
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def check_database_url():
    """Vérifier le type de base de données utilisée"""
    print_section("VÉRIFICATION : Type de Base de Données")
    
    print("🔍 Analyse des logs Render...")
    print("\nDans les logs de déploiement, cherchez:")
    print('   "💾 Database: postgresql"  ← DOIT être "postgresql"')
    print('   "💾 Database: sqlite"      ← MAUVAIS (pas de PostgreSQL)')
    print("\nSi vous voyez 'sqlite', DATABASE_URL n'est pas configurée !")


def run_all_tests():
    """Exécuter tous les tests"""
    print("\n" + "🧪 TEST CONNEXION BACKEND + POSTGRESQL ".center(60, "="))
    print(f"Backend: {BACKEND_URL}")
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Vérification préliminaire
    check_database_url()
    
    print("\n⏳ Démarrage des tests dans 3 secondes...")
    time.sleep(3)
    
    # Test 1
    results['Backend en ligne'] = test_1_health_check()
    
    if not results['Backend en ligne']:
        print("\n❌ Le backend n'est pas accessible. Tests interrompus.")
        print("\nActions recommandées:")
        print("  1. Vérifiez que le service est 'Live' sur Render")
        print("  2. Consultez les logs pour les erreurs")
        return
    
    time.sleep(1)
    
    # Test 2
    results['Lecture DB'] = test_2_database_read()
    time.sleep(1)
    
    # Test 3
    results['Écriture DB'] = test_3_database_write()
    time.sleep(1)
    
    # Test 4
    results['Statistiques'] = test_4_stats()
    time.sleep(1)
    
    # Test 5
    results['Pages Facebook'] = test_5_facebook_pages()
    
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
    
    # Diagnostic
    print("\n" + "="*60)
    print("🔍 DIAGNOSTIC")
    print("="*60)
    
    if passed == total:
        print("\n🎉 PARFAIT ! Tout fonctionne correctement !")
        print("\n✅ Votre chatbot est prêt:")
        print("   • Backend en ligne")
        print("   • PostgreSQL connectée")
        print("   • Lecture/Écriture fonctionnelles")
        print("   • API opérationnelle")
        print("\n🚀 Prochaine étape:")
        print("   • Configurer le webhook Facebook")
        print("   • Tester en envoyant un message à votre page")
    
    elif results['Backend en ligne'] and not results['Lecture DB']:
        print("\n⚠️  Backend en ligne MAIS problème de base de données")
        print("\n❌ Problème: DATABASE_URL incorrecte ou manquante")
        print("\n✅ Solution:")
        print("   1. Allez dans Render Dashboard → PostgreSQL → Info")
        print("   2. Copiez l'Internal Database URL")
        print("   3. Backend → Environment → Ajoutez DATABASE_URL")
        print("   4. Redéployez")
    
    elif results['Lecture DB'] and not results['Écriture DB']:
        print("\n⚠️  Lecture OK mais Écriture échoue")
        print("\n❌ Problème: Permissions de la base de données")
        print("\n✅ Solution:")
        print("   • Vérifiez les permissions PostgreSQL")
        print("   • Recréez la base de données si nécessaire")
    
    else:
        print("\n⚠️  Plusieurs tests ont échoué")
        print("\n📋 Checklist:")
        print("   [ ] Service backend 'Live' sur Render")
        print("   [ ] DATABASE_URL configurée (Internal URL)")
        print("   [ ] Variables Facebook ajoutées")
        print("   [ ] Logs montrent 'Database: postgresql'")


if __name__ == "__main__":
    run_all_tests()
    
    print("\n" + "="*60)
    print("✅ Tests terminés!")
    print("="*60 + "\n")