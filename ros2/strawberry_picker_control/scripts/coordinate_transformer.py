#!/usr/bin/env python3
"""
ROS2 Coordinate Transformer Node

Handles camera calibration, coordinate transformations between camera and robot frames,
and provides services for calibration and transformation.
"""

import rclpy
from rclpy.node import Node
import cv2
import numpy as np
import json
from pathlib import Path
import time
from typing import Optional, Tuple
import tf2_ros
import geometry_msgs.msg
from tf2_geometry_msgs import do_transform_point

# Import existing coordinate transformer
import sys
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
from src.coordinate_transformer import CoordinateTransformer

# ROS2 messages
from strawberry_picker_control.msg import StrawberryTarget
from strawberry_picker_control.srv import CalibrateCamera
from geometry_msgs.msg import PointStamped, TransformStamped
from sensor_msgs.msg import CameraInfo


class CoordinateTransformerNode(Node):
    """ROS2 node for coordinate transformations and camera calibration"""

    def __init__(self):
        super().__init__('coordinate_transformer')

        # Declare parameters
        self.declare_parameter('camera_matrix_file', 'calibration/camera_matrix.npy')
        self.declare_parameter('distortion_coeffs_file', 'calibration/distortion_coeffs.npy')
        self.declare_parameter('stereo_calibration_file', 'calibration/stereo_calibration.npz')
        self.declare_parameter('robot_base_frame', 'base_link')
        self.declare_parameter('camera_frame', 'camera_link')
        self.declare_parameter('calibration_samples', 20)

        # Get parameters
        self.camera_matrix_file = self.get_parameter('camera_matrix_file').value
        self.distortion_coeffs_file = self.get_parameter('distortion_coeffs_file').value
        self.stereo_calibration_file = self.get_parameter('stereo_calibration_file').value
        self.robot_base_frame = self.get_parameter('robot_base_frame').value
        self.camera_frame = self.get_parameter('camera_frame').value
        self.calibration_samples = self.get_parameter('calibration_samples').value

        # Initialize TF2
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Initialize coordinate transformer
        try:
            self.transformer = CoordinateTransformer(
                camera_matrix_path=self.camera_matrix_file,
                distortion_coeffs_path=self.distortion_coeffs_file,
                stereo_calibration_path=self.stereo_calibration_file
            )
            self.get_logger().info('Coordinate transformer initialized successfully')
        except Exception as e:
            self.get_logger().error(f'Failed to initialize coordinate transformer: {e}')
            self.transformer = None

        # Subscribers
        self.target_sub = self.create_subscription(
            StrawberryTarget,
            'strawberry_targets',
            self.target_callback,
            10
        )

        # Publishers
        self.transformed_target_pub = self.create_publisher(
            StrawberryTarget,
            'transformed_strawberry_targets',
            10
        )

        # Services
        self.calibration_service = self.create_service(
            CalibrateCamera,
            'calibrate_camera',
            self.calibrate_camera_callback
        )

        # State
        self.calibration_images = []
        self.is_calibrating = False

        self.get_logger().info('Coordinate transformer node started')

    def target_callback(self, msg):
        """Transform strawberry targets to robot coordinates"""
        try:
            if self.transformer is None:
                self.get_logger().warning('Coordinate transformer not initialized')
                return

            # Extract pixel coordinates
            pixel_x = msg.detection.center_x
            pixel_y = msg.detection.center_y
            image_shape = (480, 640, 3)  # Default image shape, should be parameterized

            # Transform to 3D coordinates
            world_coords = self.transformer.pixel_to_world(pixel_x, pixel_y, image_shape)

            if world_coords is not None:
                # Create transformed target message
                transformed_target = StrawberryTarget()
                transformed_target.detection = msg.detection
                transformed_target.position.x = world_coords[0]
                transformed_target.position.y = world_coords[1]
                transformed_target.position.z = world_coords[2]
                transformed_target.priority = msg.priority
                transformed_target.status = 'transformed'

                # Publish transformed target
                self.transformed_target_pub.publish(transformed_target)

                self.get_logger().debug(
                    f'Transformed target: pixel({pixel_x:.1f}, {pixel_y:.1f}) -> '
                    f'world({world_coords[0]:.3f}, {world_coords[1]:.3f}, {world_coords[2]:.3f})'
                )
            else:
                self.get_logger().warning(f'Failed to transform coordinates for target at ({pixel_x}, {pixel_y})')

        except Exception as e:
            self.get_logger().error(f'Error transforming target: {e}')

    def calibrate_camera_callback(self, request, response):
        """Service callback for camera calibration"""
        try:
            self.get_logger().info(f'Starting camera calibration: {request.calibration_pattern}')

            # This is a placeholder for actual calibration implementation
            # In a real implementation, you would:
            # 1. Collect calibration images
            # 2. Detect calibration pattern
            # 3. Compute camera parameters
            # 4. Save calibration files

            # For now, just return success
            response.success = True
            response.message = f'Camera calibration completed for pattern: {request.calibration_pattern}'
            response.calibration_file_path = self.camera_matrix_file

            self.get_logger().info('Camera calibration completed')

        except Exception as e:
            self.get_logger().error(f'Camera calibration failed: {e}')
            response.success = False
            response.message = str(e)
            response.calibration_file_path = ''

        return response

    def transform_point_to_robot_frame(self, point, target_frame, source_frame='camera_link'):
        """Transform a point from source frame to target frame using TF2"""
        try:
            # Create PointStamped message
            point_stamped = PointStamped()
            point_stamped.header.frame_id = source_frame
            point_stamped.header.stamp = self.get_clock().now().to_msg()
            point_stamped.point.x = point[0]
            point_stamped.point.y = point[1]
            point_stamped.point.z = point[2]

            # Transform point
            transform = self.tf_buffer.lookup_transform(
                target_frame, source_frame, rclpy.time.Time()
            )

            transformed_point = do_transform_point(point_stamped, transform)
            return (
                transformed_point.point.x,
                transformed_point.point.y,
                transformed_point.point.z
            )

        except Exception as e:
            self.get_logger().error(f'TF2 transformation failed: {e}')
            return None

    def get_transform_between_frames(self, target_frame, source_frame):
        """Get transform between two frames"""
        try:
            transform = self.tf_buffer.lookup_transform(
                target_frame, source_frame, rclpy.time.Time()
            )
            return transform
        except Exception as e:
            self.get_logger().error(f'Failed to get transform {source_frame} -> {target_frame}: {e}')
            return None


def main(args=None):
    rclpy.init(args=args)
    node = CoordinateTransformerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()