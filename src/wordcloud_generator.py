from wordcloud import WordCloud
import re
import os

def generate_wordcloud(articles, filename="wordcloud.svg"):

    # chemin vers static
    static_path = os.path.join(os.path.dirname(__file__), "../static")
    file_path = os.path.join(static_path, filename)

    # concat titres
    text = " ".join([a["title"] for a in articles])

    # nettoyage
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)

    stopwords = {
        "le", "la", "les", "de", "des", "du",
        "un", "une", "et", "en", "à", "au",
        "pour", "avec", "sur", "dans",
        "france", "monde"
    }

    wc = WordCloud(
        width=1000,
        height=500,
        background_color="white",
        stopwords=stopwords,
        colormap="viridis",
        max_words=80
    )

    wc.generate(text)

    # 🔥 génération SVG
    svg_data = wc.to_svg()

    # écrire fichier SVG
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg_data)

    return filename