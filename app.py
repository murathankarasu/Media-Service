from flask import Flask, request, jsonify
from utils.image_utils import load_image
from services.nsfw_gore_service import NSFWGoreClassifier
import os
import io
import cv2 # Video işleme için eklendi
import tempfile # Geçici dosyalar için eklendi
import numpy as np # OpenCV karelerini işlemek için eklendi
from PIL import Image # OpenCV karesini PIL Image'e dönüştürmek için eklendi

app = Flask(__name__)

# Firebase ve model başlatma
classifier = NSFWGoreClassifier()

@app.route('/')
def home():
    return 'NSFW + Gore Tespit Servisi Çalışıyor! (Firebase olmadan)'

@app.route('/analyze', methods=['POST'])
def analyze():
    pil_image = None
    image_bytes_io = None

    # Sadece doğrudan dosya yüklemesini kontrol et (multipart/form-data)
    if 'image_file' in request.files:
        image_file = request.files['image_file']
        if image_file.filename == '':
            return jsonify({"error": "Gönderilen dosya için bir dosya adı belirtilmedi."}), 400
        if not image_file:
            return jsonify({"error": "'image_file' ile dosya gönderilmedi veya dosya okunamadı."}), 400
        
        try:
            image_bytes = image_file.read()
            if not image_bytes:
                 return jsonify({"error": "Gönderilen dosya boş."}), 400
            image_bytes_io = io.BytesIO(image_bytes)
            print(f"[LOG] Doğrudan yüklenen dosya alındı ('{image_file.filename}'), boyut: {len(image_bytes)} bytes")
        except Exception as e:
            return jsonify({"error": f"Yüklenen dosya okunurken hata: {str(e)}"}), 500
    else:
        # Eğer dosya gelmediyse hata ver
        error_msg = "Analiz için 'image_file' (multipart/form-data içinde) sağlanmalı."
        return jsonify({"error": error_msg}), 400

    if image_bytes_io:
        try:
            pil_image = load_image(image_bytes_io)
            result = classifier.predict(pil_image)
            return jsonify(result)
        except Exception as e:
            if "cannot identify image file" in str(e).lower():
                 return jsonify({"error": f"Resim dosyası bozuk veya tanınamayan formatta: {str(e)}"}), 400
            return jsonify({"error": f"Resim işlenirken veya analiz edilirken hata: {str(e)}"}), 500
    else:
        return jsonify({"error": "Resim verisi işlenemedi veya alınamadı."}), 500

@app.route('/analyze_video', methods=['POST'])
def analyze_video():
    if 'video_file' not in request.files:
        return jsonify({"error": "'video_file' (multipart/form-data içinde) sağlanmalı."}), 400

    video_file = request.files['video_file']
    if video_file.filename == '':
        return jsonify({"error": "Gönderilen dosya için bir dosya adı belirtilmedi."}), 400
    
    temp_video_path = None
    try:
        # Videoyu geçici bir dosyaya kaydet
        # Sonek, OpenCV'nin dosyayı tanımasına yardımcı olabilir, ancak her zaman gerekli değildir
        temp_fd, temp_video_path = tempfile.mkstemp(suffix='.mp4') 
        video_file.save(temp_video_path)
        # tempfile.mkstemp bir dosya tanıtıcısı döndürür, bu yüzden kapatmamız gerekir.
        # OpenCV dosya yolunu kullanır.
        os.close(temp_fd)

        print(f"[LOG] Video dosyası geçici olarak şuraya kaydedildi: {temp_video_path}")

        cap = cv2.VideoCapture(temp_video_path)
        if not cap.isOpened():
            return jsonify({"error": "Video dosyası açılamadı veya bozuk."}), 400

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0: # FPS okunamıyorsa veya 0 ise (bazı formatlarda olabilir)
            fps = 25 # Varsayılan bir değer ata veya hata döndür
            print(f"[UYARI] Video FPS değeri okunamadı. Varsayılan olarak {fps} FPS kullanılıyor.")

        # Saniyede 1 kare analiz etmek için atlanacak kare sayısı
        frames_to_skip = int(fps) if fps > 0 else 1 

        frame_read_count = 0 # Okunan toplam kare sayısı
        analyzed_frame_count = 0 # Analiz edilen kare sayısı
        
        video_result = {
            "status": "güvenli", # Varsayılan durum
            "analyzed_frames": 0,
            "first_issue_at_second": None 
        }
        
        # Resim analizi için kullanılan eşik değerleri (ayarlanabilir)
        # Bu değerleri merkezi bir konfigürasyondan almak daha iyi olabilir.
        nsfw_threshold = 0.7 
        gore_threshold = 0.7

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break # Video sonu veya okuma hatası

            # Sadece her 'frames_to_skip' kareyi işle
            if frame_read_count % frames_to_skip == 0:
                analyzed_frame_count += 1
                current_time_sec = frame_read_count / fps if fps > 0 else analyzed_frame_count

                # OpenCV karesini (BGR) PIL Image'e (RGB) dönüştür
                try:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                except Exception as e:
                    print(f"[HATA] Kare PIL Image'e dönüştürülürken hata: {str(e)} (Kare: {analyzed_frame_count}, Zaman: {current_time_sec:.2f}s)")
                    continue # Bu kareyi atla

                try:
                    # Mevcut sınıflandırıcıyı kullanarak kareyi analiz et
                    result = classifier.predict(pil_image)
                    
                    nsfw_score = result.get("porn", 0) + result.get("sexy", 0) + result.get("hentai", 0)
                    gore_score = result.get("gore", 0)

                    is_nsfw = nsfw_score > nsfw_threshold
                    is_gore = gore_score > gore_threshold

                    if is_nsfw or is_gore:
                        video_result["status"] = "sakıncalı"
                        video_result["first_issue_at_second"] = round(current_time_sec, 2)
                        print(f"[LOG] Sakıncalı içerik {current_time_sec:.2f} saniyesinde tespit edildi. Video analizi durduruluyor.")
                        break # İlk sakıncalı karede analizi durdur
                except Exception as e:
                    print(f"[UYARI] Kare {analyzed_frame_count} (Zaman: {current_time_sec:.2f}s) analiz edilirken hata: {str(e)}")
                    # Hatalı kareyi atlayıp devam edebilir veya videoyu hatalı olarak işaretleyebiliriz.
                    # Şimdilik atlayıp devam edelim.

            frame_read_count += 1
        
        cap.release()
        video_result["analyzed_frames"] = analyzed_frame_count
        
        return jsonify(video_result)

    except Exception as e:
        # Genel hata yakalama
        print(f"[HATA] Video işlenirken genel hata: {str(e)}")
        return jsonify({"error": f"Video işlenirken bir hata oluştu: {str(e)}"}), 500
    finally:
        # Geçici dosyayı sil
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.remove(temp_video_path)
                print(f"[LOG] Geçici video dosyası silindi: {temp_video_path}")
            except Exception as e:
                print(f"[HATA] Geçici video dosyası {temp_video_path} silinirken hata: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True) 