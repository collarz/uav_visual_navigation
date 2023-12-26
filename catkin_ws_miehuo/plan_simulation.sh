# 启动mavros
roslaunch px4 maze.launch 
roslaunch px4 indoor3.launch &
# 启动yolo
# cd ~/catkin_ws_miehuo2;  source devel/setup.bash; roslaunch darknet_ros darknet_ros.launch

cd ~/catkin_ws_miehuo; bash scripts/xtdrone_run_vio.sh &

# cd ~/catkin_ws_miehuo2/src/test/script; python multi_vins_transfer.py iris 1 &

cd ~/catkin_ws_miehuo/src/test/script; python multirotor_communication.py iris 0  &

cd ~/catkin_ws_miehuo/src/test/script; python hover.py iris 1 vel &
# 启动ego
cd ~/catkin_ws_miehuo/src/test/script;  python2.7 ego_swarm_transfer.py iris 1 &
roslaunch ego_planner multi_uav.launch &
# cd ~; bash ego.sh
cd ~/XTDrone/motion_planning/3d; rviz -d ego_rviz.rviz
# 发布目标
cd ~/catkin_ws_miehuo2/src/test/script; python goal.py iris_0 &
