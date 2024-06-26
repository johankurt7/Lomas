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
        self.declare_parameters(
            namespace='',
            parameters=[
                ('sim_port', True),
                ('port', '/dev/ttyUSB0'),
                ('path', '/media/gcode/'),
                ('cultivation_interval', 120)
            ]
        )
        self.loadParameters()
        self.pubMachineStatus = self.create_publisher(machine_status, 'LOMAS_MachineState', 10)
        self.sub_cmd = self.create_subscription(UInt8, 'LOMAS_MachineCmd', self.cmd_callback, 10)
        self.sub_stop = self.create_subscription(Bool, 'LOMAS_MachineStop', self.stop_callback, 10)
        self.sub_abort = self.create_subscription(Bool, 'LOMAS_MachineAbort', self.abort_callback, 10)
        self.sub_intervall = self.create_subscription(UInt8, 'LOMAS_MachineSetIntervall', self.intervall_callback, 10)

        self.status = machine_status()
        self.status.ErrorNr = 99
        self.stop = False
        self.abort = False

    def loadParameters(self):
        self.IsInSimMode = self.get_parameter('sim_port').value
        self.port = self.get_parameter('port').value
        self.path = self.get_parameter('path').value
        self.status.Interval = self.get_parameter('cultivation_interval').value

        self.get_logger().info('Machine param values:')
        self.get_logger().info(f" * IsInSimMode: {self.IsInSimMode}")
        self.get_logger().info(f" * Port: {self.port}")
        self.get_logger().info(f" * Path: {self.path}")
        self.get_logger().info(f" * Interval: {self.status.Interval}")

        self.pubMachineStatus.publish(self.status)

    def connectToMachine(self):
        try:
            self.ser = serial.Serial(self.port, 115200)
            self.ser.write(b"\r\n\r\n")  # Hit enter a few times to wake the Printrbot
            time.sleep(2)  # Wait for machine to initialize
            self.ser.flushInput()  # Flush startup text in serial input
            self.status.ErrorNr = 0
            self.get_logger().info('Serial port connected to machine')
        except serial.SerialException:
            self.status.ErrorNr = 98
            self.get_logger().error('Error when opening Serial Port')

        self.pubMachineStatus.publish(self.status)

    def sendSerialCmd(self, cmd):
        if self.IsInSimMode:
            grbl_out = b'oMGok\n'
        else:
            self.ser.write(cmd)  # Send g-code block
            grbl_out = self.ser.readline()  # Wait for response with carriage return

        self.get_logger().info(f': {grbl_out.strip()}')

        return grbl_out == b'oMGok\n'

    def sendGCodeFile(self, file, seq):
        self.status.SequensStarted = True
        self.status.MachineMoving = True
        self.stop = False
        self.abort = False
        self.pubMachineStatus.publish(self.status)

        try:
            with open(file, 'r') as f:
                self.get_logger().info(f'Opening gcode file: {file}')
                for line in f:
                    l = self.remove_comment(line)
                    l = l.strip()  # Strip all EOL characters for streaming
                    if not l.isspace() and len(l) > 0:
                        ok = self.send_serial_cmd((l + '\n').encode())

                    if self.stop:
                        self.get_logger().info('Stopped')
                        self.status.SequenseNr = 90
                        self.status.MachineMoving = False
                        self.pubMachineStatus.publish(self.status)
                        while self.stop:
                            if self.abort:
                                self.status.SequenseNr = 91
                                self.get_logger().info('Aborting while')
                                self.pubMachineStatus.publish(self.status)
                                break
                            time.sleep(0.1)

                        self.get_logger().info('Restarted')
                        self.status.MachineMoving = True
                        self.status.SequenseNr = seq
                        self.pubMachineStatus.publish(self.status)

                    if self.abort:
                        self.status.SequenseNr = 91
                        self.pubMachineStatus.publish(self.status)
                        self.get_logger().info('Aborting for')
                        break

        except FileNotFoundError:
            self.get_logger().error(f"Error: File {file} not found")

        self.status.ErrorNr = 0
        self.status.SequensStarted = False
        self.status.MachineMoving = False
        self.status.SequenseNr = 0
        self.abort = False

    def sendGCodeCmd(self, cmd):

    def stopCallback(self, data):

    def abortCallback(self, data):

    def intervallCallback(self, data):

    def cmdCallback(self, data):



'''
def removeComment(string):
    if (string.find(';')==-1):
        return string
    else:
        return string[:string.index(';')]
'''


def main(args=None):
    rclpy.init(args=args)
    machine_node = MachineNode()
    try:
        rclpy.spin(machine_node)
    except KeyboardInterrupt:
        pass
    finally:
        machine_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()