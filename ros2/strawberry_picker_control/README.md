# Strawberry Picker Control - ROS2 Package

This ROS2 package provides a complete robotic strawberry harvesting system with computer vision, motion planning, and hardware control integration.

## Features

- **Computer Vision**: Real-time strawberry detection and ripeness classification using YOLOv8
- **Coordinate Transformation**: Camera-to-robot coordinate system transformations
- **Robot Control**: Integration with MoveIt2 for motion planning and execution
- **Hardware Interface**: ROS2 bridge to Arduino-based robotic arm control
- **Visualization**: RViz integration for system monitoring and debugging
- **Simulation**: Gazebo simulation support for testing without physical hardware

## Installation

### Prerequisites

- ROS2 Humble or newer
- Python 3.8+
- OpenCV
- PyTorch/TensorFlow
- MoveIt2
- Gazebo (optional, for simulation)

### Build Instructions

```bash
# Source ROS2
source /opt/ros/humble/setup.bash

# Create workspace if needed
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Copy or clone the package
cp -r /path/to/strawberryPicker/ros2/strawberry_picker_control .

# Build the package
cd ~/ros2_ws
colcon build --packages-select strawberry_picker_control

# Source the workspace
source install/setup.bash
```

## Usage

### Launch the System

```bash
# Launch the complete system
ros2 launch strawberry_picker_control strawberry_picker.launch.py

# Launch with custom parameters
ros2 launch strawberry_picker_control strawberry_picker.launch.py \
  detection_model:=/path/to/model.pt \
  camera_topic:=/usb_cam/image_raw \
  use_sim:=true
```

### ROS2 Nodes

#### Vision Processor (`vision_processor`)
- **Subscribes**: `camera/image_raw` (sensor_msgs/Image)
- **Publishes**:
  - `strawberry_detections` (strawberry_picker_control/StrawberryDetection)
  - `strawberry_targets` (strawberry_picker_control/StrawberryTarget)
  - `strawberry_markers` (visualization_msgs/MarkerArray)
  - `annotated_image` (sensor_msgs/Image)
- **Services**: `get_strawberry_targets` (strawberry_picker_control/GetStrawberryTargets)

#### Coordinate Transformer (`coordinate_transformer`)
- **Subscribes**: `strawberry_targets` (strawberry_picker_control/StrawberryTarget)
- **Publishes**: `transformed_strawberry_targets` (strawberry_picker_control/StrawberryTarget)
- **Services**: `calibrate_camera` (strawberry_picker_control/CalibrateCamera)

#### Arduino Bridge (`arduino_bridge`)
- **Subscribes**:
  - `target_pose` (geometry_msgs/Pose)
  - `gripper_command` (std_msgs/Bool)
- **Publishes**:
  - `arduino_status` (strawberry_picker_control/PickingStatus)
  - `arduino_connected` (std_msgs/Bool)

### Configuration

Edit `config/default.yaml` to customize system parameters:

```yaml
vision_processor:
  detection_model_path: "model/weights/best.pt"
  confidence_threshold: 0.5

arduino_bridge:
  port: "/dev/ttyUSB0"
  baudrate: 115200
```

### RViz Visualization

```bash
# Launch RViz with the strawberry picker configuration
ros2 launch strawberry_picker_control strawberry_picker.launch.py use_rviz:=true
```

## Architecture

```
Camera → Vision Processor → Coordinate Transformer → Robot Controller → Arduino Bridge → Hardware
   ↓           ↓                    ↓                    ↓              ↓
Annotated  Strawberry     Transformed         Motion      Serial
Images    Detections     Targets            Planning    Commands
```

## Custom Messages

### StrawberryDetection
Contains individual strawberry detection results with bounding box, confidence, and ripeness classification.

### StrawberryTarget
Represents a picking target with 3D position and priority score.

### PickingStatus
System status including statistics, current state, and error information.

## Services

### GetStrawberryTargets
Returns current detected strawberry targets for picking.

### CalibrateCamera
Triggers camera calibration procedure.

## Actions

### PickStrawberry
Coordinated action for picking a single strawberry with feedback and result reporting.

## Simulation

For testing without physical hardware:

```bash
# Launch in simulation mode
ros2 launch strawberry_picker_control strawberry_picker.launch.py use_sim:=true

# Launch Gazebo simulation
ros2 launch strawberry_picker_control gazebo.launch.py
```

## Troubleshooting

### Common Issues

1. **Camera not detected**: Check camera topic and permissions
2. **Arduino connection failed**: Verify port and baudrate settings
3. **Model loading error**: Ensure model paths are correct and accessible
4. **TF transform errors**: Check coordinate frame configurations

### Debugging

```bash
# Check active nodes
ros2 node list

# Check topics
ros2 topic list

# Monitor system status
ros2 topic echo /arduino_status

# View detection results
ros2 topic echo /strawberry_detections
```

## Contributing

1. Follow ROS2 development guidelines
2. Use descriptive commit messages
3. Update documentation for new features
4. Test changes in both simulation and hardware

## License

MIT License - see LICENSE file for details.