from setuptools import setup

package_name = 'LOMAS_ROS_pkg'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Johan Kurt',
    maintainer_email='johan10_kurt@hotmail.com',
    description='A ROS 2 package for managing LOMAS robotics operations',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'machine_node_2 = LOMAS_ROS_pkg.machine_node_2:main',
            'watering_node = LOMAS_ROS_pkg.watering_node_2:main',
            'seq_generation_node = LOMAS_ROS_pkg.seq_generation_node:main',
            'gcode_sender_test = LOMAS_ROS_pkg.gcodesender_test:main'
        ],
    },
)