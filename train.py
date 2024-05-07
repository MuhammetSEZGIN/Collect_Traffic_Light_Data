

from roboflow import Roboflow
from ultralytics import YOLO

# Roboflow API anahtarınız ve proje ID'niz
rf = Roboflow(api_key="YOUR_ROBOFLOW_API_KEY")
project = rf.workspace().project("Exk7qTDPwTgxAhmPjG7F")

# Veri setini indir
dataset = project.version(1).download("yolov8")

# Eğitim konfigürasyonunu ayarla
model = YOLO(pretrained="yolov8n.pt", classes=len(dataset.names))

# Modeli eğit
model.fit(data=dataset.location, batch_size=16, epochs=50, device="cuda")

# Modeli kaydet
model.save("trained_yolov8.pt")

print("Model eğitimi tamamlandı ve 'trained_yolov8.pt' olarak kaydedildi.")

