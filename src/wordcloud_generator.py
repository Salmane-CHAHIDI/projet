from wordcloud import WordCloud
import re
import os
import logging
import urllib.parse
from datetime import datetime
import matplotlib.font_manager as fm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_links_to_svg(svg_data):
    """Wrap each word in the SVG with a clickable link to the search page."""
    def replace_text(match):
        tag = match.group(0)
        word_match = re.search(r'>([^<]+)</text>', tag)
        if word_match:
            word = word_match.group(1).strip()
            if word:
                encoded = urllib.parse.quote(word)
                return (
                    f'<a href="/?keyword={encoded}" target="_top" '
                    f'style="cursor:pointer;text-decoration:none" '
                    f'title="Rechercher : {word}">{tag}</a>'
                )
        return tag

    return re.sub(r'<text[^>]*>[^<]+</text>', replace_text, svg_data)


def generate_wordcloud(articles, num_words=80, filename=None):
    try:
        if not articles:
            logger.warning("Aucun article fourni pour le nuage de mots")
            return None

        static_path = os.path.join(os.path.dirname(__file__), "../static")
        os.makedirs(static_path, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wordcloud_{timestamp}.svg"

        file_path = os.path.join(static_path, filename)

        text = " ".join(a.get("title", "") for a in articles if a.get("title"))

        if not text.strip():
            logger.warning("Aucun texte à traiter")
            return None

        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        stopwords = {
            "le", "la", "les", "de", "des", "du",
            "un", "une", "et", "en", "à", "au",
            "aux", "pour", "avec", "sur", "dans",
            "par", "vers", "entre", "sans",
            "que", "qui", "quoi", "dont", "où",
            "ce", "ces", "cet", "cette",
            "son", "sa", "ses",
            "leur", "leurs",
            "plus", "moins", "très", "bien",
            "pas", "encore", "déjà",
            "france", "monde", "article", "articles",
            "ainsi", "comme", "après", "avant"
        }

        font_path = fm.findfont("DejaVu Sans")

        outer_width = 1600
        outer_height = 900
        padding = 50
        inner_width = outer_width - 2 * padding
        inner_height = outer_height - 2 * padding

        wc = WordCloud(
            width=inner_width,
            height=inner_height,
            background_color="white",
            stopwords=stopwords,
            font_path=font_path,
            colormap="viridis",
            max_words=num_words,
            collocations=False,
            margin=8,
            min_font_size=10,
            max_font_size=150,
            prefer_horizontal=0.9,
            relative_scaling=0.4,
            random_state=42,
            min_word_length=3
        )

        wc.generate(text)
        svg_data = wc.to_svg(embed_font=False)

        svg_data = re.sub(
            r'<svg[^>]*width="[^"]*"[^>]*height="[^"]*"[^>]*>',
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{outer_width}" '
                f'height="{outer_height}" '
                f'viewBox="0 0 {outer_width} {outer_height}">'
                f'<rect width="100%" height="100%" fill="white"/>'
                f'<g transform="translate({padding},{padding})">'
            ),
            svg_data,
            count=1
        )
        svg_data = svg_data.replace("</svg>", "</g></svg>")

        svg_data = add_links_to_svg(svg_data)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(svg_data)

        logger.info(f"Nuage de mots généré : {filename}")
        return filename

    except Exception as e:
        logger.exception(f"Erreur génération nuage de mots : {e}")
        return None
