#! /usr/bin/python

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import sensor_msgs.msg

pub = rospy.Publisher('/new_on_the_block', LaserScan, queue_size = 10)
scann = LaserScan()
cmdvel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)

def callback (msg):


    twist = Twist()

    twist.linear.x = .3
    twist.linear.y = 0
    twist.linear.z = 0

    twist.angular.x = 0
    twist.angular.y = 0
    twist.angular.z = 0
    rospy.loginfo( "" )
    cmdvel_pub.publish(twist)

    #size_of_ranges = len(msg.ranges)
    #largestNumber = max(msg.ranges)
    #smallestNumber = min(msg.ranges)

    #message = f"the size is {size_of_ranges} with max of {largestNumber} and min of {smallestNumber}"

    #rospy.loginfo(message)



def listener():
    rospy.init_node('new_on_the_block', anonymous=True)
    sub = rospy.Subscriber('/scan', LaserScan, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()
