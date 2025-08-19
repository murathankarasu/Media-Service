
# NSFW + Gore Detection Service

This project is a Flask API that uses an open-source model to detect **Inappropriate Content (NSFW)** and **Gore/Violence** in images and videos.

## 🚀 Features

* Detect **NSFW content** (Pornography, Hentai, Explicit) in images
* Detect **Gore/Violence** (blood, graphic content) in images
* Easy integration via direct file upload

## 🛠️ Setup & Local Run

1. **Clone the repo:**

```bash
git clone <repo_url>
cd Image-Service
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

*Note: PyTorch installation may vary depending on your system and CUDA availability. Refer to the official [PyTorch installation guide](https://pytorch.org/get-started/locally/).*

3. **Start the app:**

```bash
python app.py
```

Default server runs at: `http://127.0.0.1:5000`

---

## 📡 API Usage

### `/analyze` – Image Analysis

* **Method:** `POST`
* **Data:** `multipart/form-data`

  * `image_file`: Image file to analyze

**Example with curl:**

```bash
curl -X POST -F "image_file=@/path/to/image.jpg" http://127.0.0.1:5000/analyze
```

**Example with Python:**

```python
import requests, os

def analyze_image(image_path):
    url = "http://127.0.0.1:5000/analyze"
    with open(image_path, "rb") as f:
        files = {'image_file': (os.path.basename(image_path), f)}
        response = requests.post(url, files=files)
    return response.json()

# result = analyze_image("test_images/safe.jpg")
# print(result)
```

**Sample Outputs:**

Safe image:

```json
{
  "drawings": 0.05,
  "gore": 0.01,
  "hentai": 0.08,
  "neutral": 0.75,
  "porn": 0.10,
  "sexy": 0.02
}
```

NSFW image:

```json
{
  "drawings": 0.02,
  "gore": 0.03,
  "hentai": 0.11,
  "neutral": 0.15,
  "porn": 0.80,
  "sexy": 0.75
}
```

Gore image:

```json
{
  "drawings": 0.01,
  "gore": 0.95,
  "hentai": 0.01,
  "neutral": 0.20,
  "porn": 0.05,
  "sexy": 0.03
}
```

Corrupted file:

```json
{
  "error": "Unrecognized or corrupted image file"
}
```

---

### `/analyze_video` – Video Analysis

* **Method:** `POST`
* **Data:** `multipart/form-data`

  * `video_file`: Video file to analyze

**Example with curl:**

```bash
curl -X POST -F "video_file=@/path/to/video.mp4" http://127.0.0.1:5000/analyze_video
```

**Sample Outputs:**

Safe video:

```json
{
  "status": "safe",
  "analyzed_frames": 150,
  "first_issue_at_second": null
}
```

Unsafe video (stops at first unsafe frame):

```json
{
  "status": "unsafe",
  "analyzed_frames": 65,
  "first_issue_at_second": 2.60
}
```

Corrupted video:

```json
{
  "error": "Video file could not be opened or is corrupted."
}
```

---

## 🧪 Testing

Run the included test script:

```bash
python tests/test_api.py
```

This uses sample images in `test_images/` to validate the API.

---

## ☁️ Deployment (Railway)

1. Push project to a Git repo (e.g., GitHub)
2. Create a new project on **Railway** and connect your repo
3. Railway detects the `Procfile`:

```Procfile
web: gunicorn app:app
```

4. Dependencies installed from `requirements.txt`
5. Python version from `runtime.txt`

Railway automatically builds & deploys the app, then provides a public URL.

---

## 📄 License

MIT License

---
