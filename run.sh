#!/bin/bash

# Script de lancement du projet Nuage d'Actualité

echo ""
echo "================================"
echo "  Nuage d'Actualité - Démarrage"
echo "================================"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur: Python 3 n'est pas installé"
    echo "Veuillez installer Python 3.8+ depuis python.org"
    exit 1
fi

# Vérifier version Python
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION détecté"

# Vérifier si MongoDB est accessible
echo "🔍 Vérification de la connexion MongoDB..."
if python3 -c "from pymongo import MongoClient; client = MongoClient('localhost', 27017); print('✅ MongoDB connecté')" 2>/dev/null; then
    :
else
    echo "❌ Erreur: MongoDB n'est pas disponible sur localhost:27017"
    echo "Veuillez:"
    echo "  1. Installer MongoDB Community Edition"
    echo "  2. Lancer mongod (le serveur MongoDB)"
    echo "  3. Relancer ce script"
    exit 1
fi

# Vérifier si les dépendances sont installées
echo "🔍 Vérification des dépendances Python..."
if ! python3 -c "import flask, pymongo, wordcloud, lxml" 2>/dev/null; then
    echo "📦 Installation des dépendances..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Erreur lors de l'installation des dépendances"
        exit 1
    fi
fi

echo "✅ Tous les prérequis sont satisfaits!"
echo ""
echo "🚀 Lancement de l'application..."
echo ""
echo "📍 L'application sera disponible sur: http://localhost:5000"
echo ""
echo "💡 Raccourcis:"
echo "   - Accueil: http://localhost:5000/"
echo "   - Admin: http://localhost:5000/admin"
echo "   - Nuage: http://localhost:5000/wordcloud"
echo "   - Historique: http://localhost:5000/historique"
echo ""
echo "⚠️  N'oubliez pas de modifier TEAM_INITIALS dans config.py!"
echo ""

cd src
python3 main.py
