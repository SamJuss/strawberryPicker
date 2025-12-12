#!/usr/bin/env python3
"""
ROS2 Node for Strawberry Picker Arm Control with 4DOF Inverse Kinematics

This node subscribes to detection messages and converts pixel coordinates to robot joint angles
using closed-form inverse kinematics for a 4DOF arm (base, shoulder, elbow, wrist).
"""

import rclpy
from rclpy.node import Node
from yolov8_cam.msg import Detection
import serial
import numpy as np
import math
import time

class ArmControllerNode(Node):
    def __init__(self):
        super().__init__('arm_controller_node')

        # Robot parameters (from MATLAB simulation)
        self.L1 = 0.00    # base/shoulder offset (m)
        self.L2 = 0.20    # upper arm (m)
        self.L3 = 0.145   # forearm (m)
        self.L4 = 0.080   # wrist/tool length (m)

        # Workspace parameters (adjust based on your setup)
        self.workspace_width = 0.6   # meters
        self.workspace_height = 0.4  # meters
        self.image_width = 1280      # pixels
        self.image_height = 720      # pixels

        # Serial communication
        self.serial_port = '/dev/ttyUSB0'  # Adjust as needed
        self.baud_rate = 9600
        self.serial_conn = None

        # Initialize serial connection
        self.init_serial()

        # Subscribe to detection messages
        self.subscription = self.create_subscription(
            Detection,
            'detections',
            self.detection_callback,
            10
        )

        self.get_logger().info('Arm Controller Node initialized')

    def init_serial(self):
        try:
            self.serial_conn = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            self.get_logger().info(f'Serial connection established on {self.serial_port}')
        except serial.SerialException as e:
            self.get_logger().error(f'Failed to open serial port: {e}')
            self.serial_conn = None

    def pixel_to_world(self, x_pixel, y_pixel):
        """
        Convert pixel coordinates to world coordinates (meters)
        Origin at image center, x right, y up
        """
        # Image center
        cx = self.image_width / 2
        cy = self.image_height / 2

        # Convert to centered coordinates
        x_centered = x_pixel - cx
        y_centered = cy - y_pixel  # y up in world, down in image

        # Scale to meters
        x_world = x_centered * (self.workspace_width / self.image_width)
        y_world = y_centered * (self.workspace_height / self.image_height)

        # Assume z = 0 for ground plane (adjust if needed)
        z_world = 0.0

        return x_world, y_world, z_world

    def fk4(self, theta):
        """
        Forward kinematics for 4DOF arm
        theta: [base, shoulder, elbow, wrist] in radians
        Returns: end-effector position [x, y, z]
        """
        b, s, e, w = theta

        # Joint positions
        P0 = np.array([0, 0, 0])
        P1 = np.array([0, 0, self.L1])

        # Shoulder joint
        P2 = np.array([
            np.cos(b) * self.L2 * np.cos(s),
            np.sin(b) * self.L2 * np.cos(s),
            self.L1 + self.L2 * np.sin(s)
        ])

        # Elbow joint
        P3 = np.array([
            np.cos(b) * (self.L2 * np.cos(s) + self.L3 * np.cos(s + e)),
            np.sin(b) * (self.L2 * np.cos(s) + self.L3 * np.cos(s + e)),
            self.L1 + self.L2 * np.sin(s) + self.L3 * np.sin(s + e)
        ])

        # Wrist/End-effector
        P4 = np.array([
            np.cos(b) * (self.L2 * np.cos(s) + self.L3 * np.cos(s + e) + self.L4 * np.cos(s + e + w)),
            np.sin(b) * (self.L2 * np.cos(s) + self.L3 * np.cos(s + e) + self.L4 * np.cos(s + e + w)),
            self.L1 + self.L2 * np.sin(s) + self.L3 * np.sin(s + e) + self.L4 * np.sin(s + e + w)
        ])

        return P4

    def jac4(self, theta):
        """
        Geometric Jacobian for 4DOF arm (3x4)
        """
        b, s, e, w = theta

        # Helper terms
        A = self.L2 * np.cos(s) + self.L3 * np.cos(s + e) + self.L4 * np.cos(s + e + w)
        B_s = self.L2 * np.cos(s) + self.L3 * np.cos(s + e) + self.L4 * np.cos(s + e + w)
        B_e = self.L3 * np.cos(s + e) + self.L4 * np.cos(s + e + w)
        B_w = self.L4 * np.cos(s + e + w)

        A_s = -self.L2 * np.sin(s) - self.L3 * np.sin(s + e) - self.L4 * np.sin(s + e + w)
        A_e = -self.L3 * np.sin(s + e) - self.L4 * np.sin(s + e + w)
        A_w = -self.L4 * np.sin(s + e + w)

        # Jacobian columns
        J11 = -np.sin(b) * A
        J21 = np.cos(b) * A
        J31 = 0

        J12 = np.cos(b) * A_s
        J22 = np.sin(b) * A_s
        J32 = B_s

        J13 = np.cos(b) * A_e
        J23 = np.sin(b) * A_e
        J33 = B_e

        J14 = np.cos(b) * A_w
        J24 = np.sin(b) * A_w
        J34 = B_w

        J = np.array([
            [J11, J12, J13, J14],
            [J21, J22, J23, J24],
            [J31, J32, J33, J34]
        ])

        return J

    def ik4(self, target, theta_prev=None):
        """
        4DOF Inverse Kinematics using closed-form solution
        target: [x, y, z] in meters
        Returns: [base, shoulder, elbow, wrist] in radians or None if unreachable
        """
        x, y, z = target

        # Base angle
        b = np.arctan2(y, x)

        # Planar radius and shoulder offset
        r = np.hypot(x, y)
        z2 = z - self.L1

        # Effective link length (L3 + L4)
        L3_eff = self.L3 + self.L4

        # Law of cosines
        D = (r**2 + z2**2 - self.L2**2 - L3_eff**2) / (2 * self.L2 * L3_eff)
        if abs(D) > 1:
            return None
        D = np.clip(D, -1, 1)

        # Elbow angles (up and down)
        e_up = np.arctan2(np.sqrt(max(0, 1 - D**2)), D)
        e_down = np.arctan2(-np.sqrt(max(0, 1 - D**2)), D)

        # Shoulder angles
        s_up = np.arctan2(z2, r) - np.arctan2(L3_eff * np.sin(e_up), self.L2 + L3_eff * np.cos(e_up))
        s_down = np.arctan2(z2, r) - np.arctan2(L3_eff * np.sin(e_down), self.L2 + L3_eff * np.cos(e_down))

        # Two solutions
        theta1 = np.array([b, s_up, e_up, 0])      # wrist = 0
        theta2 = np.array([b, s_down, e_down, 0])  # wrist = 0

        # Choose solution closest to previous pose
        if theta_prev is not None:
            d1 = np.linalg.norm(self.angle_diff(theta1, theta_prev))
            d2 = np.linalg.norm(self.angle_diff(theta2, theta_prev))
            theta_ik = theta1 if d1 < d2 else theta2
        else:
            theta_ik = theta2  # Default to elbow-down

        return theta_ik

    def angle_diff(self, a, b):
        """Angular difference with wrap-around"""
        diff = a - b
        return np.arctan2(np.sin(diff), np.cos(diff))

    def send_to_arduino(self, theta):
        """
        Send joint angles to Arduino
        Format: "I theta1 theta2 theta3 theta4\n"
        Angles in degrees
        """
        if self.serial_conn is None:
            self.get_logger().error('Serial connection not available')
            return

        # Convert to degrees
        theta_deg = np.rad2deg(theta)

        # Format command
        cmd = f"I {theta_deg[0]:.2f} {theta_deg[1]:.2f} {theta_deg[2]:.2f} {theta_deg[3]:.2f}\n"

        try:
            self.serial_conn.write(cmd.encode())
            self.get_logger().info(f'Sent to Arduino: {cmd.strip()}')
        except serial.SerialException as e:
            self.get_logger().error(f'Serial write error: {e}')

    def detection_callback(self, msg):
        """
        Callback for detection messages
        """
        self.get_logger().info(f'Received detection: x={msg.x}, y={msg.y}, confidence={msg.confidence}')

        # Convert pixel to world coordinates
        x_world, y_world, z_world = self.pixel_to_world(msg.x, msg.y)
        target = np.array([x_world, y_world, z_world])

        self.get_logger().info(f'World coordinates: x={x_world:.3f}, y={y_world:.3f}, z={z_world:.3f}')

        # Compute inverse kinematics
        theta_ik = self.ik4(target)
        if theta_ik is None:
            self.get_logger().error('Target unreachable')
            return

        self.get_logger().info(f'Joint angles (rad): {theta_ik}')
        self.get_logger().info(f'Joint angles (deg): {np.rad2deg(theta_ik)}')

        # Verify with forward kinematics
        ee_fk = self.fk4(theta_ik)
        error = np.linalg.norm(ee_fk - target)
        self.get_logger().info(f'FK verification error: {error:.6f} m')

        # Send to Arduino
        self.send_to_arduino(theta_ik)

def main(args=None):
    rclpy.init(args=args)
    node = ArmControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()