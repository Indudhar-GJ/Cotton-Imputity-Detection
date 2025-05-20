import torch
from ultralytics import YOLO

# Check if CUDA is available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Load the model trained on bounding boxes to continue training on segmentation
model = YOLO("/home/ar/Desktop/ctn-hybrid/hybrid-seg/runs/detect/train3/weights/best.pt")  # Use the previously trained model

# Define training parameters for segmentation
train_args = {
    "data": "/home/ar/Desktop/ctn-hybrid/hybrid-seg/data.yaml",  # Path to segmentation dataset
    "epochs": 100,  
    "imgsz": 512,  
    "batch": 16,  
    "lr0": 0.0008,  
    "lrf": 0.0005,  
    "momentum": 0.937,  
    "weight_decay": 0.0005,  
    "warmup_epochs": 5,  
    "warmup_momentum": 0.8,  
    "warmup_bias_lr": 0.1,  
    "device": device
}

# Train the model on segmentation data
results = model.train(**train_args)

# Validate model performance
metrics = model.val()
print("Validation Metrics:", metrics)

# Save the newly trained model
model_path = "yolov8-seg-bounding-box4.pt"
model.save(model_path)
print(f"Trained segmentation model saved at {model_path}")
