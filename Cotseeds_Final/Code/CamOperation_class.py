# -- coding: utf-8 --
import sys
import threading
import numpy as np
import time
import sys, os
import datetime
import inspect
import ctypes
import random
from ctypes import *

sys.path.append("../MvImport")

from CameraParams_header import *
from MvCameraControl_class import *

# 强制关闭线程
def Async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


# 停止线程
def Stop_thread(thread):
    Async_raise(thread.ident, SystemExit)


# 转为16进制字符串
def To_hex_str(num):
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


# 是否是Mono图像
def Is_mono_data(enGvspPixelType):
    if PixelType_Gvsp_Mono8 == enGvspPixelType or PixelType_Gvsp_Mono10 == enGvspPixelType \
            or PixelType_Gvsp_Mono10_Packed == enGvspPixelType or PixelType_Gvsp_Mono12 == enGvspPixelType \
            or PixelType_Gvsp_Mono12_Packed == enGvspPixelType:
        return True
    else:
        return False


# 是否是彩色图像
def Is_color_data(enGvspPixelType):
    if PixelType_Gvsp_BayerGR8 == enGvspPixelType or PixelType_Gvsp_BayerRG8 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB8 == enGvspPixelType or PixelType_Gvsp_BayerBG8 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR10 == enGvspPixelType or PixelType_Gvsp_BayerRG10 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB10 == enGvspPixelType or PixelType_Gvsp_BayerBG10 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR12 == enGvspPixelType or PixelType_Gvsp_BayerRG12 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB12 == enGvspPixelType or PixelType_Gvsp_BayerBG12 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR10_Packed == enGvspPixelType or PixelType_Gvsp_BayerRG10_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGB10_Packed == enGvspPixelType or PixelType_Gvsp_BayerBG10_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGR12_Packed == enGvspPixelType or PixelType_Gvsp_BayerRG12_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGB12_Packed == enGvspPixelType or PixelType_Gvsp_BayerBG12_Packed == enGvspPixelType \
            or PixelType_Gvsp_YUV422_Packed == enGvspPixelType or PixelType_Gvsp_YUV422_YUYV_Packed == enGvspPixelType:
        return True
    else:
        return False


# Mono图像转为python数组
def Mono_numpy(data, nWidth, nHeight):
    data_ = np.frombuffer(data, count=int(nWidth * nHeight), dtype=np.uint8, offset=0)
    data_mono_arr = data_.reshape(nHeight, nWidth)
    numArray = np.zeros([nHeight, nWidth, 1], "uint8")
    numArray[:, :, 0] = data_mono_arr
    return numArray


# 彩色图像转为python数组
def Color_numpy(data, nWidth, nHeight):
    data_ = np.frombuffer(data, count=int(nWidth * nHeight * 3), dtype=np.uint8, offset=0)
    data_r = data_[0:nWidth * nHeight * 3:3]
    data_g = data_[1:nWidth * nHeight * 3:3]
    data_b = data_[2:nWidth * nHeight * 3:3]

    data_r_arr = data_r.reshape(nHeight, nWidth)
    data_g_arr = data_g.reshape(nHeight, nWidth)
    data_b_arr = data_b.reshape(nHeight, nWidth)
    numArray = np.zeros([nHeight, nWidth, 3], "uint8")

    numArray[:, :, 0] = data_r_arr
    numArray[:, :, 1] = data_g_arr
    numArray[:, :, 2] = data_b_arr
    return numArray


