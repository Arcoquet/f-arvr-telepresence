import cv2
from aiortc import VideoStreamTrack
from av import VideoFrame

from utils import Fps, combinate_rgbd, Timer


class DumbStaticRGBD(VideoStreamTrack):
    def __init__(self, near, far):
        super().__init__()
        self.near = near
        self.far = far

        # self.rgbdhue_path = "./frame-example/tmp_rgbdhue_combined.jpg"
        self.color_path = './frame-example/rgb.jpg'
        self.depth_path = './frame-example/depth.png'
        self.fps = Fps()



    async def recv(self):
        pts, time_base = await self.next_timestamp()
        color_bgr = cv2.imread(self.color_path)
        depth16 = cv2.imread(self.depth_path, cv2.IMREAD_UNCHANGED)

        color_rgb = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2RGB)

        # with Timer(name='combinate_rgbd'):
        frame = combinate_rgbd(color_rgb, depth16, self.near, self.far, True, 'cuda')
        # frame = color_rgb #skip the depth

        # Create a VideoFrame from the NumPy array (ndarray)
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")

        self.fps.tickAndPrint()

        # Set the timing information required for streaming
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

    def stop(self):
        pass


class WebcamStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        # Open the first available webcam
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