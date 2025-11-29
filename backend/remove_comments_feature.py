"""
Script pour supprimer la fonctionnalité des commentaires
Garde uniquement les messages Messenger
"""
from models import db, Comment
from app import create_app

def remove_comments_feature():
    """Supprimer les commentaires de la base de données"""
    print("\n" + "="*70)
    print("🗑️ SUPPRESSION DE LA FONCTIONNALITÉ COMMENTAIRES")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        # Compter les commentaires
        comment_count = Comment.query.count()
        
        print(f"\n📊 Statistiques actuelles:")
        print(f"   Commentaires dans la DB: {comment_count}")
        
        if comment_count > 0:
            confirm = input(f"\n⚠️ Supprimer {comment_count} commentaire(s) ? (o/n): ").strip().lower()
            
            if confirm == 'o':
                # Supprimer tous les commentaires
                Comment.query.delete()
                db.session.commit()
                print(f"   ✅ {comment_count} commentaire(s) supprimé(s)")
            else:
                print("   ❌ Opération annulée")
        else:
            print("   ℹ️ Aucun commentaire à supprimer")
        
        print("\n" + "="*70)
        print("📝 FICHIERS À MODIFIER")
        print("="*70)
        
        print("\n✅ Modifiez les fichiers suivants:")
        print("\n1️⃣ models.py")
        print("   → Commentez ou supprimez la classe Comment")
        
        print("\n2️⃣ app.py")
        print("   → Supprimez la fonction handle_comment()")
        print("   → Supprimez le traitement 'changes' dans webhook()")
        
        print("\n3️⃣ facebook.py")
        print("   → Supprimez l'endpoint /pages/<id>/test-comment-reply")
        
        print("\n4️⃣ responses.py")
        print("   → Supprimez l'endpoint /comments")
        
        print("\n5️⃣ facebook_service.py")
        print("   → Supprimez la fonction reply_to_comment()")
        print("   → Supprimez la fonction get_comment_info()")
        print("   → Supprimez la fonction test_comment_reply()")
        
        print("\n6️⃣ response_service.py")
        print("   → Changez response_type par défaut à 'message'")
        
        print("\n" + "="*70)
        print("✅ CONFIGURATION TERMINÉE")
        print("="*70)
        
        print("\n🎯 Le bot fonctionnera maintenant uniquement avec:")
        print("   ✅ Messages Messenger")
        print("   ❌ Commentaires Facebook (désactivés)")

if __name__ == '__main__':
    remove_comments_feature()