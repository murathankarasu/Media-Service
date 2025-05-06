import requests
import os

TEST_IMAGES = {
    "safe": "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
    "nsfw_placeholder": "https://upload.wikimedia.org/wikipedia/commons/6/65/NSFW_image_placeholder.png",
    "gore_warning": "https://upload.wikimedia.org/wikipedia/commons/6/6b/Gore_warning.png",
    "anime_girl": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Anime_girl.png"
}

def download_images():
    os.makedirs("test_images", exist_ok=True)
    for name, url in TEST_IMAGES.items():
        path = f"test_images/{name}.jpg"
        if not os.path.exists(path):
            print(f"İndiriliyor: {url}")
            r = requests.get(url)
            with open(path, "wb") as f:
                f.write(r.content)
    print("Tüm test görselleri indirildi.")

def test_nsfw_gore(image_path):
    url = "http://127.0.0.1:5000/analyze"
    try:
        with open(image_path, "rb") as f:
            files = {'image_file': (os.path.basename(image_path), f)}
            response = requests.post(url, files=files)
        
        # Yanıtın içeriğini kontrol etmeden önce durum kodunu kontrol et
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Sonuçlar: {result}")
            except requests.exceptions.JSONDecodeError:
                print(f"JSON decode hatası: {response.text}")
                return # Hata durumunda fonksiyondan çık
        else:
            print(f"API Hatası: {response.status_code} - {response.text}")
            return # Hata durumunda fonksiyondan çık

    except FileNotFoundError:
        print(f"Dosya bulunamadı: {image_path}")
        return # Hata durumunda fonksiyondan çık
    except Exception as e:
        print(f"İstek sırasında bir hata oluştu: {e}")
        return # Hata durumunda fonksiyondan çık

    # Eşik değerleri örnek olarak belirlenmiştir, ihtiyaca göre ayarlanabilir
    nsfw_threshold = 0.3
    gore_threshold = 0.3

    nsfw_score = result.get("porn", 0) + result.get("sexy", 0) + result.get("hentai", 0)
    gore_score = result.get("gore", 0)

    if nsfw_score > nsfw_threshold:
        print("Bu görselde çıplaklık/müstehcenlik tespit edildi!")
    if gore_score > gore_threshold:
        print("Bu görselde kan/vahşet tespit edildi!")
    if nsfw_score <= nsfw_threshold and gore_score <= gore_threshold:
        print("Görsel güvenli.")

if __name__ == "__main__":
    # download_images() # Bu satırı yorumluyoruz, yerel görseller kullanılacak
    # Burada test etmek istediğin pathleri güncelle
    test_paths = [
        "test_images/safe.jpg",
        "test_images/IMG_4771.JPG",
        "test_images/depositphotos_446964468-stock-photo-man-holding-knife-threatening-stance.jpg"
    ]
    for path in test_paths:
        print(f"\nTest ediliyor: {path}")
        test_nsfw_gore(path)
