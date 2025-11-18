import time

import torch
import cv2
# import matplotlib.pyplot as plt

# Could test thoses alternatives (specialized in human):
# - https://www.meta.com/emerging-tech/codec-avatars/sapiens/
# - https://mediapipe-studio.webapps.google.com/demo/face_landmarker + skeleton

def get_MiDas_monodepth(image, model_mod = True):
    if model_mod == True:
        model_type = "MiDaS_small"  # MiDaS v2.1 - Small   (lowest accuracy, highest inference speed)
    else :
        model_type = "DPT_Hybrid"  # MiDaS v3 - Hybrid    (medium accuracy, medium inference speed) Trop lent pour du temps


    midas = torch.hub.load("intel-isl/MiDaS", model_type)
    print("Use CUDA" if torch.cuda.is_available() else "Use CPU")
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    midas.to(device)
    midas.eval()

    midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

    if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
        transform = midas_transforms.dpt_transform
    else:
        transform = midas_transforms.small_transform

    input_batch = transform(image).to(device)

    # i = 0 # Boucle controle de temps
    # while(i<10):
    #     time_start = time.time()
    #     i+=1
    #     with torch.no_grad():
    #         prediction = midas(input_batch)

    #         prediction = torch.nn.functional.interpolate(
    #             prediction.unsqueeze(1),
    #             size=img_midas.shape[:2],
    #             mode="bicubic",
    #             align_corners=False,
    #         ).squeeze()

    #     time_elapsed = time.time() - time_start
    #     print(f"Depth estimation time: {time_elapsed*1000:.2f} ms")
        
    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=image.shape[:2],
            mode="bicubic",
            align_corners=False,
            ).squeeze()

    output = prediction.cpu().numpy()

    # TODO use CV_16U instead
    output = cv2.normalize(output, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    return output



cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

print("q = exit")

while(True):
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to receive frame.")
        break
    d_frame = get_MiDas_monodepth(frame)
    cv2.imshow('Live Depth Camera Feed', d_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()