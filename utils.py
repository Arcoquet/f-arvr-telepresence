import time

import cv2
import numpy as np

from hue import hue_torch

import traceback
import functools

import socket


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

class Timer:
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        elapsed_ms = self.end_time - self.start_time
        if elapsed_ms > 1000.0:
            message = f"{elapsed_ms:.3f}s"
        else:
            message = f"{(elapsed_ms * 1000.0):.0f}ms"
        if self.name:
            print(f"[{self.name}] {message}")
        else:
            print(message)
        return False

def downscale(img, scale=4):
    h, w = img.shape[:2]
    return cv2.resize(img, (int(w/scale), int(h/scale)))

def print_exceptions(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            traceback.print_exc()
            raise
    return wrapper

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP