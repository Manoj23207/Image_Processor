# 🖼️ Image Processor

> A full-stack image transformation web app built with **FastAPI**, **Pillow**, and vanilla **HTML/CSS/JS**.  
> Upload an image → select operations → download the result. Also fully accessible via REST API.

---

## ✨ Features

- **Drag & drop upload** — JPG, PNG, GIF, WebP, BMP (max 20MB)
- **Pipeline of transforms** — chain multiple operations in any order
- **Async job processing** — submit returns immediately with a job ID; background thread handles processing
- **Auto file cleanup** — processed files expire after 15 minutes
- **Swagger UI** — interactive API docs at `/docs`, no setup required
- **Zero infrastructure** — no database, no Docker, no cloud; just `python run.py`

---

## 🎬 Supported Operations

| Operation | API Name | Effect |
|-----------|----------|--------|
| Flip Horizontal | `flip_horizontal` | Mirror image left-to-right |
| Flip Vertical | `flip_vertical` | Mirror image top-to-bottom |
| Grayscale | `grayscale` | Remove color (output stays RGB) |
| Rotate Left | `rotate_left` | Rotate 90° counter-clockwise |
| Rotate Right | `rotate_right` | Rotate 90° clockwise |

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/Manoj23207/Image_Processor.git
cd Image_Processor
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn pillow python-multipart aiofiles
```

### 3. Start the server

```bash
python run.py
```

### 4. Open in browser
App:       http://localhost:8000
API Docs:  http://localhost:8000/docs

---

## 📁 Project Structure

---

## 🔌 REST API

All endpoints served at `http://localhost:8000`. Full interactive docs at `/docs`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the frontend |
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |
| `GET` | `/operations` | Lists all supported operation names |
| `POST` | `/transform` | Submit a transform job (returns job ID immediately) |
| `GET` | `/jobs/{job_id}` | Poll job status |
| `GET` | `/download/{job_id}` | Download the processed image |

### Submit a job

```bash
curl -X POST http://localhost:8000/transform \
  -F "image=@photo.jpg" \
  -F 'operations=["grayscale","rotate_left"]'
```

**Response (202 Accepted):**
```json
{
  "jobId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "queued",
  "pollUrl": "/jobs/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Poll for result

```bash
curl http://localhost:8000/jobs/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

```json
{
  "jobId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "done",
  "operations": ["grayscale", "rotate_left"],
  "downloadUrl": "/download/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Download the result

```bash
curl -O http://localhost:8000/download/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## 🏗️ Architecture

The system uses a **4-layer architecture**:

┌─────────────────────────────────────────┐
│  HTTP Layer         app/main.py         │  ← Route handlers, validation, file I/O
├─────────────────────────────────────────┤
│  Job Management     app/store.py        │  ← Thread-safe in-memory job registry
├─────────────────────────────────────────┤
│  Execution Layer    app/worker.py       │  ← Worker thread + cleanup thread
├─────────────────────────────────────────┤
│  Processing Layer   app/pipeline.py     │  ← Pure image transform logic (Pillow)
└─────────────────────────────────────────┘

**Job lifecycle:**

- `POST /transform` creates the job (`queued`) and returns immediately
- Background worker picks it up, sets `processing`, runs the pipeline
- On success → `done` + files expire after 15 minutes
- On error → `failed` + error message stored in job record
- Cleanup thread deletes expired files and records every 60 seconds

---

## 🖥️ Frontend

Single HTML file (`app/static/index.html`) — no framework, no build step, no npm.

**Three-screen flow:**

1. **Drop Zone** — full-screen drag & drop with animated background
2. **Pipeline Select** — image thumbnail + 5 operation toggle buttons + live pipeline strip
3. **Result View** — animated status dot, result image preview, download button

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | [FastAPI](https://fastapi.tiangolo.com) |
| ASGI server | [Uvicorn](https://www.uvicorn.org) |
| Image processing | [Pillow](https://pillow.readthedocs.io) |
| File uploads | python-multipart |
| Frontend | Vanilla HTML / CSS / JS |
| Language | Python 3.10+ |

---

## 📋 Requirements

- Python **3.10** or higher
- No Docker, no database, no external services

---

## 🗂️ Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| `202` | Job submitted successfully |
| `400` | Invalid file type, bad operations JSON, or unknown operation name |
| `404` | Job ID does not exist |
| `409` | Job exists but not done yet |
| `410` | Files expired (15 min TTL) |
| `413` | File exceeds 20MB limit |

---

## 📄 License

Developed as an **Individual Project** for CPSC 5200 Software Architecture at **Seattle University**.

---

## 👤 Author

**Manoj Sai**  
Seattle University — MS Computer Science  
[GitHub](https://github.com/Manoj23207)
