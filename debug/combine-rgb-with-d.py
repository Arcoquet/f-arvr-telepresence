import time
from pathlib import Path
import cv2
import numpy as np

from hue import hue_torch
from utils import combinate_rgbd, Timer, downscale

dir_path = Path("frame-example")
color_path = dir_path / "rgb.jpg"
depth_path = dir_path / "depth.png"

color = cv2.imread(str(color_path))  # BGR
depth_16b = cv2.imread(str(depth_path), cv2.IMREAD_UNCHANGED)  # uint16, in mm
h, w = color.shape[:2]
# depth_16b = cv2.resize(depth_16b, (w, h)) # k2 provide is slighly bigger image (TODO fix that earlier)
depth_16b = depth_16b[0:h, 0:w]  # TODO check with above solution and fix earlier

cv2.imshow("color", downscale(color, 4))
cv2.imshow("depth", downscale(depth_16b / 4500., 4))

near, far = 500, 1500  # in mm # bc the depth as only 256 values, will keep only range 0.5m-1.5m

rgbd_combined = combinate_rgbd(color, depth_16b, near, far, False)
cv2.imshow("rgbd_combined", downscale(rgbd_combined, 4))
cv2.imwrite(str(dir_path / "rgbd_combined.jpg"), rgbd_combined)

i = 0
rgbdhue_combined = None
while (i < 5):  # loop to let torch to warm up
    with Timer(name='Hue only - cuda'):
        depth_hue = hue_torch(depth_16b, near, far, device='cuda')  # 22ms

    with Timer(name='Hue only - cpu'):
        depth_hue = hue_torch(depth_16b, near, far, device='cpu')  # 63ms

    with Timer(name='combined hue'):
        rgbdhue_combined = combinate_rgbd(color, depth_16b, near, far, True, device='cuda')
    i += 1

cv2.imshow("rgbdhue_combined", downscale(rgbdhue_combined, 4))
cv2.imwrite(str(dir_path / "rgbdhue_combined.jpg"), rgbdhue_combined)

cv2.waitKey(0)
