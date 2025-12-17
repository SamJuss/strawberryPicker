import glob
import os
import cv2
import numpy as np

# === CONFIG (must match the real board) ===
CHESSBOARD_ROWS = 8      # number of SQUARES (not corners)
CHESSBOARD_COLS = 10     # number of SQUARES (not corners)
CHECKERBOARD = (CHESSBOARD_COLS - 1, CHESSBOARD_ROWS - 1)  # (9, 7)
SQUARE_SIZE = 0.02  # meters (20 mm)
IMAGE_DIR = "calib_images"
OUTPUT_FILE = "camera_fisheye.npz"

# === Prepare object points (3D points in board coordinates) ===
# Shape: (1, N, 3)
objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

objpoints = []  # list of 1xNx3
imgpoints = []  # list of 1xNx2
img_shape = None

image_paths = sorted(glob.glob(os.path.join(IMAGE_DIR, "*.png")) +
                     glob.glob(os.path.join(IMAGE_DIR, "*.jpg")) +
                     glob.glob(os.path.join(IMAGE_DIR, "*.jpeg")))

if not image_paths:
    raise RuntimeError(f"No images found in {IMAGE_DIR}. Did you run capture_checkerboard.py?")

print(f"[INFO] Found {len(image_paths)} images.")

for fname in image_paths:
    img = cv2.imread(fname)
    if img is None:
        print(f"[WARN] Could not read {fname}, skipping.")
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if img_shape is None:
        img_shape = gray.shape[::-1]
    else:
        if img_shape != gray.shape[::-1]:
            raise RuntimeError("All images must have the same resolution.")

    ret_corners, corners = cv2.findChessboardCorners(
        gray,
        CHECKERBOARD,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
    )

    if ret_corners:
        # refine corner locations
        corners_subpix = cv2.cornerSubPix(
            gray,
            corners,
            winSize=(11, 11),
            zeroZone=(-1, -1),
            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
        )
        objpoints.append(objp)
        imgpoints.append(corners_subpix.reshape(1, -1, 2))
        print(f"[OK] {fname} used.")
    else:
        print(f"[FAIL] No checkerboard found in {fname}, skipping.")

if len(objpoints) < 10:
    raise RuntimeError(f"Too few valid images ({len(objpoints)}). Get more diverse views and try again.")

# === Fisheye calibration ===
N_OK = len(objpoints)
print(f"[INFO] Using {N_OK} valid images for calibration.")

K = np.zeros((3, 3))
D = np.zeros((4, 1))
rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for _ in range(N_OK)]
tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for _ in range(N_OK)]

rms, K, D, rvecs, tvecs = cv2.fisheye.calibrate(
    objpoints,
    imgpoints,
    img_shape,
    K,
    D,
    rvecs,
    tvecs,
    flags=cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC |
          cv2.fisheye.CALIB_CHECK_COND |
          cv2.fisheye.CALIB_FIX_SKEW,
    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6)
)

print("\n=== Calibration result (fisheye) ===")
print("RMS reprojection error:", rms)
print("K (intrinsic matrix):\n", K)
print("D (distortion coeffs):\n", D)

# === Parse fx, fy, cx, cy and k1..k4 ===
fx = K[0, 0]
fy = K[1, 1]
cx = K[0, 2]
cy = K[1, 2]
k1, k2, k3, k4 = D.ravel()

print("\n=== Parsed parameters ===")
print(f"fx = {fx}")
print(f"fy = {fy}")
print(f"cx = {cx}")
print(f"cy = {cy}")
print(f"k1 = {k1}")
print(f"k2 = {k2}")
print(f"k3 = {k3}")
print(f"k4 = {k4}")

# === Save to file ===
np.savez(
    OUTPUT_FILE,
    K=K,
    D=D,
    img_shape=img_shape,
    rms=rms,
    fx=fx,
    fy=fy,
    cx=cx,
    cy=cy,
    k1=k1,
    k2=k2,
    k3=k3,
    k4=k4,
)

print(f"\n[SAVED] Calibration data written to {OUTPUT_FILE}")

# === Quick undistortion test ===
test_img = cv2.imread(image_paths[0])
h, w = test_img.shape[:2]

map1, map2 = cv2.fisheye.initUndistortRectifyMap(
    K, D, np.eye(3), K, (w, h), cv2.CV_16SC2
)
undistorted = cv2.remap(test_img, map1, map2, interpolation=cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_CONSTANT)

cv2.imshow("Original", test_img)
cv2.imshow("Undistorted (fisheye)", undistorted)
cv2.waitKey(0)
cv2.destroyAllWindows()
