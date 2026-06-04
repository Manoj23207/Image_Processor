import threading, time
from typing import Optional
from dataclasses import dataclass, field

@dataclass
class Job:
    id: str
    status: str = "queued"
    input_path: str = ""
    output_path: str = ""
    operations: list = field(default_factory=list)
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None

class JobStore:
    def __init__(self):
        self._jobs = {}
        self._lock = threading.Lock()
    def create(self, job):
        with self._lock:
            self._jobs[job.id] = job
        return job
    def get(self, job_id):
        with self._lock:
            return self._jobs.get(job_id)
    def update(self, job_id, **kwargs):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                for k, v in kwargs.items():
                    setattr(job, k, v)
            return job
    def all_expired(self):
        now = time.time()
        with self._lock:
            return [j for j in self._jobs.values() if j.expires_at and j.expires_at < now]
    def delete(self, job_id):
        with self._lock:
            self._jobs.pop(job_id, None)

store = JobStore()
