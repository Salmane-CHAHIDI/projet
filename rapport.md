# Rapport de Projet — Nuage d'Actualité

**Université de Lorraine**  
**Master 1 — Structuration de Données**  
**Année universitaire 2025-2026**

---

**Équipe :** CSAE  
**Application :** Nuage d'Actualité  
**Technologies :** Python · Flask · MongoDB · Bootstrap 5  
**Accès local :** http://127.0.0.1:5000

---

## Table des Matières

1. [Présentation du Projet](#1-présentation-du-projet)  
2. [Architecture Technique](#2-architecture-technique)  
3. [Base de Données MongoDB](#3-base-de-données-mongodb)  
4. [Description du Code Source](#4-description-du-code-source)  
   - 4.1 [main.py — Contrôleur Flask](#41-mainpy--contrôleur-flask)  
   - 4.2 [dbMongo.py — Couche de Données](#42-dbmongopy--couche-de-données)  
   - 4.3 [scraper.py — Collecte des Articles](#43-scraperpy--collecte-des-articles)  
   - 4.4 [wordcloud_generator.py — Visualisation](#44-wordcloud_generatorpy--visualisation)  
5. [Guide d'Utilisation de l'Application](#5-guide-dutilisation-de-lapplication)  
6. [Fonctionnalités Implémentées](#6-fonctionnalités-implémentées)  
7. [Robustesse et Sécurité](#7-robustesse-et-sécurité)  
8. [Conclusion](#8-conclusion)  
9. [Annexes](#9-annexes)

---

## 1. Présentation du Projet

### 1.1 Contexte

Ce projet s'inscrit dans le cadre du cours de **Structuration de Données** du Master 1 à l'Université de Lorraine. L'objectif est de concevoir et développer une application web complète permettant de **collecter, stocker, analyser et visualiser** des articles d'actualité provenant de sources journalistiques françaises.

### 1.2 Objectifs

Le projet répond à plusieurs exigences fondamentales :

| Objectif | Description |
|---|---|
| **Collecte automatisée** | Récupérer des articles depuis des sitemaps XML de presse française |
| **Stockage structuré** | Persister les données dans MongoDB avec indexation optimisée |
| **Recherche et filtrage** | Permettre la navigation par mot-clé, date et source |
| **Visualisation** | Générer des nuages de mots SVG interactifs et cliquables |
| **Suivi des consultations** | Enregistrer l'historique de lecture de chaque utilisateur |
| **Gestion des favoris** | Sauvegarder des articles par catégories personnalisables |

### 1.3 Périmètre Fonctionnel

L'application couvre les cinq modules suivants :

- **Administration** : Gestion des sources d'actualités (abonnements aux sitemaps)
- **Consultation** : Affichage, recherche et lecture des articles
- **Nuage de mots** : Analyse textuelle et visualisation des tendances
- **Historique** : Traçabilité des articles consultés
- **Favoris** : Organisation personnelle des articles par catégories

---

## 2. Architecture Technique

### 2.1 Stack Technologique

| Couche | Technologie | Version | Rôle |
|---|---|---|---|
| **Backend** | Python Flask | 3.1.3 | Serveur web, routage, logique métier |
| **Base de données** | MongoDB + PyMongo | 8.3.1 / 4.17.0 | Stockage NoSQL des articles |
| **Parsing XML** | lxml | 6.1.0 | Analyse des sitemaps de presse |
| **HTTP Client** | requests | 2.33.1 | Téléchargement des sitemaps |
| **Visualisation** | wordcloud + matplotlib | 1.9.6 / 3.10.9 | Génération de nuages SVG |
| **Frontend** | Bootstrap 5 + Jinja2 | 5.3.0 | Interface responsive, templates |
| **Icônes** | Font Awesome | 6.4.0 | Icônes de l'interface |

### 2.2 Architecture MVC

L'application suit le patron **Modèle-Vue-Contrôleur** adapté à Flask :

```
┌────────────────────┐      ┌────────────────────┐      ┌────────────────────┐
│       VUE          │      │    CONTRÔLEUR       │      │      MODÈLE        │
│  templates/*.html  │◄────►│    src/main.py      │◄────►│  src/dbMongo.py    │
│  Bootstrap 5       │      │  Routes Flask       │      │  MongoDB           │
│  Jinja2            │      │  Logique métier     │      │  5 collections     │
└────────────────────┘      └────────────────────┘      └────────────────────┘
                                      │
                            ┌─────────┴──────────┐
                            │      SERVICES       │
                            │  scraper.py         │
                            │  wordcloud_gen.py   │
                            └────────────────────┘
```

### 2.3 Structure des Fichiers

```
projet/
├── config.py                   # Configuration centralisée
├── requirements.txt            # Dépendances pip
├── test_app.py                 # Suite de tests (6/6)
├── run.bat / run.sh            # Launchers Windows / Linux
│
├── src/
│   ├── main.py                 # Application Flask (routes)
│   ├── dbMongo.py              # Interface MongoDB (CRUD)
│   ├── scraper.py              # Collecte XML des sitemaps
│   └── wordcloud_generator.py  # Génération SVG
│
├── templates/
│   ├── base.html               # Template de base (navbar, footer)
│   ├── index.html              # Page d'accueil
│   ├── admin.html              # Administration
│   ├── wordcloud.html          # Nuage de mots
│   ├── historique.html         # Historique des consultations
│   └── favoris.html            # Gestion des favoris
│
└── static/
    ├── style.css               # Styles personnalisés
    └── wordcloud_*.svg         # Nuages générés (horodatés)
```

---

## 3. Base de Données MongoDB

### 3.1 Choix de MongoDB

MongoDB a été retenu pour plusieurs raisons techniques adaptées à ce projet :

- **Schéma flexible** : Les articles de presse n'ont pas toujours les mêmes métadonnées selon les sources (certains ont une image, d'autres non, formats de date variables).
- **Performance en lecture** : L'indexation MongoDB est particulièrement efficace pour les recherches textuelles et les tris chronologiques.
- **Aggregation Pipeline** : Les jointures entre collections (favoris ↔ articles, consultations ↔ articles) sont réalisées via des pipelines d'agrégation, plus expressifs qu'un simple JOIN SQL.
- **Documents BSON** : Le format natif correspond naturellement aux données JSON récupérées depuis les sitemaps XML.

### 3.2 Nommage des Collections

Les collections suivent la convention `G_{TEAM_INITIALS}_{nom}` définie par le sujet, avec `TEAM_INITIALS = "CSAE"` :

| Collection | Nom réel |
|---|---|
| Articles | `G_CSAE_articles` |
| Abonnements | `G_CSAE_abonnements` |
| Consultations | `G_CSAE_consultations` |
| Favoris | `G_CSAE_favoris` |
| Catégories | `G_CSAE_categories` |

### 3.3 Schémas des Collections

#### Collection `G_CSAE_articles`
```json
{
  "_id":              ObjectId,
  "title":            String,       // Titre de l'article (requis)
  "url":              String,       // URL (requis, UNIQUE)
  "date_publication": Date,         // Date de parution
  "source":           String,       // Nom de la source (ex: "Le Monde")
  "inserted_at":      Date,         // Date d'insertion en base
  "image":            String        // URL de l'image (optionnel)
}
```
**Indexes :** `url` (unique), `date_publication`, `title`, `source`

#### Collection `G_CSAE_abonnements`
```json
{
  "_id":        ObjectId,
  "name":       String,   // Nom de la source (ex: "Le Monde")
  "url":        String,   // URL du sitemap XML
  "created_at": Date,     // Date d'ajout
  "last_fetch": Date,     // Dernière collecte (null si jamais)
  "active":     Boolean   // Statut actif/inactif
}
```
**Index :** `created_at`

#### Collection `G_CSAE_consultations`
```json
{
  "_id":               ObjectId,
  "article_id":        ObjectId,  // Référence vers G_CSAE_articles
  "date_consultation": Date       // Horodatage automatique
}
```
**Indexes :** `date_consultation`, `article_id`

#### Collection `G_CSAE_favoris`
```json
{
  "_id":        ObjectId,
  "article_id": ObjectId,  // Référence vers G_CSAE_articles (unique)
  "catalogue":  String,    // Catégorie assignée
  "date_ajout": Date       // Horodatage de l'ajout
}
```
**Indexes :** `article_id` (unique), `date_ajout`, `catalogue`

#### Collection `G_CSAE_categories`
```json
{
  "_id":        ObjectId,
  "name":       String,   // Nom de la catégorie (unique)
  "created_at": Date,
  "is_default": Boolean   // true pour les 9 catégories prédéfinies
}
```
**Index :** `name` (unique)

### 3.4 Catégories Prédéfinies

Au démarrage, neuf catégories sont automatiquement initialisées si elles n'existent pas :
`Sport`, `Politique`, `Economie`, `Technologie`, `Culture`, `Santé`, `Environnement`, `International`, `Général`

### 3.5 Indexation et Performances

Les index ont été conçus pour optimiser les opérations les plus fréquentes :

- **Dédoublonnage** : L'index unique sur `articles.url` empêche l'insertion de doublons et est utilisé implicitement à chaque import de sitemap.
- **Recherche textuelle** : L'index sur `articles.title` accélère les requêtes regex (`$regex`) utilisées dans la barre de recherche.
- **Filtrage temporel** : L'index sur `articles.date_publication` optimise les filtres par plage de dates.
- **Jointures d'agrégation** : L'index sur `consultations.article_id` et `favoris.article_id` accélère les `$lookup` entre collections.

---

## 4. Description du Code Source

### 4.1 `main.py` — Contrôleur Flask

Ce fichier constitue le **point d'entrée** de l'application. Il définit toutes les routes HTTP et coordonne les services.

#### Initialisation

```python
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "../templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "../static")
)
```

Flask est instancié avec des chemins relatifs au dossier `src/`, ce qui permet de lancer l'application depuis n'importe quel répertoire.

#### Catégorisation Automatique des Articles

Un mécanisme d'inférence de catégorie est implémenté pour classer automatiquement les favoris sans intervention utilisateur :

```python
CATEGORIE_KEYWORDS = {
    "Sport":         ["sport", "football", "rugby", "tennis", ...],
    "Politique":     ["politique", "gouvernement", "parlement", ...],
    "Economie":      ["économie", "finance", "marché", ...],
    "Technologie":   ["tech", "technologie", "numérique", "ia", ...],
    ...
}

def infer_categorie(article):
    title = (article.get("title") or "").lower()
    source = (article.get("source") or "").lower()
    for label, keywords in CATEGORIE_KEYWORDS.items():
        for kw in keywords:
            if kw in title or kw in source:
                return label
    return "Général"
```

Cette fonction analyse le titre et la source de l'article. Dès qu'un mot-clé correspond, la catégorie associée est retournée. Si aucun mot-clé ne correspond, la catégorie par défaut `"Général"` est utilisée.

#### Endpoints Principaux

| Route | Méthode | Fonction |
|---|---|---|
| `/` | GET | Accueil : affichage et recherche des articles |
| `/admin` | GET | Page d'administration des abonnements |
| `/add_subscription` | POST | Ajout d'un abonnement sitemap |
| `/delete_subscription/<id>` | GET | Suppression d'un abonnement |
| `/collect_all` | GET | Collecte de tous les articles (JSON) |
| `/click/<id>` | GET | Redirection + enregistrement consultation |
| `/wordcloud` | GET | Génération et affichage du nuage de mots |
| `/historique` | GET | Historique des consultations |
| `/favoris` | GET | Page des favoris par catégorie |
| `/add_favorite[/<id>]` | POST | Ajout d'un article en favori |
| `/categories/add` | POST | Création d'une nouvelle catégorie |
| `/categories/update` | POST | Renommage d'une catégorie |
| `/categories/delete` | POST | **Suppression catégorie + suppression des favoris associés** |

#### Gestion des Favoris et Catégories

Lors de l'ajout d'un favori, la catégorie est déterminée dans cet ordre de priorité :
1. Catégorie choisie explicitement par l'utilisateur (formulaire)
2. Catégorie inférée automatiquement par `infer_categorie()`
3. Catégorie `"Général"` en dernier recours

#### Suppression de Catégorie (Modification Finale)

Lors de la suppression d'une catégorie, **tous les articles favoris appartenant à cette catégorie sont supprimés définitivement** de la collection `favoris`. Ce comportement est géré dans `dbMongo.py` et reflété dans l'interface par un avertissement explicite en rouge.

#### Collecte des Articles

```python
@app.route("/collect_all")
def collect_all():
    subs = get_subscriptions()
    total = 0
    for sub in subs:
        articles_list = fetch_articles(sub["url"])
        inserted = insert_articles(articles_list, source=sub["name"])
        total += inserted
        update_subscription_fetch(str(sub["_id"]))
    return {"articles_ajoutes": total, "success": True}
```

Cette route parcourt tous les abonnements, appelle le scraper pour chaque sitemap, insère les articles en base (les doublons sont silencieusement ignorés grâce à l'index unique), et met à jour le timestamp `last_fetch`.

---

### 4.2 `dbMongo.py` — Couche de Données

Ce module centralise **toutes les interactions avec MongoDB**. Il respecte le principe de séparation des responsabilités : `main.py` ne connaît pas la syntaxe MongoDB, il appelle uniquement des fonctions de haut niveau.

#### Connexion et Collections

```python
client = MongoClient("mongodb://localhost:27017/")
db = client["SD2026_projet"]

TEAM_INITIALS = "CSAE"

articles        = db[f"G_{TEAM_INITIALS}_articles"]
abonnements     = db[f"G_{TEAM_INITIALS}_abonnements"]
consultations   = db[f"G_{TEAM_INITIALS}_consultations"]
favoris         = db[f"G_{TEAM_INITIALS}_favoris"]
categories_col  = db[f"G_{TEAM_INITIALS}_categories"]
```

Les noms de collections sont construits dynamiquement à partir de `TEAM_INITIALS`, ce qui permet au projet d'être réutilisé par différentes équipes dans la même base de données sans collision.

#### Insertion des Articles avec Dédoublonnage

```python
def insert_articles(article_list, source="Le Monde"):
    inserted = 0
    for art in article_list:
        try:
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
            continue  # DuplicateKeyError ignorée silencieusement
    return inserted
```

L'index unique sur `url` provoque une `DuplicateKeyError` pour tout article déjà présent. L'exception est capturée et ignorée (`continue`), garantissant l'idempotence des collectes successives.

#### Recherche Multi-Critères

```python
def search_articles(keyword=None, start_date=None, end_date=None, source=None):
    query = {}
    if keyword:
        query["title"] = {"$regex": keyword, "$options": "i"}
    if start_date:
        start = datetime.fromisoformat(start_date.replace("Z", ""))
        query.setdefault("date_publication", {})["$gte"] = start
    if end_date:
        end = datetime.fromisoformat(end_date.replace("Z", ""))
        query.setdefault("date_publication", {})["$lte"] = end
    if source:
        query["source"] = source
    return list(articles.find(query).sort("date_publication", -1))
```

La construction dynamique du filtre `query` permet de combiner n'importe quel sous-ensemble de critères. Le flag `$options: "i"` rend la recherche insensible à la casse. Les dates sont parsées au format ISO 8601.

#### Agrégation pour Jointures

Pour récupérer les consultations avec les détails des articles associés :

```python
def get_consultations():
    pipeline = [
        {"$lookup": {
            "from": f"G_{TEAM_INITIALS}_articles",
            "localField": "article_id",
            "foreignField": "_id",
            "as": "article"
        }},
        {"$unwind": "$article"},
        {"$sort": {"date_consultation": -1}}
    ]
    return list(consultations.aggregate(pipeline))
```

Le `$lookup` réalise une jointure entre `consultations` et `articles` via `article_id`. `$unwind` déroule le tableau résultant en documents individuels. Cette même structure est utilisée pour les favoris.

#### Suppression de Catégorie — Comportement Défini

```python
def delete_category(name):
    if name == "Général":
        return False                          # Protection : Général ne peut pas être supprimé
    categories_col.delete_one({"name": name})
    favoris.delete_many({"catalogue": name})  # Suppression en cascade des favoris associés
    return True
```

**Comportement implémenté :** lorsqu'une catégorie est supprimée, tous les documents de la collection `favoris` ayant `catalogue == name` sont **définitivement supprimés** (`delete_many`). La catégorie `"Général"` est protégée contre la suppression.

---

### 4.3 `scraper.py` — Collecte des Articles

Ce module est responsable de la **récupération des articles** depuis les sitemaps XML des sources de presse.

#### Compatibilité Multi-Sources

Le scraper est conçu pour fonctionner avec les formats XML utilisés par les grands médias français :

- **Le Monde** — `sitemap_news.xml`
- **Le Figaro** — sitemap avec `image:image`
- **Les Échos** — sitemap avec `image:image`
- **France 24** — sitemap standard
- **France Info** — sitemap avec `news:news`
- **20 Minutes** — sitemap standard

#### Algorithme de Parsing

```python
def fetch_articles(sitemap_url):
    response = requests.get(sitemap_url, timeout=10,
                            headers={"User-Agent": "Mozilla/5.0"})
    root = etree.fromstring(response.content)
    urls = root.xpath("//*[local-name()='url']")

    for url in urls:
        # Titre : priorité à news:title, fallback sur title générique
        title = url.xpath(".//*[local-name()='news']/*[local-name()='title']/text()")
        if not title:
            title = url.xpath(".//*[local-name()='title']/text()")

        # URL : uniquement le <loc> direct (évite image:loc)
        link = url.xpath("./*[local-name()='loc']/text()")

        # Date : priorité à news:publication_date, fallback sur lastmod
        date = url.xpath(".//*[local-name()='news']/*[local-name()='publication_date']/text()")
        if not date:
            date = url.xpath("./*[local-name()='lastmod']/text()")

        # Image : premier image:loc direct sous image:image
        image_candidates = url.xpath("./*[local-name()='image']/*[local-name()='loc']/text()")
```

L'utilisation de `local-name()` dans les XPath permet d'ignorer les espaces de noms XML (`news:`, `image:`, etc.) qui varient selon les sources. C'est la clé de la compatibilité universelle du scraper.

#### Gestion des Erreurs Réseau

Le scraper gère trois types d'erreurs distinctement :
- `requests.RequestException` : problème réseau (timeout, DNS, etc.)
- `etree.XMLSyntaxError` : XML malformé
- `Exception` : toute autre erreur inattendue par article

Dans tous les cas, l'erreur est loguée et la fonction retourne une liste vide (ou continue au prochain article), sans bloquer l'application.

---

### 4.4 `wordcloud_generator.py` — Visualisation

Ce module génère des **nuages de mots en format SVG** à partir des titres des articles.

#### Pipeline de Génération

```
Titres des articles
        │
        ▼
Concaténation + mise en minuscules
        │
        ▼
Suppression de la ponctuation (regex)
        │
        ▼
Filtrage des stopwords français (60+ termes)
        │
        ▼
Génération du nuage (WordCloud)
        │
        ▼
Export SVG + ajout des liens cliquables
        │
        ▼
Sauvegarde dans static/wordcloud_{timestamp}.svg
```

#### Configuration du Nuage

```python
wc = WordCloud(
    width=1500, height=850,
    background_color="white",
    stopwords=stopwords,
    colormap="viridis",        # Palette de couleurs scientifique
    max_words=num_words,       # Configurable : 10 à 200
    collocations=False,        # Évite les paires de mots artificielles
    min_font_size=10,
    max_font_size=150,
    prefer_horizontal=0.9,     # 90% des mots horizontaux (lisibilité)
    relative_scaling=0.4,      # Taille proportionnelle à la fréquence
    random_state=42,           # Reproductibilité
    min_word_length=3          # Filtre les mots trop courts
)
```

#### Liens Cliquables dans le SVG

```python
def add_links_to_svg(svg_data):
    def replace_text(match):
        tag = match.group(0)
        word_match = re.search(r'>([^<]+)</text>', tag)
        if word_match:
            word = word_match.group(1).strip()
            encoded = urllib.parse.quote(word)
            return (
                f'<a href="/?keyword={encoded}" target="_top" ...>{tag}</a>'
            )
        return tag
    return re.sub(r'<text[^>]*>[^<]+</text>', replace_text, svg_data)
```

Chaque balise `<text>` du SVG est encapsulée dans une balise `<a>` pointant vers la page d'accueil avec le mot comme mot-clé de recherche. Cela transforme le nuage en **outil de navigation interactif**.

#### Fichiers Horodatés

Le nom de fichier inclut un timestamp (`wordcloud_20260514_143022.svg`) pour éviter les conflits entre générations successives et assurer la traçabilité.

---

## 5. Guide d'Utilisation de l'Application

### 5.1 Démarrage

**Windows :**
```
double-clic sur run.bat
```
ou manuellement :
```
cd src
python main.py
```
Puis ouvrir : **http://127.0.0.1:5000**

### 5.2 Étape 1 — Configurer les Sources (Administration)

Accéder à **Administration** dans la navigation.

1. Dans le formulaire "Ajouter un abonnement", saisir :
   - **Nom :** `Le Monde`
   - **URL :** `https://www.lemonde.fr/sitemap_news.xml`
2. Cliquer sur **Ajouter**.
3. Répéter pour d'autres sources :
   - Le Figaro : `https://www.lefigaro.fr/sitemap_news.xml`
   - Les Échos : `https://www.lesechos.fr/sitemap_news.xml`
   - France 24 : `https://www.france24.com/fr/sitemap_news.xml`

### 5.3 Étape 2 — Collecter les Articles

Depuis la page **Administration** :
- Cliquer sur **"Récupérer tous les articles"**
- Le système parcourt tous les sitemaps configurés et insère les nouveaux articles
- Un message indique le nombre d'articles ajoutés

### 5.4 Étape 3 — Consulter les Articles (Accueil)

La page d'accueil affiche les articles **organisés par source**.

**Recherche et filtres disponibles :**
- **Mot-clé** : recherche dans les titres (insensible à la casse)
- **Date début / Date fin** : filtrage par plage temporelle
- **Source** : afficher uniquement une source

Cliquer sur un article **ouvre l'article original** dans un nouvel onglet et **enregistre la consultation** dans l'historique.

Pour **ajouter en favori** : cliquer sur l'icône étoile, choisir une catégorie (ou laisser la catégorie automatique) et valider.

### 5.5 Étape 4 — Générer un Nuage de Mots

Accéder à **Nuage de Mots**.

**Paramètres configurables :**
- **Nombre de mots** : entre 10 et 200 (défaut : 80)
- **Date début / fin** : restreindre aux articles d'une période
- **Source** : générer depuis une seule source

Cliquer sur **"Générer le nuage de mots"**.
- Le nuage s'affiche inline dans la page
- Cliquer sur un mot redirige vers la recherche correspondante
- Bouton **"Télécharger le SVG"** pour sauvegarder localement

### 5.6 Étape 5 — Historique des Consultations

Accéder à **Historique**.

Affiche tous les articles consultés avec horodatage. Filtres disponibles :
- Mot-clé dans le titre
- Plage de dates de consultation

### 5.7 Étape 6 — Gestion des Favoris

Accéder à **Favoris**.

**Fonctionnalités :**
- Articles organisés par catégories (avec compteur)
- Filtre par catégorie en haut de page
- **Gérer les catégories** :
  - **Créer** : saisir un nom, cliquer "Créer"
  - **Renommer** : icône crayon → saisir le nouveau nom
  - **Supprimer** : icône poubelle → confirmation requise

> **Important :** La suppression d'une catégorie **supprime définitivement tous les articles favoris** de cette catégorie. Un avertissement explicite est affiché dans la fenêtre de confirmation.

---

## 6. Fonctionnalités Implémentées

### 6.1 Correspondance avec les Exigences du Sujet

| Exigence | Implémentation | Fichier |
|---|---|---|
| Collecte d'articles via sitemaps XML | `fetch_articles()` avec parsing lxml multi-sources | `scraper.py` |
| Stockage en base de données | 5 collections MongoDB avec indexes | `dbMongo.py` |
| Nommage `G_{initiales}_*` | `TEAM_INITIALS = "CSAE"` | `dbMongo.py` |
| Recherche par mot-clé | Regex MongoDB `$options: "i"` | `dbMongo.py` |
| Filtrage par date | `$gte` / `$lte` sur `date_publication` | `dbMongo.py` |
| Filtrage par source | Requête exacte sur champ `source` | `dbMongo.py` |
| Historique des consultations | Collection `consultations` avec `article_id` et horodatage | `dbMongo.py` |
| Nuage de mots | SVG généré avec `wordcloud`, liens cliquables | `wordcloud_generator.py` |
| Interface web | Flask + Bootstrap 5, 5 pages, responsive | `main.py` + templates |
| Gestion des favoris | Collection `favoris` avec catégories | `dbMongo.py` |
| Suppression catégorie → suppression des favoris | `delete_many({"catalogue": name})` | `dbMongo.py` |

### 6.2 Fonctionnalités Avancées

- **Inférence automatique de catégorie** : classification des favoris par mots-clés dans les titres
- **Nuage de mots interactif** : chaque mot est cliquable et déclenche une recherche
- **SVG horodaté** : chaque génération crée un fichier unique téléchargeable
- **Organisation par source** : la page d'accueil groupe les articles par journal
- **Protection "Général"** : la catégorie par défaut ne peut pas être supprimée
- **Migration automatique** : au démarrage, les favoris sans catégorie sont reclassés

---

## 7. Robustesse et Sécurité

### 7.1 Gestion des Erreurs

Toutes les opérations critiques sont encadrées par des blocs `try/except` :
- Requêtes réseau (timeout 10s, gestion des codes HTTP)
- Opérations MongoDB (DuplicateKeyError, ObjectId invalide)
- Parsing de dates ISO 8601 (formats variables selon les sources)
- Génération du nuage (retour `None` si échec, message d'erreur à l'utilisateur)

### 7.2 Logging Structuré

```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Exemples : logger.info(...), logger.error(...), logger.warning(...)
```

Chaque module dispose de son propre logger nommé, permettant d'identifier l'origine de chaque message dans les logs.

### 7.3 Validation des Entrées

- Les `ObjectId` sont validés avant toute requête MongoDB (évite les injections)
- Les dates sont parsées explicitement (`datetime.fromisoformat`) avec fallback silencieux
- Les URLs des sitemaps sont passées directement à `requests.get` avec timeout
- Les noms de catégories sont nettoyés avec `.strip()` avant insertion

### 7.4 Sécurité des Templates

Les templates Jinja2 échappent automatiquement toutes les variables (`{{ variable }}`), ce qui protège contre les injections XSS. L'application ne stocke aucune donnée sensible.

---

## 8. Conclusion

### 8.1 Bilan

Le projet "Nuage d'Actualité" a été entièrement réalisé et répond à l'ensemble des exigences du sujet. L'application est fonctionnelle, robuste et déployable localement.

Les points forts du projet sont :
- **Architecture modulaire** : chaque fichier a une responsabilité unique et bien définie
- **Base de données optimisée** : indexes conçus pour les requêtes réelles de l'application
- **Compatibilité multi-sources** : le scraper fonctionne avec 6+ sources de presse sans configuration spécifique
- **Interface utilisateur moderne** : Bootstrap 5 responsive, navigation fluide, interactions JavaScript minimalistes
- **Comportement cohérent** : la suppression d'une catégorie supprime les favoris associés (cohérence référentielle)

### 8.2 Compétences Mises en Œuvre

| Domaine | Compétence |
|---|---|
| Base de données | MongoDB, requêtes NoSQL, aggregation pipeline, indexation |
| Backend | Python, Flask, routing HTTP, Jinja2 |
| Collecte de données | Parsing XML/XPath, requêtes HTTP, gestion d'erreurs réseau |
| Visualisation | Génération SVG, manipulation de texte, stopwords |
| Frontend | Bootstrap 5, HTML5, JavaScript natif |

### 8.3 Perspectives d'Évolution

- Collecte automatique planifiée (cron ou APScheduler)
- Export des favoris en CSV/PDF
- Analyse de sentiment sur les titres d'articles
- Statistiques de consultation par source et par période
- API REST pour intégration externe

---

## 9. Annexes

### Annexe A — Dépendances (`requirements.txt`)

```
Flask==3.1.3
pymongo==4.17.0
lxml==6.1.0
requests==2.33.1
wordcloud==1.9.6
matplotlib==3.10.9
pillow==12.2.0
```

### Annexe B — Installation et Lancement

```bash
# 1. Vérifier que MongoDB est démarré
mongod

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
cd src
python main.py

# 4. Ouvrir dans le navigateur
# http://127.0.0.1:5000
```

### Annexe C — Résultats des Tests Automatisés

```
✅ Test 1 : Connexion MongoDB        — OK (v8.3.1)
✅ Test 2 : Collections              — OK (5 collections, indexes créés)
✅ Test 3 : Scraper                  — OK (199 articles récupérés)
✅ Test 4 : Wordcloud Generator      — OK (SVG généré)
✅ Test 5 : Opérations BD            — OK (CRUD complet)
✅ Test 6 : Routes Flask             — OK (11 routes actives)

Résultat global : 6/6 PASS
```

### Annexe D — Endpoints de l'API

| Route | Méthode | Paramètres | Description |
|---|---|---|---|
| `/` | GET | `keyword`, `start_date`, `end_date`, `source` | Accueil — recherche articles |
| `/admin` | GET | — | Administration des abonnements |
| `/add_subscription` | POST | `name`, `url` | Ajouter un sitemap |
| `/delete_subscription/<id>` | GET | `id` | Supprimer un abonnement |
| `/collect_all` | GET | — | Collecte globale (JSON) |
| `/click/<id>` | GET | `id` | Lire + enregistrer consultation |
| `/wordcloud` | GET | `num_words`, `start_date`, `end_date`, `source` | Générer nuage |
| `/historique` | GET | `keyword`, `start_date`, `end_date` | Historique consultations |
| `/favoris` | GET | `categorie` | Afficher les favoris |
| `/add_favorite[/<id>]` | POST | `article_id`, `categorie` | Ajouter un favori |
| `/categories/add` | POST | `name` | Créer une catégorie |
| `/categories/update` | POST | `old_name`, `new_name` | Renommer une catégorie |
| `/categories/delete` | POST | `name` | Supprimer catégorie + favoris |

---

*Rapport rédigé dans le cadre du cours de Structuration de Données — Master 1, Université de Lorraine, 2025-2026.*
