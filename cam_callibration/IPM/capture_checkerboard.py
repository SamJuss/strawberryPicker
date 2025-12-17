import cv2
import os

# === CONFIG ===
CAMERA_ID = 1  # try 0, 1, 2 if needed
SAVE_DIR = "calib_images"
CHESSBOARD_ROWS = 8      # number of squares
CHESSBOARD_COLS = 10    # number of squares
CHECKERBOARD = (CHESSBOARD_COLS - 1, CHESSBOARD_ROWS - 1)  # (9,7)

os.makedirs(SAVE_DIR, exist_ok=True)

print("[INFO] OpenCV version:", cv2.__version__)
print(f"[INFO] Trying to open camera index {CAMERA_ID}...")

# On Windows, use CAP_DSHOW to avoid some backend issues
cap = cv2.VideoCapture(CAMERA_ID)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    raise RuntimeError(
        f"Cannot open camera at index {CAMERA_ID}. "
        "Try another index (0, 1, 2) or check Windows camera privacy settings."
    )

print("[INFO] Camera opened successfully.")
print("[INFO] Press SPACE to save frame when checkerboard is detected.")
print("[INFO] Press ESC to quit.")

img_count = 0

def display_frame(frame):
    # Resize frame for display if too large
    max_width = 1280
    if frame.shape[1] > max_width:
        scale = max_width / frame.shape[1]
        frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    return frame

while True:
    ret, frame = cap.read()
    if not ret:
        print("[WARN] Failed to grab frame. Exiting loop.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ret_corners, corners = cv2.findChessboardCorners(
        gray,
        CHECKERBOARD,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH +
              cv2.CALIB_CB_FAST_CHECK +
              cv2.CALIB_CB_NORMALIZE_IMAGE
    )

    draw_frame = frame.copy()
    if ret_corners:
        cv2.drawChessboardCorners(draw_frame, CHECKERBOARD, corners, ret_corners)
        cv2.putText(draw_frame, "Checkerboard detected", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    else:
        cv2.putText(draw_frame, "NO checkerboard", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
    draw_frame = display_frame(draw_frame)

    cv2.imshow("Capture checkerboard", draw_frame)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC
        break
    elif key == 32 and ret_corners:  # SPACE + valid pattern
        img_path = os.path.join(SAVE_DIR, f"calib_{img_count:03d}.png")
        cv2.imwrite(img_path, frame)
        print(f"[SAVED] {img_path}")
        img_count += 1

cap.release()
cv2.destroyAllWindows()
