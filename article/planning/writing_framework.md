# Dissertation 写作框架

整理日期：2026 年 10 月 25 日。本文依据 article 内的学校文件、当前源码和本机已有报告，规划论文章节、论证关系、图表及待补实验。章节安排和页数为写作建议；实验结果仅覆盖相应报告记录的条件。本文未运行新的训练或驾驶实验。

## 1 论文定位

选题沿用导师确认的方向：

**Integrating LiDAR and Machine Learning on Low-Cost ARM Microcontrollers for Autonomous Navigation**

建议以以下问题贯穿全文：在低成本 ARM 微控制器的计算与存储约束下，如何利用仿真教师生成训练数据，构建仅依赖 LiDAR 的轻量控制模型，并通过离线、闭环及硬件实验评价其性能？

当前工作形成的技术路线为：

```text
Gazebo 几何与车辆状态 → 特权 PPO 教师 → 动作标签
                           同步采集 LiDAR
                                   ↓
                按地图组织的 LiDAR—动作数据
                                   ↓
                  随机森林训练及独立地图验证
                                   ↓
                    Gazebo LiDAR 闭环驾驶
                                   ↓
                  C++ 导出与主机推理一致性验证
                                   ↓
             ARM 资源与时延测试、实车闭环验证（待补）
```

研究范围应写清为静态场景、固定目标前进速度下的局部避障巡航。当前系统没有体现完整的目标点导航、全局路径规划或 SLAM；现有正轮速动作也不支持原地旋转与倒车。标题中的 autonomous navigation 应在 Introduction 中由实际任务定义限定。

可提出三个研究问题：

- **RQ1 数据与学习**：特权教师生成的 LiDAR—动作数据，能否支持仅输入 LiDAR 的随机森林学习巡航控制，并在未参与森林拟合的地图上有效运行？
- **RQ2 闭环与鲁棒性**：离线动作一致性与实际闭环表现之间有什么关系？雷达缺失、起始偏差和地图变化会怎样影响驾驶？
- **RQ3 嵌入式可行性**：模型能否在目标 ARM 板上满足存储、推理和完整控制周期要求？仿真效果能在多大程度上迁移至实车？

RQ1 和 RQ2 已有部分结果；RQ3 尚缺目标板资源与实车量化证据。贡献可以围绕数据流程、轻量策略实现和分层验证组织，暂不宣称提出新的 PPO 或随机森林算法，也不在缺少文献比较时宣称首创。

## 2 学校文件中的要求

### 2.1 写作与版式

依据 [SPMS dissertation 指南](../guidelines/SPMS_Guideline_MSc_Dissertation.pdf)，并对照 [MSPSI Word 指南](../guidelines/MSPSI_Guideline_Dissertation.docx)：

| 项目 | 本地指南内容 |
| --- | --- |
| 语言与叙述 | 英文，第三人称；表达清晰、简洁，使用自己的语言 |
| 篇幅 | 约 60–100 页为指南建议；说明会也列出该范围 |
| 正文 | Times New Roman，12 pt，1.5 倍行距 |
| 纸张与页边距 | A4；左侧约 3.5 cm，其余约 3 cm |
| 单位 | 使用 SI 单位；数据保存的 mm 与模型/运动学使用的 m 应明确换算 |
| 章节 | 通常不超过六至七章；包含引言、文献综述、实际工作、结果分析和结论 |
| 摘要 | 通常约一页，包含问题、方法、实际结果和贡献 |
| 图表 | 按章依次编号，有标题，在正文引用，尽量靠近讨论位置 |
| 参考文献与附录 | 参考文献只列实际引用的来源；附录按 A、B 等编号并在正文引用 |

前置及后置内容按指南正文的顺序规划：Title Page、Statement of Originality、Supervisor Declaration Statement、Authorship Attribution Statement、Table of Contents、Abstract、可选致谢/缩略语/符号表、List of Figures、List of Tables、正文章节、References、可选 Appendices。封面和声明页使用学校提供的样式。

