# Strawberry Picker

This repository contains the code and documentation for a robotic arm designed to pick strawberries efficiently. The system is built using the Robot Operating System (ROS) to ensure modularity and scalability.

## Features

- **Precision Picking**: The robotic arm is equipped with sensors to identify and pick ripe strawberries without damaging them.
- **ROS Integration**: Utilizes ROS for communication between different components of the system.
- **Customizable**: Easily adaptable for different environments and strawberry varieties.

## Requirements

- ROS (tested on ROS Noetic)
- Python 3.x
- OpenCV (for image processing)
- Hardware: Robotic arm, camera, and gripper

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/strawberryPicker.git
    cd strawberryPicker
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your ROS workspace:
    ```bash
    mkdir -p ~/catkin_ws/src
    cp -r strawberryPicker ~/catkin_ws/src/
    cd ~/catkin_ws
    catkin_make
    source devel/setup.bash
    ```

## Usage

1. Launch the ROS nodes:
    ```bash
    roslaunch strawberry_picker picker.launch
    ```

2. Monitor the system using RViz:
    ```bash
    rosrun rviz rviz
    ```

3. Adjust parameters in the `config/` directory to optimize performance for your setup.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- ROS community for their extensive documentation and support.
- Open-source contributors for libraries and tools used in this project.
- University guidance for project development.
