#!/usr/bin/env python
#coding:utf-8
from cmath import pi
from ipaddress import v4_int_to_packed, v6_int_to_packed
from operator import pos
from turtle import width
import rospy
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import Twist, PoseStamped
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image
from sensor_msgs import point_cloud2
from std_msgs.msg import String
import sys 
# sys.path.append('/home/robin/catkin_ws/devel/lib/python2.7/dist-packages')
from pyquaternion import Quaternion
from darknet_ros_msgs.msg import BoundingBoxes
import cv2
from cv_bridge import CvBridge, CvBridgeError
import message_filters
from message_filters import ApproximateTimeSynchronizer
import rospy
import time
import math
import numpy as np


    
# 找到yolo目标检测框
def darknet_callback(data):
    global real_camera
    global get_time
    global u,v #目标检测中心点
    global box_minX, box_minY, box_maxX, box_maxY
    send_pos_flag = 'flase'
    for target in data.bounding_boxes:
        if target.id==0 and real_camera == False:
            print('find fire')
            u = (target.xmax+target.xmin)/2
            v = (target.ymax+target.ymin)/2
            box_minX = target.xmin
            box_minY = target.ymin
            box_maxX = target.xmax
            box_maxY = target.ymax
            get_time = False
            
            #订阅realsense相机的rgb与深度话题
            color = message_filters.Subscriber(vehicle_type+'_'+vehicle_id+'/realsense/depth_camera/color/image_raw', Image)
            depth = message_filters.Subscriber(vehicle_type+'_'+vehicle_id+'/realsense/depth_camera/depth/image_raw', Image)
            color_depth = message_filters.ApproximateTimeSynchronizer([color, depth], 10, 1, allow_headerless=True)
            color_depth.registerCallback(callback_depthinfo) 
            
        # 真实相机测试
        if target.id == 0 and real_camera == True:
            print('find fire_real')
            u = (target.xmax+target.xmin)/2
            v = (target.ymax+target.ymin)/2
            box_minX = target.xmin
            box_minY = target.ymin
            box_maxX = target.xmax
            box_maxY = target.ymax
            get_time = False
            
            #订阅d435i相机的rgb与深度话题
            color = message_filters.Subscriber('/camera/color/image_raw', Image)
            depth = message_filters.Subscriber('/camera/aligned_depth_to_color/image_raw', Image)
            color_depth = message_filters.ApproximateTimeSynchronizer([color, depth], 10, 1, allow_headerless=True)
            color_depth.registerCallback(callback_depthinfo) 
    
        
# def local_pose_callback(data):
#     global X_w,Y_w,Z_w, target_set,Rot
#     X_w = data.pose.position.x   
#     Y_w = data.pose.position.y  
#     Z_w = data.pose.position.z 

#     # 构造四元数，并将之转化为旋转矩阵
#     q = Quaternion(data.pose.orientation.w, data.pose.orientation.x, data.pose.orientation.y, data.pose.orientation.z)
#     Rot = q.rotation_matrix

#     if not target_set:   
#         target_set = True

#仿真相机位姿回调函数 
def gazebo_model_state_callback(msg):
    global X_w,Y_w,Z_w, target_set,Rot
    id = msg.name.index(vehicle_type+'_'+str(vehicle_id))
    msg.pose[id]
    X_w = msg.pose[id].position.x   
    Y_w = msg.pose[id].position.y  
    Z_w = msg.pose[id].position.z 
    
    # 构造四元数，并将之转化为旋转矩阵
    q = Quaternion(msg.pose[id].orientation.w, msg.pose[id].orientation.x, msg.pose[id].orientation.y, msg.pose[id].orientation.z)
    Rot = q.rotation_matrix

    if not target_set:   
        target_set = True    

#真实相机位姿回调函数   
def vins_odometry_callback(msg):
    global X_w,Y_w,Z_w, target_set,Rot
    
    X_w = msg.pose.pose.position.x   
    Y_w = msg.pose.pose.position.y  
    Z_w = msg.pose.pose.position.z 
    
    # 构造四元数，并将之转化为旋转矩阵
    q = Quaternion(msg.pose.pose.orientation.w, msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z)
    Rot = q.rotation_matrix

    if not target_set:   
        target_set = True  
        

def callback_pointcloud(data):
    #用subscriber接收深度相机topic下的点云数据，获取点云中的XYZ坐标
    global target_pose

    assert isinstance(data, PointCloud2)
    gen = point_cloud2.read_points(data, field_names=("x", "y", "z"), skip_nans=True)
    time.sleep(1)
    count=0