### 2.2 提交事项

[AY2526 T3 说明会材料](../guidelines/AY2526_T3_Dissertation_Briefing.pdf) 第 6 页写明 iThenticate 相似度低于 20%、Artificial Intelligence Index 低于 30%；指南另写提交 Turnitin HTML 原创性报告。两份本地文件对工具名称的表述不同，提交前应确认学院实际要求。说明会文件注明更新于 2026 年 1 月 14 日且可能调整，本文不把其内容当成已核实的最新校方政策。

说明会要求答辩包含题目、具体目标、意义、方法、创新成果和参考文献，最终幻灯片至少提前一天提交。因此章节中应能直接提取“研究目标—方法—结果—贡献”的证据。

## 3 当前材料能够支持的论述

### 3.1 平台和方法

| 已有材料 | 可以支撑的写作内容 | 需要区分的边界 |
| --- | --- | --- |
| `hardware/`、`software/C_code/collect_data/`、`software/C_code/selfdrive/` | 车辆、Teensy 4.0、雷达接口、采集和控制程序 | 源码与编译记录不等于实车运行结果；成本需 BOM 支撑 |
| `Gazebo_simulation/my_gazebo_launch/vehicle_config.h` | 差速模型、共享参数、LiDAR 分桶、标签到轮速的映射 | 仿真使用轮速接口，旧实车固件使用 PWM，不能直接等同 |
| `rl_training/privileged/observation.py` | 地图真值距离场与车辆状态组成的教师观测 | 教师不是只看 LiDAR 的可部署策略 |
| `rl_training/privileged/collect_data.py`、`collection_spawns.py` | 教师标注、时间配对、初始扰动、近墙起步和数据增强 | 近墙起步不等于学生失误后的在线专家纠正 |
| `software/MLcode/train_model.py` | 地图分组、数据校验、森林拟合、指标和 C++ 导出 | 当前正式基线为 200 列全部保留；K 筛选是可选实验 |
| `run_random_forest.py`、`rl_training/common/forest_evaluation.py` | LiDAR 闭环驾驶与可重复评估 | GUI 驾驶与暂停步进评分的运行时序不同 |
| `rl_training/privileged/train_multi_map.py` | 多地图联合训练与独立验收的实现设计 | 不能据此认定当前采集教师已由该脚本完成多地图训练 |

共享仿真配置目前为：目标前进速度 0.2 m/s、15 个转向标签 0–14、7 直行、控制步长在当前采集记录中为 0.2 s；雷达为 200 列毫米距离，前方有效扇区，364 原始点/圈、5.5 Hz。编号 50–150 的列固定为零，实际有效角度列为 99 个，不能将输入宽度 200 写成 200 个有效方向测量。

教师观测为 17×17 距离场加速度、角速度及上一动作，共 292 维。学生当前仅使用一帧 LiDAR。这种输入信息差异意味着教师动作未必能由单帧 LiDAR 唯一恢复，应作为动作误差的一种可能解释，不能未经实验认定为唯一原因。

### 3.2 已有数值与证据位置

以下数字取自报告，不是本次重新运行实验所得。

