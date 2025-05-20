from ultralytics import YOLO

model = YOLO("/home/ar/Desktop/ctn-hybrid/hybrid-seg/yolov8-seg-bounding-box3-int8.engine")
print(model.names)  # Should list all 7 classes

