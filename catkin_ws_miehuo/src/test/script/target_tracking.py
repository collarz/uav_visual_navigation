import rospy
from geometry_msgs.msg import Twist, PoseStamped
from std_msgs.msg import String
import sys 
sys.path.append('/home/origami-hui/catkin_ws/devel/lib/python3/dist-packages')
from pyquaternion import Quaternion
from darknet_ros_msgs.msg import BoundingBoxes
import time
import math

#引入点云数据
from sensor_msgs.msg import PointCloud2
from sensor_msgs import point_cloud2

def darknet_callback(data):

    for target in data.bounding_boxes:
        if(target.id==0): #此处根据bounding_boxes话题的目标点id设置
            print('发现目标点')
        return True
    return False
    
        
def local_pose_callback(data):
    global height, target_height, target_set
    height = data.pose.position.z    
    if not target_set:
        target_height = height     
        target_set = True    

def cam_pose_callback(data):
    global theta
    q = Quaternion(data.pose.orientation.w, data.pose.orientation.x, data.pose.orientation.y, data.pose.orientation.z)
    theta = q.yaw_pitch_roll[1]

def callback_pointcloud(data):
    #用subscriber接收深度相机topic下的点云数据，获取点云中的XYZ坐标
    assert isinstance(data, PointCloud2)
    gen = point_cloud2.read_points(data, field_names=("x", "y", "z"), skip_nans=True)
    time.sleep(1)
    #print (type(gen))
    for p in gen:
        print ('x: '+str(p[0])+',y: '+str(p[1])+',z: '+str(p[2]))
            
if __name__ == "__main__":
    height = 0  
    target_height = 0
    target_set = False
    find_cnt = 0
    find_cnt_last = 0
    not_find_time = 0
    get_time = False
    twist = Twist()
    cmd = String()
    theta = 0
    u_center=640/2 
    v_center=360/2
    fx = 205.46963709898583
    fy = 205.46963709898583
    Kp_xy = 0.5
    Kp_z = 1
    vehicle_type = sys.argv[1]
    vehicle_id = sys.argv[2]
    rospy.init_node('fire_tracking')
    rospy.Subscriber("/uav_"+vehicle_id+"/darknet_ros/bounding_boxes", BoundingBoxes, darknet_callback,queue_size=1)
    rospy.Subscriber(vehicle_type+'_'+vehicle_id+"/mavros/local_position/pose", PoseStamped, local_pose_callback,queue_size=1)
    rospy.Subscriber('/xtdrone/'+vehicle_type+'_'+vehicle_id+'/cam_pose', PoseStamped, cam_pose_callback,queue_size=1)

    rospy.Subscriber(vehicle_type+'_'+vehicle_id+'/realsense/depth_camera/depth/points',PointCloud2, callback_pointcloud)


    cmd_vel_pub = rospy.Publisher('/xtdrone/'+vehicle_type+'_'+vehicle_id+'/cmd_vel_flu', Twist, queue_size=1)
    cmd_pub = rospy.Publisher('/xtdrone/'+vehicle_type+'_'+vehicle_id+'/cmd', String, queue_size=1)
    rate = rospy.Rate(60) 
    while not rospy.is_shutdown():
        rate.sleep()
        cmd_vel_pub.publish(twist)
        cmd_pub.publish(cmd)
        if find_cnt - find_cnt_last == 0:
            if not get_time:
                not_find_time = rospy.get_time()
                get_time = True
            if rospy.get_time() - not_find_time > 5.0:
                twist.linear.x = 0.0
                twist.linear.y = 0.0
                twist.linear.z = 0.0
                cmd = 'HOVER'
                print(cmd)
                get_time = False
        find_cnt_last = find_cnt