# 相机操作类
class CameraOperation:

    def __init__(self, obj_cam, st_device_list, n_connect_num=0, b_open_device=False, b_start_grabbing=False,
                 h_thread_handle=None,
                 b_thread_closed=False, st_frame_info=None, b_exit=False, b_save_bmp=False, b_save_jpg=False,
                 buf_save_image=None,
                 n_save_image_size=0, n_win_gui_id=0, frame_rate=0, exposure_time=0, gain=0):

        self.obj_cam = obj_cam
        self.st_device_list = st_device_list
        self.n_connect_num = n_connect_num
        self.b_open_device = b_open_device
        self.b_start_grabbing = b_start_grabbing
        self.b_thread_closed = b_thread_closed
        self.st_frame_info = st_frame_info
        self.b_exit = b_exit
        self.b_save_bmp = b_save_bmp
        self.b_save_jpg = b_save_jpg
        self.buf_grab_image = None
        self.buf_grab_image_size = 0
        self.buf_save_image = buf_save_image
        self.n_save_image_size = n_save_image_size
        self.h_thread_handle = h_thread_handle
        self.b_thread_closed
        self.frame_rate = frame_rate
        self.exposure_time = exposure_time
        self.gain = gain
        self.buf_lock = threading.Lock()  # 取图和存图的buffer锁

    # 打开相机
    def Open_device(self):
        if not self.b_open_device:
            if self.n_connect_num < 0:
                return MV_E_CALLORDER

            # ch:选择设备并创建句柄 | en:Select device and create handle
            nConnectionNum = int(self.n_connect_num)
            stDeviceList = cast(self.st_device_list.pDeviceInfo[int(nConnectionNum)],
                                POINTER(MV_CC_DEVICE_INFO)).contents
            self.obj_cam = MvCamera()
            ret = self.obj_cam.MV_CC_CreateHandle(stDeviceList)
            if ret != 0:
                self.obj_cam.MV_CC_DestroyHandle()
                return ret

            ret = self.obj_cam.MV_CC_OpenDevice()
            if ret != 0:
                return ret
            print("open device successfully!")
            self.b_open_device = True
            self.b_thread_closed = False

            # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
            if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
                nPacketSize = self.obj_cam.MV_CC_GetOptimalPacketSize()
                if int(nPacketSize) > 0:
                    ret = self.obj_cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
                    if ret != 0:
                        print("warning: set packet size fail! ret[0x%x]" % ret)
                else:
                    print("warning: set packet size fail! ret[0x%x]" % nPacketSize)

            stBool = c_bool(False)
            ret = self.obj_cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", stBool)
            if ret != 0:
                print("get acquisition frame rate enable fail! ret[0x%x]" % ret)

            # ch:设置触发模式为off | en:Set trigger mode as off
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
            if ret != 0:
                print("set trigger mode fail! ret[0x%x]" % ret)
            return MV_OK

    # 开始取图
    def Start_grabbing(self, winHandle):
        if not self.b_start_grabbing and self.b_open_device:
            self.b_exit = False
            ret = self.obj_cam.MV_CC_StartGrabbing()
            if ret != 0:
                return ret
            self.b_start_grabbing = True
            print("start grabbing successfully!")
            try:
                thread_id = random.randint(1, 10000)
                self.h_thread_handle = threading.Thread(target=CameraOperation.Work_thread, args=(self, winHandle))
                self.h_thread_handle.start()
                self.b_thread_closed = True
            finally:
                pass
            return MV_OK

        return MV_E_CALLORDER

    # 停止取图
    def Stop_grabbing(self):
        if self.b_start_grabbing and self.b_open_device:
            # 退出线程
            if self.b_thread_closed:
                Stop_thread(self.h_thread_handle)
                self.b_thread_closed = False
            ret = self.obj_cam.MV_CC_StopGrabbing()
            if ret != 0:
                return ret
            print("stop grabbing successfully!")
            self.b_start_grabbing = False
            self.b_exit = True
            return MV_OK
        else:
            return MV_E_CALLORDER

    # 关闭相机
    def Close_device(self):
        if self.b_open_device:
            # 退出线程
            if self.b_thread_closed:
                Stop_thread(self.h_thread_handle)
                self.b_thread_closed = False
            ret = self.obj_cam.MV_CC_CloseDevice()
            if ret != 0:
                return ret

        # ch:销毁句柄 | Destroy handle
        self.obj_cam.MV_CC_DestroyHandle()
        self.b_open_device = False
        self.b_start_grabbing = False
        self.b_exit = True
        print("close device successfully!")

        return MV_OK

    # 设置触发模式
    def Set_trigger_mode(self, is_trigger_mode):
        if not self.b_open_device:
            return MV_E_CALLORDER

        if not is_trigger_mode:
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", 0)
            if ret != 0:
                return ret
        else:
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", 1)
            if ret != 0:
                return ret
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerSource", 7)
            if ret != 0:
                return ret

        return MV_OK

    # 软触发一次
    def Trigger_once(self):
        if self.b_open_device:
            return self.obj_cam.MV_CC_SetCommandValue("TriggerSoftware")

    # 获取参数
    def Get_parameter(self):
        if self.b_open_device:
            stFloatParam_FrameRate = MVCC_FLOATVALUE()
            memset(byref(stFloatParam_FrameRate), 0, sizeof(MVCC_FLOATVALUE))
            stFloatParam_exposureTime = MVCC_FLOATVALUE()
            memset(byref(stFloatParam_exposureTime), 0, sizeof(MVCC_FLOATVALUE))
            stFloatParam_gain = MVCC_FLOATVALUE()
            memset(byref(stFloatParam_gain), 0, sizeof(MVCC_FLOATVALUE))
            ret = self.obj_cam.MV_CC_GetFloatValue("AcquisitionFrameRate", stFloatParam_FrameRate)
            if ret != 0:
                return ret
            self.frame_rate = stFloatParam_FrameRate.fCurValue

            ret = self.obj_cam.MV_CC_GetFloatValue("ExposureTime", stFloatParam_exposureTime)
            if ret != 0:
                return ret
            self.exposure_time = stFloatParam_exposureTime.fCurValue

            ret = self.obj_cam.MV_CC_GetFloatValue("Gain", stFloatParam_gain)
            if ret != 0:
                return ret
            self.gain = stFloatParam_gain.fCurValue

            return MV_OK

    # 设置参数
    def Set_parameter(self):
        if self.b_open_device:
            ret = self.obj_cam.MV_CC_SetEnumValue("ExposureAuto", 2)
            if ret != 0:
                print('show error', 'set ExposureAuto fail! ret = ' + To_hex_str(ret))
                return ret
            time.sleep(0.2)

            ret = self.obj_cam.MV_CC_SetBoolValue("AcquisitionLineRateEnable", True)
            if ret != 0:
                print('show error', 'set AcquisitionLineRateEnable fail! ret = ' + To_hex_str(ret))
                return ret    

            ret = self.obj_cam.MV_CC_SetIntValue("AcquisitionLineRate", 2600)
            if ret != 0:
                print('show error', 'set acquistion line rate fail! ret = ' + To_hex_str(ret))
                return ret
            
            ret = self.obj_cam.MV_CC_SetIntValue("AutoExposureTimeLowerLimit", 3)
            if ret != 0:
                print('show error', 'set AutoExposureTimeLowerLimit fail! ret = ' + To_hex_str(ret))
                return ret
            
            ret = self.obj_cam.MV_CC_SetIntValue("AutoExposureTimeUpperLimit", 400)
            if ret != 0:
                print('show error', 'set AutoExposureTimeUpperLimit fail! ret = ' + To_hex_str(ret))
                return ret
            
            ret = self.obj_cam.MV_CC_SetIntValue("Width", 8192)
            if ret != 0:
                print('show error', 'set Width fail! ret = ' + To_hex_str(ret))
                return ret
            
            ret = self.obj_cam.MV_CC_SetIntValue("Height", 512)
            if ret != 0:
                print('show error', 'set Height fail! ret = ' + To_hex_str(ret))
                return ret
            
            ret = self.obj_cam.MV_CC_SetBoolValue("ReverseX", False)
            if ret != 0:
                print('show error', 'set ReverseX fail! ret = ' + To_hex_str(ret))
                return ret
            
            ret = self.obj_cam.MV_CC_SetEnumValue("BalanceWhiteAuto", 1)
            if ret != 0:
                print('show error', 'set BalanceWhiteAuto fail! ret = ' + To_hex_str(ret))
                return ret
                
            ret = self.obj_cam.MV_CC_SetEnumValue("PixelFormat", 0x01080009)
            if ret != 0:
                print('show error', 'set PixelFormat fail! ret = ' + To_hex_str(ret))
                return ret
            
            ret = self.obj_cam.MV_CC_SetBoolValue("GammaEnable", True)
            if ret != 0:
                print('show error', 'set GammaEnable fail! ret = ' + To_hex_str(ret))
                return ret
            
            ret = self.obj_cam.MV_CC_SetEnumValue("GammaSelector", 2)
            if ret != 0:
                print('show error', 'set GammaSelector fail! ret = ' + To_hex_str(ret))
                return ret
            
            ret = self.obj_cam.MV_CC_SetBoolValue("HueEnable", True)
            if ret != 0:
                print('show error', 'set HueEnable fail! ret = ' + To_hex_str(ret))
                return ret
            
            ret = self.obj_cam.MV_CC_SetBoolValue("SaturationEnable", True)
            if ret != 0:
                print('show error', 'set SaturationEnable fail! ret = ' + To_hex_str(ret))
                return ret
            print('show info', 'set parameter success!')

            return MV_OK
        
    def Save_Bmp(self):

        if 0 == self.buf_save_image:
            return

        # 获取缓存锁
        self.buf_lock.acquire()

        file_path = "images/"+ str(self.st_frame_info.nFrameNum) + ".bmp"
        c_file_path = file_path.encode('ascii')

        stSaveParam = MV_SAVE_IMAGE_TO_FILE_PARAM_EX()
        stSaveParam.enPixelType = self.st_frame_info.enPixelType  # ch:相机对应的像素格式 | en:Camera pixel type
        stSaveParam.nWidth = self.st_frame_info.nWidth  # ch:相机对应的宽 | en:Width
        stSaveParam.nHeight = self.st_frame_info.nHeight  # ch:相机对应的高 | en:Height
        stSaveParam.nDataLen = self.st_frame_info.nFrameLen
        stSaveParam.pData = cast(self.buf_save_image, POINTER(c_ubyte))
        stSaveParam.enImageType = MV_Image_Bmp  # ch:需要保存的图像类型 | en:Image format to save
        stSaveParam.nQuality = 8
        stSaveParam.pcImagePath = ctypes.create_string_buffer(c_file_path)
        stSaveParam.iMethodValue = 2
        ret = self.obj_cam.MV_CC_SaveImageToFileEx(stSaveParam)

        self.buf_lock.release()

        return ret

    def Work_thread(self, winHandle):
        # Create necessary structures
        stFrameInfo = MV_FRAME_OUT_INFO_EX()
        img_buff = None
        numArray = None

        # Get PayloadSize (size of the image to be grabbed)
        stPayloadSize = MVCC_INTVALUE_EX()
        ret_temp = self.obj_cam.MV_CC_GetIntValueEx("PayloadSize", stPayloadSize)
        if ret_temp != MV_OK:
            return
        NeedBufSize = int(stPayloadSize.nCurValue)

        while True:
            # Check if the buffer size is sufficient for the frame, else reallocate
            if self.buf_grab_image_size < NeedBufSize:
                self.buf_grab_image = (c_ubyte * NeedBufSize)()
                self.buf_grab_image_size = NeedBufSize

            # Grab a single frame with a timeout
            ret = self.obj_cam.MV_CC_GetOneFrameTimeout(self.buf_grab_image, self.buf_grab_image_size, stFrameInfo)

            if 0 == ret:
                # Copy image data and frame info to buffer
                if self.buf_save_image is None:
                    self.buf_save_image = (c_ubyte * stFrameInfo.nFrameLen)()

                self.st_frame_info = stFrameInfo

                # Lock the buffer to safely copy image data
                self.buf_lock.acquire()
                # Using numpy to handle image buffer copying more efficiently
                np_buffer = np.frombuffer(self.buf_grab_image, dtype=np.uint8, count=self.st_frame_info.nFrameLen)
                np.copyto(np.frombuffer(self.buf_save_image, dtype=np.uint8, count=self.st_frame_info.nFrameLen), np_buffer)
                self.buf_lock.release()

                # Debugging output
                print(f"get one frame: Width[{self.st_frame_info.nWidth}], Height[{self.st_frame_info.nHeight}], "
                    f"nFrameNum[{self.st_frame_info.nFrameNum}]")

                # Optionally save the image (you can customize this function based on your needs)
                self.Save_Bmp()

            else:
                print(f"no data, ret = {To_hex_str(ret)}")
                continue

            # Prepare for displaying the image
            stDisplayParam = MV_DISPLAY_FRAME_INFO()
            ctypes.memset(byref(stDisplayParam), 0, sizeof(stDisplayParam))
            stDisplayParam.hWnd = int(winHandle)
            stDisplayParam.nWidth = self.st_frame_info.nWidth
            stDisplayParam.nHeight = self.st_frame_info.nHeight
            stDisplayParam.enPixelType = self.st_frame_info.enPixelType
            stDisplayParam.pData = self.buf_save_image
            stDisplayParam.nDataLen = self.st_frame_info.nFrameLen

            # Display the frame using the camera API
            self.obj_cam.MV_CC_DisplayOneFrame(stDisplayParam)

            # Check if we should exit the thread
            if self.b_exit:
                if img_buff is not None:
                    del img_buff
                if self.buf_save_image is not None:
                    del self.buf_save_image
                break




    # 存jpg图像
    def Save_jpg(self):

        if self.buf_save_image is None:
            return

        # 获取缓存锁
        self.buf_lock.acquire()

        file_path = str(self.st_frame_info.nFrameNum) + ".jpg"
        c_file_path = file_path.encode('ascii')
        stSaveParam = MV_SAVE_IMAGE_TO_FILE_PARAM_EX()
        stSaveParam.enPixelType = self.st_frame_info.enPixelType  # ch:相机对应的像素格式 | en:Camera pixel type
        stSaveParam.nWidth = self.st_frame_info.nWidth  # ch:相机对应的宽 | en:Width
        stSaveParam.nHeight = self.st_frame_info.nHeight  # ch:相机对应的高 | en:Height
        stSaveParam.nDataLen = self.st_frame_info.nFrameLen
        stSaveParam.pData = cast(self.buf_save_image, POINTER(c_ubyte))
        stSaveParam.enImageType = MV_Image_Jpeg  # ch:需要保存的图像类型 | en:Image format to save
        stSaveParam.nQuality = 80
        stSaveParam.pcImagePath = ctypes.create_string_buffer(c_file_path)
        stSaveParam.iMethodValue = 2
        ret = self.obj_cam.MV_CC_SaveImageToFileEx(stSaveParam)

        self.buf_lock.release()
        return ret

    # 存BMP图像
    

