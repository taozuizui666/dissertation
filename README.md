# **dissertation**

*a self-driving car project based on AI model*

author ： TAO RAN

## 仿真采集训练集

使用已验证的 PPO 教师控制 Gazebo 小车，同步记录动作执行前的雷达帧：

```bash
python Gazebo_simulation/rl_training/privileged/collect_data.py --check
python Gazebo_simulation/rl_training/privileged/collect_data.py
```

配置在采集脚本顶部。默认采集一回合、最多 3 分钟，随后生成随机将约 5% 非零雷达点
置零的增强副本。原始数据和增强数据数量为 1:1，保存到
`Gazebo_simulation/results/datasets/<批次>/`，仅原始和增强 CSV 原样复制到
`dataset/simulation/<批次>/`。采集元信息、逐行时间戳及日志保留在 Gazebo 的原始目录。
采集不执行数据清理、K 特征选择或随机森林训练。

后续训练统一从 `dataset/` 递归读取 `physical/`、`simulation/`。
训练前需统一实车/仿真标签含义，允许增强数据中的零值，并将同一回合的原始/增强
文件放入相同的训练/验证分组。详见
[采集说明](Gazebo_simulation/rl_training/privileged/README.md#采集随机森林训练数据)。

## 数据训练与模型部署

将采集的操作记录放进根目录 `dataset/`，每行应为 200 个雷达距离加一个操作标签。
正式训练入口为 `software/MLcode/train_model.py`，完成清理、K 特征选择、训练、导出和同步。
K、雷达点数、路径及清理参数集中在脚本顶部。

```bash
python software/MLcode/train_model.py
```

成功后生成 `software/ML_model/randomForest.h` 并备份、同步到
`software/C_code/selfdrive/main/randomForest.h`，打开对应 `main.ino` 编译上传。
模型头文件和训练输出属于生成产物，不手动修改，也不提交到 Git。
首次获取工程时，需要先准备数据并运行训练脚本，生成模型后再编译固件。
本机已配置 `python` 使用 Python 3，并安装用户级训练和 Notebook 依赖。
如需补装全部依赖，在项目根目录执行：

```bash
python -m pip install --user -r software/MLcode/requirements-notebook.txt
```

默认需要 `g++` 校验导出模型。
其他环境的安装和配置详见 [训练说明](software/MLcode/README.md)。

想逐步理解数据如何变成模型，可打开 [教学 Notebook](software/MLcode/training_walkthrough.ipynb)。
选择 `/usr/bin/python3` 内核，逐格运行；默认用临时模拟数据，不覆盖正式模型。
