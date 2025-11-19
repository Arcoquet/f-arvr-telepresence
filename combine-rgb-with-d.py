import time
from pathlib import Path
import cv2
import numpy as np

from hue import hue_torch

dir_path = Path("frame-example")
color_path = dir_path / "rgb.jpg"
depth_path = dir_path / "depth.png"

def downscale(img, scale=4):
    h, w = img.shape[:2]
    return cv2.resize(img, (int(w/scale), int(h/scale)))


color = cv2.imread(str(color_path)) # BGR
depth_16b = cv2.imread(str(depth_path), cv2.IMREAD_UNCHANGED) # uint16, in mm
h, w = color.shape[:2]
#depth_16b = cv2.resize(depth_16b, (w, h)) # k2 provide is slighly bigger image (TODO fix that earlier)
depth_16b = depth_16b[0:h, 0:w] # TODO check with above solution and fix earlier

cv2.imshow("color", downscale(color, 4))
cv2.imshow("depth", downscale(depth_16b / 4500., 4))

near, far = 500, 1500 # in mm # bc the depth as only 256 values, will keep only range 0.5m-1.5m
depth_8bit = np.clip((((depth_16b - near) / (far - near)) * 255.0), 0, 255).astype(np.uint8)
depth_bgr = cv2.cvtColor(depth_8bit, cv2.COLOR_GRAY2BGR)

rgbd_combined = np.concatenate((color, depth_bgr), axis=0)
cv2.imshow("rgbd_combined", downscale(rgbd_combined, 4))
cv2.imwrite(str(dir_path / "rgbd_combined.jpg"), rgbd_combined)

i = 0
while(i<5): #loop to let torch to warm up
    time_start = time.time()
    depth_hue = hue_torch(depth_16b, near, far, device='cuda')
    print(f"Hue: {time.time() - time_start:.3f}s")
    i += 1

rgbdhue_combined = np.concatenate((color, depth_hue), axis=0)
cv2.imshow("rgbdhue_combined", downscale(rgbdhue_combined, 4))
cv2.imwrite(str(dir_path / "rgbdhue_combined.jpg"), rgbdhue_combined)

cv2.waitKey(0)



