#!/usr/bin/env python3
"""
Launch file for the Strawberry Picker ROS2 system
"""

import os
import launch
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Get package directory
    package_dir = get_package_share_directory('strawberry_picker_control')

    # Declare launch arguments
    detection_model_arg = DeclareLaunchArgument(
        'detection_model',
        default_value=os.path.join(package_dir, '../../../model/weights/best.pt'),
        description='Path to YOLOv8 detection model'
    )

    classification_model_arg = DeclareLaunchArgument(
        'classification_model',
        default_value=os.path.join(package_dir, '../../../model/ripeness_classifier.h5'),
        description='Path to ripeness classification model'
    )

    camera_topic_arg = DeclareLaunchArgument(
        'camera_topic',
        default_value='/camera/image_raw',
        description='Camera image topic'
    )

    use_sim_arg = DeclareLaunchArgument(
        'use_sim',
        default_value='false',
        description='Use simulation instead of real hardware'
    )

    # Vision processor node
    vision_processor = Node(
        package='strawberry_picker_control',
        executable='vision_processor',
        name='vision_processor',
        parameters=[{
            'detection_model_path': LaunchConfiguration('detection_model'),
            'classification_model_path': LaunchConfiguration('classification_model'),
            'camera_topic': LaunchConfiguration('camera_topic'),
        }],
        output='screen'
    )

    # Coordinate transformer node
    coordinate_transformer = Node(
        package='strawberry_picker_control',
        executable='coordinate_transformer',
        name='coordinate_transformer',
        output='screen'
    )

    # Arduino bridge node (only if not using simulation)
    arduino_bridge = Node(
        package='strawberry_picker_control',
        executable='arduino_bridge',
        name='arduino_bridge',
        condition=launch.conditions.UnlessCondition(LaunchConfiguration('use_sim')),
        output='screen'
    )

    return LaunchDescription([
        detection_model_arg,
        classification_model_arg,
        camera_topic_arg,
        use_sim_arg,
        vision_processor,
        coordinate_transformer,
        arduino_bridge,
    ])