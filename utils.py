import time

import cv2
import numpy as np

from hue import hue_torch


def combinate_rgbd(color, depth_16b, near, far, is_hue = True, device='cuda'):
    assert color.shape[:2] == depth_16b.shape[:2], "Color and Depth must have same w x h"
    assert color.shape[2], "Color must have 3 channels"
    assert len(depth_16b.shape) == 2 or depth_16b.shape[2], "Depth must have 1 channel"

    depth_bgr = None

    if is_hue:
        depth_bgr = hue_torch(depth_16b, near, far, device)
    else:
        depth_8bit = np.clip((((depth_16b - near) / (far - near)) * 255.0), 0, 255).astype(np.uint8)
        depth_bgr = cv2.cvtColor(depth_8bit, cv2.COLOR_GRAY2BGR)

    combined_rgbd = np.concatenate((color, depth_bgr), axis=0)
    return combined_rgbd


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