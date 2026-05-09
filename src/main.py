from flask import Flask, render_template, request, redirect

import os
from scraper import fetch_articles
from dbMongo import insert_articles, add_consultation, add_subscription, get_subscriptions, delete_subscription, get_articles, search_articles
from wordcloud_generator import generate_wordcloud
from bson.objectid import ObjectId

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "../templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "../static")
)

@app.route("/collect_all")
def collect_all():
    subs = get_subscriptions()
    total = 0

    for sub in subs:
        articles = fetch_articles(sub["url"])
        total += insert_articles(articles)

    return {"articles_ajoutes": total}

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

@app.route("/click/<id>")
def click(id):
    article = articles.find_one({"_id": ObjectId(id)})

    if article:
        add_consultation(article["_id"])
        return redirect(article["url"])

    return "Article introuvable"

@app.route("/wordcloud")
def wordcloud():
    articles = get_articles(200)
    image_file = generate_wordcloud(articles)

    return render_template("wordcloud.html", image=image_file)

@app.route("/collect")
def collect():
    url = "https://www.lemonde.fr/sitemap_news.xml"

    articles = fetch_articles(url)
    nb_inserted = insert_articles(articles)

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
    keyword = request.args.get("keyword")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    articles = search_articles(keyword, start_date, end_date)

    return render_template("index.html", articles=articles)

if __name__ == "__main__":
    app.run(debug=True, threaded=True, use_reloader=False)