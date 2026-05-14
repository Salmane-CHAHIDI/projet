from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["SD2026_projet"]

TEAM_INITIALS = "CSAE"

articles = db[f"G_{TEAM_INITIALS}_articles"]
abonnements = db[f"G_{TEAM_INITIALS}_abonnements"]
consultations = db[f"G_{TEAM_INITIALS}_consultations"]
favoris = db[f"G_{TEAM_INITIALS}_favoris"]
categories_col = db[f"G_{TEAM_INITIALS}_categories"]

# Index pour les requêtes
articles.create_index("url", unique=True)
articles.create_index("date_publication")
articles.create_index("title")
articles.create_index("source")
abonnements.create_index("created_at")
consultations.create_index("date_consultation")
consultations.create_index("article_id")
favoris.create_index("article_id", unique=True)
favoris.create_index("date_ajout")
favoris.create_index("catalogue")
categories_col.create_index("name", unique=True)

DEFAULT_CATEGORIES = [
    "Sport", "Politique", "Economie", "Technologie",
    "Culture", "Santé", "Environnement", "International", "Général"
]


def seed_default_categories():
    for cat in DEFAULT_CATEGORIES:
        try:
            categories_col.insert_one({"name": cat, "created_at": datetime.now(), "is_default": True})
        except Exception:
            pass


seed_default_categories()


def add_subscription(name, url):
    result = abonnements.insert_one({
        "name": name,
        "url": url,
        "created_at": datetime.now(),
        "last_fetch": None,
        "active": True
    })
    return str(result.inserted_id)


def get_subscriptions():
    return list(abonnements.find())


def delete_subscription(id):
    abonnements.delete_one({"_id": ObjectId(id)})


def get_consultations():
    pipeline = [
        {
            "$lookup": {
                "from": f"G_{TEAM_INITIALS}_articles",
                "localField": "article_id",
                "foreignField": "_id",
                "as": "article"
            }
        },
        {"$unwind": "$article"},
        {"$sort": {"date_consultation": -1}}
    ]
    return list(consultations.aggregate(pipeline))


def search_consultations(keyword=None, start_date=None, end_date=None):
    pipeline = [
        {
            "$lookup": {
                "from": f"G_{TEAM_INITIALS}_articles",
                "localField": "article_id",
                "foreignField": "_id",
                "as": "article"
            }
        },
        {"$unwind": "$article"},
    ]

    match = {}
    if keyword:
        match["article.title"] = {"$regex": keyword, "$options": "i"}
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            match.setdefault("date_consultation", {})["$gte"] = start
        except Exception:
            pass
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            match.setdefault("date_consultation", {})["$lte"] = end
        except Exception:
            pass

    if match:
        pipeline.append({"$match": match})

    pipeline.append({"$sort": {"date_consultation": -1}})
    return list(consultations.aggregate(pipeline))


def add_consultation(article_id):
    consultations.insert_one({
        "article_id": article_id,
        "date_consultation": datetime.now()
    })


def add_favorite(article_id, categorie=None):
    try:
        favoris.insert_one({
            "article_id": article_id,
            "date_ajout": datetime.now(),
            "catalogue": categorie or "Général"
        })
        return True
    except Exception:
        if categorie:
            try:
                favoris.update_one(
                    {"article_id": article_id},
                    {"$set": {"catalogue": categorie}}
                )
            except Exception:
                pass
        return False


def get_favorites():
    pipeline = [
        {
            "$lookup": {
                "from": f"G_{TEAM_INITIALS}_articles",
                "localField": "article_id",
                "foreignField": "_id",
                "as": "article"
            }
        },
        {"$unwind": "$article"},
        {"$sort": {"date_ajout": -1}}
    ]
    return list(favoris.aggregate(pipeline))


def get_categories():
    return sorted([c["name"] for c in categories_col.find({}, {"name": 1})])


def add_category(name):
    try:
        categories_col.insert_one({
            "name": name.strip(),
            "created_at": datetime.now(),
            "is_default": False
        })
        return True
    except Exception:
        return False


def update_category(old_name, new_name):
    new_name = new_name.strip()
    if not new_name:
        return False
    categories_col.update_one({"name": old_name}, {"$set": {"name": new_name}})
    favoris.update_many({"catalogue": old_name}, {"$set": {"catalogue": new_name}})
    return True


def delete_category(name):
    if name == "Général":
        return False
    categories_col.delete_one({"name": name})
    favoris.delete_many({"catalogue": name})
    return True


def search_articles(keyword=None, start_date=None, end_date=None, source=None):
    query = {}

    if keyword:
        query["title"] = {"$regex": keyword, "$options": "i"}

    if start_date:
        try:
            start = datetime.fromisoformat(start_date.replace("Z", ""))
            query.setdefault("date_publication", {})["$gte"] = start
        except Exception:
            pass

    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace("Z", ""))
            query.setdefault("date_publication", {})["$lte"] = end
        except Exception:
            pass

    if source:
        query["source"] = source

    return list(articles.find(query).sort("date_publication", -1))


def get_articles(limit=50):
    return list(articles.find().sort("date_publication", -1).limit(limit))


def insert_articles(article_list, source="Le Monde"):
    inserted = 0
    for art in article_list:
        try:
            pub_date = None
            if art.get("date"):
                try:
                    pub_date = datetime.fromisoformat(art["date"].replace("Z", ""))
                except Exception:
                    pub_date = datetime.now()
            else:
                pub_date = datetime.now()

            articles.insert_one({
                "title": art["title"],
                "url": art["url"],
                "date_publication": pub_date,
                "source": source,
                "inserted_at": datetime.now(),
                "image": art.get("image")
            })
            inserted += 1
        except Exception:
            continue

    return inserted


def get_sources():
    return articles.distinct("source")


def update_subscription_fetch(sub_id):
    try:
        abonnements.update_one(
            {"_id": ObjectId(sub_id)},
            {"$set": {"last_fetch": datetime.now()}}
        )
    except Exception:
        pass


def get_articles_by_source(source, limit=50):
    return list(articles.find({"source": source}).sort("date_publication", -1).limit(limit))
