import numpy as np
import cv2
import sys
import os
from pylibfreenect2 import Freenect2, SyncMultiFrameListener
from pylibfreenect2 import FrameType, Registration, Frame
from pylibfreenect2 import createConsoleLogger, setGlobalLogger
from pylibfreenect2 import LoggerLevel
import time
import FreeSimpleGUI as sg
from datetime import datetime
from pathlib import Path

class Fps:
    num = 0
    time_s = time.time()

    def tickAndPrint(self):
        self.num += 1
        if time.time() - self.time_s > 1:  # display fps every sec
            out = "{:.3f}".format(1 / ((time.time() - self.time_s) / self.num))
            print("fps:" + out)
            self.num = 0
            self.time_s = time.time()
            return out

class Gui:
    def __init__(self, dir):

        layout = [
            [sg.Text('Dir:'), sg.Text(dir)],
            [sg.Text('Fps:'), sg.Text(size=(8), key='fps')],
            [sg.Button('Snapshot (s)'), sg.Checkbox("Record", key='record'),sg.Text('Last rec frame:'), sg.Text(size=(6), key='numframestr')],
            [sg.Button('Quit (q)')]
        ]

        self.window = sg.Window('kinectv2record.py', layout)

        self.fps = Fps()

    def waitKey(self):
        event, values = self.window.read(timeout=0)
        key = cv2.waitKey(1)
        if(key == -1):
            if event == 'Snapshot (s)':
                key = ord('s')
            if event == 'Record (r)':
                key = ord('r')
            if event == 'Quit (q)' or event == sg.WIN_CLOSED or key == 27:
                key = ord('q')
            if event == 'Rotate':
                self.rotate = not self.rotate

        fpsstr = self.fps.tickAndPrint()
        if fpsstr:
            self.window['fps'].update(fpsstr)

        return key

    def updateNumFrame(self, numframe: int):
        self.window['numframestr'].update(f"{numframe:06}")

    def isRecording(self):
        return self.window['record'].Get()


try:
    from pylibfreenect2 import OpenGLPacketPipeline
    pipeline = OpenGLPacketPipeline()
except:
    try:
        from pylibfreenect2 import OpenCLPacketPipeline
        pipeline = OpenCLPacketPipeline()
    except:
        from pylibfreenect2 import CpuPacketPipeline
        pipeline = CpuPacketPipeline()
print("Packet pipeline:", type(pipeline).__name__)

# Create and set logger
logger = createConsoleLogger(LoggerLevel.Debug)
setGlobalLogger(logger)

fn = Freenect2()
num_devices = fn.enumerateDevices()
if num_devices == 0:
    print("No device connected!")
    sys.exit(1)

serial = fn.getDeviceSerialNumber(0)
device = fn.openDevice(serial, pipeline=pipeline)

listener = SyncMultiFrameListener(FrameType.Color | FrameType.Ir | FrameType.Depth)

# Register listeners
device.setColorFrameListener(listener)
device.setIrAndDepthFrameListener(listener)

device.start()

# NOTE: must be called after device.start()
registration = Registration(device.getIrCameraParams(), device.getColorCameraParams())

cam = device.getIrCameraParams()

undistorted = Frame(512, 424, 4)
registered = Frame(512, 424, 4)

# Optinal parameters for registration
# set True if you need
need_bigdepth = True
need_color_depth_map = False

bigdepth = Frame(1920, 1082, 4) if need_bigdepth else None
color_depth_map = np.zeros((424, 512),  np.int32).ravel() if need_color_depth_map else None

numframe = 0

dir = Path('tmp_frames') / datetime.now().strftime('%Y%m%d-%H%M')

gui = Gui(dir)

while True:
    frames = listener.waitForNewFrame()

    color = frames["color"]
    ir = frames["ir"]
    depth = frames["depth"]

    registration.apply(color, depth, undistorted, registered, bigdepth=bigdepth, color_depth_map=color_depth_map)

    # NOTE for visualization:
    # cv2.imshow without OpenGL backend seems to be quite slow to draw all
    # things below. Try commenting out some imshow if you don't have a fast
    # visualization backend.
    cv2.imshow("ir", ir.asarray() / 65535.)
    cv2.imshow("depth", depth.asarray() / 4500.)
    cv2.imshow("color", cv2.resize(color.asarray(),(int(1920/3), int(1080/3))))
    # cv2.imshow("undistorded", undistorted.asarray(np.uint8))
    cv2.imshow("color registered", registered.asarray(np.uint8))

    # out.write(color.asarray())

    if need_bigdepth:
        cv2.imshow("bigdepth", cv2.resize(bigdepth.asarray(np.float32), (int(1920 / 3), int(1082 / 3))))
    if need_color_depth_map:
        cv2.imshow("color_depth_map", color_depth_map.reshape(424, 512))

    key = gui.waitKey()

    if key == ord('q'):
        break
    if key == ord('s') or gui.isRecording():
        print(f"Save in {dir}")
        os.makedirs(dir, exist_ok=True)
        cv2.imwrite(dir / f"{numframe:06}_rgb-mirror.jpg", color.asarray())
        depthFloat = depth.asarray()
        depthInt16 = depthFloat.astype(np.uint16)
        cv2.imwrite(dir / f"{numframe:06}_depth-mirror.png", depthInt16) #CV_16UC1
        cv2.imwrite(dir / f"{numframe:06}_registered-mirror.jpg", registered.asarray(np.uint8))  # CV_16UC1
        bigdepthFloat = bigdepth.asarray(np.float32)
        bigdepthInt16 = bigdepthFloat.astype(np.uint16)
        cv2.imwrite(dir / f"{numframe:06}_bigdepth-mirror.png", bigdepthInt16)
        # TODO _bigdepth.png (cropped to 1080x1920) and _rgb.jpg
        # convert 58077_rgb-mirror.jpg -flop 58077_rgb.jpg
        # convert 58077_bigdepth-mirror.png -flop -crop 1920x1080+0+0 58077_bigdepth.png
        # mogrify -flop *.jpg
        # mogrify -crop 1920x1080+0+0 *.png
        # mkdir -p 320x180 && mogrify -path 320x180 -resize 320x180 *.png
        gui.updateNumFrame(numframe)

    listener.release(frames)
    numframe+=1

# out.release()
device.stop()
device.close()

sys.exit(0)

# window.close()

