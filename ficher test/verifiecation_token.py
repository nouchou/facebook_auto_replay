#!/usr/bin/env python3
"""
Vérifier que le verify token est correct
"""

import requests
import os

BASE_URL = "https://facebook-auto-replay.onrender.com"

print("\n" + "="*70)
print("🔐 VÉRIFICATION DU VERIFY TOKEN")
print("="*70)

# 1. Quel est votre verify token actuel ?
print("\n📋 Vérifiez votre fichier config.py ou .env")
print("\nQuel est votre FACEBOOK_VERIFY_TOKEN ?")
print("(Le token que vous avez configuré dans votre application)")

verify_token = input("\nVerify Token: ").strip()

if not verify_token:
    print("\n❌ Token requis!")
    exit(1)

# 2. Tester si le webhook répond avec ce token
print(f"\n🧪 Test du webhook avec le token : {verify_token}")

try:
    response = requests.get(
        f"{BASE_URL}/webhook",
        params={
            'hub.mode': 'subscribe',
            'hub.verify_token': verify_token,
            'hub.challenge': 'test_challenge_12345'
        },
        timeout=10
    )
    
    print(f"\n📥 Réponse du serveur:")
    print(f"   Status: {response.status_code}")
    print(f"   Body: {response.text}")
    
    if response.status_code == 200:
        if response.text == 'test_challenge_12345':
            print("\n✅ PARFAIT! Le verify token fonctionne!")
            print("\n📋 Assurez-vous que ce MÊME token est configuré sur:")
            print("   Facebook Developers → Webhooks → Verify Token")
        else:
            print("\n⚠️ Le serveur répond, mais pas avec le bon challenge")
    elif response.status_code == 403:
        print("\n❌ PROBLÈME: Verify token incorrect!")
        print("\n🔧 SOLUTIONS:")
        print("   1. Vérifiez que le token dans config.py correspond")
        print("   2. Sur Facebook Developers:")
        print("      - Webhooks → Modifier")
        print(f"      - Verify Token: {verify_token}")
        print("      - Enregistrez et re-vérifiez")
    else:
        print(f"\n❌ Erreur inattendue: {response.status_code}")

except Exception as e:
    print(f"\n❌ Erreur: {e}")

print("\n" + "="*70)
print("📖 INSTRUCTIONS POUR FACEBOOK DEVELOPERS")
print("="*70)

print(f"""
1. Allez sur: https://developers.facebook.com/apps
2. Sélectionnez votre app
3. Produits → Webhooks
4. Section 'Pages' → Cliquez 'Modifier'
5. Vérifiez:
   ✓ URL: {BASE_URL}/webhook
   ✓ Verify Token: {verify_token}
6. Cliquez 'Vérifier et enregistrer'
7. Le statut doit devenir VERT ✓

Si le statut reste ROUGE ❌:
   → Le verify token ne correspond pas
   → Vérifiez le fichier config.py
   → Redéployez sur Render si vous l'avez modifié
""")

print("="*70 + "\n")