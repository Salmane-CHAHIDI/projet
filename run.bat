@echo off
REM Script de lancement du projet Nuage d'Actualité

echo.
echo ================================
echo  Nuage d'Actualité - Démarrage
echo ================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Erreur: Python n'est pas installé ou non accessible
    echo Veuillez installer Python 3.8+ depuis python.org
    pause
    exit /b 1
)

REM Vérifier si MongoDB est accessible
echo 🔍 Vérification de la connexion MongoDB...
python -c "from pymongo import MongoClient; client = MongoClient('localhost', 27017); print('✅ MongoDB connecté')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Erreur: MongoDB n'est pas disponible sur localhost:27017
    echo Veuillez:
    echo   1. Installer MongoDB Community Edition
    echo   2. Lancer mongod (le serveur MongoDB)
    echo   3. Relancer ce script
    pause
    exit /b 1
)

REM Vérifier si les dépendances sont installées
echo 🔍 Vérification des dépendances Python...
python -c "import flask, pymongo, wordcloud, lxml" 2>nul
if %errorlevel% neq 0 (
    echo 📦 Installation des dépendances...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Erreur lors de l'installation des dépendances
        pause
        exit /b 1
    )
)

echo ✅ Tous les prérequis sont satisfaits!
echo.
echo 🚀 Lancement de l'application...
echo.
echo 📍 L'application sera disponible sur: http://localhost:5000
echo.
echo 💡 Raccourcis:
echo   - Accueil: http://localhost:5000/
echo   - Admin: http://localhost:5000/admin
echo   - Nuage: http://localhost:5000/wordcloud
echo   - Historique: http://localhost:5000/historique
echo.
echo ⚠️  N'oubliez pas de modifier TEAM_INITIALS dans config.py!
echo.

cd src
python main.py

pause
