# 📰 Nuage d'Actualité - Application Web

Application de collecte et visualisation d'actualités sous forme de nuage de mots, développée avec Flask et MongoDB.

## 🎯 Fonctionnalités

### Mode Administration
- ✅ Gestion d'abonnements à des sources d'actualités (via sitemaps)
- ✅ Suppression d'abonnements
- ✅ Récupération automatique des articles
- ✅ Suivi de la dernière récupération

### Mode Consultation
- ✅ Parcourir les articles d'actualité
- ✅ Recherche par mot-clé
- ✅ Filtrage par date (début/fin)
- ✅ Filtrage par source
- ✅ Organisation des articles par source
- ✅ Historique des consultations
- ✅ Génération de nuage de mots SVG
- ✅ Customisation du nombre de mots
- ✅ Téléchargement du nuage en SVG

## 📋 Prérequis

- Python 3.8+
- MongoDB (en local sur `localhost:27017`)
- pip

## 🚀 Installation

### 1. Installation des dépendances

```bash
cd projet
pip install -r requirements.txt
```

### 2. Configuration MongoDB

Assurez-vous que MongoDB est installé et en cours d'exécution sur le port 27017.

Pour vérifier la connexion :
```bash
python -c "from pymongo import MongoClient; client = MongoClient('localhost', 27017); print('Connecté à:', client.server_info()['version'])"
```

### 3. Configuration de l'équipe (IMPORTANT)

Avant de lancer l'application, modifiez les initiales de votre équipe dans `src/dbMongo.py` :

```python
TEAM_INITIALS = "TEST"  # À remplacer par vos initiales (ex: "DFSB")
```

Les collections utiliseront ce format : `G_DFSB_articles`, `G_DFSB_abonnements`, `G_DFSB_consultations`

## ▶️ Lancement

```bash
cd src
python main.py
```

L'application sera disponible sur `http://localhost:5000`

## 📱 Utilisation

### Page d'Accueil (`/`)
- Affiche tous les articles organisés par source
- Recherche par mot-clé
- Filtrage par date
- Filtrage par source
- Clic sur un titre : ouvre l'article dans un nouvel onglet

### Administration (`/admin`)
- Ajouter une source (sitemap)
- Voir les abonnements actifs
- Supprimer un abonnement
- Bouton de récupération manuelle des articles

### Nuage de Mots (`/wordcloud`)
- Spécifier le nombre de mots (10-200)
- Filtrer par date
- Filtrer par source
- Générer et télécharger en SVG

### Historique (`/historique`)
- Vue de tous les articles consultés
- Horodatage de chaque consultation

## 🔌 Endpoints API

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET | Accueil - articles avec recherche |
| `/admin` | GET | Page d'administration |
| `/add_subscription` | POST | Ajouter un abonnement |
| `/delete_subscription/<id>` | GET | Supprimer un abonnement |
| `/collect_all` | GET | Récupérer tous les articles |
| `/collect` | GET | Tester récupération (Le Monde) |
| `/test` | GET | Teste le scraper |
| `/click/<id>` | GET | Enregistre consultation et redirige |
| `/wordcloud` | GET | Page nuage de mots |
| `/historique` | GET | Historique des consultations |

## 📊 Structure de Données

### Collection `articles`
```javascript
{
  _id: ObjectId,
  title: String,
  url: String,
  date_publication: Date,
  source: String,
  inserted_at: Date
}
```

### Collection `abonnements`
```javascript
{
  _id: ObjectId,
  name: String,
  url: String,
  created_at: Date,
  last_fetch: Date,
  active: Boolean
}
```

### Collection `consultations`
```javascript
{
  _id: ObjectId,
  article_id: ObjectId,
  date_consultation: Date
}
```

## 🔍 Exemple de Sitemaps

| Source | URL |
|--------|-----|
| Le Monde | https://www.lemonde.fr/sitemap_news.xml |
| France 24 | https://www.france24.com/sitemap_news.xml |
| Reuters | https://www.reuters.com/news/ |

## 📦 Dépendances Principales

- **Flask** : Framework web
- **PyMongo** : Driver MongoDB
- **wordcloud** : Génération de nuages de mots
- **lxml** : Parsing XML/HTML
- **requests** : Requêtes HTTP

## ⚠️ Notes Importantes

1. **Pas d'authentification** : L'application utilise une connexion non authentifiée à MongoDB (académique)
2. **Unique URL** : Les articles sont dédoublonnés par URL
3. **Indexes** : Créés automatiquement pour optimiser les requêtes
4. **Stopwords FR** : Les mots vides français sont automatiquement ignorés du nuage
5. **SVG dynamique** : Chaque génération crée un nouveau fichier SVG daté

## 🛠️ Troubleshooting

### Erreur de connexion MongoDB
```
ConnectionFailure: [Errno 111] Connection refused
```
Assurez-vous que MongoDB est lancé : `mongod`

### Erreur lors de la récupération du sitemap
Vérifiez que l'URL du sitemap est correcte et accessible

### Aucun article dans le nuage
- Vérifiez qu'il y a des articles en base de données
- Cliquez sur "Récupérer tous les articles" depuis l'admin
- Vérifiez les filtres de date/source

## 📝 Optimisations Implémentées

✅ **Indexation MongoDB** : Sur `url`, `date_publication`, `title`, `source`  
✅ **Recherche optimisée** : Regex case-insensitive, filtres multiples  
✅ **Gestion des doublons** : Index unique sur URL  
✅ **Wordcloud optimisé** : Stopwords, min_font_size, pagination  
✅ **Error handling** : Gestion robuste des erreurs réseau  
✅ **Logging** : Suivi des opérations importantes  

## 👥 Équipe

À remplir avec les noms et initiales de votre équipe

## 📄 Rapport de Projet

Voir `rapport.pdf` pour les détails de conception et d'optimisation.

---

**Dernière mise à jour** : Mai 2026  
**Statut** : Production ✅