#计算目标深度值
def box_ave(depth_image, u, v):

    z = depth_image[v, u] 
    box_centerX = (box_minX + box_maxX)/2
    box_centerY = (box_minY + box_maxY)/2
    bias = 10
    count_current = 0
    sum_Z = 0
    if(math.isnan(z)==False):
        u = u
        v = v
    else:
        # print(box_minX, box_maxX, box_minY, box_maxY)
        # for i in range(box_centerX-bias, box_centerX+bias):
        #     for j in range(box_centerY-bias, box_centerY+bias):
        for i in range(box_minX, box_maxX):
            for j in range(box_minY, box_maxY):
                z_current = depth_image[j, i] 
                if(math.isnan(z_current)==False):
                    count_current = count_current + 1
                    sum_Z = sum_Z + z_current
        if count_current != 0:
            z = sum_Z/count_current
        print(count_current)
    return z

def callback_depthinfo(data1, data2):
    global real_camera
    global bridge,u,v,Rot
    global target_pose
    global send_pos_flag #是否检测到目标,同时目标点具有深度值
    global last_pos, first_stable_flag
    bridge = CvBridge()

    #pub = rospy.Publisher('/Distance', Distance, queue_size=1)
    #rate = rospy.Rate(10)
    color_image = bridge.imgmsg_to_cv2(data1, 'bgr8')
    depth_image = bridge.imgmsg_to_cv2(data2, '32FC1') #利用rostopic echo /iris_0/realsense/depth_camera/depth/image_raw/encoding 查看话题的编码
    # print(depth_image)
    # cv2.imshow('color_image',color_image)
    # cv2.imshow('depth_image',depth_image)
    # cv2.waitKey(1000)
    
    #目标中心点的xy坐标(u,v)
    u = int(u)-1
    v = int(v)-1
    #中心点深度值
    Zc = box_ave(depth_image, u, v) 
    print(u,v)
    # print('Zc',Zc)
    # if math.isnan(Zc)==False:
    #     flag = 'true'   
    
    if real_camera == False :
        #相机内参矩阵
        # 参数配置文件在～/PX4_Firmware/Tools/sitl_gazebo/models/realsense_camera/realsense_camera.sdf
        intrinsic_M = np.array([[554.254691191187, 0.0, 320.5],  [0.0, 554.254691191187, 240.5],  [0.0, 0.0, 1.0]])     
        # 像素坐标系
        uv_M = np.array([[u],[v],[1]])
        
        # 相机坐标系
        pos_C = np.dot(np.linalg.inv(intrinsic_M), uv_M)*Zc
        # print('pos_C',pos_C)
        
        #相机坐标系ENU
        pos_Cx_ENU = pos_C[2]
        pos_Cy_ENU = pos_C[0]*(-1)
        pos_Cz_ENU = pos_C[1]*(-1)
        pos_C_ENU = (pos_Cx_ENU, pos_Cy_ENU, pos_Cz_ENU)
        # print('pos_C_ENU',pos_C_ENU)
        
        # 世界坐标系(两种方法),经实验验证,这是以无人机为原点的ENU世界坐标系
        T = np.array([[X_w],[Y_w],[Z_w]])
        # pos_W = np.dot(np.linalg.inv(Rot), (pos_C_ENU - T))
        pos_W = np.dot(Rot, pos_C_ENU) + T
        # print('T',T)
        # print('pos_W',pos_W)
            
        # extrinsic_M =  np.hstack((Rot, T))
        # extrinsic_M = np.vstack((extrinsic_M, np.array([[0,0,0,1]]) ) )#坐标齐次化
        # pos_C_ENU = np.vstack((pos_C_ENU, np.array([1])))
        # pos_W1 = np.dot(np.linalg.inv(extrinsic_M), pos_C_ENU)
        # print('pos_W1',pos_W1)
        
        
        # target_pose.pose.position.x = pos_W[0]
        # target_pose.pose.position.y = pos_W[1]
        # target_pose.pose.position.z = pos_W[2]
        
        if first_stable_flag == True and stable_count == 2:
            target_pose.pose.position.x = pos_W[0]
            target_pose.pose.position.y = pos_W[1]
            target_pose.pose.position.z = pos_W[2]
            print('pos_W',pos_W)
            send_pos_flag = 'true' 
            first_stable_flag = False
            
        stabilize_position(pos_W, last_pos)
        
        last_pos[0] = pos_W[0]
        last_pos[1] = pos_W[1]
        last_pos[2] = pos_W[2]
        
    # 真实相机
    elif real_camera == True:
        intrinsic_M = np.array([[909.2666015625, 0.0, 630.6053466796875],  [0.0, 909.1947021484375, 353.4368896484375],  [0.0, 0.0, 1.0]]) 
        uv_M = np.array([[u],[v],[1]])
        # 真实相机的深度值是毫米
        pos_C = np.dot(np.linalg.inv(intrinsic_M), uv_M)*Zc*0.001
        # print('pos_C',pos_C)
        pos_C_x = pos_C[2]
        pos_C_y = -1*pos_C[0]
        pos_C_z = -1*pos_C[1]
        pos_C_ENU = (pos_C_x, pos_C_y, pos_C_z)
        print('pos_C_ENU',pos_C_ENU)
        T = np.array([[X_w],[Y_w],[Z_w]])
        # pos_W = np.dot(np.linalg.inv(Rot), (pos_C_ENU - T))
        
        # 真实相机的位置如何测试？？？
        pos_W = np.dot(Rot, pos_C_ENU) + T
        print('pos_W',pos_W)
        
        #加入稳定坐标代码
        
        
