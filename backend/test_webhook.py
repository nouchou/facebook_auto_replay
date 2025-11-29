"""
Script de diagnostic complet pour Facebook Auto-Reply
Usage: 
    flask shell
    >>> from diagnostic import run_full_diagnostic
    >>> run_full_diagnostic(page_id=1)
"""

import requests
from models import FacebookPage, Comment, Message, AutoResponse, db

def run_full_diagnostic(page_id):
    """
    Diagnostic complet du système
    """
    print("\n" + "="*70)
    print("🔍 DIAGNOSTIC COMPLET FACEBOOK AUTO-REPLY")
    print("="*70)
    
    # ÉTAPE 1: Vérifier la page
    print("\n📄 ÉTAPE 1: Vérification de la page")
    print("-"*70)
    
    page = FacebookPage.query.get(page_id)
    if not page:
        print(f"❌ Page ID {page_id} introuvable dans la base de données")
        return False
    
    print(f"✅ Page trouvée:")
    print(f"   - Nom: {page.page_name}")
    print(f"   - Page ID: {page.page_id}")
    print(f"   - Active: {page.is_active}")
    print(f"   - Token: {page.access_token[:20]}...")
    
    access_token = page.access_token
    fb_page_id = page.page_id
    
    # ÉTAPE 2: Vérifier le token
    print("\n🔑 ÉTAPE 2: Validation du token")
    print("-"*70)
    
    token_url = f"https://graph.facebook.com/v18.0/me"
    token_response = requests.get(token_url, params={
        'access_token': access_token,
        'fields': 'id,name'
    })
    
    if token_response.status_code != 200:
        print(f"❌ Token invalide!")
        print(f"   Erreur: {token_response.json()}")
        return False
    
    page_info = token_response.json()
    print(f"✅ Token valide")
    print(f"   - Page Name: {page_info.get('name')}")
    print(f"   - Page ID: {page_info.get('id')}")
    
    # ÉTAPE 3: Vérifier les permissions
    print("\n🔐 ÉTAPE 3: Vérification des permissions")
    print("-"*70)
    
    perms_url = f"https://graph.facebook.com/v18.0/me/permissions"
    perms_response = requests.get(perms_url, params={
        'access_token': access_token
    })
    
    if perms_response.status_code != 200:
        print(f"❌ Impossible de récupérer les permissions")
        return False
    
    permissions = perms_response.json().get('data', [])
    granted = [p['permission'] for p in permissions if p['status'] == 'granted']
    
    critical_perms = {
        'pages_messaging': '💬 Messages Messenger',
        'pages_manage_metadata': '⚙️ Métadonnées',
        'pages_read_engagement': '👀 Lecture engagement',
        'pages_manage_posts': '🔥 RÉPONDRE AUX COMMENTAIRES (CRITIQUE!)'
    }
    
    all_perms_ok = True
    for perm, description in critical_perms.items():
        if perm in granted:
            print(f"   ✅ {description}: {perm}")
        else:
            print(f"   ❌ {description}: {perm} (MANQUANT!)")
            all_perms_ok = False
    
    if not all_perms_ok:
        print("\n   ⚠️ ATTENTION: Permissions manquantes!")
        print("   📝 Pour corriger:")
        print("   1. https://developers.facebook.com/tools/explorer")
        print("   2. Générez un nouveau token avec TOUTES les permissions")
        print("   3. Mettez à jour le token dans votre app")
        return False
    
    print("\n   ✅ Toutes les permissions sont OK!")
    
    # ÉTAPE 4: Vérifier l'abonnement webhook
    print("\n📡 ÉTAPE 4: Vérification de l'abonnement webhook")
    print("-"*70)
    
    webhook_url = f"https://graph.facebook.com/v18.0/{fb_page_id}/subscribed_apps"
    webhook_response = requests.get(webhook_url, params={
        'access_token': access_token
    })
    
    if webhook_response.status_code != 200:
        print(f"❌ Erreur vérification webhook: {webhook_response.json()}")
        return False
    
    subscribed_data = webhook_response.json().get('data', [])
    
    if not subscribed_data:
        print("   ❌ Page NON abonnée aux webhooks!")
        print("\n   💡 Solution immédiate:")
        print(f"   POST https://votre-domaine.com/api/facebook/pages/{page_id}/subscribe-webhooks")
        print("\n   Ou avec curl:")
        print(f"   curl -X POST https://votre-domaine.com/api/facebook/pages/{page_id}/subscribe-webhooks")
        return False
    
    app_data = subscribed_data[0]
    subscribed_fields = app_data.get('subscribed_fields', [])
    
    critical_fields = {
        'feed': '📝 Posts et feed (CRITIQUE pour commentaires!)',
        'comments': '💬 Commentaires (CRITIQUE!)',
        'messages': '📩 Messages Messenger'
    }
    
    all_fields_ok = True
    print("   Champs abonnés:")
    for field, description in critical_fields.items():
        if field in subscribed_fields:
            print(f"   ✅ {description}: {field}")
        else:
            print(f"   ❌ {description}: {field} (MANQUANT!)")
            all_fields_ok = False
    
    if not all_fields_ok:
        print("\n   ⚠️ Champs critiques manquants!")
        print("   💡 Solution:")
        print(f"   POST https://votre-domaine.com/api/facebook/pages/{page_id}/subscribe-webhooks")
        return False
    
    print("\n   ✅ Tous les champs critiques sont abonnés!")
    
    # ÉTAPE 5: Tester récupération des posts
    print("\n📋 ÉTAPE 5: Test de récupération des posts")
    print("-"*70)
    
    posts_url = f"https://graph.facebook.com/v18.0/{fb_page_id}/feed"
    posts_response = requests.get(posts_url, params={
        'access_token': access_token,
        'limit': 5,
        'fields': 'id,message,created_time'
    })
    
    if posts_response.status_code != 200:
        print(f"   ⚠️ Impossible de récupérer les posts: {posts_response.json()}")
    else:
        posts = posts_response.json().get('data', [])
        print(f"   ✅ {len(posts)} posts récents trouvés")
        
        if posts:
            latest_post = posts[0]
            print(f"\n   Post le plus récent:")
            print(f"   - ID: {latest_post['id']}")
            print(f"   - Message: {latest_post.get('message', 'Pas de texte')[:50]}...")
            
            # Test des commentaires
            post_id = latest_post['id']
            comments_url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
            comments_response = requests.get(comments_url, params={
                'access_token': access_token,
                'limit': 5,
                'fields': 'id,message,from'
            })
            
            if comments_response.status_code == 200:
                comments = comments_response.json().get('data', [])
                print(f"\n   ✅ {len(comments)} commentaires trouvés sur ce post")
                
                if comments:
                    print(f"\n   Commentaire le plus récent:")
                    comment = comments[0]
                    print(f"   - ID: {comment['id']}")
                    print(f"   - Auteur: {comment.get('from', {}).get('name')}")
                    print(f"   - Message: {comment.get('message', '')[:50]}...")
                    
                    print(f"\n   💡 Pour tester la réponse automatique:")
                    print(f"   POST /api/facebook/pages/{page_id}/test-comment-reply")
                    print(f"   Body: {{'comment_id': '{comment['id']}'}}")
    
    # ÉTAPE 6: Vérifier les réponses automatiques
    print("\n🤖 ÉTAPE 6: Vérification des réponses automatiques")
    print("-"*70)
    
    responses = AutoResponse.query.filter_by(is_active=True).all()
    print(f"   Réponses actives: {len(responses)}")
    
    if not responses:
        print("   ⚠️ Aucune réponse automatique configurée!")
        print("   💡 Ajoutez des réponses via: POST /api/responses")
    else:
        for resp in responses[:5]:
            print(f"\n   - Mot-clé: {resp.trigger_keyword}")
            print(f"     Réponse: {resp.response_text[:50]}...")
            print(f"     Type: {resp.response_type}")
    
    # ÉTAPE 7: Vérifier l'historique
    print("\n📊 ÉTAPE 7: Historique des interactions")
    print("-"*70)
    
    total_messages = Message.query.filter_by(page_id=page_id).count()
    total_comments = Comment.query.filter_by(page_id=page_id).count()
    auto_messages = Message.query.filter_by(page_id=page_id, is_automated=True).count()
    auto_comments = Comment.query.filter_by(page_id=page_id, is_automated=True).count()
    
    print(f"   Messages reçus: {total_messages}")
    print(f"   - Automatiques: {auto_messages}")
    print(f"   Commentaires reçus: {total_comments}")
    print(f"   - Automatiques: {auto_comments}")
    
    if total_comments > 0:
        latest_comment = Comment.query.filter_by(page_id=page_id).order_by(
            Comment.timestamp.desc()
        ).first()
        print(f"\n   Dernier commentaire:")
        print(f"   - De: {latest_comment.user_name}")
        print(f"   - Texte: {latest_comment.comment_text[:50]}...")
        print(f"   - Réponse: {latest_comment.response_sent[:50] if latest_comment.response_sent else 'Aucune'}...")
        print(f"   - Date: {latest_comment.timestamp}")
    
    # RÉSUMÉ FINAL
    print("\n" + "="*70)
    print("📋 RÉSUMÉ DU DIAGNOSTIC")
    print("="*70)
    
    issues = []
    
    if not all_perms_ok:
        issues.append("❌ Permissions manquantes")
    
    if not all_fields_ok:
        issues.append("❌ Webhooks mal configurés")
    
    if not responses:
        issues.append("⚠️ Aucune réponse automatique")
    
    if issues:
        print("\n🚨 PROBLÈMES DÉTECTÉS:\n")
        for issue in issues:
            print(f"   {issue}")
        print("\n   Corrigez ces problèmes avant de continuer.")
        return False
    else:
        print("\n✅ TOUT EST CONFIGURÉ CORRECTEMENT!")
        print("\n   Le système est prêt à répondre aux commentaires.")
        print("\n   📝 Pour tester:")
        print("   1. Faites un post sur votre page Facebook")
        print("   2. Commentez avec un mot-clé configuré")
        print("   3. Vérifiez les logs en temps réel")
        print("\n   📊 Surveillez les logs:")
        print("   - Sur Render: Dashboard > Logs")
        print("   - En local: terminal où tourne Flask")
        return True

