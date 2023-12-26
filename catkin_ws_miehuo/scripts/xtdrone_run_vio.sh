rosrun vins vins_node ~/catkin_ws/src/VINS-Fusion/config/xtdrone_sitl/px4_sitl_stereo_imu_config.yaml __ns:="iris_0"&
roslaunch vins vins_rviz.launch &
cd ~/catkin_ws_miehuo2/src/test/script; python multi_vins_transfer.py iris 1 &
# cd ~/catkin_ws_miehuo2/src/test/script; python multirotor_communication.py iris 0  &
# cd ~/catkin_ws/src/fire_find/scripts; python hover.py iris 1 vel &