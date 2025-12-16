# Message for individual strawberry detection results
std_msgs/Header header

# Bounding box coordinates (x, y, width, height)
float32 x
float32 y
float32 width
float32 height

# Detection confidence
float32 confidence

# Ripeness classification
string ripeness_class
float32 ripeness_confidence

# Center point in pixel coordinates
float32 center_x
float32 center_y