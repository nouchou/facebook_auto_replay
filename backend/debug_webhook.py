#!/usr/bin/env python3
"""
Script de diagnostic si les webhooks ne sont pas reçus
"""

import requests
import json

# Configuration
BASE_URL = "https://facebook-auto-replay.onrender.com"
PAGE_ID = "847215158480695"
ACCESS_TOKEN = "EAAMO3n7MHVgBQKNG7jhZBJpK3dmkGIdGGQjZCOokuqMEfXawgO8lOfhczdUSnWEyI9KoPvXgocxxFfo6iIqUfMbgZCr47Ob5ZAZAyZBaSetZBQTbKCXUkyo7dZBKY0f0OOwMw7cVdjSAuZB2Dfqpbx7essNtj1UJi4kNZCJcfn2DmzPp7VZAOnrO4Gub2ftSqj6C4G0WZA2Y7iTZAKQZDZD"

def check_webhook_configuration():
    """Vérifier la configuration webhook sur Facebook"""
    
    print("\n" + "="*70)
    print("🔍 DIAGNOSTIC WEBHOOK FACEBOOK")
    print("="*70)
    
    # 1. Vérifier les webhooks de l'app
    print("\n1️⃣ Configuration webhook de l'application")
    print("   Pour vérifier manuellement:")
    print("   1. Allez sur https://developers.facebook.com")
    print("   2. Sélectionnez votre app")
    print("   3. Produits → Webhooks")
    print("   4. Vérifiez:")
    print(f"      ✓ URL: {BASE_URL}/webhook")
    print("      ✓ Verify Token: (votre token)")
    print("      ✓ Statut: Vert/Vérifié")
    
    # 2. Vérifier l'abonnement de la page
    print("\n2️⃣ Abonnement de la page aux webhooks")
    
    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/subscribed_apps"
    response = requests.get(url, params={'access_token': ACCESS_TOKEN})
    
    if response.status_code == 200:
        data = response.json()
        apps = data.get('data', [])
        
        if not apps:
            print("   ❌ PROBLÈME: La page n'est abonnée à AUCUNE application!")
            print("\n   💡 SOLUTION:")
            print("      1. Allez sur https://developers.facebook.com")
            print("      2. Votre app → Produits → Webhooks")
            print("      3. Cliquez sur 'Modifier l'abonnement' pour Pages")
            print("      4. Sélectionnez votre page dans la liste")
            print("      5. Cochez 'feed' et 'messages'")
            print("      6. Enregistrez")
            return False
        
        print(f"   ✅ Page abonnée à {len(apps)} app(s)")
        
        for app in apps:
            app_id = app.get('id')
            fields = app.get('subscribed_fields', [])
            
            print(f"\n   App ID: {app_id}")
            print(f"   Champs abonnés: {', '.join(fields)}")
            
            # Vérifier les champs critiques
            critical_missing = []
            if 'feed' not in fields:
                critical_missing.append('feed')
            if 'messages' not in fields:
                critical_missing.append('messages')
            
            if critical_missing:
                print(f"   ⚠️ MANQUANT: {', '.join(critical_missing)}")
                return False
            else:
                print("   ✅ Tous les champs critiques présents")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        print(f"   {response.json()}")
        return False
    
    # 3. Tester l'endpoint webhook
    print("\n3️⃣ Test de l'endpoint webhook")
    
    try:
        response = requests.get(f"{BASE_URL}/webhook", params={
            'hub.mode': 'subscribe',
            'hub.verify_token': 'test',
            'hub.challenge': 'test123'
        }, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Endpoint accessible")
            print(f"   Réponse: {response.text}")
        elif response.status_code == 403:
            print(f"   ✅ Endpoint accessible (403 = verify_token incorrect)")
        else:
            print(f"   ⚠️ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # 4. Vérifier les permissions
    print("\n4️⃣ Permissions du token")
    
    url = "https://graph.facebook.com/v18.0/me/permissions"
    response = requests.get(url, params={'access_token': ACCESS_TOKEN})
    
    if response.status_code == 200:
        perms_data = response.json().get('data', [])
        granted = [p['permission'] for p in perms_data if p['status'] == 'granted']
        
        critical_perms = {
            'pages_manage_posts': False,
            'pages_read_engagement': False,
            'pages_messaging': False
        }
        
        for perm in granted:
            if perm in critical_perms:
                critical_perms[perm] = True
        
        all_ok = all(critical_perms.values())
        
        for perm, has_it in critical_perms.items():
            icon = "✅" if has_it else "❌"
            print(f"   {icon} {perm}")
        
        if not all_ok:
            print("\n   ❌ PROBLÈME: Permissions manquantes!")
            print("\n   💡 SOLUTION:")
            print("      1. Allez sur https://developers.facebook.com/tools/explorer")
            print("      2. Sélectionnez votre app")
            print("      3. Générez un nouveau token avec:")
            print("         • pages_manage_posts")
            print("         • pages_read_engagement")
            print("         • pages_messaging")
            print("      4. Mettez à jour le token dans votre app")
            return False
    
    # 5. Instructions pour tester manuellement
    print("\n" + "="*70)
    print("📋 CHECKLIST MANUELLE")
    print("="*70)
    
    print("\n✅ Allez sur https://developers.facebook.com/apps")
    print("✅ Sélectionnez votre application")
    print("✅ Produits → Webhooks → Pages")
    print("\nVérifiez:")
    print("   ☐ URL du webhook est bien configurée")
    print("   ☐ Verify Token correspond")
    print("   ☐ Statut est 'Vérifié' (vert)")
    print("   ☐ Les champs 'feed' et 'messages' sont cochés")
    print("   ☐ Votre page Facebook est sélectionnée")
    
    print("\n" + "="*70)
    print("🧪 TEST MANUEL")
    print("="*70)
    print("\n1. Créez un post sur votre page Facebook")
    print("2. Commentez immédiatement (dans les 5 secondes)")
    print("3. Surveillez les logs Render en temps réel")
    print("4. Cherchez '📨 WEBHOOK REÇU'")
    
    print("\n📊 Si vous ne voyez RIEN dans les logs:")
    print("   → Facebook n'envoie PAS le webhook")
    print("   → Vérifiez la checklist ci-dessus")
    print("   → Assurez-vous que la page est bien LIÉE à l'app")
    
    return True

def test_comment_manually():
    """Permettre de tester un commentaire manuellement"""
    
    print("\n" + "="*70)
    print("🧪 TEST MANUEL D'UN COMMENTAIRE")
    print("="*70)
    
    print("\nCollez l'URL d'un commentaire Facebook:")
    print("(Format: https://www.facebook.com/...)")
    
    comment_url = input("\nURL: ").strip()
    
    if not comment_url:
        print("Annulé.")
        return
    
    # Extraire le comment_id de l'URL
    # Format: POST_ID_COMMENT_ID
    try:
        # Essayer d'extraire l'ID
        if 'comment_id=' in comment_url:
            comment_id = comment_url.split('comment_id=')[1].split('&')[0]
        elif '/comments/' in comment_url:
            comment_id = comment_url.split('/comments/')[1].split('/')[0]
        else:
            print("❌ Format d'URL non reconnu")
            print("Entrez directement le comment_id (format: 123456_789012):")
            comment_id = input("Comment ID: ").strip()
        
        print(f"\nComment ID détecté: {comment_id}")
        print("Tentative de réponse...")
        
        # Utiliser l'API directement
        url = f"https://graph.facebook.com/v18.0/{comment_id}/comments"
        
        response = requests.post(url, json={
            'message': '✅ Test manuel - Le bot fonctionne!',
            'access_token': ACCESS_TOKEN
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ SUCCÈS! Réponse postée.")
            print(f"ID de la réponse: {result.get('id')}")
        else:
            error = response.json()
            print(f"\n❌ ERREUR:")
            print(json.dumps(error, indent=2))
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║           DIAGNOSTIC WEBHOOK - FACEBOOK AUTO-REPLY            ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    print("\nQue voulez-vous faire?")
    print("1. Diagnostic complet de la configuration")
    print("2. Tester une réponse manuelle à un commentaire")
    print("3. Afficher les instructions complètes")
    
    choice = input("\nChoix (1-3): ").strip()
    
    if choice == "1":
        check_webhook_configuration()
    
    elif choice == "2":
        test_comment_manually()
    
    elif choice == "3":
        print("\n" + "="*70)
        print("📖 GUIDE COMPLET DE CONFIGURATION WEBHOOK")
        print("="*70)
        
        print("\n🔧 ÉTAPE 1: Configuration sur Facebook Developers")
        print("   1. Allez sur: https://developers.facebook.com/apps")
        print("   2. Sélectionnez votre application")
        print("   3. Dans le menu → Produits → Webhooks")
        print("   4. Pour 'Pages', cliquez 'Modifier l'abonnement'")
        print("   5. Vérifiez:")
        print(f"      • URL: {BASE_URL}/webhook")
        print("      • Verify Token: (votre token de vérification)")
        print("   6. Cochez ces champs:")
        print("      ☑ feed (commentaires et posts)")
        print("      ☑ messages (messages privés)")
        print("   7. Enregistrez")
        
        print("\n🔗 ÉTAPE 2: Lier votre page à l'app")
        print("   1. Toujours sur developers.facebook.com")
        print("   2. Produits → Webhooks → Pages")
        print("   3. Cliquez 'Modifier l'abonnement'")
        print("   4. Sélectionnez votre page dans la liste déroulante")
        print("   5. Enregistrez")
        
        print("\n✅ ÉTAPE 3: Vérification")
        print("   1. Le statut doit être 'Vérifié' (pastille verte)")
        print("   2. La page doit apparaître comme abonnée")
        
        print("\n🧪 ÉTAPE 4: Test")
        print("   1. Créez un post sur votre page")
        print("   2. Commentez-le avec 'bonjour'")
        print("   3. Surveillez les logs Render")
        print("   4. Le bot doit répondre en quelques secondes")
        
        print("\n" + "="*70)
    
    else:
        print("❌ Choix invalide")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()