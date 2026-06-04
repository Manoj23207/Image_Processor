import os, time, threading, logging
from app.store import store, Job
from app.pipeline import process

log = logging.getLogger(__name__)

def _do_job(job: Job):
    store.update(job.id, status="processing")
    try:
        process(job.input_path, job.operations, job.output_path)
        store.update(job.id, status="done", expires_at=time.time() + 900)
        log.info(f"Job {job.id} done.")
    except Exception as exc:
        store.update(job.id, status="failed", error=str(exc))
        log.error(f"Job {job.id} failed: {exc}")

def _cleanup_loop():
    while True:
        time.sleep(60)
        for job in store.all_expired():
            for path in (job.input_path, job.output_path):
                try:
                    if path and os.path.exists(path):
                        os.remove(path)
                except OSError:
                    pass
            store.delete(job.id)

def _worker_loop():
    while True:
        queued = [j for j in store._jobs.values() if j.status == "queued"]
        if queued:
            job = min(queued, key=lambda j: j.created_at)
            _do_job(job)
        else:
            time.sleep(0.2)

def start_worker():
    threading.Thread(target=_worker_loop, daemon=True, name="worker").start()
    threading.Thread(target=_cleanup_loop, daemon=True, name="cleanup").start()
