#!/usr/bin/env python3
"""
ROS2 Vision Processor Node for Strawberry Detection and Classification

This node integrates the existing computer vision pipeline with ROS2,
providing real-time strawberry detection and ripeness classification.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import cv2
import numpy as np
from cv_bridge import CvBridge
import time
from pathlib import Path
import sys
import os

# Add the project root to Python path to import existing modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.integrated_detection_classification import IntegratedDetectorClassifier

# ROS2 message imports
from sensor_msgs.msg import Image
from strawberry_picker_control.msg import StrawberryDetection, StrawberryTarget
from strawberry_picker_control.srv import GetStrawberryTargets
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point


class VisionProcessor(Node):
    """ROS2 node for strawberry detection and classification"""

    def __init__(self):
        super().__init__('vision_processor')

        # Declare parameters
        self.declare_parameter('detection_model_path', 'model/weights/best.pt')
        self.declare_parameter('classification_model_path', 'model/ripeness_classifier.h5')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('camera_topic', '/camera/image_raw')
        self.declare_parameter('publish_rate', 10.0)  # Hz

        # Get parameters
        self.detection_model_path = self.get_parameter('detection_model_path').value
        self.classification_model_path = self.get_parameter('classification_model_path').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.camera_topic = self.get_parameter('camera_topic').value
        self.publish_rate = self.get_parameter('publish_rate').value

        # Initialize CV bridge
        self.bridge = CvBridge()

        # Initialize detector/classifier
        try:
            self.detector = IntegratedDetectorClassifier(
                detection_model_path=self.detection_model_path,
                classification_model_path=self.classification_model_path,
                confidence_threshold=self.confidence_threshold
            )
            self.get_logger().info('Vision processor initialized successfully')
        except Exception as e:
            self.get_logger().error(f'Failed to initialize vision processor: {e}')
            raise

        # QoS profile for reliable image transport
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            self.camera_topic,
            self.image_callback,
            qos_profile
        )

        # Publishers
        self.detection_pub = self.create_publisher(
            StrawberryDetection,
            'strawberry_detections',
            10
        )

        self.target_pub = self.create_publisher(
            StrawberryTarget,
            'strawberry_targets',
            10
        )

        self.marker_pub = self.create_publisher(
            MarkerArray,
            'strawberry_markers',
            10
        )

        self.annotated_image_pub = self.create_publisher(
            Image,
            'annotated_image',
            10
        )

        # Services
        self.target_service = self.create_service(
            GetStrawberryTargets,
            'get_strawberry_targets',
            self.get_targets_callback
        )

        # State variables
        self.current_targets = []
        self.last_processing_time = 0.0
        self.frame_count = 0

        # Timer for periodic processing
        self.timer = self.create_timer(1.0 / self.publish_rate, self.timer_callback)

        self.get_logger().info(f'Vision processor node started. Camera topic: {self.camera_topic}')

    def image_callback(self, msg):
        """Process incoming camera images"""
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Process frame
            start_time = time.time()
            results = self.detector.process_frame(cv_image)
            processing_time = time.time() - start_time

            # Convert results to ROS messages
            detections = self._create_detections(results, msg.header)
            targets = self._create_targets(detections, cv_image.shape)

            # Update current targets
            self.current_targets = targets
            self.last_processing_time = processing_time
            self.frame_count += 1

            # Publish detections
            for detection in detections:
                self.detection_pub.publish(detection)

            # Publish targets
            for target in targets:
                self.target_pub.publish(target)

            # Publish visualization markers
            markers = self._create_markers(targets, msg.header)
            self.marker_pub.publish(markers)

            # Publish annotated image
            annotated_image = self._create_annotated_image(cv_image, detections)
            annotated_msg = self.bridge.cv2_to_imgmsg(annotated_image, encoding='bgr8')
            annotated_msg.header = msg.header
            self.annotated_image_pub.publish(annotated_msg)

            # Log performance
            if self.frame_count % 30 == 0:  # Log every 30 frames
                self.get_logger().info(
                    f'Processed frame {self.frame_count}. '
                    f'Detections: {len(detections)}, '
                    f'Processing time: {processing_time:.3f}s'
                )

        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def _create_detections(self, results, header):
        """Convert detection results to ROS messages"""
        detections = []

        for detection in results.get('detections', []):
            msg = StrawberryDetection()
            msg.header = header
            msg.x = float(detection['bbox'][0])
            msg.y = float(detection['bbox'][1])
            msg.width = float(detection['bbox'][2])
            msg.height = float(detection['bbox'][3])
            msg.confidence = float(detection['confidence'])
            msg.ripeness_class = detection.get('ripeness', 'unknown')
            msg.ripeness_confidence = float(detection.get('ripeness_confidence', 0.0))

            # Calculate center
            msg.center_x = msg.x + msg.width / 2
            msg.center_y = msg.y + msg.height / 2

            detections.append(msg)

        return detections

    def _create_targets(self, detections, image_shape):
        """Convert detections to picking targets (filter for ripe strawberries)"""
        targets = []

        for detection in detections:
            # Only create targets for ripe strawberries
            if detection.ripeness_class != 'ripe':
                continue

            target = StrawberryTarget()
            target.detection = detection
            target.position.x = 0.0  # Will be filled by coordinate transformer
            target.position.y = 0.0
            target.position.z = 0.0
            target.priority = detection.confidence * detection.ripeness_confidence
            target.status = 'detected'

            targets.append(target)

        # Sort by priority
        targets.sort(key=lambda t: t.priority, reverse=True)

        return targets

    def _create_markers(self, targets, header):
        """Create RViz markers for visualization"""
        marker_array = MarkerArray()

        for i, target in enumerate(targets):
            # Bounding box marker
            marker = Marker()
            marker.header = header
            marker.ns = 'strawberry_targets'
            marker.id = i
            marker.type = Marker.CUBE
            marker.action = Marker.ADD

            # Position (placeholder - will be updated by coordinate transformer)
            marker.pose.position.x = 0.0
            marker.pose.position.y = 0.0
            marker.pose.position.z = 0.0

            # Size based on detection
            marker.scale.x = target.detection.width / 100.0  # Scale down for visualization
            marker.scale.y = target.detection.height / 100.0
            marker.scale.z = 0.01

            # Color based on ripeness
            if target.detection.ripeness_class == 'ripe':
                marker.color.r = 0.0
                marker.color.g = 1.0
                marker.color.b = 0.0
            elif target.detection.ripeness_class == 'unripe':
                marker.color.r = 1.0
                marker.color.g = 1.0
                marker.color.b = 0.0
            else:  # overripe
                marker.color.r = 1.0
                marker.color.g = 0.0
                marker.color.b = 0.0

            marker.color.a = 0.7
            marker.lifetime.sec = 1  # Markers disappear after 1 second

            marker_array.markers.append(marker)

        return marker_array

    def _create_annotated_image(self, image, detections):
        """Create annotated image with bounding boxes and labels"""
        annotated = image.copy()

        for detection in detections:
            # Draw bounding box
            x, y, w, h = int(detection.x), int(detection.y), int(detection.width), int(detection.height)

            # Color based on ripeness
            if detection.ripeness_class == 'ripe':
                color = (0, 255, 0)
            elif detection.ripeness_class == 'unripe':
                color = (0, 255, 255)
            else:  # overripe
                color = (0, 0, 255)

            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

            # Add label
            label = f"{detection.ripeness_class} ({detection.confidence:.2f})"
            cv2.putText(annotated, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return annotated

    def get_targets_callback(self, request, response):
        """Service callback to get current strawberry targets"""
        response.targets = self.current_targets
        response.success = True
        response.message = f"Returned {len(self.current_targets)} targets"
        return response

    def timer_callback(self):
        """Periodic timer callback for status updates"""
        # Publish processing statistics
        self.get_logger().debug(
            f'Vision processor status: {len(self.current_targets)} targets, '
            f'processing time: {self.last_processing_time:.3f}s'
        )


def main(args=None):
    rclpy.init(args=args)
    node = VisionProcessor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()