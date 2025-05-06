# NSFW + Gore Tespit Servisi

Bu proje, bir görüntüdeki Uygunsuz İçerik (NSFW) ve Kan/Vahşet (Gore) içeriğini tespit etmek için açık kaynaklı bir model kullanan bir Flask API'sidir.

## Özellikler

-   Resimlerde NSFW (Pornografi, Hentai, Müstehcen) tespiti
-   Resimlerde Gore (Kan/Vahşet) tespiti
-   Doğrudan dosya yükleme ile kolay entegrasyon

## Kurulum ve Yerel Çalıştırma

1.  **Depoyu klonlayın:**
    ```bash
    git clone <depo_adresi>
    cd Image-Service
    ```

2.  **Gerekli kütüphaneleri yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
    *Not: PyTorch kurulumu sisteminize ve CUDA durumunuza göre değişiklik gösterebilir. Resmi PyTorch [kurulum talimatlarına](https://pytorch.org/get-started/locally/) göz atın.*

3.  **Uygulamayı başlatın:**
    ```bash
    python app.py
    ```
    Uygulama varsayılan olarak `http://127.0.0.1:5000` adresinde çalışacaktır.

## API Kullanımı

### `/analyze`

Resim analizi için ana endpoint.

-   **Method:** `POST`
-   **Veri:** `multipart/form-data`
    -   `image_file`: Analiz edilecek resim dosyası.

**Örnek `curl` isteği:**

```bash
curl -X POST -F "image_file=@/path/to/your/image.jpg" http://127.0.0.1:5000/analyze
```

**Örnek Python ile istek:**

(Bkz: `tests/test_api.py` içerisindeki `test_nsfw_gore` fonksiyonu)

```python
import requests
import os

def analyze_image(image_path):
    url = "http://127.0.0.1:5000/analyze"
    try:
        with open(image_path, "rb") as f:
            files = {'image_file': (os.path.basename(image_path), f)}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Hatası: {response.status_code} - {response.text}"}
    except FileNotFoundError:
        return {"error": f"Dosya bulunamadı: {image_path}"}
    except Exception as e:
        return {"error": f"İstek sırasında bir hata oluştu: {str(e)}"}

# Kullanım
# result = analyze_image("test_images/safe.jpg")
# print(result)
```

**Örnek Çıktılar:**

*   Güvenli bir resim için:
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

*   Uygunsuz (NSFW) içerik barındıran bir resim için:
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
*   Kan/Vahşet (Gore) içeren bir resim için:
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
*   Hatalı veya bozuk bir resim dosyası için:
    ```json
    {
      "error": "Resim dosyası bozuk veya tanınamayan formatta: cannot identify image file <_io.BytesIO object at 0x...>"
    }
    ```

### `/analyze_video`

Video analizi için endpoint.

-   **Method:** `POST`
-   **Veri:** `multipart/form-data`
    -   `video_file`: Analiz edilecek video dosyası.

**Örnek `curl` isteği:**

```bash
curl -X POST -F "video_file=@/path/to/your/video.mp4" http://127.0.0.1:5000/analyze_video
```

**Örnek Çıktılar:**

*   Tamamı güvenli bir video için:
    ```json
    {
      "status": "güvenli",
      "analyzed_frames": 150,
      "first_issue_at_second": null
    }
    ```

*   Sakıncalı içerik bulunan bir video için (ilk sakıncalı karede analiz durur):
    ```json
    {
      "status": "sakıncalı",
      "analyzed_frames": 65,
      "first_issue_at_second": 2.60
    }
    ```
*   Açılamayan veya bozuk bir video dosyası için:
    ```json
    {
      "error": "Video dosyası açılamadı veya bozuk."
    }
    ```

## Testler

API'yi test etmek için `tests/test_api.py` scriptini kullanabilirsiniz:

```bash
python tests/test_api.py
```
Bu script, `test_images` klasöründeki örnek resimleri kullanarak API'yi test eder.

## Railway'e Dağıtım

Bu proje Railway'e dağıtım için yapılandırılmıştır.

1.  Projenizi bir Git deposuna yükleyin (örneğin GitHub).
2.  Railway'de yeni bir proje oluşturun ve Git deponuzu bağlayın.
3.  Railway, `Procfile` dosyasını algılayarak uygulamayı otomatik olarak başlatacaktır:
    ```Procfile
    web: gunicorn app:app
    ```
4.  Gerekli bağımlılıklar `requirements.txt` dosyasından yüklenecektir.
5.  Python sürümü için `runtime.txt` dosyası kullanılabilir.

Railway, dağıtım sürecini otomatik olarak yönetecektir. Dağıtım tamamlandığında, size uygulamanız için genel bir URL sağlayacaktır. 