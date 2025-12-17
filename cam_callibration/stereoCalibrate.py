import cv2
import numpy as np
from pathlib import Path

# ================= USER SETTINGS =================

LEFT_INTR = r"C:\Users\ASUS\Documents\campus related\5. fifth semester\Macchine Learning\\kamera kalibrasi\calibration\camN_intrinsics.npz"
RIGHT_INTR = r"C:\Users\ASUS\Documents\campus related\5. fifth semester\Macchine Learning\kamera kalibrasi\calibration\camW_intrinsics.npz"

LEFT_DIR = Path(r"C:\Users\ASUS\Documents\campus related\5. fifth semester\Macchine Learning\kamera kalibrasi\1920x1080n")
RIGHT_DIR = Path(r"C:\Users\ASUS\Documents\campus related\5. fifth semester\Macchine Learning\kamera kalibrasi\pinhole_images")

ROWS = 7          # inner corners
COLS = 9
SQUARE = 0.02     # meters
IMAGE_SIZE = (1920, 1080)  # (width, height)

# ================================================

# ---- Safety checks ----
assert Path(LEFT_INTR).exists(), "LEFT_INTR not found"
assert Path(RIGHT_INTR).exists(), "RIGHT_INTR not found"
assert LEFT_DIR.exists(), "LEFT_DIR not found"
assert RIGHT_DIR.exists(), "RIGHT_DIR not found"

# ---- Load intrinsics ----
dataL = np.load(LEFT_INTR)
dataR = np.load(RIGHT_INTR)

KL = dataL["K"]
distL = dataL["dist"]

KR = dataR["K"]
distR = dataR["dist"]

# ---- Prepare object points ----
pattern_size = (COLS, ROWS)

objp = np.zeros((ROWS * COLS, 3), np.float32)
objp[:, :2] = np.mgrid[0:COLS, 0:ROWS].T.reshape(-1, 2)
objp *= SQUARE

objpoints = []
imgpointsL = []
imgpointsR = []

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)

# ---- Load image pairs ----
left_images = sorted(LEFT_DIR.glob("*.jpg"))
assert len(left_images) > 0, "No left images found"

for imgL_path in left_images:
    imgR_path = RIGHT_DIR / imgL_path.name
    if not imgR_path.exists():
        continue

    imgL = cv2.imread(str(imgL_path))
    imgR = cv2.imread(str(imgR_path))

    if imgL is None or imgR is None:
        continue

    grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
    grayR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

    okL, cornersL = cv2.findChessboardCorners(grayL, pattern_size)
    okR, cornersR = cv2.findChessboardCorners(grayR, pattern_size)

    if not (okL and okR):
        continue

    cornersL = cv2.cornerSubPix(grayL, cornersL, (11,11), (-1,-1), criteria)
    cornersR = cv2.cornerSubPix(grayR, cornersR, (11,11), (-1,-1), criteria)

    objpoints.append(objp)
    imgpointsL.append(cornersL)
    imgpointsR.append(cornersR)

print(f"[INFO] Using {len(objpoints)} valid stereo pairs")
assert len(objpoints) >= 10, "Not enough valid pairs for stereo calibration"

# ---- Stereo calibration ----
flags = cv2.CALIB_FIX_INTRINSIC

ret, _, _, _, _, R, T, E, F = cv2.stereoCalibrate(
    objpoints,
    imgpointsL,
    imgpointsR,
    KL, distL,
    KR, distR,
    IMAGE_SIZE,
    criteria=criteria,
    flags=flags
)

print("[INFO] Stereo RMS error:", ret)
print("[INFO] Translation vector T (meters):\n", T)
print("[INFO] Baseline (meters):", np.linalg.norm(T))

# ---- Rectification ----
R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(
    KL, distL,
    KR, distR,
    IMAGE_SIZE,
    R, T,
    flags=cv2.CALIB_ZERO_DISPARITY,
    alpha=0
)

# ---- Save results ----
output_dir = Path("calibration")
output_dir.mkdir(exist_ok=True)

np.savez(
    output_dir / "stereo_rectified.npz",
    R=R, T=T,
    R1=R1, R2=R2,
    P1=P1, P2=P2,
    Q=Q
)

print("[DONE] Stereo calibration and rectification saved")
