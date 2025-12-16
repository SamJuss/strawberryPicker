from setuptools import setup
import os
from glob import glob

package_name = 'strawberry_picker_control'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        # Include config files
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.rviz')),
        # Include URDF and SDF files
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='ROS2 package for AI-powered robotic strawberry harvesting system',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'vision_processor = strawberry_picker_control.vision_processor:main',
            'robot_controller = strawberry_picker_control.robot_controller:main',
            'coordinate_transformer = strawberry_picker_control.coordinate_transformer:main',
            'picking_coordinator = strawberry_picker_control.picking_coordinator:main',
            'arduino_bridge = strawberry_picker_control.arduino_bridge:main',
        ],
    },
)