from ultralytics import YOLO
import torch
from ultralytics.engine.results import Boxes
# Load a model
model = YOLO("/media/cotseeds11/FreeAgent Drive/ctn-hybrid/hybrid-seg/yolov8-seg-bounding-box4-int8.engine",task="detect")  # pretrained YOLO11n model

allowed_classes = torch.tensor([0,3,4,5,6]) 
# Run batched inference on a list of images
results = model(["a.png", "a.png", "a.png", "a.png", "a.png", "a.png", "a.png", "a.png", "a.png", "a.png", "a.png", "a.png", "a.png", "a.png", "a.png", "a.png"],imgsz=512)  # return a list of Results objects
# Process results list
# for result in results:
#     boxes = result.boxes  # Boxes object for bounding box outputs
#     filtered_boxes = []
#     for box in boxes:
#         class_id = int(box.cls)
#         if class_id in allowed_classes:
#             filtered_boxes.append(box) 
#     result.boxes = filtered_boxes
#     masks = result.masks  # Masks object for segmentation masks outputs
#     keypoints = result.keypoints  # Keypoints object for pose outputs
#     probs = result.probs  # Probs object for classification outputs
#     obb = result.obb  # Oriented boxes object for OBB outputs
#     # print("box.cls :",box.cls)
#     # print("box.cls[0].item() :",box.cls[0].item())

#     result.show()  # display to screen
#     print("boxes ", boxes)
#     result.save(filename="result.jpg")  # save to disk

thread_count=0
for i, result in enumerate(results):
    tile_results = []   
    for box in result.boxes:
        x_min, y_min, x_max, y_max = box.xyxy[0].tolist()
        confidence_score = box.conf[0].item()
        class_score = int(box.cls[0].item())  # Convert class index to int

        # Filter out unwanted classes
        if confidence_score >= 0.1 and class_score in allowed_classes:
            box_data = [int(x_min), int(y_min), int(x_max), int(y_max)]
            tile_results.append((box_data, confidence_score, class_score))
            thread_count += 1

    print("thread_count :",thread_count)
    # tile_results.plot()
    print("tile_results :",tile_results)
