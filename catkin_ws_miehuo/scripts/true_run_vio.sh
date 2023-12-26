roslaunch realsense2_camera rs_camera_vins.launch &
rosrun vins vins_node ~/catkin_ws_miehuo/src/VINS-Fusion/config/realsense_d435i/realsense_stereo_imu_config.yaml __ns:="iris_0" &
cd ~/catkin_ws_miehuo/src/test/script; python multi_vins_transfer.py iris 1 