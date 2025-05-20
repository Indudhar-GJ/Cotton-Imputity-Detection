from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO("/home/cotseeds/Desktop/ctn-hybrid/hybrid-seg/runs/detect/train3/weights/best.pt",task="detect")

# Export the model to TensorRT format
model.export(format="engine", half = True,imgsz=512, batch = 16,data="/home/cotseeds/Desktop/ctn-hybrid/calib_ds/data.yaml")  # creates 'yolov8n.engine'

# Load the exported TensorRT model
#tensorrt_model = YOLO("best.engine")

# Run inference
#results = tensorrt_model("test.png", imgsz=512)