| 项目 | 已核对记录 | 可用于论文的表述 |
| --- | --- | --- |
| 特权教师 | `rl_models/privileged/policies/validated_privileged_2392588_20261011_074049/validation_summary.json` | 2,392,588 训练步；记录的 8 回合共约 4,800 仿真秒，约 959.90 m，零碰撞及列出的运动失败 |
| 数据采集 | `results/datasets/collection_20261023_092900_850f9f/metadata.json` | 4 图×20 回合×3,600 s；80 回合均达到时限；60 个普通扰动起步、20 个近墙起步 |
| 原始与增强数据 | 同上 | 原始 1,439,983 行，增强 1,439,983 行；17 个缺帧决策点未保存为样本 |
| 森林划分 | `software/ML_model/simulation/training_report.json` | 三图训练 1,079,984 行；`ellipse_002` 留出 359,999 行；仅使用 dropout 版本；验证地图未重新参与拟合 |
| 森林配置 | 同上 | 88 棵树，最大深度 3，保留全部 200 列，随机种子 42 |
| 离线表现 | 同上 | accuracy 74.9799%；训练多数类策略在验证上的 accuracy 62.4121%；macro F1 0.44244；档位 MAE 0.25023；±1 档准确率 99.99917% |
| C++ 导出 | 同上 `export_checks` | 3,149 个主机验证输入通过；该轮 Teensy build 检查关闭 |
| RF 常规闭环 | `results/random_forest/evaluation_20261025_135333_cab2aa/evaluation.json` | 4 图×5 回合×180 s，20 回合均达到时限；约 719.96 m，零碰撞/卡住/绕圈/持续低速/越界；自定义评分 95.3983/100 |
| RF 缺失短测 | `results/random_forest/evaluation_20261025_140050_ed5c24/evaluation.json` | `ellipse_002` 上 5% 丢点、10% 丢点、连续扇区缺失各 1 回合，每回合 10 s，均到时限；不足以代表正式鲁棒性实验 |

表内相对路径中，`rl_models/` 和 `results/` 位于 `Gazebo_simulation/` 下；训练报告位于仓库根目录的 `software/` 下。

需保留的解释：

1. 本机当前 RF 模型的 SHA-256 与上述常规闭环报告一致，值为 `174279ddbe9decc96f8e4a4ad1427c2fffb56939561e7837baabf8d6e4166b99`。
2. 当前教师保存的 `run_config.json` 记录训练地图为 `train_world3`，不能用当前多地图脚本顶部配置替代历史模型实际配置。若后续换教师，应重新记录模型、归一化状态、地图与数据批次。
3. `ellipse_002` 是当前森林的留出地图。教师是否见过某图、森林是否拟合某图、调参是否使用某图，需要分别记录。若反复据其结果调参，该图将成为验证图，最终测试应另留地图。
4. 当前森林实际学习到的类别为 5、6、7、8、9、12，不是全部 15 类。大量连续采样行与增强副本不等于同样数量的独立场景。
5. 顶层 macro F1 按验证实际出现的类别计算；报告中固定类别 `classification_report` 的 macro avg 为另一口径，不能混写。极少数动作的召回率为零，需要同时展示类别数量。
6. 20/20 回合成功只表明该组条件下的观察结果，不能宣称未知场景可靠性为 100%。跨模型比较应采用相同地图、起点、速度、噪声和时长。
7. 部分常规闭环回合的保守圆盘净空最小值为 0，但没有碰撞信号。这两种指标定义不同；需要结合轨迹解释，不能把零碰撞写成始终保有安全净空。净空实现将负值截断为零。
8. 现有 LiDAR PPO 验收摘要记录约 0.1 m/s，而特权教师及 RF 为约 0.2 m/s，不能直接用两份历史报告排名。

## 4 建议目录与各章任务

采用七章，正文初步预算 61–77 页；加前置页、参考文献及必要附录，尽量控制在约 75–95 页。页数用于控制重点，并非学校对各章的规定。

### Chapter 1 Introduction 引言 5–6 页

1.1 Background of Low-Cost Autonomous Mobile Platforms  
1.2 Motivation and Problem Statement  
1.3 Research Objectives and Questions  
1.4 Scope and Constraints  
1.5 Contributions of the Dissertation  
1.6 Organization of the Dissertation

从传感器、嵌入式算力和自主巡航需求引出问题，说明为何在仿真中训练教师、为何最终使用轻量学生。将三个研究问题对应到可测指标。贡献先以待验证目标组织，最终随实验结果改写。

图表：整体技术路线图；研究目标和评价指标对应表。避免大篇幅泛谈人工智能或工业自动驾驶。

### Chapter 2 Literature Review 文献综述 9–11 页

