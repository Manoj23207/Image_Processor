import os, uuid, json, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.store import store, Job
from app.worker import start_worker
from app.pipeline import OPERATIONS

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
STATIC_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
MAX_FILE_SIZE = 20 * 1024 * 1024

@asynccontextmanager
async def lifespan(app):
    start_worker()
    yield

app = FastAPI(title="Image Processor API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def root():
    index = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"message": "Image Processor API"}

@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}

@app.get("/operations")
def list_operations():
    return {"operations": list(OPERATIONS.keys())}

@app.post("/transform", status_code=202)
async def submit_transform(
    image: UploadFile = File(...),
    operations: str = Form(...)
):
    ext = os.path.splitext(image.filename or "upload.jpg")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not allowed.")
    content = await image.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max 20MB.")
    try:
        ops = json.loads(operations)
        if not isinstance(ops, list) or len(ops) == 0:
            raise ValueError()
    except:
        raise HTTPException(status_code=400, detail="operations must be a non-empty JSON array.")
    unknown = [op for op in ops if op not in OPERATIONS]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown operations: {unknown}")
    job_id = str(uuid.uuid4())
    input_path  = os.path.join(UPLOADS_DIR, f"{job_id}{ext}")
    output_ext  = ".png" if ext in (".png", ".gif") else ".jpg"
    output_path = os.path.join(OUTPUTS_DIR, f"{job_id}_out{output_ext}")
    with open(input_path, "wb") as f:
        f.write(content)
    store.create(Job(id=job_id, input_path=input_path, output_path=output_path, operations=ops))
    return {"jobId": job_id, "status": "queued", "pollUrl": f"/jobs/{job_id}"}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    resp = {"jobId": job.id, "status": job.status, "operations": job.operations}
    if job.status == "done":
        resp["downloadUrl"] = f"/download/{job_id}"
    if job.status == "failed":
        resp["error"] = job.error
    return resp

@app.get("/download/{job_id}")
def download_result(job_id: str):
    job = store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != "done":
        raise HTTPException(status_code=409, detail=f"Job is '{job.status}', not done yet.")
    if not os.path.exists(job.output_path):
        raise HTTPException(status_code=410, detail="Result file has expired.")
    ext = os.path.splitext(job.output_path)[1].lower()
    media_type = "image/png" if ext == ".png" else "image/jpeg"
    return FileResponse(job.output_path, media_type=media_type, filename=f"processed{ext}")
