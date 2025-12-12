import cv2
import torch
import numpy as np

def load_midas(model_mod=True):
    print("Loading MiDaS model...")

    if model_mod:
        model_type = "MiDaS_small"
    else:
        model_type = "DPT_Hybrid"

    midas = torch.hub.load("intel-isl/MiDaS", model_type)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using:", device)
    midas.to(device)
    midas.eval()

    midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
    if model_type in ["DPT_Large", "DPT_Hybrid"]:
        transform = midas_transforms.dpt_transform
    else:
        transform = midas_transforms.small_transform

    return midas, transform, device


def get_MiDas_monodepth(image, midas, transform, device):
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    input_batch = transform(img_rgb).to(device)

    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=image.shape[:2],
            mode="bicubic",
            align_corners=False
        ).squeeze()

    output = prediction.cpu().numpy()
    output = cv2.normalize(output, None, 0, 255, cv2.NORM_MINMAX)
    return output.astype(np.uint8)
