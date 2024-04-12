import rclpy
from rclpy.node import Node
import serial
import time
import argparse

from serial import SerialException
from LOMAS_ROS_pkg.msg import machine_status
from std_msgs.msg import *


class MachineNode(Node):
    def __init__(self):
        super().__init__('machine_node')