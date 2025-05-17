# -- coding: utf-8 --

from PyQt5.QtWidgets import *
from CamOperation_class import CameraOperation
from MvCameraControl_class import *
from MvErrorDefine_const import *
from CameraParams_header import *
from PyUICBasicDemo import Ui_MainWindow
import time
from threading import Thread, Event
import threading
from queue import Queue, Empty
import os
from concurrent.futures import ThreadPoolExecutor
import serial
from ultralytics import YOLO
import cv2
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import uuid
import glob
import datetime
import atexit

timer_queue = Queue()
stop_timer = Event()
thread_count = 0
def write_to_file():
    with open("results_count1.txt", "a") as file:
        file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Threads Detected: {thread_count}\n")        
atexit.register(write_to_file)

class ImageDetector:
    def __init__(self, model_path, img_size=512, confidence_threshold=0.5):
        self.model = YOLO(model_path,task="detect")
        self.img_size = img_size
        self.confidence_threshold = confidence_threshold

    def preprocess_tile(self, tile_image):
        tile_array = cv2.resize(tile_image, (self.img_size, self.img_size))
        return tile_array
        
    def process_tiles(self, tiles):
        results = self.model(tiles, imgsz=self.img_size, verbose=False)
        all_results = []
        tiles_with_impurities = []
        global thread_count

        # Index of classes that should be detected
        allowed_classes = {0, 3, 4, 5}
        for i, result in enumerate(results):
            tile_results = []
            for box in result.boxes:
                x_min, y_min, x_max, y_max = box.xyxy[0].tolist()
                confidence_score = box.conf[0].item()
                class_score = box.cls[0].item()

                if confidence_score >= self.confidence_threshold and class_score in allowed_classes:
                    box_data = [int(x_min), int(y_min), int(x_max), int(y_max)]
                    tile_results.append((box_data, confidence_score, int(class_score)))
                    thread_count += 1
            all_results.append(tile_results)
            if tile_results:
                tiles_with_impurities.append(i)

                unique_id = str(uuid.uuid4())   
                filename = f"result_{unique_id}.jpg"
                
        return all_results
		  


def split_image_fast(image_path, tile_size):
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    tiles = [image[:, x:x+tile_size] for x in range(0, width, tile_size)]
    return tiles

# Get the index of the selected device information by parsing the characters between []
def TxtWrapBy(start_str, end, all):
    start = all.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = all.find(end, start)
        if end >= 0:
            return all[start:end].strip()
            
def decimal_to_hex_concat(dec_list):
    # Ensure the list contains numbers from 1 to 16, filling gaps with 0000
    present_numbers = set(dec_list)
    hex_list = [format(i, '04X') if i in present_numbers else '0000' for i in range(1, 17)]
    
    # Concatenate the hexadecimal values
    result = ''.join(hex_list)
    return result
    