# 判断目标世界坐标是否稳定
def stabilize_position(current_pos, last_pos):
    global stable_count
    detaX = abs(current_pos[0] - last_pos[0]) 
    detaY = abs(current_pos[1] - last_pos[1]) 
    detaZ = abs(current_pos[2] - last_pos[2]) 
    if detaX < 1 and detaY < 1 and detaZ < 1:
        stable_count = stable_count + 1
    else:
        stable_count = 0

def  callback_img_depth(data):
    # 使用cv_bridge将ROS的图像数据转换成OpenCV的图像格式
    try:
        cv_image = CvBridge().imgmsg_to_cv2(data, "32FC1")
    except CvBridgeError as e:
        print(e)
    # # 在opencv的显示窗口中绘制一个圆，作为标记
    # cv2.imshow("Image_depth", cv_image)
    # cv2.waitKey(3)

    
def  callback_img_color(data):
    # 使用cv_bridge将ROS的图像数据转换成OpenCV的图像格式
    try:
        cv_image = CvBridge().imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
        print(e)
    # # 在opencv的显示窗口中绘制一个圆，作为标记
    # cv2.imshow("Image_color", cv_image)
    # cv2.waitKey(3)
    

if __name__ == "__main__":
    # 是否使用真实相机
    real_camera = True# Fasle
    
    box_minX = 0
    box_minY = 0
    box_maxX = 0 
    box_maxY = 0
    X_w = 0
    Y_w = 0
    Z_w = 0 
    send_pos_flag = 'flase'
    target_pose = PoseStamped()

    target_set = False
    u=320.0
    v=240.0
    
    stable_count = 0
    first_stable_flag = True
    stable_pos = [0,0,0]
    last_pos = [0,0,0]

    
    vehicle_type = sys.argv[1]
    vehicle_id = sys.argv[2]
    rospy.init_node('yolo_interface')
    rospy.Subscriber("/uav_"+vehicle_id+"/darknet_ros/bounding_boxes", BoundingBoxes, darknet_callback)
    
    # /mavros/local_position/pose获取相对于无人机初始位置位移坐标
    # rospy.Subscriber(vehicle_type+'_'+vehicle_id+"/mavros/local_position/pose", PoseStamped, local_pose_callback)
    
    # 仿真中无人机位置的获取
    # /gazebo/model_states获取无人机世界坐标
    rospy.Subscriber("/gazebo/model_states", ModelStates, gazebo_model_state_callback,queue_size=1)# 订阅真实位姿
    # rospy.Subscriber('/xtdrone/'+vehicle_type+'_'+vehicle_id+'/cam_pose', PoseStamped, cam_pose_callback)
    
    # 实际无人机位置的获取 通过vins-fusion算法得到,回调函数获得无人机的平移矩阵和旋转矩阵
    rospy.Subscriber("/iris_0/vins_estimator/camera_pose", Odometry, vins_odometry_callback,queue_size=1)# 订阅真实位姿
    
    
    
    # /iris_0/realsense/depth_camera/depth/points
    rospy.Subscriber(vehicle_type+'_'+vehicle_id+'/realsense/depth_camera/depth/points',PointCloud2, callback_pointcloud)
    rospy.Subscriber(vehicle_type+'_'+vehicle_id+'/realsense/depth_camera/depth/image_raw',Image, callback_img_depth)
    rospy.Subscriber(vehicle_type+'_'+vehicle_id+'/realsense/depth_camera/color/image_raw',Image, callback_img_color)
    
    
    find_target_flag = rospy.Publisher('/zzz/'+vehicle_type+'_'+vehicle_id+'/found_target_flag', String, queue_size=2)
    target_pos = rospy.Publisher('/zzz/'+vehicle_type+'_'+vehicle_id+'/target_pos', PoseStamped, queue_size=10)
    
    rate = rospy.Rate(60) 
    while not rospy.is_shutdown():
        rate.sleep()
        # 发布是否找到yolo目标点标志
        find_target_flag.publish(send_pos_flag)
        if send_pos_flag == 'true':
            target_pos.publish(target_pose)
        
        
        