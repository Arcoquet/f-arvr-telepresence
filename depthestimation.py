import time

import torch
import cv2
# import matplotlib.pyplot as plt

def get_MiDas_monodepth(filepath, model="small"):
    if model == "small":
        model_type = "MiDaS_small"  # MiDaS v2.1 - Small   (lowest accuracy, highest inference speed)
    else :
        model_type = "DPT_Hybrid"  # MiDaS v3 - Hybrid    (medium accuracy, medium inference speed)


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

    img_midas = cv2.imread(filepath)
    img_midas = cv2.cvtColor(img_midas, cv2.COLOR_BGR2RGB)

    input_batch = transform(img_midas).to(device)

    i = 0

    while(i<100):
        time_start = time.time()
        i+=1
        with torch.no_grad():
            prediction = midas(input_batch)

            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img_midas.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        time_elapsed = time.time() - time_start
        print(f"Depth estimation time: {time_elapsed*1000:.2f} ms")

    output = prediction.cpu().numpy()

    # TODO use CV_16U instead
    output = cv2.normalize(output, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    cv2.imshow("depth colored", output)
    cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # plt.imshow(output)
    # plt.show()


get_MiDas_monodepth("right.png")