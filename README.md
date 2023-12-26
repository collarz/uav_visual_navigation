### winglab无人机项目视觉导航仿真代码（Ubuntu18.04）


 **安装过程** 

```
cd ~
git clone https://github.com/collarz/uav_visual_navigation.git
mv uav_visual_navigation/catkin_miehuo .
rm -rf uav_visual_navigation
```

如果没有配置ros基本环境执行此部分内容
```
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu focal main" > /etc/apt/sources.list.d/ros-latest.list'
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
sudo apt update
sudo apt install ros-melodic-desktop
echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

如果没有配置ceres请执行此部分内容
```
sudo apt-get install cmake
sudo apt-get install libgoogle-glog-dev libgflags-dev
sudo apt-get install libatlas-base-dev
sudo apt-get install libeigen3-dev
sudo apt-get install libsuitesparse-dev

wget ceres-solver.org/ceres-solver-1.14.0.tar.gz
#解压安装包
tar -xvf ceres-solver-1.14.0.tar.gz

cd ceres-solver-1.14.0
mkdir build
cd build
cmake ..
sudo make 
sudo make test
sudo make install
```

配置realsense的SDK
```
git clone -b v2.50.0 https://github.com/IntelRealSense/librealsense.git 
#2）安装依赖包
sudo apt-get install libudev-dev pkg-config libgtk-3-dev
sudo apt-get install libusb-1.0-0-dev pkg-config
sudo apt-get install libglfw3-dev
sudo apt-get install libssl-dev
#3）安装权限脚本
cd ~/librealsense
sudo cp config/99-realsense-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && udevadm trigger 
#4）编译
mkdir build
cd build
cmake ../ -DBUILD_EXAMPLES=true
make
sudo make install
#5）使用
realsense-viewer
```

配置realsense-ros
```
sudo apt-get install ros-$ROS_DISTRO-realsense2-camera
sudo apt-get install ros-$ROS_DISTRO-realsense2-description
```
编译
```
##请确保已配置好上述基本环境
cd ~/catkin_miehuo
catkin_make 
source ~/catkin_ws/devel/setup.bash
```

配置mavros
```
sudo apt-get install ros-melodic-mavros ros-melodic-mavros-extras ros-melodic-control-toolbox
cd /opt/ros/melodic/lib/mavros
sudo ./install_geographiclib_datasets.sh
```

 **仿真测试** 

参考语雀文档https://www.yuque.com/xtdrone/manual_cn/basic_config 搭建XTDrone和PX4

参考 ~/catkin_ws_miehuo/plan_simulation.sh中的代码依次执行