2.1 LiDAR-Based Local Navigation and Reactive Obstacle Avoidance  
2.2 Machine Learning on Resource-Constrained Microcontrollers  
2.3 Decision Trees and Random Forests for Control  
2.4 Reinforcement Learning and PPO for Mobile Robots  
2.5 Privileged Teachers and Imitation Learning  
2.6 Simulation to Reality and Sensor Robustness  
2.7 Research Gap and Positioning of This Work

综述围绕选择依据和研究缺口：规则避障、神经策略、树模型分别需要什么输入和算力；教师如何利用仿真真值；学生如何从示范中学习；为何离线分类不能代替闭环评价。

图表：相关研究对比表，字段包括任务、传感器、策略、部署平台、仿真/实车证据、资源指标和局限。优先引用论文原文；工具文档用于说明实现，不承担全部研究背景。

### Chapter 3 System Architecture and Platform Design 系统与平台 9–11 页

3.1 System Requirements and Overall Architecture  
3.2 Physical Vehicle and ARM Microcontroller Platform  
3.3 LiDAR Interface and Observation Representation  
3.4 Differential-Drive Model and Discrete Steering Actions  
3.5 Gazebo Environment and Map Construction  
3.6 Control Timing and Simulation to Hardware Interfaces

说明车体、Teensy、雷达、电机驱动和供电连接；给出差速运动学和标签到左右轮速的关系。解释原始扫描、整数角度分桶、有效扇区、零值含义及 mm/m 换算。地图用几何参数和用途说明，包含训练、选模和测试划分。

对 MSPSI 方向，应着重呈现测量链和控制链：雷达安装方向、扫描周期、量程、盲区、测量误差、数据时效性，以及它们如何影响决策。当前仿真噪声标准差 1 cm 是配置假设，不是已完成的传感器标定结果。

图表：系统框图、实车照片与尺寸、接线图、BOM 与实际成本、雷达分桶示意图、差速模型图、地图总览和平台参数表。

### Chapter 4 Privileged Teacher and Demonstration Data 教师与数据 11–14 页

4.1 Problem Formulation and Teacher Student Information  
4.2 Privileged Observation and PPO Teacher  
4.3 Reward Design and Episode Termination  
4.4 Teacher Training and Qualification Protocol  
4.5 LiDAR Action Pairing and Data Provenance  
4.6 Spawn Perturbation and Near-Wall Recovery Starts  
4.7 Dropout Augmentation and Dataset Composition

形式化教师输入、学生输入、动作和监督目标。PPO 理论只介绍支持实际设计所需的部分。奖励要与动作约束、碰撞/卡住/绕圈/低速终止一起说明，不能只列公式。

用保存的教师配置叙述已执行训练；将多地图训练能力与已完成实验分开。展示时间轴：有效扫描 → 决策边界 → 教师动作 → 执行结束；说明不是假定所有传感器完全同步。解释缺帧跳过、连续缺帧停止、来源指纹和回合行号范围。

解释普通起步扰动和近墙起步如何扩大状态覆盖。近墙回合比例为 25%，不等于近墙样本占全部行数的 25%。增强是对非零距离抽样置零，保留标签；同一原始/增强样本必须在划分同一侧。

图表：教师与学生信息流、奖励及终止规则表、配对时间轴、起步场景图、数据量和标签分布、教师曲线与验收摘要。曲线须对应实际采集所用模型及其续训链。

### Chapter 5 Random Forest Learning and Embedded Implementation 森林与嵌入式实现 9–11 页

5.1 Data Validation and Leakage Prevention  
5.2 Input Features and Optional Feature Selection  
5.3 Random Forest Training and Model Complexity  
5.4 Offline Metrics and Class Imbalance  
5.5 C++ Export and Inference Consistency  
5.6 Embedded Control Integration and Resource Measurement

围绕现有正式入口描述数据校验、地图留出、冻结模型和输出报告。当前基线是全部 200 列、88 棵树、深度 3；K 特征筛选放在消融方案中，结果产生后再写结论。

说明精确动作一致率、macro F1、混淆矩阵、档位 MAE 和容差准确率分别回答什么问题。明确监督标签是教师动作，离线评价测量动作模仿，不是直接测量安全性。

