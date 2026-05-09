import requests
from lxml import etree


def fetch_articles(sitemap_url):
    response = requests.get(sitemap_url)

    if response.status_code != 200:
        print("Erreur récupération sitemap")
        return []

    root = etree.fromstring(response.content)

    articles = []

    # On ignore les namespaces avec XPath
    urls = root.xpath("//*[local-name()='url']")

    for url in urls:
        try:
            title = url.xpath(".//*[local-name()='title']/text()")
            link = url.xpath(".//*[local-name()='loc']/text()")
            date = url.xpath(".//*[local-name()='publication_date']/text()")

            if title and link:
                articles.append({
                    "title": title[0],
                    "url": link[0],
                    "date": date[0] if date else None
                })

        except Exception as e:
            print("Erreur :", e)
            continue

    return articles