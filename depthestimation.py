import cv2
import torch
import numpy as np

# Could test thoses alternatives (specialized in human):
# - https://www.meta.com/emerging-tech/codec-avatars/sapiens/
# - https://mediapipe-studio.webapps.google.com/demo/face_landmarker + skeleton


def load_midas(model_mod=0):
    print("Loading MiDaS model...")

    if model_mod == 0:
        model_type = "MiDaS_small"   # MiDaS v2.1 - Small   (lowest accuracy, highest inference speed)
    elif model_mod == 1:
        model_type = "DPT_Hybrid"    # MiDaS v3 - Hybrid    (medium accuracy, medium inference speed) Trop lent pour du temps réel sur cpu
    else:
        model_mod = "DPT_Large"       # MiDaS V3 - Large (better accuracy, low inference seed) A tester en gpu uniquement

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
    output = output.astype(np.uint8)

    return output



midas, transform, device = load_midas(model_mod=True)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

print("q = exit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to receive frame.")
        break

    d_frame = get_MiDas_monodepth(frame, midas, transform, device)

    cv2.imshow("Depth Map", d_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