# Convert the returned error code to hexadecimal display
def ToHexStr(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2 ** 32
    while num >= 16:
        digit = num % 16
        hexStr = chaDic.get(digit, str(digit)) + hexStr
        num //= 16
    hexStr = chaDic.get(num, str(num)) + hexStr
    return hexStr

if __name__ == "__main__":
    global deviceList
    deviceList = MV_CC_DEVICE_INFO_LIST()
    global cam
    cam = MvCamera()
    global nSelCamIndex
    nSelCamIndex = 0
    global obj_cam_operation
    obj_cam_operation = 0
    global isOpen
    isOpen = False
    global isGrabbing
    isGrabbing = False
    global isCalibMode  # Is it calibration mode (get original image)
    isCalibMode = True
    
    tile_list = []
    counter = 0
    T = 4.0
    t = 0.8
    # Bind the dropdown list to the device information index
    def xFunc(event):
        global nSelCamIndex
        nSelCamIndex = TxtWrapBy("[", "]", ui.ComboDevices.get())

    # Enumerate devices
    def enum_devices():
        global deviceList
        global obj_cam_operation

        deviceList = MV_CC_DEVICE_INFO_LIST()
        ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, deviceList)
        if ret != 0:
            strError = "Enum devices fail! ret = :" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
            return ret

        if deviceList.nDeviceNum == 0:
            QMessageBox.warning(mainWindow, "Info", "Find no device", QMessageBox.Ok)
            return ret
        print("Find %d devices!" % deviceList.nDeviceNum)

        devList = []
        for i in range(0, deviceList.nDeviceNum):
            mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
                print("\nGigE device: [%d]" % i)
                chUserDefinedName = ""
                for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName:
                    if 0 == per:
                        break
                    chUserDefinedName = chUserDefinedName + chr(per)
                print("Device user define name: %s" % chUserDefinedName)

                chModelName = ""
                for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                    if 0 == per:
                        break
                    chModelName = chModelName + chr(per)

                print("Device model name: %s" % chModelName)

                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                print("Current IP: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
                devList.append(
                    "[" + str(i) + "]GigE: " + chUserDefinedName + " " + chModelName + "(" + str(nip1) + "." + str(
                        nip2) + "." + str(nip3) + "." + str(nip4) + ")")
            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                print("\nU3V device: [%d]" % i)
                chUserDefinedName = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName:
                    if per == 0:
                        break
                    chUserDefinedName = chUserDefinedName + chr(per)
                print("Device user define name: %s" % chUserDefinedName)

                chModelName = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                    if 0 == per:
                        break
                    chModelName = chModelName + chr(per)
                print("Device model name: %s" % chModelName)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print("User serial number: %s" % strSerialNumber)
                devList.append("[" + str(i) + "]USB: " + chUserDefinedName + " " + chModelName
                               + "(" + str(strSerialNumber) + ")")

        ui.deviceInfoLabel.setText(devList[0])

    # Open device
    def open_device():
        global deviceList
        global nSelCamIndex
        global obj_cam_operation
        global isOpen
        if isOpen:
            QMessageBox.warning(mainWindow, "Error", 'Camera is Running!', QMessageBox.Ok)
            return MV_E_CALLORDER

        nSelCamIndex = 0
        if nSelCamIndex == -1:
            QMessageBox.warning(mainWindow, "Error", 'Please select a camera!', QMessageBox.Ok)
            return MV_E_CALLORDER

        obj_cam_operation = CameraOperation(cam, deviceList, 0)
        ret = obj_cam_operation.Open_device()
        if 0 != ret:
            strError = "Open device failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
            isOpen = False
        else:
            #set_continue_mode()
            set_trigger_mode()
            set_param()

            isOpen = True
            enable_controls()

    # Start grabbing image
    def start_grabbing():
        global obj_cam_operation
        global isGrabbing
        global stop_thread
        global thread
        ret = obj_cam_operation.Start_grabbing(ui.widgetDisplay.winId())
        if ret != 0:
            strError = "Start grabbing failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        else:
            isGrabbing = True
            enable_controls()
            stop_thread = False
            thread = threading.Thread(target=trigger_once)
            thread.start()

    # Stop grabbing image
    def stop_grabbing():
        global obj_cam_operation
        global isGrabbing
        global stop_thread
        ret = obj_cam_operation.Stop_grabbing()
        if ret != 0:
            strError = "Stop grabbing failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        else:
            isGrabbing = False
            stop_thread = True
            enable_controls()

    def send_to_PLC(detected_tiles, arduino, delay):
        hex_bytes = bytes.fromhex(detected_tiles)
        print(f"Sending to PLC")
        arduino.write(hex_bytes)

    def trigger_once():
        global stop_thread
        global detector
        global counter
        folder_path = "images"
        image_extension = "*.bmp"

        try:
            while True:
                if stop_thread:
                    break
                image_files = []
                if not any(os.scandir('images')):
                    ret = obj_cam_operation.Trigger_once()
                    pic_click_time = time.time()
                    if ret != 0:
                        strError = f"TriggerSoftware failed ret: {ToHexStr(ret)}"
                        print(strError)
                    while not any(os.scandir('images')):
                        pass
                else:
                    image_files.extend(glob.glob(os.path.join(folder_path, image_extension)))
                    image_path = image_files[0]
                    time.sleep(0.1)

                    try:
                        tiles = split_image_fast(image_path, 512)
                        with ThreadPoolExecutor() as executor:
                            preprocessed_tiles = list(executor.map(detector.preprocess_tile, tiles))
                            start_time = time.time()
                            batch_results = detector.process_tiles(preprocessed_tiles)
                            end_time = time.time()
                        
                        print(f"Inference execution time: {end_time - start_time} seconds")
                        detected_tiles = [idx +1 for idx, results in enumerate(batch_results) if results]
                        
                        print(detected_tiles)
                        
                        if detected_tiles:
                            hex_string = decimal_to_hex_concat(detected_tiles)
                            print(hex_string)
                            send_to_PLC(hex_string, arduino, 0)
                        os.remove(image_path)
                    
                    except Exception as e:
                        print(f"Error processing image {image_path}: {e}")
        
        finally:
            stop_timer.set()
            

    thread = None
    stop_thread = False        

    # Refresh device
    def refresh_device():
        close_device()
        enum_devices()
        open_device()

    # Close device
    def close_device():
        global isOpen
        global isGrabbing
        global obj_cam_operation

        if isOpen:
            obj_cam_operation.Close_device()
            isOpen = False

        isGrabbing = False

        enable_controls()

    # Set continuous trigger mode
    def set_continue_mode():
        strError = None
        ret = obj_cam_operation.Set_trigger_mode(False)
        if ret != 0:
            strError = "Set continue mode failed ret:" + ToHexStr(ret) + " mode is " + str(is_trigger_mode)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)  

    # Set continuous trigger mode
    def set_trigger_mode():
        strError = None
        ret = obj_cam_operation.Set_trigger_mode(True)
        if ret != 0:
            strError = "Set trigger mode failed ret:" + ToHexStr(ret) + " mode is " + str(is_trigger_mode)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)          

    # Save image
    def save_bmp():
        ret = obj_cam_operation.Save_Bmp()
        if ret != MV_OK:
            strError = "Save BMP failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        else:
            print("Save image success")

    # Set parameters
    def set_param():
        ret = obj_cam_operation.Set_parameter()
        if ret != MV_OK:
            strError = "Set param failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return MV_OK

    # Set control status
    def enable_controls():
        global isGrabbing
        global isOpen
        ui.bnStart.setEnabled(isOpen and (not isGrabbing))
        ui.bnStop.setEnabled(isOpen and isGrabbing)


    # Initialize app, bind UI and API
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)

    #bounding box + segment recall model
    #detector = ImageDetector("/home/cotseeds/Desktop/Cotseeds_Final/Code/int8_model_recall.engine", 512)
    #detector = ImageDetector("/home/cotseeds/Desktop/Cotseeds_Final/Code/fp16_model_recall.engine", 512)
    #bounding box + segment precision model
    detector = ImageDetector("/home/cotseeds/Desktop/Cotseeds_Final/Code/int8_model_precision.engine", 512)
    #detector = ImageDetector("/home/cotseeds/Desktop/Cotseeds_Final/Code/fp16_model_precision.engine", 512)
    # Remove references to bnEnum, bnOpen, bnClose
    # (These buttons are no longer part of the UI)
    ui.bnStart.clicked.connect(start_grabbing)
    ui.bnStop.clicked.connect(stop_grabbing)
    ui.bnRefresh.clicked.connect(refresh_device)

    serial_port = "/dev/ttyUSB0"
    baud_rate = 115200
    arduino = serial.Serial(serial_port, baud_rate)
    time.sleep(2)

    # Automatically enumerate and open the first device at startup
    enum_devices()
    if deviceList.nDeviceNum > 0:
        open_device()  # Open the selected device
    else:
        QMessageBox.warning(mainWindow, "Info", "No devices found. Please connect a camera and try again.", QMessageBox.Ok)

        
    mainWindow.show()
    app.exec_()

    close_device()
    sys.exit()
