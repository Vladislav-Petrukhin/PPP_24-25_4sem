import requests
from bs4 import BeautifulSoup

def crawl_site(start_url: str, max_depth: int = 2):
    visited = set()
    edges = []
    def crawl(url, depth):
        if depth > max_depth or url in visited:
            return
        visited.add(url)
        try:
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if href.startswith("/"):
                    href = requests.compat.urljoin(url, href)
                if href.startswith(start_url):
                    edges.append((url, href))
                    crawl(href, depth + 1)
        except Exception:
            pass
    crawl(start_url, 0)
    # Минимальный GraphML
    graphml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
        '  <graph id="G" edgedefault="directed">'
    ]
    for node in visited:
        graphml.append(f'    <node id="{node}"/>')
    for src, dst in edges:
        graphml.append(f'    <edge source="{src}" target="{dst}"/>')
    graphml.append('  </graph>')
    graphml.append('</graphml>')
    return "\n".join(graphml)
