from ultralytics import YOLO

# Load the trained model
model_path = "/home/ar/Desktop/ctn-hybrid/hybrid-seg/runs/detect/train3/weights/last.pt"  # Update this with your model path
model = YOLO(model_path)

# Path to test dataset
test_data = "/home/ar/Desktop/ctn-hybrid/hybrid-seg/data.yaml"  # Update this with your dataset path

# Run evaluation
metrics = model.val(data=test_data)  # Evaluate model on the test set

# Print metrics
print("Model Metrics:")
print(metrics)
