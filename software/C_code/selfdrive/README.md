# Teensy 4.0 自动驾驶程序

在 Arduino IDE 中打开 `main/main.ino`，开发板选择 **Teensy 4.0**，
USB Type 选择 **Serial**，然后编译、上传。

## 文件与依赖

- `main.ino`：读取雷达、提取特征、运行随机森林、控制车轮。
- `Lidar.h` / `Lidar.cpp`：基于 Teensy 数据采集项目的本地雷达驱动，使用
  `Serial2`、115200 波特率和标准 5 字节扫描点协议。
- `control_slide.h` / `control_slide.cpp`：沿用 Teensy 数据采集程序的左右轮
  控制公式及左轮补偿值 10，增加 PWM 的 0–255 限幅。
- `randomForest.h`：从现有 UNO 自动驾驶项目复制的 **8 特征模型**。

需要安装 Arduino IDE 的 Teensy 开发板支持包。此项目不需要外部
`RPLidarDriver`、`SoftwareSerial`、SD 或 SPI 库。

## 接线

沿用 `collecting_data/main_lidar_SD_test -teensy -lidar.h/main` 的接线：

| 设备信号 | Teensy 4.0 引脚 |
| --- | --- |
| 雷达 TX | 7（Serial2 RX） |
| 雷达 RX | 8（Serial2 TX） |
| 雷达电机控制 | 9（PWM） |
| 左轮驱动控制 | 14（PWM） |
| 右轮驱动控制 | 15（PWM） |
| 错误指示 LED | 2 |
| 就绪指示 LED | 3 |
| 雷达、车轮驱动器 GND | 与 Teensy GND 共地 |

引脚 0/1 的 `Serial1` 在本程序中未使用，可以保留原来的蓝牙接线，
但本程序不读取蓝牙指令。`Serial` 是电脑 USB 调试接口。
车轮和雷达电机通过已有驱动电路控制；电机供电不能直接接 GPIO。
Teensy 4.0 输入不耐受 5V，UART 信号应与其 3.3V 电平兼容。
参见 [PJRC 串口引脚说明](https://www.pjrc.com/teensy/td_uart.html) 和
[Teensy 4.0 硬件说明](https://www.pjrc.com/store/teensy40.html)。

## 运行与参数

上电时先停止车轮，启动雷达。首次取得全部 8 个有效特征后，自动开始
行驶；无需连接电脑。先架空车轮检查左右轮方向和转向，再落地测试。

`main.ino` 顶部可修改：

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| `CAR_SPEED` | 100 | 车轮基础 PWM |
| `STEERING_SENSITIVITY` | 2 | Teensy 原采集程序的转向灵敏度 |
| `LIDAR_MOTOR_PWM` | 200 | 雷达电机 PWM |
| `CONTROL_INTERVAL_MS` | 150 | 模型推理和车轮控制间隔 |
| `FEATURE_TIMEOUT_MS` | 500 | 任一模型输入过期后的停车阈值 |

红色/错误指示引脚 2：启动扫描失败时每 500 ms 翻转；特征缺失或
过期时保持高电平。引脚 3：全部模型输入有效且未过期时保持高电平。
启动扫描失败后，检查接线并重启开发板；运行中短暂断流停车后，
全部特征重新有效时自动恢复行驶。
串口监视器每约 500 ms 输出一次 `steering=...`。

## 模型输入约定

保留现有自动驾驶程序的 200 个角度分箱、整数角度转换，以及顺序固定的
特征索引 `{22, 23, 24, 25, 26, 27, 28, 29}`，距离单位为毫米。
该模型返回类别索引 0–15，本程序沿用原自动驾驶程序将索引直接作为
转向指令的约定。如果重新训练时类别标签不是连续的 0–15，需要加入
对应训练模型 `classes_` 的索引到指令映射。

请保持雷达安装方向与训练数据一致。不要直接换成
`randomForest_anticlockwise_kbest12.h` 或 `software/MLcode/randomForest.h`：
更换模型时必须同步确认特征数量、顺序和类别映射。
雷达驱动沿用参考项目的标准扫描协议，不代表支持所有 RPLIDAR 型号。

## 验证

已使用本机 Teensy 1.62.0 开发板支持包，按
`teensy:avr:teensy40:usb=serial` 完整编译通过。
主机模拟测试覆盖扫描响应超时、分段扫描点、无效角度、特征完整性、
数据过期停车、PWM 限幅和 `millis()` 回绕。
尚未执行实物上传和行驶验证，转向效果取决于已有模型和电机标定。