介绍 Python/C++ 在真实样本、零值、随机输入和阈值边界上的一致性。目标板应测编译后 Flash、RAM、推理时间和完整控制周期。当前 `.h` 文件字节数只是源文件体积，不能当作板上占用。

硬件整合仍需统一：仿真 7 直行与旧固件 10 直行；轮速目标与 PWM 控制；允许缺失零值与旧固件逐特征新鲜度条件；仿真 200 ms 与固件 150 ms 的周期。尤其保留 200 列中的固定零列时，需要评估旧固件是否会一直等待这些列被更新。此处记录设计缺口，不能写成已经完成仿真模型的实车部署。

图表：数据/模型流程、复杂度参数、Python/C++ 校验表、目标板内存和时延表、嵌入式控制时序图。

### Chapter 6 Experimental Results and Discussion 实验结果与讨论 14–18 页

6.1 Experimental Design and Reproducibility  
6.2 Teacher Qualification and Dataset Coverage  
6.3 Offline Action Prediction Results  
6.4 Closed-Loop Driving on Fitting and Held-Out Maps  
6.5 Sensor Dropout and Starting-State Robustness  
6.6 Model Complexity and Data Augmentation Ablations  
6.7 Embedded Resource and Physical Driving Results  
6.8 Failure Cases and Limitations

先固定实验条件，再按研究问题组织结果。现有常规闭环结果可先成表，未完成部分保留明确的待补状态，不能预写成功结论。

推荐主要闭环指标：完成率、失败原因、行驶距离、每百米碰撞回合数、净空分位数、安全净空时间比例、速度合规率、动作切换频率和推理时延。当前实现每回合在碰撞后终止，碰撞统计应写清为碰撞回合计数。

95.40/100 是项目自定义分数，包含 40 分无碰撞、30 分完成、20 分检查点进展和 10 分净空，不能写成外部通用标准。进展使用按顺序到达检查点后累计的弦长，属于代理量，不是道路弧长或真实里程；短测未到下一检查点会没有进展分。

讨论至少包括：精确动作一致率约 75% 为何仍可能保持巡航；相邻档误差与闭环累积误差的区别；少数动作不足；单帧学生的信息限制；重复轨迹和单一留出地图的局限；零碰撞与净空不足的区别；理想速度接口与实车电机差异。

图表：离线指标及多数类基线、混淆矩阵、按图/按噪声闭环结果、轨迹叠图、净空分布、模型规模权衡、实车结果与失败案例。

### Chapter 7 Conclusions and Future Work 结论 4–6 页

7.1 Summary of the Work  
7.2 Findings in Relation to the Research Questions  
7.3 Contributions and Limitations  
7.4 Recommendations for Future Work

逐一回答 RQ1–RQ3，区分已证明、仅初步支持和仍未验证的内容。后续方向可以包括补采稀有动作、学生访问状态的专家标注、时序输入、传感器标定、更广地图与实车迁移。原地转向/倒车意味着改变动作空间、教师、学生和控制接口，应作为独立扩展。

### References 与 Appendices

References 使用统一编号格式，可沿用学校示例的 IEEE 风格。附录建议包括 A 车辆与接线参数、B 雷达和数据契约、C PPO/森林完整配置、D 完整逐回合结果与来源指纹、E 关键控制和导出说明。正文保留解释方法所需的图表，不堆整份源码。

## 5 实验补充顺序

以下为实验设计建议，不代表已执行，也不构成对代码修改的批准。

