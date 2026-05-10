# Configuration du projet Nuage d'Actualité

# Initiales de l'équipe 
# Format: 4 initiales majuscules (ex: "DFSB" pour Dupont, Fuss, Schaeffer, Briot)
TEAM_INITIALS = "CSAE"

# Configuration MongoDB
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "SD2026_projet"

# Configuration Flask
FLASK_DEBUG = True
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000

# Configuration scraper
DEFAULT_SITEMAP = "https://www.lemonde.fr/sitemap_news.xml"
REQUEST_TIMEOUT = 10

# Configuration wordcloud
DEFAULT_NUM_WORDS = 80
MIN_NUM_WORDS = 10
MAX_NUM_WORDS = 200

# Stopwords français
FRENCH_STOPWORDS = {
    "le", "la", "les", "de", "des", "du",
    "un", "une", "et", "en", "à", "au",
    "pour", "avec", "sur", "dans",
    "france", "monde", "article", "articles",
    "que", "qui", "ce", "ces", "cet", "cette",
    "dans", "entre", "vers", "par", "pas",
    "plus", "moins", "bien", "très", "dont",
    "soit", "aussi", "comme", "covid", "guerre",
    "vous", "nous", "me", "te", "se", "lui",
    "lui", "elle", "elles", "ils", "eux"
}
