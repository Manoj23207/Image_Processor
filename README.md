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
