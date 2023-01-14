#! /usr/bin/python

import rospy
from rosgraph_msgs.msg import Clock
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import sensor_msgs.msg
import numpy as np
from datetime import datetime


pub = rospy.Publisher('/new_on_the_block', LaserScan, queue_size = 10)
scann = LaserScan()
cmdvel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)

relative_position = np.array([0, 0, 0])
previous_velocities = np.array([0, 0, 0])
previous_t = datetime.timestamp( datetime.now() )
block_size = 1 #1 metre width, 1 metre height of a block
blockades = {}


def create_mini_map_details (ranges, destination):

    max_distance = -1
    quadrant = 0
    index_tracker = 0
    for k in ranges:
        if k == float('inf'):
            continue
        max_distance = max(max_distance, k)
        quadrant = 0 if index_tracker < 90 else ( 1 if index_tracker < 180 else ( 2if index_tracker < 270 else 3  )  )

        if quadrant==0:
            pass
        elif quadrant==1:
            pass
        elif quadrant==2:
            pass
        else:
            pass

        index_tracker += 1

    maxes = relative_position + max_distance
    mins = relative_position - max_distance

    return { 'maxes':maxes, 'mins':mins,
             'start':relative_position, 'end':destination }



def callback (msg):

    global previous_t
    global previous_velocities
    global relative_position

    current_t = datetime.timestamp(datetime.now())
    delta_t = current_t - previous_t
    delta_distance = previous_velocities * delta_t
    #relative_position = relative_position + delta_distance

    new_velocities = np.array([ .1, 0, 0 ])

    twist = Twist()
    stop_vehicle = rospy.is_shutdown()
    twist.linear.x = 0 if stop_vehicle else new_velocities[0]
    twist.linear.y = 0 if stop_vehicle else new_velocities[1]
    twist.linear.z = 0 if stop_vehicle else new_velocities[2]

    twist.angular.x = 0
    twist.angular.y = 0
    twist.angular.z = 0
    #message = f"vel x {new_velocities[0]}"
    #rospy.loginfo( f"Suspected position {relative_position}" )
    #cmdvel_pub.publish(twist)
    previous_velocities = new_velocities
    previous_t = current_t
    #size_of_ranges = len(msg.ranges)
    #largestNumber = max(msg.ranges)
    #smallestNumber = min(msg.ranges)
    rospy.loginfo(create_mini_map_details
            (
                msg.ranges,
                []
            ))
   #message = f"the size is {size_of_ranges} with max of {largestNumber} and min of {smallestNumber}"

    #rospy.loginfo(message)


def listener():
    rospy.init_node('new_on_the_block', anonymous=True)
    scan_Sub = rospy.Subscriber('/scan', LaserScan, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()


