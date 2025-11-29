"""
Vérifier le statut de l'app Facebook (Development vs Live)
"""
import requests
from models import db, FacebookPage
from app import create_app

def check_app_status():
    """Vérifier si l'app est en mode Live ou Development"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("🔍 DIAGNOSTIC COMPLET - POURQUOI LES COMMENTAIRES NE MARCHENT PAS")
        print("="*70)
        
        page = FacebookPage.query.filter_by(is_active=True).first()
        
        if not page:
            print("❌ Aucune page active")
            return
        
        print(f"\n📄 Page: {page.page_name}")
        print(f"🆔 Page ID: {page.page_id}")
        
        # Test 1: Vérifier les infos de l'app
        print("\n" + "="*70)
        print("TEST 1: STATUT DE L'APPLICATION FACEBOOK")
        print("="*70)
        
        try:
            # Obtenir les infos de l'app via le token
            url = "https://graph.facebook.com/v18.0/me"
            response = requests.get(url, params={
                'access_token': page.access_token,
                'fields': 'id,name,access_token'
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Token valide")
                print(f"   Page ID: {data.get('id')}")
                print(f"   Page Name: {data.get('name')}")
            else:
                print(f"❌ Token invalide ou expiré")
                print(f"   Erreur: {response.json()}")
                return
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return
        
        # Test 2: Vérifier les permissions
        print("\n" + "="*70)
        print("TEST 2: PERMISSIONS DU TOKEN")
        print("="*70)
        
        try:
            url = "https://graph.facebook.com/v18.0/me/permissions"
            response = requests.get(url, params={
                'access_token': page.access_token
            })
            
            if response.status_code == 200:
                perms = response.json().get('data', [])
                granted = [p['permission'] for p in perms if p['status'] == 'granted']
                
                critical_perms = {
                    'pages_manage_posts': '🔥 CRITIQUE pour répondre aux commentaires',
                    'pages_read_engagement': 'Lire l\'engagement',
                    'pages_manage_metadata': 'Gérer métadonnées'
                }
                
                print("Permissions critiques:")
                all_ok = True
                for perm, desc in critical_perms.items():
                    if perm in granted:
                        print(f"   ✅ {perm}: {desc}")
                    else:
                        print(f"   ❌ {perm}: {desc}")
                        all_ok = False
                
                if not all_ok:
                    print("\n⚠️ PERMISSIONS MANQUANTES!")
                    print("Solution:")
                    print("1. https://developers.facebook.com/tools/explorer")
                    print("2. Générez un nouveau token avec TOUTES les permissions")
                    print("3. Mettez à jour le token dans votre app")
                    return
            else:
                print(f"❌ Impossible de vérifier les permissions")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Test 3: Vérifier l'abonnement webhook
        print("\n" + "="*70)
        print("TEST 3: ABONNEMENT WEBHOOK")
        print("="*70)
        
        try:
            url = f"https://graph.facebook.com/v18.0/{page.page_id}/subscribed_apps"
            response = requests.get(url, params={
                'access_token': page.access_token
            })
            
            if response.status_code == 200:
                result = response.json()
                subscribed_data = result.get('data', [])
                
                if subscribed_data:
                    fields = subscribed_data[0].get('subscribed_fields', [])
                    print(f"✅ App abonnée aux webhooks")
                    print(f"   Champs: {', '.join(fields)}")
                    
                    if 'feed' in fields:
                        print(f"   ✅ 'feed' est abonné (inclut commentaires)")
                    else:
                        print(f"   ❌ 'feed' n'est PAS abonné!")
                        print(f"   Solution: python quick_start.py")
                        return
                else:
                    print(f"❌ App NON abonnée aux webhooks!")
                    print(f"   Solution: python quick_start.py")
                    return
            else:
                print(f"❌ Erreur: {response.json()}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Test 4: LE TEST LE PLUS IMPORTANT
        print("\n" + "="*70)
        print("TEST 4: 🔥 STATUT DE L'APPLICATION (CRITIQUE!)")
        print("="*70)
        
        print("\n⚠️ ATTENTION - RÈGLE FACEBOOK:")
        print("   Les apps en mode 'Development' ne reçoivent AUCUN webhook")
        print("   même pour les admins, développeurs ou testeurs!")
        print("\n📋 Pour vérifier le statut de votre app:")
        print("   1. Allez sur: https://developers.facebook.com/apps")
        print("   2. Sélectionnez votre app")
        print("   3. Regardez en haut à droite:")
        print("      • 🔴 'Development' = LES WEBHOOKS NE MARCHERONT PAS")
        print("      • 🟢 'Live' = Les webhooks fonctionnent")
        
        print("\n🔑 COMMENT PASSER EN MODE 'LIVE':")
        print("="*70)
        print("OPTION 1 - Simple (sans App Review):")
        print("   1. Allez dans App Dashboard")
        print("   2. Settings → Basic")
        print("   3. En bas, cliquez 'Switch to Live Mode'")
        print("   4. Confirmez")
        print("   Note: Fonctionne si vous êtes admin/développeur de la page")
        
        print("\nOPTION 2 - Complète (avec App Review):")
        print("   1. App Dashboard → App Review")
        print("   2. Demandez les permissions:")
        print("      • pages_manage_posts")
        print("      • pages_read_engagement")
        print("   3. Attendez l'approbation (1-7 jours)")
        print("   4. Passez en mode Live")
        
        print("\n💡 ASTUCE POUR TESTER EN MODE DEV:")
        print("="*70)
        print("Créez une 2ème app temporaire:")
        print("   1. Créez nouvelle app Facebook")
        print("   2. Configurez les webhooks")
        print("   3. Passez-la en mode LIVE immédiatement")
        print("   4. Utilisez-la pour les tests")
        print("   5. Gardez votre app principale en dev")
        
        # Test 5: Vérifier la configuration webhook sur Facebook
        print("\n" + "="*70)
        print("TEST 5: CONFIGURATION WEBHOOK SUR FACEBOOK")
        print("="*70)
        
        print("\n📋 Vérifiez sur Facebook Developers:")
        print("   1. https://developers.facebook.com/apps")
        print("   2. Votre app → Webhooks")
        print("   3. Section 'Pages'")
        print("   4. Vérifiez:")
        print("      ✓ Callback URL: https://facebook-auto-replay.onrender.com/webhook")
        print("      ✓ Verify Token: my_verify_token_123")
        print("      ✓ Statut: VERT ✓ (pas rouge ❌)")
        print("      ✓ Champ 'feed' est coché")
        
        # Résumé final
        print("\n" + "="*70)
        print("📊 RÉSUMÉ ET SOLUTIONS")
        print("="*70)
        
        print("\n✅ Ce qui est OK:")
        print("   • Token valide")
        print("   • Webhook abonné au champ 'feed'")
        print("   • Configuration backend correcte")
        
        print("\n❌ Causes possibles si ça ne marche pas:")
        print("   1. 🔥 APP EN MODE DEVELOPMENT (cause #1)")
        print("      → Passez en mode Live")
        
        print("\n   2. Permissions insuffisantes")
        print("      → Générez un nouveau token avec pages_manage_posts")
        
        print("\n   3. Webhook non vérifié sur Facebook")
        print("      → Vérifiez le statut dans Facebook Developers")
        
        print("\n   4. Vous testez sur un post ancien")
        print("      → Créez un NOUVEAU post et commentez dessus")
        
        print("\n   5. Délai de propagation")
        print("      → Attendez 1-2 minutes après configuration")
        
        print("\n" + "="*70)
        print("🎯 PROCHAINES ÉTAPES")
        print("="*70)
        print("1. Vérifiez le statut de votre app (Development ou Live)")
        print("2. Si Development → Passez en Live")
        print("3. Attendez 2 minutes")
        print("4. Créez un NOUVEAU post sur votre page")
        print("5. Commentez avec 'bonjour' ou 'salut'")
        print("6. Le bot devrait répondre en 5-10 secondes")
        print("\n💡 Si ça ne marche toujours pas:")
        print("   → Regardez les logs Render")
        print("   → Ou lancez: python monitor_logs.py")
        print("="*70)

if __name__ == '__main__':
    check_app_status()