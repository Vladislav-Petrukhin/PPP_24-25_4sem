import re, urllib.parse, time, networkx as nx, requests
from collections import deque
from bs4 import BeautifulSoup

def is_internal(base: str, link: str) -> bool:
    return urllib.parse.urlparse(link).netloc == urllib.parse.urlparse(base).netloc

class SiteParser:
    def __init__(self, url: str, max_depth: int = 3):
        self.url = url.rstrip("/")
        self.max_depth = max_depth
        self.graph = nx.DiGraph()
        self.seen = set()

    def fetch_links(self, url: str) -> list[str]:
        try:
            resp = requests.get(url, timeout=10)
        except requests.RequestException:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        return [
            urllib.parse.urljoin(url, a.get("href"))
            for a in soup.find_all("a", href=True)
        ]

    def run(self, progress_cb=None):
        q = deque([(self.url, 0)])
        start = time.time()

        while q:
            current, depth = q.popleft()
            if current in self.seen or depth > self.max_depth:
                continue
            self.seen.add(current)
            self.graph.add_node(current)

            links = self.fetch_links(current)
            for lnk in links:
                if not lnk:
                    continue
                if is_internal(self.url, lnk):
                    self.graph.add_edge(current, lnk)
                    q.append((lnk, depth + 1))

            if progress_cb:
                pct = int(len(self.seen) / (len(self.seen) + q.__len__()) * 100)
                progress_cb(pct, current, len(self.seen), self.graph.number_of_edges())

        elapsed = time.time() - start
        return elapsed

    def save_graph(self, path: str):
        nx.write_graphml(self.graph, path)
