import cv2
import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit

# Load TensorRT engine
def load_engine(engine_path):
    TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
    with open(engine_path, "rb") as f, trt.Runtime(TRT_LOGGER) as runtime:
        return runtime.deserialize_cuda_engine(f.read())

# Allocate buffers for inference
def allocate_buffers(engine):
    inputs, outputs, bindings = [], [], []
    stream = cuda.Stream()
    for binding in engine:
        size = trt.volume(engine.get_binding_shape(binding)) * np.dtype(np.float32).itemsize
        dtype = trt.nptype(engine.get_binding_dtype(binding))
        host_mem = cuda.pagelocked_empty(size, dtype)
        device_mem = cuda.mem_alloc(host_mem.nbytes)
        bindings.append(int(device_mem))
        if engine.binding_is_input(binding):
            inputs.append({'host': host_mem, 'device': device_mem})
        else:
            outputs.append({'host': host_mem, 'device': device_mem})
    return inputs, outputs, bindings, stream

# Perform inference
def infer(context, inputs, outputs, bindings, stream):
    [cuda.memcpy_htod_async(inp['device'], inp['host'], stream) for inp in inputs]
    context.execute_async_v2(bindings, stream.handle, None)
    [cuda.memcpy_dtoh_async(out['host'], out['device'], stream) for out in outputs]
    stream.synchronize()
    return [out['host'] for out in outputs]

# Preprocess camera frame
def preprocess_frame(frame, input_shape):
    frame_resized = cv2.resize(frame, (input_shape[1], input_shape[2]))
    frame_transposed = frame_resized.transpose((2, 0, 1))
    return np.ascontiguousarray(frame_transposed, dtype=np.float32) / 255.0

# Load TensorRT engine
engine_path = "/home/cotseeds/Desktop/ctn-hybrid/hybrid-seg/yolov8-seg-bounding-box4-int8.engine"
engine = load_engine(engine_path)
context = engine.create_execution_context()
inputs, outputs, bindings, stream = allocate_buffers(engine)
input_shape = (3, 512, 512)  # Adjust according to your model

# Open camera
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Preprocess and set input
    inputs[0]['host'][:] = preprocess_frame(frame, input_shape).ravel()
    output = infer(context, inputs, outputs, bindings, stream)
    
    # Process and visualize output (Add your detection post-processing here)
    cv2.imshow("Object Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

