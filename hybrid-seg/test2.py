import cv2
import os
from ultralytics import YOLO
import torch
# Paths
test_folder = "/home/cotseeds/Desktop/ctn-hybrid/hybrid-seg/test/images"
output_folder = "/home/cotseeds/Desktop/ctn-hybrid/hybrid-seg/output_img3"
model_path = "/home/cotseeds/Desktop/ctn-hybrid/hybrid-seg/yolov8-seg-bounding-box4.pt"

# Create output folder if not exists
os.makedirs(output_folder, exist_ok=True)

# Load YOLO model
model = YOLO(model_path)

# Process images
for image_name in os.listdir(test_folder):
    if image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(test_folder, image_name)
        
        # Read original image
        original = cv2.imread(image_path)

        # Run inference
        results = model(image_path)

        # # Get predicted image
        # pred_image = results[0].plot()  # YOLO's built-in function to draw detections

        result = results[0]
        allowed_classes = torch.tensor([0,3,4,5,6], device="cpu") 

        # Filter detections
        # filtered_boxes = result.boxes[result.boxes.cls.isin([0,3,4,5,6])]

        # mask = torch.isin(result.boxes.cls, allowed_classes)  # Correct way to filter
        # filtered_boxes = result.boxes[mask]  # Apply the mask

        # # Update result with filtered boxes
        # result.boxes = filtered_boxes  
        # pred_image = result.plot()
        cls_tensor = result.boxes.cls.cpu() 
        mask = torch.isin(cls_tensor, allowed_classes)  # Correct usage of isin()

#        Apply the mask to filter detections
        filtered_boxes = result.boxes[mask]

        # Update result with filtered boxes
        result.boxes = filtered_boxes  

        # Get predicted image (only with allowed classes)
        pred_image = result.plot()

        # Resize both images to the same height
        height = min(original.shape[0], pred_image.shape[0])
        original_resized = cv2.resize(original, (int(original.shape[1] * (height / original.shape[0])), height))
        pred_resized = cv2.resize(pred_image, (int(pred_image.shape[1] * (height / pred_image.shape[0])), height))

        # Concatenate horizontally
        combined = cv2.hconcat([original_resized, pred_resized])

        # Save output
        output_path = os.path.join(output_folder, image_name)
        cv2.imwrite(output_path, combined)

print("Processing complete. Check the output folder.")
