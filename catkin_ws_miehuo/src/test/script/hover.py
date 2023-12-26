# encoding = utf-8
from time import sleep
import rospy
from geometry_msgs.msg import Twist
import sys, select, os
import tty, termios
from std_msgs.msg import String


MAX_LINEAR = 20
MAX_ANG_VEL = 3
LINEAR_STEP_SIZE = 0.01
ANG_VEL_STEP_SIZE = 0.01

cmd_vel_mask = False
ctrl_leader = False

if __name__=="__main__":

    settings = termios.tcgetattr(sys.stdin)

    multirotor_type = sys.argv[1]
    multirotor_num = int(sys.argv[2])
    control_type = sys.argv[3]
    
    if multirotor_num == 18:
        formation_configs = ['waiting', 'cuboid', 'sphere', 'diamond']
    elif multirotor_num == 9:
        formation_configs = ['waiting', 'cube', 'pyramid', 'triangle']
    elif multirotor_num == 6:
        formation_configs = ['waiting', 'T', 'diamond', 'triangle']
    
    cmd= String()
    twist = Twist()   
    
    rospy.init_node('hover')
        
        
    if control_type == 'vel':
        multi_cmd_vel_flu_pub = [None]*multirotor_num
        multi_cmd_pub = [None]*multirotor_num
        for i in range(multirotor_num):
            multi_cmd_vel_flu_pub[i] = rospy.Publisher('/xtdrone/'+multirotor_type+'_'+str(i)+'/cmd_vel_flu', Twist, queue_size=10)
            multi_cmd_pub[i] = rospy.Publisher('/xtdrone/'+multirotor_type+'_'+str(i)+'/cmd',String,queue_size=10)
        leader_cmd_vel_flu_pub = rospy.Publisher("/xtdrone/leader/cmd_vel_flu", Twist, queue_size=10)
        leader_cmd_pub = rospy.Publisher("/xtdrone/leader/cmd", String, queue_size=10)
 
    else:
        multi_cmd_accel_flu_pub = [None]*multirotor_num
        multi_cmd_pub = [None]*multirotor_num
        for i in range(multirotor_num):
            multi_cmd_accel_flu_pub[i] = rospy.Publisher('/xtdrone/'+multirotor_type+'_'+str(i)+'/cmd_accel_flu', Twist, queue_size=10)
            multi_cmd_pub[i] = rospy.Publisher('/xtdrone/'+multirotor_type+'_'+str(i)+'/cmd',String,queue_size=10)
        leader_cmd_accel_flu_pub = rospy.Publisher("/xtdrone/leader/cmd_accel_flu", Twist, queue_size=10)
        leader_cmd_pub = rospy.Publisher("/xtdrone/leader/cmd", String, queue_size=10)
    
    forward  = 0.0
    leftward  = 0.0
    upward  = 0.0
    angular = 0.0

    icount = 0
    while(1):  
        icount +=1
        # print(icount)
        if icount == 1:

            upward = 0.5
            print(upward)

        elif icount == 2:
            cmd = 'OFFBOARD'
            print(upward)
            print(cmd)
            sleep(1)
        elif icount == 3:
            cmd = 'ARM'
            print(upward)
            print(cmd)
            sleep(1)
        elif icount == 4:
            forward   = 0.0
            leftward   = 0.0
            upward   = 0.0
            angular  = 0.0
            cmd = 'HOVER'
            print(upward)
            print(cmd)
            sleep(8)
        else:
            m = icount
            sleep(5)
            
            
        twist.linear.x = forward; twist.linear.y = leftward ; twist.linear.z = upward
        twist.angular.x = 0.0; twist.angular.y = 0.0;  twist.angular.z = angular
        
        print(twist)
        
        for i in range(multirotor_num):
            if ctrl_leader:
                if control_type == 'vel':
                    leader_cmd_vel_flu_pub.publish(twist)
                else:
                    leader_cmd_aceel_flu_pub.publish(twist)
                leader_cmd_pub.publish(cmd)
            else:
                if not cmd_vel_mask:
                    if control_type == 'vel':
                        multi_cmd_vel_flu_pub[i].publish(twist)   
                    else:
                        multi_cmd_accel_flu_pub[i].publish(twist)
                multi_cmd_pub[i].publish(cmd)
                
        cmd = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
