from celery_worker import celery
from app.services.parser import parse_website

@celery.task(bind=True)
def run_parse_task(self, url, max_depth, fmt):
    import asyncio
    loop = asyncio.get_event_loop()
    graphml = loop.run_until_complete(parse_website(url, max_depth))
    return graphml
