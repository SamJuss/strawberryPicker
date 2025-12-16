#!/usr/bin/env python3
"""
ROS2 Arduino Bridge Node

Provides ROS2 interface to the existing Arduino-based robotic arm control system.
Handles serial communication and translates ROS2 commands to Arduino protocol.
"""

import rclpy
from rclpy.node import Node
import serial
import time
from typing import Optional
import threading
from pathlib import Path

# Import existing Arduino bridge
import sys
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
from src.arduino_bridge import ArduinoBridge

# ROS2 messages
from geometry_msgs.msg import Pose
from std_msgs.msg import Bool, String
from strawberry_picker_control.msg import PickingStatus


class ArduinoBridgeNode(Node):
    """ROS2 node for Arduino robotic arm control"""

    def __init__(self):
        super().__init__('arduino_bridge')

        # Declare parameters
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('timeout', 1.0)
        self.declare_parameter('max_retries', 3)

        # Get parameters
        self.port = self.get_parameter('port').value
        self.baudrate = self.get_parameter('baudrate').value
        self.timeout = self.get_parameter('timeout').value
        self.max_retries = self.get_parameter('max_retries').value

        # Initialize Arduino bridge
        try:
            self.arduino = ArduinoBridge(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.get_logger().info(f'Arduino bridge initialized on {self.port}')
        except Exception as e:
            self.get_logger().error(f'Failed to initialize Arduino bridge: {e}')
            self.arduino = None

        # Subscribers
        self.pose_sub = self.create_subscription(
            Pose,
            'target_pose',
            self.pose_callback,
            10
        )

        self.gripper_sub = self.create_subscription(
            Bool,
            'gripper_command',
            self.gripper_callback,
            10
        )

        # Publishers
        self.status_pub = self.create_publisher(
            PickingStatus,
            'arduino_status',
            10
        )

        self.connection_pub = self.create_publisher(
            Bool,
            'arduino_connected',
            10
        )

        # State
        self.is_connected = False
        self.last_command_time = 0.0

        # Connection monitoring timer
        self.timer = self.create_timer(1.0, self.connection_check_callback)

        # Try initial connection
        self.connect_arduino()

    def connect_arduino(self):
        """Attempt to connect to Arduino"""
        if self.arduino is None:
            return False

        try:
            success = self.arduino.connect()
            if success:
                self.arduino.initialize_servos()
                self.is_connected = True
                self.get_logger().info('Successfully connected to Arduino')
                self.connection_pub.publish(Bool(data=True))
                return True
            else:
                self.is_connected = False
                self.connection_pub.publish(Bool(data=False))
                self.get_logger().warning('Failed to connect to Arduino')
                return False
        except Exception as e:
            self.is_connected = False
            self.connection_pub.publish(Bool(data=False))
            self.get_logger().error(f'Arduino connection error: {e}')
            return False

    def pose_callback(self, msg):
        """Handle pose commands for robot arm"""
        if not self.is_connected:
            self.get_logger().warning('Arduino not connected, ignoring pose command')
            return

        try:
            # Extract position
            x, y, z = msg.position.x, msg.position.y, msg.position.z

            self.get_logger().info(f'Moving to position: ({x:.3f}, {y:.3f}, {z:.3f})')

            # Send command to Arduino
            success = self.arduino.move_to_position(x, y, z)

            if success:
                self.last_command_time = time.time()
                self.get_logger().info('Position command sent successfully')
            else:
                self.get_logger().error('Failed to send position command')

        except Exception as e:
            self.get_logger().error(f'Error in pose callback: {e}')

    def gripper_callback(self, msg):
        """Handle gripper open/close commands"""
        if not self.is_connected:
            self.get_logger().warning('Arduino not connected, ignoring gripper command')
            return

        try:
            if msg.data:
                # Close gripper
                self.get_logger().info('Closing gripper')
                success = self.arduino.close_gripper()
            else:
                # Open gripper
                self.get_logger().info('Opening gripper')
                success = self.arduino.open_gripper()

            if success:
                self.last_command_time = time.time()
                self.get_logger().info('Gripper command sent successfully')
            else:
                self.get_logger().error('Failed to send gripper command')

        except Exception as e:
            self.get_logger().error(f'Error in gripper callback: {e}')

    def connection_check_callback(self):
        """Periodic connection status check"""
        # Publish connection status
        self.connection_pub.publish(Bool(data=self.is_connected))

        # Publish status message
        status = PickingStatus()
        status.header.stamp = self.get_clock().now().to_msg()
        status.system_state = 'connected' if self.is_connected else 'disconnected'
        status.last_error = 'No errors' if self.is_connected else 'Arduino not connected'

        self.status_pub.publish(status)

        # Try to reconnect if disconnected
        if not self.is_connected:
            self.get_logger().debug('Attempting to reconnect to Arduino...')
            self.connect_arduino()

    def send_custom_command(self, command: str) -> bool:
        """Send custom command to Arduino"""
        if not self.is_connected or self.arduino is None:
            return False

        try:
            # Use the Arduino bridge's send_command method
            return self.arduino.send_command(command)
        except Exception as e:
            self.get_logger().error(f'Error sending custom command: {e}')
            return False

    def get_status(self) -> dict:
        """Get Arduino bridge status"""
        return {
            'connected': self.is_connected,
            'port': self.port,
            'baudrate': self.baudrate,
            'last_command_time': self.last_command_time
        }


def main(args=None):
    rclpy.init(args=args)
    node = ArduinoBridgeNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.arduino:
            node.arduino.disconnect()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()