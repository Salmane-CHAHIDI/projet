import requests
from lxml import etree
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_articles(sitemap_url):
    """
    Fetch articles from a sitemap URL.
    Handles news sitemaps with namespace-aware XPath.
    """
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()

        if response.status_code != 200:
            logger.warning(f"Erreur récupération sitemap {sitemap_url}: {response.status_code}")
            return []

        root = etree.fromstring(response.content)

        articles = []

        # Récupère les balises url
        urls = root.xpath("//*[local-name()='url']")

        for url in urls:
            try:
                title = url.xpath(".//*[local-name()='title']/text()")
                link = url.xpath(".//*[local-name()='loc']/text()")
                date = url.xpath(".//*[local-name()='publication_date']/text()")
                
                # Essayer plusieurs chemins pour les images dans les sitemaps news
                image = None
                
                # Chemin 1: image:image (standard news sitemap)
                image_candidates = url.xpath(".//*[local-name()='image']/text()")
                if image_candidates:
                    image = image_candidates[0]
                
                # Chemin 2: news:image (dans la balise news)
                if not image:
                    image_candidates = url.xpath(".//*[local-name()='news']//*[local-name()='image']/text()")
                    if image_candidates:
                        image = image_candidates[0]
                
                # Chemin 3: image:loc (URL de l'image)
                if not image:
                    image_candidates = url.xpath(".//*[local-name()='image']//*[local-name()='loc']/text()")
                    if image_candidates:
                        image = image_candidates[0]
                
                # Alternative for news sitemaps
                if not date:
                    date = url.xpath(".//*[local-name()='news']//*[local-name()='publication_date']/text()")

                if title and link:
                    articles.append({
                        "title": title[0].strip(),
                        "url": link[0].strip(),
                        "date": date[0] if date else None,
                        "image": image.strip() if image else None
                    })

            except Exception as e:
                logger.error(f"Erreur parsing article: {e}")
                continue

        logger.info(f"Récupéré {len(articles)} articles de {sitemap_url}")
        return articles
        
    except requests.RequestException as e:
        logger.error(f"Erreur requête sitemap {sitemap_url}: {e}")
        return []
    except etree.XMLSyntaxError as e:
        logger.error(f"Erreur parsing XML {sitemap_url}: {e}")
        return []
    except Exception as e:
        logger.error(f"Erreur inattendue {sitemap_url}: {e}")
        return []