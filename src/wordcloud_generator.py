from wordcloud import WordCloud
import re
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_wordcloud(articles, num_words=80, filename=None):
    """
    Generate an SVG word cloud from articles.
    
    Args:
        articles: List of article dictionaries with 'title' key
        num_words: Maximum number of words to display (default: 80)
        filename: Output filename (default: wordcloud_{timestamp}.svg)
    
    Returns:
        Filename of the generated SVG
    """
    try:
        if not articles:
            logger.warning("Aucun article fourni pour le nuage de mots")
            return None

        # chemin vers static
        static_path = os.path.join(os.path.dirname(__file__), "../static")
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wordcloud_{timestamp}.svg"
        
        file_path = os.path.join(static_path, filename)

        # concat titres
        text = " ".join([a.get("title", "") for a in articles if a.get("title")])

        if not text.strip():
            logger.warning("Aucun texte à traiter pour le nuage de mots")
            return None

        # nettoyage
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)

        # Stopwords français étendus
        stopwords = {
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

        wc = WordCloud(
            width=1200,
            height=600,
            background_color="white",
            stopwords=stopwords,
            colormap="viridis",
            max_words=num_words,
            margin=5,
            min_font_size=12,
            max_font_size=120,
            prefer_horizontal=0.9,
            relative_scaling=0.5,
            random_state=42,
            min_word_length=3  # Ignorer les mots < 3 caractères
        )

        wc.generate(text)

        # génération SVG
        svg_data = wc.to_svg(embed_font=True)

        # écrire fichier SVG
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(svg_data)

        logger.info(f"Nuage de mots généré: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Erreur génération nuage de mots: {e}")
        return None