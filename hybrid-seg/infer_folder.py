import os
import cv2
import numpy as np
from ultralytics import YOLO

# Define input and output folders
input_folder = "/home/ar/Desktop/ctn-hybrid/hybrid-seg/test/images"
output_folder = "/home/ar/Desktop/ctn-hybrid/hybrid-seg/output_img2"
os.makedirs(output_folder, exist_ok=True)

# Load the YOLO model
model = YOLO("/home/ar/Desktop/ctn-hybrid/hybrid-seg/yolov8-seg-bounding-box3-int8.engine", task="detect")

# Get list of images in the input folder
image_files = [f for f in os.listdir(input_folder) if f.endswith(('.jpg', '.png'))]
image_paths = [os.path.join(input_folder, f) for f in image_files]

# Define batch size to match TensorRT optimization profile
batch_size = 16  # Since TensorRT supports up to 16 images in one batch

# Process images in batches
for i in range(0, len(image_paths), batch_size):
    batch = image_paths[i:i + batch_size]  # Get a batch of 16 or fewer images
    results = model(batch, imgsz=512)  # Run inference on the batch
    
    for img_path, result in zip(batch, results):
        # Load original image
        img = cv2.imread(img_path)
        
        # Draw results on image
        result_img = result.plot()
        
        # Combine original and predicted images side by side
        combined_img = np.hstack((img, result_img))
        
        # Save combined image
        output_path = os.path.join(output_folder, os.path.basename(img_path))
        cv2.imwrite(output_path, combined_img)
        
print("Processing complete. Combined images saved in output folder.")
