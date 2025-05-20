from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO("/home/cotseeds11/Desktop/v12/yolov8-seg-bounding-box-v12-7.pt",task="detect")

# Export the model to TensorRT format
model.export(format="engine", half = True,imgsz=512, batch = 16,data="/home/cotseeds11/Desktop/v12/data.yaml")  # creates 'yolov8n.engine'

# Load the exported TensorRT model
#tensorrt_model = YOLO("best.engine")

# Run inference
#results = tensorrt_model("test.png", imgsz=512)


