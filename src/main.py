from flask import Flask, render_template, request, redirect, jsonify, url_for
import os
import logging
from datetime import datetime, timedelta
from scraper import fetch_articles
from dbMongo import (
    insert_articles, add_consultation, add_subscription, get_subscriptions,
    delete_subscription, get_articles, search_articles, get_consultations,
    articles, get_sources, update_subscription_fetch, get_articles_by_source,
    add_favorite, get_favorites
)
from wordcloud_generator import generate_wordcloud
from bson.objectid import ObjectId

from dbMongo import articles as articles_collection

# Supprimer les articles de plus de 30 jours de la source Le Monde
result = articles_collection.delete_many({
})

print(f"{result.deleted_count} articles supprimés.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "../templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "../static")
)

@app.route("/collect_all")
def collect_all():
    try:
        subs = get_subscriptions()
        total = 0

        for sub in subs:
            articles_list = fetch_articles(sub["url"])
            inserted = insert_articles(articles_list, source=sub["name"])
            total += inserted
            update_subscription_fetch(str(sub["_id"]))

        return {"articles_ajoutes": total, "success": True}
    except Exception as e:
        logger.error(f"Erreur collecte articles: {e}")
        return {"error": str(e), "success": False}, 500

@app.route("/delete_subscription/<id>")
def delete_sub(id):
    delete_subscription(id)
    return redirect("/admin")

@app.route("/add_subscription", methods=["POST"])
def add_sub():
    name = request.form.get("name")
    url = request.form.get("url")

    add_subscription(name, url)
    return redirect("/admin")

@app.route("/admin")
def admin():
    subs = get_subscriptions()
    return render_template("admin.html", subs=subs)

@app.route("/historique")
def historique():
    data = get_consultations()
    return render_template("historique.html", data=data)

@app.route("/favoris")
def favoris():
    favorites = get_favorites()
    return render_template("favoris.html", favorites=favorites)

@app.route("/add_favorite", defaults={"id": None}, methods=["POST"])
@app.route("/add_favorite/<id>", methods=["POST"])
def add_favorite_route(id=None):
    article_id = request.form.get("article_id") or id

    try:
        if article_id:
            article_obj = ObjectId(article_id)
            add_favorite(article_obj)
    except Exception as e:
        logger.error(f"Erreur ajout favoris: {e}")

    return redirect(request.referrer or "/")

@app.route("/click/<id>")
def click(id):
    try:
        article = articles.find_one({"_id": ObjectId(id)})

        if article:
            add_consultation(article["_id"])
            return redirect(article["url"])

        return "Article introuvable", 404
    except Exception as e:
        logger.error(f"Erreur lors du clic: {e}")
        return "Erreur", 500

@app.route("/wordcloud")
def wordcloud():
    try:
        num_words = request.args.get("num_words", 80, type=int)
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        source = request.args.get("source")
        
        articles_list = search_articles(start_date=start_date, end_date=end_date, source=source)
        
        if not articles_list:
            articles_list = get_articles(200)
        
        image_file = generate_wordcloud(articles_list, num_words=num_words)
        sources = get_sources()
        
        return render_template("wordcloud.html", image=image_file, sources=sources, num_words=num_words)
    except Exception as e:
        logger.error(f"Erreur génération wordcloud: {e}")
        return render_template("wordcloud.html", error="Erreur lors de la génération du nuage de mots")

@app.route("/collect")
def collect():
    url = "https://www.lemonde.fr/sitemap_news.xml"

    articles = fetch_articles(url)
    nb_inserted = insert_articles(articles, source="Le Monde")
    return {
        "total_recuperes": len(articles),
        "nouveaux_articles": nb_inserted
    }

@app.route("/test")
def test():
    url = "https://www.lemonde.fr/sitemap_news.xml"
    articles = fetch_articles(url)

    return {
        "nombre": len(articles),
        "articles": articles[:5]
    }

@app.route("/", methods=["GET"])
def index():
    keyword = request.args.get("keyword", "").strip()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    source = request.args.get("source")
    
    articles_found = search_articles(keyword=keyword if keyword else None, 
                                      start_date=start_date, 
                                      end_date=end_date,
                                      source=source)
    
    # Organiser par source
    articles_by_source = {}
    for article in articles_found:
        src = article.get("source", "Le Monde")
        if src not in articles_by_source:
            articles_by_source[src] = []
        articles_by_source[src].append(article)
    
    sources = get_sources()
    
    return render_template("index.html", articles_by_source=articles_by_source, 
                         sources=sources, keyword=keyword, 
                         start_date=start_date, end_date=end_date, source=source)

if __name__ == "__main__":
    app.run(debug=True, threaded=True, use_reloader=False)