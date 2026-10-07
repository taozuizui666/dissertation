# Teensy 4.0 自动驾驶程序

在 Arduino IDE 中打开 `main/main.ino`，开发板选择 **Teensy 4.0**，
USB Type 选择 **Serial**，然后编译、上传。

## 文件与依赖

- `main.ino`：读取雷达、提取特征、运行随机森林、控制车轮。
- `Lidar.h` / `Lidar.cpp`：基于 Teensy 数据采集项目的本地雷达驱动，使用
  `Serial2`、115200 波特率和标准 5 字节扫描点协议。
- `control_slide.h` / `control_slide.cpp`：沿用 Teensy 数据采集程序的左右轮
  控制公式及左轮补偿值 10，增加 PWM 的 0–255 限幅。
- `randomForest.h`：训练生成的模型及 `ModelConfig` 输入配置、类别到指令映射。
  由训练脚本同步，不手动修改或提交到 Git；首次编译前需生成该文件。

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

上电时先停止车轮，启动雷达。首次取得全部 K 个有效特征后，自动开始
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

分辨率、距离上界、采集扇区、K 和特征索引均读取 `randomForest.h` 的
`ModelConfig`。距离单位为毫米，保持采集程序的整数角度转换。
模型返回类别索引，通过 `ModelConfig::commandForClass()` 转为真实操作指令后
再控制车轮，因此支持训练标签不连续的情况。

在 dissertation 根目录运行 `python3 software/MLcode/train_model.py` 即可重新训练
并同步模型，K 等参数在该脚本顶部修改。详见 [训练说明](../../MLcode/README.md)。
模型头文件属于生成产物，Git 不跟踪；首次获取工程时需要先准备数据并生成模型。

请保持雷达安装方向与训练数据一致。重新训练时，使用 `MLcode/train_model.py`
生成并同步完整模型，确保森林、特征索引及指令映射一起更新。
雷达驱动沿用参考项目的标准扫描协议，不代表支持所有 RPLIDAR 型号。

## 验证

已使用本机 Teensy 1.62.0 开发板支持包，按
`teensy:avr:teensy40:usb=serial` 完整编译通过。
主机模拟测试覆盖扫描响应超时、分段扫描点、无效角度、特征完整性、
数据过期停车、PWM 限幅和 `millis()` 回绕。
尚未执行实物上传和行驶验证，转向效果取决于已有模型和电机标定。
