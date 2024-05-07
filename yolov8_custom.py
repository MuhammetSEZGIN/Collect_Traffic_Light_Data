from ultralytics import YOLO
from pathlib import Path
import cv2

modelpath=Path('yolov8s.pt')
imagepath=Path('valid/images/0_jpg.rf.1544ac3eb9d8141db4561a55756a4a72.jpg')

model=YOLO(modelpath)

results = model(imagepath)


"""
cv2.imshow('YOLO', results.imgs[0])
"""


