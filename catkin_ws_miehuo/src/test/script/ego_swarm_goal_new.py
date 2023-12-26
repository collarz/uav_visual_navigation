#!/usr/bin/env python
#coding:utf-8
import rospy
from geometry_msgs.msg import PoseStamped
import sys

vehicle_type = sys.argv[1]
vehicle_id = sys.argv[2]
goal_point = PoseStamped()

def callback(data):
    global goal_point
    goal_point.header.frame_id = 'map'
    goal_point.pose.position.x=data.pose.position.x
    goal_point.pose.position.y=data.pose.position.y
    goal_point.pose.position.z=data.pose.position.z
    goal_point.pose.orientation.x=0
    goal_point.pose.orientation.y=0
    goal_point.pose.orientation.z=0
    goal_point.pose.orientation.w=1      
            
def goal_publisher(): 
    rospy.init_node(vehicle_type+"_"+vehicle_id+'_ego_swarm_goal')
    rospy.Subscriber('iris_0/goal_control/goal_point',PoseStamped, callback)
    
    goal_pub = rospy.Publisher(vehicle_type+"_"+vehicle_id+"/move_base_simple/goal", PoseStamped, queue_size=1)
    rate = rospy.Rate(20) 

    while not rospy.is_shutdown():
        global goal_point
        # 无人机初始位置
        initial_X = float(sys.argv[3])
        initial_Y = float(sys.argv[4])
        initial_Z = float(sys.argv[5])
        goal_point.pose.position.x = goal_point.pose.position.x + initial_X
        goal_point.pose.position.y = goal_point.pose.position.y + initial_Y
        goal_point.pose.position.z = goal_point.pose.position.z + initial_Z
        

        goal_point.header.stamp = rospy.Time.now()
        goal_pub.publish(goal_point) 
        try:
            rate.sleep()
        except:
            continue

if __name__ == '__main__':
    goal_point=PoseStamped()
    try:
        goal_publisher()
    except rospy.ROSInterruptException:
        pass