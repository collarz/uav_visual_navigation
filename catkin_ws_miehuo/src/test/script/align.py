#!/usr/bin/env python
#coding:utf-8
from turtle import distance
import rospy
from geometry_msgs.msg import Twist, PoseStamped
from std_msgs.msg import String
from nav_msgs.msg import Odometry
import sys 
#sys.path.append('/home/origami-hui/catkin_ws/devel/lib/python3/dist-packages')
from pyquaternion import Quaternion
from darknet_ros_msgs.msg import BoundingBoxes
from gazebo_msgs.msg import ModelStates
import time
import math
import numpy as np
        
def callback_targetflag(data):
    global target_flag
    target_flag = data 


def callback_targetpos(data):
    global target_pos
    target_pos[0] = data.pose.position.x
    target_pos[1] = data.pose.position.y
    target_pos[2] = data.pose.position.z

def callback_target_iris_pos(data):
    global target_iris_pos
    target_iris_pos[0] = data.pose.position.x
    target_iris_pos[1] = data.pose.position.y
    target_iris_pos[2] = data.pose.position.z

def gazebo_model_state_callback(msg):
    global xt_pos, Rot, yaw
    global initial_X, initial_Y, initial_Z
    # 需要加上无人机起始偏移量
    xt_pos[0] = msg.pose.pose.position.x + initial_X
    xt_pos[1] = msg.pose.pose.position.y + initial_Y
    xt_pos[2] = msg.pose.pose.position.z + initial_Z
    
    # 构造四元数，并将之转化为旋转矩阵
    q = Quaternion(msg.pose.pose.orientation.w, msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z)
    Rot = q.rotation_matrix
    yaw = q.yaw_pitch_roll[0]


def distance(xt_pos,target_pos):
    return math.sqrt(pow(xt_pos[0]-target_pos[0], 2)+pow(xt_pos[1]-target_pos[1], 2)+pow(xt_pos[2]-target_pos[2], 2))

def align_target():

    global align_flag,a_flag,h_flag
    
    
    twist = Twist()
    
    # L1为无人机指向目标点向量，L2为无人机在xOy平面的方向向量

    L1 = np.array([target_pos[0]-xt_pos[0], target_pos[1]-xt_pos[1]])

    if -math.pi/2 < yaw < math.pi/2 : # 一四象限
        L2 = np.array([1,math.tan(yaw)])
    elif yaw > math.pi/2: # 第二象限
        L2 = np.array([-1,-math.tan(yaw)])
    elif yaw == math.pi/2:
        L2 = np.array([0,1])
    elif yaw == -math.pi/2:
        L2 = np.array([0,-1])
    else: # 第三象限
        L2 = np.array([-1,math.tan(yaw)])
        
    print('yaw:', yaw, math.tan(yaw))
    print('L1:', L1)
    print('L2:', L2)
    
    # 计算两向量间夹角

    delta = math.asin(np.cross(L1,L2)/ (np.linalg.norm(L1) * np.linalg.norm(L2)))
    print('delta:', delta)
    print('aligning....')

    h_off = xt_pos[2]-target_pos[2]

    # 左右转向
    if delta < -offset1:
        twist.angular.z = 0.3
    elif -offset1 <= delta <= offset1:
        a_flag = 1
        twist.angular.z = 0
    else:
        twist.angular.z = -0.3

    # if  -offset1 <= delta <= offset1:
    #     a_flag = 1
    #     twist.angular.z = 0
    # else:
    #     twist.angular.z = 0.3
    # # 上下移动
    # if h_off < -offset2:
    #     twist.linear.z = 0.3
    # elif -offset2 <= h_off <= offset2:
    #     h_flag = 1
    #     twist.linear.z = 0
    # else:
    #     twist.linear.z = -0.3
    
    # 发布角度
    cmd_pub.publish(twist)

    if(a_flag * h_flag == 1):
        print('已对准目标点')
        align_flag = 1
                


if __name__ == "__main__":

    xt_pos = [0,0,0]    # 无人机当前位置
    target_pos = [0,0,0]    #目标的位置
    target_iris_pos = [0,0,0]   #无人机i的目标位置
    
    target_flag = "flase"
    arrive_flag = "flase"
    
    u_center=640/2 
    v_center=360/2

    offset1 = 0.1 #角度偏移阈值
    offset2 = 0.05 #高度偏移阈值

    align_flag = 0
    a_flag = h_flag = 0
    yaw = 0

    vehicle_type = sys.argv[1]
    vehicle_id = sys.argv[2]
    
    # 无人机初始位置
    initial_X = float(sys.argv[3])
    initial_Y = float(sys.argv[4])
    initial_Z = float(sys.argv[5])
        
    rospy.init_node(vehicle_type+"_"+vehicle_id+'_align')
     # iris_0是否检测到目标点，由yolo_interface.py发布
    rospy.Subscriber('/zzz/iris_0/found_target_flag', String, callback_targetflag, queue_size=2)
    # iris_0目标位置，也就是检测目标点的位置，由yolo_interface.py发布
    rospy.Subscriber('/zzz/iris_0/target_pos', PoseStamped, callback_targetpos, queue_size=10)
    
    # iris_i目标位置，和检测目标点位置有偏差
    rospy.Subscriber(vehicle_type+"_"+vehicle_id+"/move_base_simple/goal", PoseStamped, callback_target_iris_pos, queue_size=10)
    
    # rospy.Subscriber("/gazebo/model_states", ModelStates, gazebo_model_state_callback,queue_size=1)# 订阅真实位姿
    # 以下位置话题不是世界位置话题，而是每一个无人机起始位置都为(0,0,0)
    rospy.Subscriber("/iris_"+vehicle_id+"/mavros/local_position/odom", Odometry, gazebo_model_state_callback,queue_size=1)
    
    cmd_pub = rospy.Publisher('/xtdrone/'+vehicle_type+'_'+vehicle_id+'/cmd_vel_flu', Twist, queue_size=1)
    arrive_target_flag = rospy.Publisher('/zzz/'+vehicle_type+'_'+vehicle_id+'/arrive_target_flag', String, queue_size=2)
    
    rate = rospy.Rate(60) 
    while not rospy.is_shutdown() and align_flag == 0:
        #print('target_flag', target_flag)

        rate.sleep()
        print(vehicle_id)
        print(xt_pos)
        print(target_iris_pos)
        if distance(xt_pos,target_iris_pos) < 3 :
            # 如果距离小于一定值且检测到目标，则执行对准函数
            align_target()
            arrive_flag = "true"
            arrive_target_flag.publish(arrive_flag)
        else:
            print ('未到达目标点附近')

    sys.exit(0)
