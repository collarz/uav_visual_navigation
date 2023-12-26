#!/usr/bin/env python
#coding:utf-8
from itertools import count
from mimetypes import init
from tokenize import Double
import rospy
import numpy as np
import math
import sys
from traj_utils.msg import Bspline
from mavros_msgs.msg import PositionTarget, State, HomePosition
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import String
import string

class Pub_goal:
    def __init__(self, iris_n, angle, flag_yolo, goal_point):
        # 无人机序号
        self.iris_n = iris_n
        # 无人机开始飞行方向
        self.angle = angle
        # yolo是否检测到目标的信号
        self.target_flag = flag_yolo
        # yolo检测到的目标点位置
        self.target_pos =  goal_point

        self.pos_x = 0
        self.pos_y = 0
        
        self.target_pos_1 = PoseStamped()
        # 订阅 单机
        #rospy.Subscriber('/zzz/'+self.iris_n+"/found_target_flag", String, self.target_flag_callback)
        #rospy.Subscriber('/zzz/'+self.iris_n+"/target_pos", PoseStamped, self.target_pos_callback)
        # 发布
        # self.local_target_pub = rospy.Publisher(self.iris_n+'/goal_control/goal_point', PoseStamped, queue_size=10)
        # self.local_target_pub = rospy.Publisher(self.iris_n+'/goal_control/goal_point', PoseStamped, queue_size=10)
        self.local_target_pub = rospy.Publisher(self.iris_n+'/move_base_simple/goal', PoseStamped, queue_size=10)
       
    def start(self):
        node_name = self.iris_n+'_goal_control'
        rospy.init_node(node_name )
        rate = rospy.Rate(45) 
        while not rospy.is_shutdown():
            self.pub_goal_point_0()
            # yolo检测到目标点并带有深度值, target_flag第一次检测到目标点之后就一直是true
            # if self.target_flag:
                # self.pub_goal_point_1()
            # yolo没有检测到目标点
            # else:
                # self.pub_goal_point_0()
            rate.sleep()
            
    def target_flag_callback(self,data):
        target_flag =  data.data
        if (target_flag == 'true') and (math.isnan(self.target_pos[0])==False):#if(math.isnan(z)==False):
            self.target_flag = True  
        
    def target_pos_callback(self,data):
        if self.target_flag == True : 
            self.target_pos[0] = data.pose.position.x
            self.target_pos[1] = data.pose.position.y
            self.target_pos[2] = data.pose.position.z
        
    # 沿着大致方向飞的代码, angel东北系坐标下，发布目标点
    def pub_goal_point_0(self):
        # angle为[0, 180)和[-180, 0)；angle = 0度, 机头朝向正东；angle = 90度, 机头朝向正北；angle = -90度, 机头朝向正南；
        cos_angle = math.cos(self.angle*1.0/90*math.pi/2)
        sin_angle = math.sin(self.angle*1.0/90*math.pi/2)
        # print(cos_angle)
        # print(sin_angle)
        self.pos_x = -3.5
        self.pos_y = -2
            
        target_pos_0 = PoseStamped()
        target_pos_0.pose.position.x = self.pos_x
        target_pos_0.pose.position.y = self.pos_y
        target_pos_0.pose.position.z = 1
        # print('goal_point[0]', goal_point[0])
        #发布目标位置
        self.local_target_pub.publish(target_pos_0)
    
    #朝向目标检测位点飞 ，发布目标点
    def pub_goal_point_1(self):
        

        if math.isnan(self.target_pos[0]) == False:
            self.target_pos_1.pose.position.x = self.target_pos[0] - 1
            self.target_pos_1.pose.position.y = self.target_pos[1] 
            self.target_pos_1.pose.position.z = self.target_pos[2]

        #发布目标位置
        self.local_target_pub.publish(self.target_pos_1)
    

        

if __name__=="__main__":
    goal_point = [6,3,1]
    count_goal = 0
    if len(sys.argv) > 1:
        iris_n = sys.argv[1]
    else:
        iris_n = ""
    # angel为无人机飞行方向
    #  angle为[0, 180)和[-180, 0)；angle = 0度, 机头朝向正东；angle = 90度, 机头朝向正北；angle = -90度, 机头朝向正南；
    angle = 0
    flag_yolo = False
    pub_goal = Pub_goal(iris_n, angle, flag_yolo, goal_point)
    pub_goal.start()
    
  
