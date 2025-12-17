import cv2
import numpy as np
from pathlib import Path

# ================= SETTINGS =================
IMG_DIR = Path(
    r"C:\Users\ASUS\Documents\campus related\5. fifth semester\Macchine Learning\kamera kalibrasi\pinhole_images"
)

OUT_FILE = Path("calibration/camW_intrinsics.npz")

ROWS = 7
COLS = 9
SQUARE = 0.02
# ===========================================

pattern_size = (COLS, ROWS)

objp = np.zeros((ROWS * COLS, 3), np.float32)
objp[:, :2] = np.mgrid[0:COLS, 0:ROWS].T.reshape(-1, 2)
objp *= SQUARE

objpoints = []
imgpoints = []

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)

for img_path in sorted(IMG_DIR.glob("*.jpg")):
    img = cv2.imread(str(img_path))
    if img is None:
        print("[WARN] Cannot read:", img_path)
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ok, corners = cv2.findChessboardCorners(gray, pattern_size)
    if not ok:
        continue

    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

    objpoints.append(objp)
    imgpoints.append(corners)

print("[INFO] Images used:", len(objpoints))
assert len(objpoints) >= 10, "Not enough valid images"

ret, K, dist, _, _ = cv2.calibrateCamera(
    objpoints,
    imgpoints,
    gray.shape[::-1],
    None,
    None
)

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
np.savez(OUT_FILE, K=K, dist=dist, rms=ret)

print("[DONE] camW intrinsics saved to:", OUT_FILE)
print("RMS:", ret)
print("K:\n", K)
print("dist:", dist.ravel())
