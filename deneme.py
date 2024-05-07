from pathlib import Path
from ultralytics import YOLO

# Yolu doğru biçimde tanımla
modelpath = Path("best.pt")
imagepath = Path("dataset/train/images/0_jpg.rf.94bbc54de088e70ec81707eb61dbadfe.jpg")

# Modeli CPU üzerinde çalışacak şekilde yükle
model = YOLO(modelpath).to('gpu')
result = model(imagepath)
