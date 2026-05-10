"""
Script de test - Vérifie que l'application fonctionne correctement
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pymongo import MongoClient
from datetime import datetime
import time

def test_mongodb_connection():
    """Test la connexion MongoDB"""
    print("\n🔌 Test 1: Connexion MongoDB...")
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["SD2026_projet"]
        server_info = client.server_info()
        print(f"   ✅ Connecté à MongoDB {server_info['version']}")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_collections_creation():
    """Test la création des collections"""
    print("\n📚 Test 2: Collections...")
    try:
        from dbMongo import articles, abonnements, consultations, TEAM_INITIALS
        
        print(f"   ✅ Collections trouvées (Initiales: {TEAM_INITIALS})")
        print(f"      - {articles.full_name}")
        print(f"      - {abonnements.full_name}")
        print(f"      - {consultations.full_name}")
        
        # Afficher les indexes
        indexes = articles.list_indexes()
        print(f"   ✅ Indexes sur articles: {len(list(indexes))}")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_scraper():
    """Test le scraper"""
    print("\n🔍 Test 3: Scraper...")
    try:
        from scraper import fetch_articles
        
        # Test avec une URL de démonstration
        print("   ⏳ Récupération d'articles de test...")
        articles = fetch_articles("https://www.lemonde.fr/sitemap_news.xml")
        
        if articles:
            print(f"   ✅ {len(articles)} articles récupérés")
            print(f"      Premier article: {articles[0]['title'][:50]}...")
            return True
        else:
            print("   ⚠️  Aucun article récupéré (vérifier la connexion)")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_wordcloud():
    """Test la génération de wordcloud"""
    print("\n☁️  Test 4: Wordcloud Generator...")
    try:
        from wordcloud_generator import generate_wordcloud
        
        # Créer des articles de test
        test_articles = [
            {"title": "France économie croissance PIB"},
            {"title": "Monde politique élections gouvernement"},
            {"title": "Technologie innovation intelligence artificielle"},
            {"title": "Sports football match équipe victoire"},
            {"title": "Culture art musée exposition"}
        ]
        
        result = generate_wordcloud(test_articles, num_words=10)
        
        if result:
            print(f"   ✅ Wordcloud généré: {result}")
            return True
        else:
            print("   ❌ Impossible de générer le wordcloud")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_database_operations():
    """Test les opérations CRUD"""
    print("\n💾 Test 5: Opérations base de données...")
    try:
        from dbMongo import (
            add_subscription, get_subscriptions, delete_subscription,
            insert_articles, get_articles, abonnements
        )
        
        # Test ajout abonnement
        print("   ⏳ Test ajout abonnement...")
        sub_id = add_subscription("Test Source", "https://www.lefigaro.fr/sitemap_news.xml")
        print(f"      ✅ Abonnement créé: {sub_id}")
        
        # Test récupération
        subs = get_subscriptions()
        print(f"      ✅ {len(subs)} abonnements en base")
        
        # Test insertion articles
        test_articles = [
            {"title": "Article 1", "url": "https://example.com/1", "date": "2026-05-09T10:00:00"},
            {"title": "Article 2", "url": "https://example.com/2", "date": "2026-05-09T11:00:00"}
        ]
        inserted = insert_articles(test_articles, source="Test")
        print(f"      ✅ {inserted} articles insérés")
        
        # Test récupération articles
        articles = get_articles(10)
        print(f"      ✅ {len(articles)} articles récupérés")
        
        # Nettoyage
        abonnements.delete_one({"_id": sub_id})
        print("      ✅ Abonnement supprimé")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_image_extraction():
    """Test l'extraction d'images"""
    print("\n🖼️  Test 7: Extraction d'images...")
    try:
        from scraper import fetch_articles
        
        print("   ⏳ Test extraction d'images...")
        articles = fetch_articles("https://www.lemonde.fr/sitemap_news.xml")
        
        if articles:
            # Compter les articles avec et sans images
            with_images = sum(1 for art in articles if art.get('image'))
            without_images = len(articles) - with_images
            
            print(f"   ✅ {with_images} articles avec image, {without_images} sans image")
            if with_images > 0:
                print(f"      Exemple d'image: {articles[0].get('image', 'N/A')[:100]}...")
            return True
        else:
            print("   ❌ Aucun article récupéré")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def main():
    print("=" * 50)
    print("  Nuage d'Actualité - Test Suite")
    print("=" * 50)
    
    tests = [
        test_mongodb_connection,
        test_collections_creation,
        test_scraper,
        test_wordcloud,
        test_database_operations,
        test_flask_import,
        test_image_extraction
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Erreur non gérée: {e}")
            results.append(False)
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests réussis: {passed}/{total}")
    
    if passed == total:
        print("\n✅ TOUT EST OPÉRATIONNEL!")
        print("\nVous pouvez lancer l'application avec:")
        print("  - Windows: run.bat")
        print("  - Linux/Mac: ./run.sh")
        print("  - Ou: cd src && python main.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) échoué(s)")
        print("\nVérifiez les erreurs ci-dessus et relancez le test")
        return 1

if __name__ == "__main__":
    sys.exit(main())
