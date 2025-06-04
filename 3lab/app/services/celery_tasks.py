import os, datetime
from pathlib import Path
from app.core.celery_app import celery_app
from app.services.parser import SiteParser
from app.services.notifier import publish
from app.core.database import SessionLocal
from app.models.task import Task, TaskStatus
from app.cruds.task import update

@celery_app.task(bind=True, name="parse_website_task")
def parse_website_task(self, task_id: str):
    db = SessionLocal()
    task: Task = db.query(Task).get(task_id)
    if not task:
        return

    update(db, task, status=TaskStatus.started, started_at=datetime.datetime.utcnow())
    publish(task.user_id, task.id, {
        "status": "STARTED",
        "task_id": task.id,
        "url": task.url,
        "max_depth": task.max_depth,
    })

    parser = SiteParser(task.url, task.max_depth)

    def progress_cb(pct, current_url, pages_parsed, links_found):
        update(db, task,
               status=TaskStatus.progress,
               progress=pct,
               pages_parsed=pages_parsed,
               links_found=links_found)
        publish(task.user_id, task.id, {
            "status": "PROGRESS",
            "task_id": task.id,
            "progress": pct,
            "current_url": current_url,
            "pages_parsed": pages_parsed,
            "links_found": links_found,
        })

    elapsed = parser.run(progress_cb=progress_cb)

    graph_dir = Path("graphs"); graph_dir.mkdir(exist_ok=True)
    graph_path = graph_dir / f"{task.id}.graphml"
    parser.save_graph(graph_path)

    update(db, task,
           status=TaskStatus.completed,
           progress=100,
           finished_at=datetime.datetime.utcnow(),
           result_path=str(graph_path))

    publish(task.user_id, task.id, {
        "status": "COMPLETED",
        "task_id": task.id,
        "total_pages": task.pages_parsed,
        "total_links": task.links_found,
        "elapsed_time": f"{elapsed:.2f}s",
        "result": str(graph_path)
    })
    db.close()
