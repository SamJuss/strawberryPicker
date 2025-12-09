import cv2
import sys

img_path = sys.argv[1] if len(sys.argv) > 1 else 'cama/WIN_20251205_14_52_55_Pro.jpg'
img = cv2.imread(img_path)
if img is None:
    print(f"Failed to read {img_path}")
    sys.exit(1)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

patterns = [(9,6), (8,6), (7,6), (6,9), (6,8), (6,7), (7,9), (8,9), (9,7), (10,7), (7,10), (11,8), (8,11), (5,8), (8,5)]
for (w,h) in patterns:
    ret, corners = cv2.findChessboardCorners(gray, (w,h), flags=cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE)
    if ret:
        print(f"Pattern ({w},{h}) found!")
        # refine
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners_refined = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        print(f"First corner: {corners_refined[0]}")
        break
else:
    print("No pattern found.")