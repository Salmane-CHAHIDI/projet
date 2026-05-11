import requests
from lxml import etree
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_articles(sitemap_url):
    """
    Récupère les articles depuis un sitemap XML.

    Compatible avec :
    - Le Monde
    - Le Figaro
    - Les Échos
    - Franceinfo
    - France 24
    - 20 Minutes

    Champs extraits :
    - title
    - url
    - date
    - image
    """
    try:
        response = requests.get(
            sitemap_url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )
        response.raise_for_status()

        if response.status_code != 200:
            logger.warning(
                f"Erreur récupération sitemap {sitemap_url}: "
                f"{response.status_code}"
            )
            return []

        root = etree.fromstring(response.content)
        articles = []

        # Récupère toutes les balises <url>
        urls = root.xpath("//*[local-name()='url']")

        for url in urls:
            try:
                # --------------------------------------------------
                # TITRE
                # --------------------------------------------------
                title = url.xpath(
                    ".//*[local-name()='news']/*[local-name()='title']/text()"
                )

                # Fallback si le titre n'est pas dans news:title
                if not title:
                    title = url.xpath(
                        ".//*[local-name()='title']/text()"
                    )

                # --------------------------------------------------
                # URL DE L'ARTICLE
                # IMPORTANT : on prend uniquement le loc DIRECT
                # de <url>, sinon on risque de récupérer image:loc
                # --------------------------------------------------
                link = url.xpath(
                    "./*[local-name()='loc']/text()"
                )

                # --------------------------------------------------
                # DATE DE PUBLICATION
                # --------------------------------------------------
                date = url.xpath(
                    ".//*[local-name()='news']/*[local-name()='publication_date']/text()"
                )

                # Fallback : lastmod
                if not date:
                    date = url.xpath(
                        "./*[local-name()='lastmod']/text()"
                    )

                # --------------------------------------------------
                # IMAGE
                # IMPORTANT :
                # Les Échos et Le Figaro utilisent :
                # <image:image>
                #   <image:loc>https://...jpg</image:loc>
                # </image:image>
                #
                # On prend UNIQUEMENT le PREMIER image:loc direct
                # sous image:image.
                # --------------------------------------------------
                image_candidates = url.xpath(
                    "./*[local-name()='image']/*[local-name()='loc']/text()"
                )

                # Fallback pour d'autres formats
                if not image_candidates:
                    image_candidates = url.xpath(
                        ".//*[local-name()='image']/text()"
                    )

                image = (
                    image_candidates[0].strip()
                    if image_candidates and image_candidates[0]
                    else None
                )

                # --------------------------------------------------
                # VALIDATION
                # --------------------------------------------------
                if title and link:
                    articles.append({
                        "title": title[0].strip(),
                        "url": link[0].strip(),
                        "date": (
                            date[0].strip()
                            if date and date[0]
                            else None
                        ),
                        "image": image
                    })

            except Exception as e:
                logger.error(f"Erreur parsing article: {e}")
                continue

        logger.info(
            f"Récupéré {len(articles)} articles de {sitemap_url}"
        )
        return articles

    except requests.RequestException as e:
        logger.error(
            f"Erreur requête sitemap {sitemap_url}: {e}"
        )
        return []

    except etree.XMLSyntaxError as e:
        logger.error(
            f"Erreur parsing XML {sitemap_url}: {e}"
        )
        return []

    except Exception as e:
        logger.error(
            f"Erreur inattendue {sitemap_url}: {e}"
        )
        return []