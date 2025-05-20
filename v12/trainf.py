import torch
from ultralytics import YOLO

# Check if CUDA is available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Load the previous model for transfer learning
model = YOLO("/home/cotseeds11/Desktop/v12/yolov8-seg-bounding-box-v12-7.pt")

# Define optimized training parameters
train_args = {
    "data": "/home/cotseeds11/Desktop/v12/data.yaml",  # Path to segmentation dataset
    "epochs": 40,  # Increase epochs for better convergence
    "imgsz": 512,  # Higher resolution for better small object detection
    "batch": 16,  # Larger batch size for stability (adjust based on GPU memory)
    "lr0": 0.001,  # Slightly higher initial learning rate
    "lrf": 0.0001,  # Lower final learning rate for fine-tuning
    "momentum": 0.95,  # Slightly increased for better optimization
    "weight_decay": 0.0004,  # Reduce weight decay slightly
    "warmup_epochs": 3,  # Reduce warmup for faster adaptation
    "warmup_momentum": 0.9,  
    "warmup_bias_lr": 0.2,  
    "cos_lr": True,  # Use cosine learning rate schedule
    "device": device,
    "patience": 20,  # Early stopping patience
    "optimizer": "AdamW",  # AdamW can help with convergence
    "augment": True,  # Enable strong augmentations
    "hsv_h": 0.015,  # Color augmentations
    "hsv_s": 0.7,
    "hsv_v": 0.4,
    "flipud": 0.5,  # Vertical flip probability
    "fliplr": 0.5,  # Horizontal flip probability
    "degrees": 10,  # Rotation augmentation
    "translate": 0.1,  # Translate augmentation
    "scale": 0.5,  # Scale augmentation
    "shear": 2  # Shear augmentation
}

# Train the model
results = model.train(**train_args)

# Validate model performance
metrics = model.val()
print("Validation Metrics:", metrics)

# Save the newly trained model
model_path = "yolov8-seg-bounding-box-v12-8.pt"
model.save(model_path)
print(f"Trained segmentation model saved at {model_path}")
