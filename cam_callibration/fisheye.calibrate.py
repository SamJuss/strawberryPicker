import cv2
import numpy as np
from pathlib import Path

# ================= USER SETTINGS =================

# Folder containing chessboard images (ALL SAME RESOLUTION)
IMAGES_DIR = Path(r"C:\Users\ASUS\Documents\campus related\5. fifth semester\Macchine Learning\cam_callibration\kamera kalibrasi\1920x1080w")

# Output folder
OUT_DIR = Path("output_fisheye")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Chessboard parameters (INNER corners)
ROWS = 7
COLS = 9
SQUARE_SIZE = 0.02  # meters

# Image resolution (must match images)
IMAGE_SIZE = (1920, 1080)  # (width, height)

# =================================================

pattern_size = (COLS, ROWS)

# Correct fisheye object points: (N,1,3), float32
objp = np.zeros((ROWS * COLS, 1, 3), np.float32)
objp[:, 0, :2] = np.mgrid[0:COLS, 0:ROWS].T.reshape(-1, 2)
objp *= SQUARE_SIZE

objpoints = []
imgpoints = []

# Corner refinement criteria
criteria = (
    cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
    30,
    1e-6
)

# -------------------------------------------------
# Detect corners
# -------------------------------------------------
images = sorted(IMAGES_DIR.glob("*.jpg")) + sorted(IMAGES_DIR.glob("*.png"))

if len(images) == 0:
    raise RuntimeError("No images found")

print(f"[INFO] Found {len(images)} images")

for img_path in images:
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"[SKIP] Cannot read {img_path}")
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(
        gray,
        pattern_size,
        cv2.CALIB_CB_ADAPTIVE_THRESH +
        cv2.CALIB_CB_NORMALIZE_IMAGE
    )

    if not ret:
        print(f"[WARN] Corners not found: {img_path.name}")
        continue

    corners = cv2.cornerSubPix(
        gray,
        corners,
        (11, 11),
        (-1, -1),
        criteria
    )

    objpoints.append(objp.copy())
    imgpoints.append(corners.reshape(-1, 1, 2))

    print(f"[OK] {img_path.name}")

# -------------------------------------------------
# Validate
# -------------------------------------------------
if len(objpoints) < 10:
    raise RuntimeError("Not enough valid images for calibration (need >= 10)")

# -------------------------------------------------
# Fisheye calibration
# -------------------------------------------------
K = np.zeros((3, 3))
D = np.zeros((4, 1))

flags = (
    cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC |
    cv2.fisheye.CALIB_CHECK_COND |
    cv2.fisheye.CALIB_FIX_SKEW
)

rms, K, D, rvecs, tvecs = cv2.fisheye.calibrate(
    objpoints,
    imgpoints,
    IMAGE_SIZE,
    K,
    D,
    None,
    None,
    flags=flags,
    criteria=criteria
)

# -------------------------------------------------
# Save results
# -------------------------------------------------
np.savez(
    OUT_DIR / "fisheye_intrinsics.npz",
    K=K,
    D=D,
    rms=rms
)

print("\n===== FISHEYE CALIBRATION DONE =====")
print(f"RMS reprojection error: {rms:.6f}")
print("Camera matrix K:\n", K)
print("Distortion coefficients D:\n", D.ravel())
print(f"Saved to: {OUT_DIR / 'fisheye_intrinsics.npz'}")
