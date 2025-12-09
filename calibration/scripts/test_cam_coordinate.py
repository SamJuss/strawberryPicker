import cv2
import numpy as np

# Load the matrices from the file or hardcoded
camera1_matrix = np.array([
    [2263.50596,      0.0,        964.761094],
    [0.0,         2275.52656,     698.162562],
    [0.0,              0.0,           1.0    ]
], dtype=np.float32)

camera1_dist = np.array([-0.40170703, 0.5627054, 0.00803042, -0.00481173, -0.58891806], dtype=np.float32)

camera2_matrix = np.array([
    [1190.33622,   0.0,        1384.23659],
    [0.0,          1195.47438,  833.37699],
    [0.0,              0.0,         1.0  ]
], dtype=np.float32)

camera2_dist = np.array([-0.35899454, 0.11213625, -0.00363389, -0.00311402, -0.01137052], dtype=np.float32)

# Test undistortion on a dummy image
dummy = np.zeros((720, 1280, 3), dtype=np.uint8)
und1 = cv2.undistort(dummy, camera1_matrix, camera1_dist)
und2 = cv2.undistort(dummy, camera2_matrix, camera2_dist)
print("Undistortion test passed.")