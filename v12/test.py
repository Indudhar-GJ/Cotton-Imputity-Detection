from ultralytics import YOLO

# Load the trained model
model_path = "/home/cotseeds11/Desktop/v12/yolov8-seg-bounding-box-v12-8.pt"  # Update this with your model path
model = YOLO(model_path)

# Path to test dataset
test_data = "/home/cotseeds11/Desktop/v12/data.yaml"  # Update this with your dataset path

# Run evaluation
metrics = model.val(data=test_data)  # Evaluate model on the test set

# Print metrics
print("Model Metrics:")
print(metrics)
