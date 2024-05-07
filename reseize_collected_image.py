from PIL import Image
import os

def resize_and_save_images(source_folder, target_folder, output_size=(800, 600)):
    # Kaynak klasördeki tüm dosyaları listele
    files = os.listdir(source_folder)

    # Her bir dosya için
    for file in files:
        # Dosyanın tam yolunu oluştur
        source_file_path = os.path.join(source_folder, file)
        
        # Hedef dosya yolu
        target_file_path = os.path.join(target_folder, file)
        
        # Dosyanın resim olup olmadığını kontrol et
        if source_file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                # Resmi aç
                with Image.open(source_file_path) as img:
                    # Resmi yeniden boyutlandır
                    resized_img = img.resize(output_size, Image.ANTIALIAS)
                    
                    # Resmi yeni klasöre kaydet
                    resized_img.save(target_file_path)
                    print(f"Resized {file} saved successfully in {target_folder}.")
            except Exception as e:
                print(f"Error resizing {file}: {e}")

# Fonksiyonu kullanarak bir klasördeki resimleri yeniden boyutlandır ve yeni bir klasöre kaydet
source_folder = r'C:\Yolov9_Train\high_quality_images\Yellow'
target_folder = r'C:\Yolov9_Train\resized_images'
resize_and_save_images(source_folder, target_folder)
