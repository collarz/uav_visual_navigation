# 启动mavros
roslaunch mavros px4.launch fcu_url:="/dev/ttyACM0:921600" __ns:="iris_0"
# 启动yolo
# cd ~/catkin_ws_miehuo;  source devel/setup.bash; roslaunch darknet_ros darknet_ros.launch
# 启动d435i相机 + 启动vins + vins转换成px4可以用的形式
cd ~/catkin_ws_miehuo; bash scripts/true_run_vio.sh &
# # 查看vins里程计
# roslaunch vins vins_rviz.launch 
# 通讯代码
cd ~/catkin_ws_miehuo/src/test/script; python multirotor_communication.py iris 0
cd ~/catkin_ws_miehuo/src/test/script; python hover.py iris 1 vel 
# 启动ego
cd ~/catkin_ws_miehuo/src/test/script;  python2.7 ego_swarm_transfer.py iris 1 &
roslaunch ego_planner multi_uav.launch &
# 发布目标
cd ~/XTDrone/motion_planning/3d; rviz -d ego_rviz.rviz

