import os
import torch
import onnxruntime
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import numpy as np
import cv2
from ultralytics import YOLO

# Load and preprocess an image
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (640, 640))  # Resize to match YOLO input size
    image = image[:, :, ::-1]  # Convert BGR to RGB
    image = image / 255.0  # Normalize to [0,1]
    image = np.transpose(image, (2, 0, 1))  # HWC -> CHW
    return np.expand_dims(image, axis=0).astype(np.float32)  # Add batch dimension

# 1️⃣ PyTorch Inference
def infer_pytorch(model, image):
    with torch.no_grad():
        output = model(torch.tensor(image, dtype=torch.float32))
    return output[0].numpy()

# 2️⃣ ONNX Inference
def infer_onnx(session, image):
    output = session.run(None, {"images": image})
    return output[0]

# 3️⃣ TensorRT Inference
def infer_tensorrt(context, d_input, d_output, stream, image, output_shape):
    cuda.memcpy_htod_async(d_input, image, stream)
    context.execute_async_v2([int(d_input), int(d_output)], stream.handle, None)
    output_trt = np.empty(output_shape, dtype=np.float32)
    cuda.memcpy_dtoh_async(output_trt, d_output, stream)
    stream.synchronize()
    return output_trt

# Load models
model_pt = YOLO("/home/ar/Desktop/ctn-hybrid/hybrid-seg/yolov8-seg-bounding-box3.pt")
session_onnx = onnxruntime.InferenceSession("/home/ar/Desktop/ctn-hybrid/hybrid-seg/yolov8-seg-bounding-box3.onnx")

# Load TensorRT engine
TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
runtime = trt.Runtime(TRT_LOGGER)
with open("/home/ar/Desktop/ctn-hybrid/hybrid-seg/yolov8-seg-bounding-box3-fp16.engine", "rb") as f:
    engine = runtime.deserialize_cuda_engine(f.read())
context = engine.create_execution_context()

# Allocate memory for TensorRT
input_shape = (1, 3, 640, 640)
output_shape = (1, 84, 8400)  # Adjust based on YOLO version
d_input = cuda.mem_alloc(np.prod(input_shape) * np.float32().nbytes)
d_output = cuda.mem_alloc(np.prod(output_shape) * np.float32().nbytes)
stream = cuda.Stream()

# Process multiple images
image_folder = "/home/ar/Desktop/ctn-hybrid/hybrid-seg/test/images"
image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(".jpg")]

diffs_onnx, diffs_trt = [], []

for image_path in image_files:
    image = preprocess_image(image_path)

    output_pt = infer_pytorch(model_pt, image)
    output_onnx = infer_onnx(session_onnx, image)
    output_trt = infer_tensorrt(context, d_input, d_output, stream, image, output_shape)

    diff_onnx = np.mean(np.abs(output_pt - output_onnx))
    diff_trt = np.mean(np.abs(output_pt - output_trt))

    diffs_onnx.append(diff_onnx)
    diffs_trt.append(diff_trt)

    print(f"Image: {os.path.basename(image_path)}")
    print(f"🔹 ONNX vs PyTorch Difference: {diff_onnx:.6f}")
    print(f"🔹 TensorRT vs PyTorch Difference: {diff_trt:.6f}\n")

# Compute overall accuracy loss
mean_diff_onnx = np.mean(diffs_onnx)
mean_diff_trt = np.mean(diffs_trt)

print("📊 Final Accuracy Evaluation:")
print(f"✅ Average ONNX vs PyTorch Difference: {mean_diff_onnx:.6f}")
print(f"✅ Average TensorRT vs PyTorch Difference: {mean_diff_trt:.6f}")

if mean_diff_trt < 0.01:
    print("🚀 TensorRT conversion is accurate!")
else:
    print("⚠️ Significant accuracy drop detected. Consider re-exporting ONNX or tweaking TensorRT settings.")
