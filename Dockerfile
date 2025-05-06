# Python'un resmi imajını temel al
FROM python:3.10.12-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Önbelleği ve gereksiz dosyaları temizlemek için ortam değişkenleri
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off 
ENV PIP_DISABLE_PIP_VERSION_CHECK=on 
ENV PIP_DEFAULT_TIMEOUT=100

# requirements.txt dosyasını kopyala ve bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# CLIP modelini Docker imajı oluşturulurken indir
# Bu, uygulamanın ilk başlatılmasında indirme süresini ortadan kaldırır.
RUN python -c "import clip; print(clip.load('ViT-B/32'))"

# Geri kalan uygulama kodunu kopyala
COPY . .

# Gunicorn'un Railway tarafından sağlanan PORT'u kullanması önemlidir.
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]

RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender1 