# Fonction helper pour tester un commentaire spécifique
def test_specific_comment(page_id, comment_id):
    """
    Tester la réponse à un commentaire spécifique
    """
    print("\n" + "="*70)
    print(f"🧪 TEST DE RÉPONSE AU COMMENTAIRE {comment_id}")
    print("="*70)
    
    page = FacebookPage.query.get(page_id)
    if not page:
        print(f"❌ Page {page_id} introuvable")
        return False
    
    # Récupérer les infos du commentaire
    comment_url = f"https://graph.facebook.com/v18.0/{comment_id}"
    comment_response = requests.get(comment_url, params={
        'access_token': page.access_token,
        'fields': 'id,message,from,created_time'
    })
    
    if comment_response.status_code != 200:
        print(f"❌ Commentaire introuvable: {comment_response.json()}")
        return False
    
    comment_data = comment_response.json()
    print(f"\n✅ Commentaire trouvé:")
    print(f"   - Message: {comment_data.get('message')}")
    print(f"   - Auteur: {comment_data.get('from', {}).get('name')}")
    
    # Tenter de répondre
    reply_url = f"https://graph.facebook.com/v18.0/{comment_id}/comments"
    reply_response = requests.post(reply_url, json={
        'message': 'Test automatique - Réponse fonctionnelle! ✅',
        'access_token': page.access_token
    })
    
    if reply_response.status_code == 200:
        result = reply_response.json()
        print(f"\n✅ SUCCÈS! Réponse envoyée")
        print(f"   - ID de la réponse: {result.get('id')}")
        return True
    else:
        error = reply_response.json()
        print(f"\n❌ ÉCHEC de la réponse:")
        print(f"   - Erreur: {error}")
        return False

# Usage dans Flask shell:
# >>> from diagnostic import run_full_diagnostic, test_specific_comment
# >>> run_full_diagnostic(1)
# >>> test_specific_comment(1, "123456_789012")