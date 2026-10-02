import serial
import math
import numpy as np
from matplotlib import pyplot as plt
from collections import deque
import time
from matplotlib.animation import FuncAnimation

class RPLidarVisualizer:
    def __init__(self, port='COM12', baudrate=115200):
        """
        初始化RPLidar可视化器
        """
        # 串口参数
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        
        # Lidar数据参数
        self.Lidar_data_bin_num = 5
        self.Lidar_head_num = 7
        
        # 数据缓冲区 - 使用deque提高性能
        self.max_points = 360  # 最大显示点数
        self.angle_buff = deque(maxlen=self.max_points)
        self.dist_buff = deque(maxlen=self.max_points)
        
        # 批处理参数
        self.batch_size = 100  # 每批处理的数据点数
        self.temp_angles = []
        self.temp_dists = []
        
        # 性能监控
        self.last_update_time = time.time()
        self.update_interval = 0.01  # 50ms更新一次（20 FPS）
        self.frame_count = 0
        self.fps_update_time = time.time()
        
        # 图形对象
        self.fig = None
        self.ax = None
        self.scat = None
        
    def connect_serial(self):
        """连接串口"""
        while not self.ser:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=0.01)
                print(f"成功连接到 {self.port}")
                return True
            except serial.SerialException:
                print(f"等待连接 {self.port}...")
                time.sleep(1)
        return False
    
    def wait_for_header(self):
        """等待正确的数据头"""
        print("等待Lidar数据头...")
        while True:
            if self.ser.in_waiting >= self.Lidar_head_num:
                data = self.ser.read(self.Lidar_head_num)
                head_values = ' '.join(f'{b:02X}' for b in data)
                if head_values == "A5 5A 05 00 00 40 81":
                    print("检测到正确的数据头，开始接收数据")
                    return True
            time.sleep(0.01)
    
    def setup_plot(self):
        """设置极坐标图"""
        plt.ion()
        self.fig, self.ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(10, 10))
        
        self.ax.set_theta_zero_location('N')
        self.ax.set_theta_direction(-1)
        self.ax.set_ylim(0, 10)
        self.ax.set_title("RPLidar Graph")
        
        # 初始化散点图
        self.scat = self.ax.scatter([], [], c='b', s=2, alpha=0.6)
        
        # 添加网格和标签
        self.ax.grid(True, alpha=0.3)
        
        # 添加FPS显示
        self.fps_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes,
                                    fontsize=10, verticalalignment='top',
                                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
    def process_data(self):
        """处理串口数据 - 批量读取"""
        # 检查可用数据量
        available = self.ser.in_waiting
        
        if available < self.Lidar_data_bin_num:
            return False
        
        # 批量读取数据（限制一次读取量，避免阻塞）
        read_size = min(available, self.Lidar_data_bin_num * 100)  # 一次最多读100个数据点
        read_size = (read_size // self.Lidar_data_bin_num) * self.Lidar_data_bin_num  # 确保是5的倍数
        
        data_chunk = self.ser.read(read_size)
        
        # 批量解析数据
        for i in range(0, len(data_chunk), self.Lidar_data_bin_num):
            data = data_chunk[i:i+self.Lidar_data_bin_num]
            
            if len(data) == self.Lidar_data_bin_num:
                # 解析角度和距离
                angle_raw = ((data[2] << 8) | data[1]) >> 1
                distance_raw = (data[4] << 8) | data[3]
                
                angle_real = angle_raw / 64.0
                distance_real = distance_raw / 4000.0
                
                # 过滤无效数据
                if 0 <= angle_real <= 360 and 0.1 <= distance_real <= 10:
                    angle_rad = math.radians(angle_real)
                    self.temp_angles.append(angle_rad)
                    self.temp_dists.append(distance_real)
        
        # 批量更新缓冲区
        if len(self.temp_angles) >= self.batch_size:
            self.angle_buff.extend(self.temp_angles[:self.batch_size])
            self.dist_buff.extend(self.temp_dists[:self.batch_size])
            
            # 清除已处理的数据
            self.temp_angles = self.temp_angles[self.batch_size:]
            self.temp_dists = self.temp_dists[self.batch_size:]
            
            return True
        
        return False
    
    def update_plot(self):
        """更新图形显示 - 限制更新频率"""
        current_time = time.time()
        
        # 限制更新频率
        if current_time - self.last_update_time < self.update_interval:
            return
        
        if len(self.angle_buff) > 0:
            # 使用numpy数组提高性能
            angles = np.array(self.angle_buff)
            dists = np.array(self.dist_buff)
            
            # 更新散点图数据
            self.scat.set_offsets(np.c_[angles, dists])
            
            # 更新FPS显示
            self.frame_count += 1
            if current_time - self.fps_update_time >= 0.1:
                fps = self.frame_count / (current_time - self.fps_update_time)
                self.fps_text.set_text(f'FPS: {fps:.1f}\nNumber: {len(self.angle_buff)}')
                self.frame_count = 0
                self.fps_update_time = current_time
            
            # 高效更新画布
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
            
            self.last_update_time = current_time
    
    def run(self):
        """主运行循环"""
        # 连接串口
        self.connect_serial()
        
        # 等待数据头
        self.wait_for_header()
        
        # 设置图形
        self.setup_plot()
        
        print("开始实时显示...")
        print("提示：")
        print("- 优化了批处理，减少更新频率")
        print("- 使用deque提高缓冲区性能")
        print("- 限制FPS为20，平衡流畅度和CPU占用")
        
        try:
            while True:
                # 处理数据
                self.process_data()
                
                # 更新显示
                self.update_plot()
                
                # 避免CPU占用过高
                time.sleep(0.001)
                
        except KeyboardInterrupt:
            print("\n停止运行")
        finally:
            if self.ser:
                self.ser.close()
            plt.close('all')

# 使用示例
if __name__ == "__main__":
    visualizer = RPLidarVisualizer(port='COM12', baudrate=115200)
    visualizer.run()