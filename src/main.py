from flask import Flask, render_template, request, redirect
import os
import logging
from scraper import fetch_articles
from dbMongo import (
    insert_articles, add_consultation, add_subscription, get_subscriptions,
    delete_subscription, get_articles, search_articles, get_consultations,
    search_consultations, articles, get_sources, update_subscription_fetch,
    add_favorite, get_favorites, get_categories, add_category,
    update_category, delete_category
)
from wordcloud_generator import generate_wordcloud
from bson.objectid import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "../templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "../static")
)

AUTO_CATEGORIE_LABEL = "Automatique"

CATEGORIE_KEYWORDS = {
    "Sport": ["sport", "football", "rugby", "tennis", "basket", "olymp", "match", "coupe", "victoire", "compétition"],
    "Politique": ["politique", "gouvernement", "parlement", "élection", "ministre", "loi", "sénat", "président", "vote"],
    "Economie": ["économie", "finance", "marché", "entreprise", "banque", "croissance", "conjoncture", "inflation", "commerce"],
    "Technologie": ["tech", "technologie", "numérique", "ia", "intelligence", "robot", "données", "cyber", "startup"],
    "Culture": ["culture", "cinéma", "musique", "festival", "art", "livre", "théâtre", "exposition"],
    "Santé": ["santé", "médical", "hôpital", "vaccin", "bien-être", "psychologie", "médecine"],
    "Environnement": ["climat", "écologie", "environnement", "biodiversité", "pollution", "renouvelable", "écologique"],
    "International": ["international", "étranger", "monde", "diplomatie", "conflit", "guerre", "onu"]
}


def infer_categorie(article):
    if not article:
        return "Général"
    title = (article.get("title") or "").lower()
    source = (article.get("source") or "").lower()
    for label, keywords in CATEGORIE_KEYWORDS.items():
        for kw in keywords:
            if kw in title or kw in source:
                return label
    return "Général"


def group_favorites_by_categorie(favorites):
    grouped = {}
    for fav in favorites:
        cat = fav.get("catalogue") or infer_categorie(fav.get("article"))
        grouped.setdefault(cat, []).append(fav)
    return grouped


def migrate_missing_favorite_categories():
    from dbMongo import favoris as favoris_col
    favorites = get_favorites()
    for fav in favorites:
        if not fav.get("catalogue"):
            cat = infer_categorie(fav.get("article")) or "Général"
            try:
                favoris_col.update_one({"_id": fav["_id"]}, {"$set": {"catalogue": cat}})
            except Exception as e:
                logger.warning(f"Migration catégorie favori {fav['_id']}: {e}")


migrate_missing_favorite_categories()


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
    keyword = request.args.get("keyword", "").strip()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if keyword or start_date or end_date:
        data = search_consultations(
            keyword=keyword if keyword else None,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None
        )
    else:
        data = get_consultations()

    return render_template(
        "historique.html",
        data=data,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date
    )


@app.route("/favoris")
def favoris_page():
    selected_categorie = request.args.get("categorie")
    favorites = get_favorites()
    favorites_by_categorie = group_favorites_by_categorie(favorites)
    all_categories = get_categories()

    if selected_categorie:
        favorites_by_categorie = {
            selected_categorie: favorites_by_categorie.get(selected_categorie, [])
        }

    return render_template(
        "favoris.html",
        favorites=favorites,
        favorites_by_categorie=favorites_by_categorie,
        categories=all_categories,
        selected_categorie=selected_categorie
    )


@app.route("/categories/add", methods=["POST"])
def add_categorie_route():
    name = request.form.get("name", "").strip()
    if name:
        add_category(name)
    return redirect("/favoris")


@app.route("/categories/update", methods=["POST"])
def update_categorie_route():
    old_name = request.form.get("old_name", "").strip()
    new_name = request.form.get("new_name", "").strip()
    if old_name and new_name and old_name != new_name:
        update_category(old_name, new_name)
    return redirect("/favoris")


@app.route("/categories/delete", methods=["POST"])
def delete_categorie_route():
    name = request.form.get("name", "").strip()
    if name and name != "Général":
        delete_category(name)
    return redirect("/favoris")


@app.route("/add_favorite", defaults={"id": None}, methods=["POST"])
@app.route("/add_favorite/<id>", methods=["POST"])
def add_favorite_route(id=None):
    article_id = request.form.get("article_id") or id
    # Accepter les deux noms de champ (ancien et nouveau)
    categorie = request.form.get("categorie") or request.form.get("catalogue")

    try:
        if article_id:
            article_obj = ObjectId(article_id)
            article = articles.find_one({"_id": article_obj})

            if not categorie or categorie == AUTO_CATEGORIE_LABEL:
                categorie = infer_categorie(article)
            else:
                categorie = categorie.strip() or infer_categorie(article)

            if not categorie:
                categorie = "Général"

            add_favorite(article_obj, categorie=categorie)
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


@app.route("/", methods=["GET"])
def index():
    keyword = request.args.get("keyword", "").strip()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    source = request.args.get("source")

    articles_found = search_articles(
        keyword=keyword if keyword else None,
        start_date=start_date,
        end_date=end_date,
        source=source
    )

    articles_by_source = {}
    for article in articles_found:
        src = article.get("source", "Inconnu")
        articles_by_source.setdefault(src, []).append(article)

    sources = get_sources()
    categories = get_categories()

    return render_template(
        "index.html",
        articles_by_source=articles_by_source,
        sources=sources,
        categories=categories,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date,
        source=source
    )


if __name__ == "__main__":
    app.run(debug=True, threaded=True, use_reloader=False)