| 优先级 | 实验或整理 | 最小比较设计 | 解决的问题 |
| --- | --- | --- | --- |
| P0 | 固定实验版本 | 教师、归一化、数据批次、森林、地图、配置和报告建立对应表 | 避免把当前配置写成历史实验条件 |
| P0 | 目标板性能 | 使用待部署的同一模型，重复测推理和完整控制周期，记录 Flash/RAM、均值、P95 和最大值 | 支撑 ARM 和实时可行性 |
| P0 | 实车闭环 | 接口统一并完成架空验证后，固定路线、起点、速度目标和停止条件，多次运行 | 支撑题目中的硬件集成和迁移 |
| P1 | 正式传感器缺失测试 | 同一冻结模型，四图 normal/dropout05/dropout10/sector，每组至少沿用 5×180 s | 将 10 s 短测扩展成可比较结果 |
| P1 | 增强消融 | 同批 raw 训练与 dropout 训练，结构和划分一致；在相同清洁与缺失输入上测试 | 判断增强的实际收益 |
| P1 | 最终独立地图 | 预留未用于森林训练或调参的地图；明确教师是否见过，并冻结后评估 | 扩大现有单图留出的证据范围 |
| P1 | 基线比较 | 规则避障或单棵树与 RF 使用相同场景；教师作为特权参考并标明额外信息 | 衡量复杂度和性能取舍 |
| P2 | K 与复杂度消融 | 少量 K、树深或树数设置，每次只改变一个主要因素 | 比较动作性能、闭环、模型体积和板上时延 |
| P2 | 起步状态测试 | 固定正常、偏航和近墙起点，比较同一模型的恢复表现 | 补充正常巡航以外的覆盖 |

已有 20 回合闭环结果无需仅为写框架重复运行。正式统计以回合、起点、地图或独立训练种子作为重复单元；不能把相邻 CSV 行或增强副本当成独立重复。只有一个森林种子时应明确说明，不把不同出生点回合当作独立重训结果。

如果时间有限，优先补 ARM 资源、接口一致性和实车记录，因为它们直接决定原选题可以支持到什么程度；大量额外 PPO 调参并不能替代这部分证据。

## 6 文献清单的整理方向

当前 [references 文件](../references/reading_list.md) 是阅读链接清单，需要逐条补作者、年份、题目、出处和 DOI/URL，并确认正文的引用用途。本次未修改原清单。

本次核对的三个原始来源：

1. Leo Breiman, **Random Forests**, 2001。[作者托管原文](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf)。用于森林原理及复杂度选择的理论背景。
2. John Schulman et al., **Proximal Policy Optimization Algorithms**, 2017。[原始论文](https://arxiv.org/abs/1707.06347)。用于 PPO 方法依据。
3. Stéphane Ross, Geoffrey Gordon and Drew Bagnell, **A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning**, AISTATS 2011, pp. 627–635。[PMLR 原文页面](https://proceedings.mlr.press/v15/ross11a.html)。这是模仿学习/DAgger 的相关论文，不是随机森林原始论文；适合解释动作影响后续观测以及分布偏移的问题。

当前方法可以表述为“特权教师示范上的行为克隆”。没有学生执行、专家重新标注和迭代聚合流程，不能称已实现 DAgger；没有概率或软标签匹配目标，也不应擅自写成特定的软标签蒸馏算法。

尚需补充的文献主题包括：低成本移动机器人、嵌入式树模型、特权学习、LiDAR 局部避障、仿真到实车和传感器缺失。NVIDIA Isaac Lab 可作为学习背景或相关工具介绍；当前工程实验平台为 Gazebo，不能写成已经完成 Isaac Lab 实验。持续学习和灾难性遗忘只有与实际实验对应时才需要成为综述重点。

## 7 写作推进安排

建议先写 Chapter 3–5 的方法部分，同时整理 Chapter 6 的现有结果和待补表格。随后写 Introduction、围绕实际问题扩展 Literature Review，实验冻结后再完成结论和摘要。

第一批可直接整理的材料：系统框图、车辆与雷达参数、四图总览、教师/学生输入差异、数据配对时间轴、采集统计和类别分布、现有离线指标表、20 回合闭环表及代表轨迹。[RL_video_round_1.webm](../media/RL_video_round_1.webm) 可作演示材料，但应先确认对应的模型和条件；视频本身不能替代逐回合结果。

写作中每个重要结论都应有对应图表和报告来源。对于未完成实验，先写方法和判定规则，结果留待实测填写。
