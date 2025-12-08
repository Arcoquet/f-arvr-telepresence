import colorsys

import cv2
import numpy as np
from matplotlib.colors import hsv_to_rgb
import torch


# For learning purpose, I'll keep here multiples implementations of the hue encoding:
# Hue can have 1535 different values when encoded with RGB 3x8bits whereas grayscale can have only 256 values when encoded with RGB 3x8bit
# 1. Looping
# 2. Vectorized (cpu)
# 3. GPU -> takes 4ms on my RTX. A version using vulkan/opengl, can be easily done and is probably faster than using torch (taichi, opengl)

def hue_torch(depths_mm_np: np.ndarray, near: int, far: int, device='cuda'):
    depths_mm = torch.from_numpy(depths_mm_np).to(device).float()
    mask = (depths_mm >= near) & (depths_mm <= far)
    depths_01 = (depths_mm - near) / (far - near)
    depths_01 = torch.clamp(depths_01, 0, 1)
    depths_01 *= 6.0  # [0, 6]
    r = torch.abs(depths_01 - 3) - 1
    g = 2 - torch.abs(depths_01 - 2)
    b = 2 - torch.abs(depths_01 - 4)
    r = torch.clamp(r, 0, 1)
    g = torch.clamp(g, 0, 1)
    b = torch.clamp(b, 0, 1)
    image = torch.stack([b, g, r], dim=-1)
    image = image * 255.0
    image = image * mask.unsqueeze(-1)
    return image.to(torch.uint8).cpu().numpy()


def hue_np(depths_mm, near, far):
    mask = (depths_mm >= near) & (depths_mm <= far)  # mask used to avoid processing exluded depths
    depths_01 = np.zeros(depths_mm.shape, dtype=np.float32)
    np.divide(depths_mm - near, far - near, out=depths_01, where=mask)  # depths_01 = (depths_mm - near) / (far - near)
    np.clip(depths_01, 0, 1, out=depths_01)
    depths_01 *= 6.0  # now in [0, 6]

    r = np.abs(depths_01 - 3) - 1
    g = 2 - np.abs(depths_01 - 2)
    b = 2 - np.abs(depths_01 - 4)

    np.clip(r, 0, 1, out=r)
    np.clip(g, 0, 1, out=g)
    np.clip(b, 0, 1, out=b)

    h_img, w_img = depths_mm.shape
    image = np.zeros((h_img, w_img, 3), dtype=np.uint8)

    image[..., 0] = (b * 255).astype(np.uint8) * mask
    image[..., 1] = (g * 255).astype(np.uint8) * mask
    image[..., 2] = (r * 255).astype(np.uint8) * mask
    return image  # BGR


def hue_matplotlib(depths_mm, near, far):
    mask = (depths_mm >= near) & (depths_mm <= far)
    h, w = depths_mm.shape
    norm_depth = (depths_mm - near) / (far - near)
    hsv = np.zeros((h, w, 3), dtype=np.float32)
    hsv[mask, 0] = norm_depth[mask]
    hsv[mask, 1] = 1.0
    hsv[mask, 2] = 1.0
    rgb = hsv_to_rgb(hsv)
    rgb_uint8 = (rgb * 255).astype(np.uint8)
    bgr_image = rgb_uint8[..., ::-1]
    return bgr_image


def hue_loop(depths_mm, near, far):
    h, w = depths_mm.shape
    image = np.zeros((h, w, 3), np.uint8)
    for x in range(0, w):
        for y in range(0, h):
            depthmm = depths_mm[y, x]
            if near <= depthmm <= far:
                depthclipped = (depthmm - near) / (far - near)
                hsv = colorsys.hsv_to_rgb(depthclipped, 1, 1)  # 1530 different possible values (hsv : [0-1])
                image[y, x] = tuple(reversed((hsv[0] * 255, hsv[1] * 255, hsv[2] * 255)))
    return image
