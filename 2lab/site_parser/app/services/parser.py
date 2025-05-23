import aiohttp
from urllib.parse import urljoin, urlparse
from lxml import html
import networkx as nx

async def fetch_page(session, url):
    async with session.get(url) as resp:
        return await resp.text()

async def parse_website(start_url, max_depth=3):
    graph = nx.DiGraph()
    visited = set()

    async def crawl(url, depth):
        if url in visited or depth > max_depth:
            return
        visited.add(url)
        try:
            async with aiohttp.ClientSession() as session:
                content = await fetch_page(session, url)
            doc = html.fromstring(content)
            links = set(
                urljoin(url, l)
                for l in doc.xpath('//a/@href')
                if urlparse(urljoin(url, l)).netloc == urlparse(start_url).netloc
            )
            graph.add_node(url)
            for l in links:
                graph.add_edge(url, l)
            for l in links:
                await crawl(l, depth + 1)
        except Exception as e:
            pass

    await crawl(start_url, 1)
    return '\n'.join(nx.generate_graphml(graph))
