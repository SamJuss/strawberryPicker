#!/usr/bin/env python3
import cv2
import numpy as np
from pathlib import Path

# =========================
# USER SETTINGS (EDITED)
# =========================

FISHEYE_NPZ = r"C:\Users\ASUS\Documents\campus related\5. fifth semester\Macchine Learning\kamera kalibrasi\output_fisheye\fisheye_intrinsics.npz"

IMAGE_DIR = r"C:\Users\ASUS\Documents\campus related\5. fifth semester\Macchine Learning\kamera kalibrasi\1920x1080w"
IMAGE_GLOB = "*.jpg"

OUTPUT_DIR = r"C:\Users\ASUS\Documents\campus related\5. fifth semester\Macchine Learning\kamera kalibrasi\pinhole_images"

IMG_WIDTH = 2560
IMG_HEIGHT = 1440
IMAGE_SIZE = (IMG_WIDTH, IMG_HEIGHT)

BALANCE = 0.0  # 0

# =========================
# LOAD FISHEYE CALIBRATION
# =========================

data = np.load(FISHEYE_NPZ)
K_fisheye = data["K"]
D_fisheye = data["D"]

print("[INFO] Loaded fisheye intrinsics")
print("K_fisheye:\n", K_fisheye)
print("D_fisheye:\n", D_fisheye.ravel())

# =========================
# CREATE PINHOLE CAMERA
# =========================

# Identity rectification
R = np.eye(3)

# Compute optimal pinhole camera matrix
K_pinhole = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
    K_fisheye,
    D_fisheye,
    IMAGE_SIZE,
    R,
    balance=BALANCE,
    new_size=IMAGE_SIZE
)

print("\n[INFO] Generated virtual pinhole camera")
print("K_pinhole:\n", K_pinhole)

# =========================
# UNDISTORTION MAP
# =========================

map1, map2 = cv2.fisheye.initUndistortRectifyMap(
    K_fisheye,
    D_fisheye,
    R,
    K_pinhole,
    IMAGE_SIZE,
    cv2.CV_16SC2
)

# =========================
# PROCESS IMAGES
# =========================

input_dir = Path(IMAGE_DIR)
output_dir = Path(OUTPUT_DIR)
output_dir.mkdir(parents=True, exist_ok=True)

images = sorted(input_dir.glob(IMAGE_GLOB))

if not images:
    raise RuntimeError("No images found.")

for img_path in images:
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"[WARN] Cannot read {img_path}")
        continue

    undistorted = cv2.remap(
        img,
        map1,
        map2,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT
    )

    out_path = output_dir / img_path.name
    cv2.imwrite(str(out_path), undistorted)
    print(f"[OK] Saved {out_path}")

print("\n[DONE] Fisheye → pinhole conversion complete")
print("Next step: run standard pinhole calibration on these images.")
