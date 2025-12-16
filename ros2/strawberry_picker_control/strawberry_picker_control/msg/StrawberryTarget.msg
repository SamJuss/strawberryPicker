# Message for strawberry picking targets with 3D coordinates
std_msgs/Header header

# Detection information
StrawberryDetection detection

# 3D position in robot base frame
geometry_msgs/Point position

# Priority score for picking (higher = better target)
float32 priority

# Target status
string status  # "pending", "selected", "picked", "failed"