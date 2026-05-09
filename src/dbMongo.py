from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["SD2026_projet"]

articles = db["G_articles"]
abonnements = db["G_abonnements"]
consultations = db["G_consultations"]

# index unique pour éviter doublons
articles.create_index("url", unique=True)

def add_subscription(name, url):
    abonnements.insert_one({
        "name": name,
        "url": url
    })

def get_subscriptions():
    return list(abonnements.find())

def delete_subscription(id):
    from bson.objectid import ObjectId
    abonnements.delete_one({"_id": ObjectId(id)})

def get_consultations():
    return list(consultations.find().sort("date_consultation", -1))

def add_consultation(article_id):
    consultations.insert_one({
        "article_id": article_id,
        "date_consultation": datetime.now()
    })

def search_articles(keyword=None, start_date=None, end_date=None):
    query = {}

    if keyword:
        query["title"] = {"$regex": keyword, "$options": "i"}  # insensible à la casse

    if start_date and end_date:
        query["date_publication"] = {
            "$gte": start_date,
            "$lte": end_date
        }

    return list(articles.find(query).sort("date_publication", -1))

def get_articles(limit=50):
    return list(articles.find().sort("date_publication", -1).limit(limit))

def insert_articles(article_list):
    inserted = 0

    for art in article_list:
        try:
            articles.insert_one({
                "title": art["title"],
                "url": art["url"],
                "date_publication": datetime.fromisoformat(art["date"].replace("Z", "")),
                "source": "LeMonde",
            })
            inserted += 1
        except:
            # doublon → ignoré
            continue

    return inserted