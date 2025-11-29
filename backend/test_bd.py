#!/usr/bin/env python3
"""
Test rapide pour vérifier si la page est liée à l'app
"""

import requests
import sys

# Configuration
PAGE_ID = "847215158480695"
ACCESS_TOKEN = "EAAMO3n7MHVgBQKNG7jhZBJpK3dmkGIdGGQjZCOokuqMEfXawgO8lOfhczdUSnWEyI9KoPvXgocxxFfo6iIqUfMbgZCr47Ob5ZAZAyZBaSetZBQTbKCXUkyo7dZBKY0f0OOwMw7cVdjSAuZB2Dfqpbx7essNtj1UJi4kNZCJcfn2DmzPp7VZAOnrO4Gub2ftSqj6C4G0WZA2Y7iTZAKQZDZD"

print("\n" + "="*70)
print("🔍 TEST RAPIDE - VÉRIFICATION PAGE/APP")
print("="*70)

# Test 1: La page est-elle abonnée à une app ?
print("\n📋 Vérification de l'abonnement de la page...")

url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/subscribed_apps"

try:
    response = requests.get(url, params={'access_token': ACCESS_TOKEN}, timeout=10)
    
    if response.status_code != 200:
        print(f"\n❌ ERREUR API: {response.status_code}")
        print(response.json())
        sys.exit(1)
    
    data = response.json()
    apps = data.get('data', [])
    
    print(f"\nNombre d'apps abonnées : {len(apps)}")
    
    if len(apps) == 0:
        print("\n" + "="*70)
        print("❌ PROBLÈME TROUVÉ : LA PAGE N'EST ABONNÉE À AUCUNE APP!")
        print("="*70)
        
        print("\n🔧 SOLUTION :")
        print("\n1. Allez sur : https://developers.facebook.com/apps")
        print("2. Sélectionnez votre application")
        print("3. Menu gauche → Produits → Webhooks")
        print("4. Section 'Pages' → Cliquez 'Modifier l'abonnement'")
        print("5. Dans le menu déroulant, sélectionnez 'Message auto replay'")
        print("6. Cochez les cases : feed, messages, mention")
        print("7. Cliquez 'Enregistrer'")
        
        print("\n📸 CAPTURES D'ÉCRAN :")
        print("   https://imgur.com/a/facebook-webhook-setup")
        
        print("\n" + "="*70)
        
        sys.exit(1)
    
    print("\n✅ La page est abonnée à des applications!")
    
    for i, app in enumerate(apps, 1):
        print(f"\n📱 Application #{i}")
        print(f"   ID : {app.get('id')}")
        print(f"   Link : {app.get('link', 'N/A')}")
        
        fields = app.get('subscribed_fields', [])
        print(f"   Champs abonnés : {', '.join(fields) if fields else 'AUCUN'}")
        
        # Vérifier les champs critiques
        critical = ['feed', 'messages']
        missing = [f for f in critical if f not in fields]
        
        if missing:
            print(f"\n   ⚠️ CHAMPS MANQUANTS : {', '.join(missing)}")
            print(f"\n   🔧 SOLUTION :")
            print(f"      1. Allez sur Facebook Developers")
            print(f"      2. Webhooks → Pages → Modifier l'abonnement")
            print(f"      3. Cochez : {', '.join(missing)}")
        else:
            print(f"   ✅ Tous les champs critiques sont présents!")
    
    # Test 2: Les permissions sont-elles OK ?
    print("\n\n📋 Vérification des permissions...")
    
    url = "https://graph.facebook.com/v18.0/me/permissions"
    response = requests.get(url, params={'access_token': ACCESS_TOKEN}, timeout=10)
    
    if response.status_code == 200:
        perms_data = response.json().get('data', [])
        granted = [p['permission'] for p in perms_data if p['status'] == 'granted']
        
        critical_perms = [
            'pages_manage_posts',
            'pages_read_engagement',
            'pages_messaging'
        ]
        
        missing_perms = [p for p in critical_perms if p not in granted]
        
        if missing_perms:
            print(f"\n❌ PERMISSIONS MANQUANTES : {', '.join(missing_perms)}")
            print("\n🔧 SOLUTION :")
            print("   1. Générez un nouveau token sur :")
            print("   https://developers.facebook.com/tools/explorer")
            print("   2. Sélectionnez ces permissions :")
            for perm in missing_perms:
                print(f"      • {perm}")
            print("   3. Mettez à jour le token dans votre app")
        else:
            print("✅ Toutes les permissions critiques sont présentes!")
    
    # Résumé final
    print("\n" + "="*70)
    
    if len(apps) > 0 and not missing:
        print("✅ TOUT EST CONFIGURÉ CORRECTEMENT!")
        print("="*70)
        
        print("\n🧪 TESTEZ MAINTENANT :")
        print("   1. Allez sur votre page Facebook")
        print("   2. Créez un nouveau post")
        print("   3. Commentez avec 'bonjour'")
        print("   4. Surveillez les logs Render")
        print("      https://dashboard.render.com → Votre service → Logs")
        
        print("\n📊 Dans les logs, vous devriez voir :")
        print("   📨 WEBHOOK REÇU")
        print("   💭 TRAITEMENT COMMENTAIRE")
        print("   ✅ SUCCÈS COMPLET")
        
        print("\n⏰ Si après 30 secondes rien ne se passe :")
        print("   → Vérifiez que le webhook URL est bien configuré")
        print("   → Essayez de re-vérifier le webhook sur Facebook Developers")
    else:
        print("⚠️ CONFIGURATION INCOMPLÈTE - SUIVEZ LES INSTRUCTIONS CI-DESSUS")
        print("="*70)
    
    print()

except requests.exceptions.RequestException as e:
    print(f"\n❌ ERREUR RÉSEAU : {e}")
    print("\nVérifiez votre connexion Internet et réessayez.")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ ERREUR : {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)