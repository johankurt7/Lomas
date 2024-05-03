import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter

from pyfirmata import Arduino, util
from lomas_ros_pkg.msgfolder.msg import WateringStatus
from std_msgs.msg import UInt8, Bool

# Global variable
status = WateringStatus()
status.error_nr = 99


class WateringNode(Node):
    def __init__(self):
        super().__init__('watering_node')
        self.declare_parameter('sim_mode', True)
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('watering_interval', 120)
        self.declare_parameter('watering_time', 120)
        self.declare_parameter('watering_valve_pin', 13)

        self.load_parameters()

        self.pub_watering_status = self.create_publisher(WateringStatus, 'LOMAS_WateringState', 10)

        self.sub_watering_cmd = self.create_subscription(UInt8, 'LOMAS_WateringCmd', self.cmd_callback, 10)
        self.sub_watering_abort = self.create_subscription(Bool, 'LOMAS_WateringAbort', self.abort_callback, 10)
        self.sub_watering_set_interval = self.create_subscription(UInt8, 'LOMAS_WateringSetInterval', self.interval_callback, 10)
        self.sub_watering_set_duration = self.create_subscription(UInt8, 'LOMAS_WateringSetDuration', self.duration_callback, 10)

    def load_parameters(self):
        self.sim_mode = self.get_parameter('sim_mode').get_parameter_value().bool_value
        self.port = self.get_parameter('port').get_parameter_value().string_value
        status.interval = self.get_parameter('watering_interval').get_parameter_value().integer_value
        status.duration = self.get_parameter('watering_time').get_parameter_value().integer_value
        self.watering_valve_pin = self.get_parameter('watering_valve_pin').get_parameter_value().integer_value

        self.get_logger().info(f'Watering param values:')
        self.get_logger().info(f' * Sim Mode: {self.sim_mode}')
        self.get_logger().info(f' * Port: {self.port}')
        self.get_logger().info(f' * Interval: {status.interval}')
        self.get_logger().info(f' * Duration: {status.duration}')
        self.get_logger().info(f' * Valve pin: {self.watering_valve_pin}')

        self.pub_watering_status.publish(status)

    def abort_callback(self, data):
        abort = data.data
        if abort:
            if not self.sim_mode:
                board.digital[13].write(0)
                status.watering = False
            else:
                self.get_logger().info('Warning! Simulating valve turn off')
                status.watering = False
            self.pub_watering_status.publish(status)

    def interval_callback(self, data):
        status.interval = data.data
        self.get_logger().info('Set interval')
        self.get_logger().info(data.data)
        self.set_parameters([Parameter('watering_interval', Parameter.Type.INTEGER, msg.data)])
        self.pub_watering_status.publish(status)

    def duration_callback(self, data):
        status.duration = data.data
        self.get_logger().info('Set duration')
        self.get_logger().info(data.data)
        self.set_parameters([Parameter('watering_time', Parameter.Type.INTEGER, msg.data)])
        self.pub_watering_status.publish(status)

    def cmd_callback(self, data):
        if not self.sim_mode:
            status.watering = bool(data.data == 1)
            board.digital[13].write(data.data)
        else:
            if data.data == 0:
                self.get_logger().info('Warning: Simulating valve turn off')
            else:
                self.get_logger().info('Warning: Simulating valve turn on')

            status.watering = bool(data.data == 1)
        self.pub_watering_status.publish(status)

    def connect_to_telemetry(self):
        if not self.sim_mode:
            global board
            board = Arduino(self.port)
            ctrl_value = int(status.watering == True)

            # Turn off watering
            board.digital[13].write(ctrl_value)
            self.get_logger().info('Connected to telemetry control board')
        else:
            self.get_logger().info('Warning: Simulated telemetry control board')


def main(args=None):
    rclpy.init(args=args)
    watering_node = WateringNode()
    watering_node.connect_to_telemetry()

    rclpy.spin(watering_node)

    watering_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
