from PIL import Image
# from services.nsfw_gore_service import NSFWGoreClassifier # Bu satırı yorumluyoruz veya siliyoruz, çünkü sys.path ayarından sonra import edilecek
import os
import sys # sys modülünü import ediyoruz

# Proje ana dizinini Python path'ine ekliyoruz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.nsfw_gore_service import NSFWGoreClassifier # Şimdi import ediyoruz

def test_local_image(image_path):
    """
    Yerel bir görseli NSFWGoreClassifier ile test eder.
    """
    # Proje ana dizinine göre yolu düzelt -> Script ana dizinden çalıştırıldığı için direkt image_path kullanılabilir.
    full_image_path = image_path # os.path.join("..", image_path) yerine direkt image_path
    
    if not os.path.exists(full_image_path):
        print(f"[HATA] Görsel bulunamadı: {full_image_path}")
        return

    try:
        # Modeli başlat
        # NSFWGoreClassifier, services klasöründe olduğu için sys.path ayarlaması gerekebilir
        # Eğer ModuleNotFoundError alırsanız, aşağıdaki iki satırı aktif edin:
        # import sys
        # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        # from services.nsfw_gore_service import NSFWGoreClassifier
        
        classifier = NSFWGoreClassifier()
        print(f"[BİLGİ] NSFWGoreClassifier başarıyla başlatıldı.")

        # Görseli yükle (PIL Image objesi olarak)
        pil_image = Image.open(full_image_path)
        print(f"[BİLGİ] Görsel yüklendi: {full_image_path}")

        # Tahmin yap
        result = classifier.predict(pil_image)
        print(f"[SONUÇ] '{os.path.basename(image_path)}' için tahmin: {result}")

    except ModuleNotFoundError:
        print("[HATA] services.nsfw_gore_service modülü bulunamadı.")
        print("Lütfen test_local_model.py dosyasını projenizin ana dizininden çalıştırdığınızdan emin olun")
        print("veya script içindeki sys.path yorumlarını kaldırıp tekrar deneyin.")
    except Exception as e:
        print(f"[HATA] '{os.path.basename(image_path)}' testi sırasında bir hata oluştu: {e}")

if __name__ == '__main__':
    # test_api.py dosyasında kullanılan görseller
    images_to_test = [
        "test_images/safe.jpg",
        "test_images/IMG_4771.JPG",
        "test_images/depositphotos_446964468-stock-photo-man-holding-knife-threatening-stance.jpg"
    ]

    print(f"Yerel model testi başlatılıyor...")
    for image_file in images_to_test:
        print(f"\n--- Test ediliyor: {image_file} ---")
        test_local_image(image_file) 