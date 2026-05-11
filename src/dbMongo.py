from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["SD2026_projet"]

# Configuration avec initiales de l'équipe 
TEAM_INITIALS = "CSAE"  

articles = db[f"G_{TEAM_INITIALS}_articles"]
abonnements = db[f"G_{TEAM_INITIALS}_abonnements"]
consultations = db[f"G_{TEAM_INITIALS}_consultations"]
favoris = db[f"G_{TEAM_INITIALS}_favoris"]

# Indexes pour optimisation des requêtes
articles.create_index("url", unique=True)
articles.create_index("date_publication")
articles.create_index("title")
articles.create_index("source")
abonnements.create_index("created_at")
consultations.create_index("date_consultation")
consultations.create_index("article_id")
favoris.create_index("article_id", unique=True)
favoris.create_index("date_ajout")

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
    from bson.objectid import ObjectId
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
        {
            "$unwind": "$article"
        },
        {
            "$sort": {"date_consultation": -1}
        }
    ]
    return list(consultations.aggregate(pipeline))

def add_consultation(article_id):
    consultations.insert_one({
        "article_id": article_id,
        "date_consultation": datetime.now()
    })

def add_favorite(article_id):
    try:
        favoris.insert_one({
            "article_id": article_id,
            "date_ajout": datetime.now()
        })
        return True
    except Exception:
        # Already in favorites
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
        {
            "$unwind": "$article"
        },
        {
            "$sort": {"date_ajout": -1}
        }
    ]
    return list(favoris.aggregate(pipeline))

def search_articles(keyword=None, start_date=None, end_date=None, source=None):
    query = {}

    if keyword:
        query["title"] = {"$regex": keyword, "$options": "i"}  # insensible à la casse

    if start_date:
        try:
            from datetime import datetime as dt
            start = dt.fromisoformat(start_date.replace("Z", ""))
            if not query.get("date_publication"):
                query["date_publication"] = {}
            query["date_publication"]["$gte"] = start
        except:
            pass

    if end_date:
        try:
            from datetime import datetime as dt
            end = dt.fromisoformat(end_date.replace("Z", ""))
            if not query.get("date_publication"):
                query["date_publication"] = {}
            query["date_publication"]["$lte"] = end
        except:
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
                except:
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
        except Exception as e:
            # doublon → ignoré
            continue

    return inserted

def get_sources():
    """Récupère la liste des sources d'articles"""
    return articles.distinct("source")

def update_subscription_fetch(sub_id):
    """Met à jour la date de dernière récupération"""
    try:
        abonnements.update_one(
            {"_id": ObjectId(sub_id)},
            {"$set": {"last_fetch": datetime.now()}}
        )
    except:
        pass

def get_articles_by_source(source, limit=50):
    """Récupère les articles d'une source spécifique"""
    return list(articles.find({"source": source}).sort("date_publication", -1).limit(limit))