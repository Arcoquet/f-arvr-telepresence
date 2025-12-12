import cv2
from aiortc import VideoStreamTrack
from av import VideoFrame
import torch

from utils import Fps, combinate_rgbd, downscale, print_exceptions
from depthestimation import load_midas, get_MiDas_monodepth

device = "cuda" if torch.cuda.is_available() else "cpu"
correct, total = 0., 0.


class DumbStaticRGBD(VideoStreamTrack):
    def __init__(self, near, far, is_hue=True, show=True):
        super().__init__()
        self.near = near
        self.far = far

        # self.rgbdhue_path = "./frame-example/tmp_rgbdhue_combined.jpg"
        self.color_path = './frame-example/rgb.jpg'
        self.depth_path = './frame-example/depth.png'
        self.fps = Fps()
        self.show = show
        self.is_hue = is_hue

    @print_exceptions
    async def recv(self):
        pts, time_base = await self.next_timestamp()
        color_bgr = cv2.imread(self.color_path)
        depth16 = cv2.imread(self.depth_path, cv2.IMREAD_UNCHANGED)

        # with Timer(name='combinate_rgbd'):
        frame_bgr = combinate_rgbd(color_bgr, depth16, self.near, self.far, self.is_hue, device)
        frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        # frame = color_bgr #skip the depth

        if self.show:
            cv2.imshow('frame_bgr', downscale(frame_bgr, 4))
            cv2.waitKey(1)

        # Create a VideoFrame from the NumPy array (ndarray)
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")

        self.fps.tickAndPrint()

        # Set the timing information required for streaming
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

    def stop(self):
        pass


class DumbWebcamStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Could not read frame from webcam")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

    def stop(self):
        if self.cap.isOpened():
            self.cap.release()


class DumbMonoDepth(VideoStreamTrack):
    def __init__(self, show=True, model_mod=True):
        super().__init__()
        
        self.cap = cv2.VideoCapture(0)
        self.midas, self.transform, self.device = load_midas(model_mod)

        self.show = show

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Could not read frame from webcam")

        depth = get_MiDas_monodepth(frame, self.midas, self.transform, self.device)

        if self.show:
            cv2.imshow("MonoDepth", depth)
            cv2.waitKey(1)

        depth_rgb = cv2.cvtColor(depth, cv2.COLOR_GRAY2RGB)

        video_frame = VideoFrame.from_ndarray(depth_rgb, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

    def stop(self):
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
