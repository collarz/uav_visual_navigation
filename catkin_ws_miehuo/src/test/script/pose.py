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
        print(box_minX, box_maxX)
        for i in range(box_centerX-bias, box_centerX+bias):
            for j in range(box_centerY-bias, box_centerY+bias):
        # for i in range(box_minX, box_maxX):
        #     for j in range(box_minY, box_maxY):
                z_current = depth_image[i, j] 
                if(math.isnan(z_current)==False):
                    count_current = count_current + 1
                    sum_Z = sum_Z + z_current
        if count_current != 0:
            z = sum_Z/count_current
        print(count_current)
    return z

def callback_depthinfo(data1, data2):
    global bridge,u,v,Rot
    global target_pose
    bridge = CvBridge()

    #pub = rospy.Publisher('/Distance', Distance, queue_size=1)
    #rate = rospy.Rate(10)
    color_image = bridge.imgmsg_to_cv2(data1, 'bgr8')
    depth_image = bridge.imgmsg_to_cv2(data2, '32FC1') #利用rostopic echo /iris_0/realsense/depth_camera/depth/image_raw/encoding 查看话题的编码

    # cv2.imshow('color_image',color_image)
    # cv2.imshow('depth_image',depth_image)
    # cv2.waitKey(1000)
    
    #目标中心点的xy坐标(u,v)
    u = int(u)
    v = int(v)
    #中心点深度值
    Zc = box_ave(depth_image, u, v) 
    #相机内参矩阵
    intrinsic_M = np.array([[554.254691191187, 0.0, 320.5],  [0.0, 554.254691191187, 240.5],  [0.0, 0.0, 1.0]])
    
    # 像素坐标系
    uv_M = np.array([[u],[v],[1]])
    
    # 相机坐标系
    pos_C = np.dot(np.linalg.inv(intrinsic_M), uv_M)*Zc
    print('pos_C',pos_C)
    
    #相机坐标系ENU
    pos_Cx_ENU = pos_C[2]
    pos_Cy_ENU = pos_C[0]*(-1)
    pos_Cz_ENU = pos_C[1]*(-1)
    pos_C_ENU = (pos_Cx_ENU, pos_Cy_ENU, pos_Cz_ENU)
    
    # 世界坐标系(两种方法)
    T = np.array([[X_w],[Y_w],[Z_w]])
    pos_W = np.dot(np.linalg.inv(Rot), (pos_C_ENU - T))
    print('pos_W',pos_W)
        
    extrinsic_M =  np.hstack((Rot, T))
    extrinsic_M = np.vstack((extrinsic_M, np.array([[0,0,0,1]]) ) )#坐标齐次化
    pos_C_ENU = np.vstack((pos_C_ENU, np.array([1])))
    pos_W1 = np.dot(np.linalg.inv(extrinsic_M), pos_C_ENU)
    print('pos_W1',pos_W1)

