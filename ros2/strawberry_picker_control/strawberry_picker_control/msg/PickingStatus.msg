# Message for overall picking system status
std_msgs/Header header

# System state
string system_state  # "idle", "detecting", "picking", "error"

# Statistics
uint32 total_detections
uint32 ripe_strawberries
uint32 successful_picks
uint32 failed_picks

# Performance metrics
float32 average_processing_time
float32 success_rate

# Current target information
StrawberryTarget current_target

# Error information
string last_error
uint32 error_count