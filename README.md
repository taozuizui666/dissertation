# **dissertation**

*a self-driving car project based on AI model*

author ： TAO RAN

## 仿真采集训练集

使用已验证的 PPO 教师控制 Gazebo 小车，同步记录动作执行前的雷达帧：

```bash
python Gazebo_simulation/rl_training/privileged/collect_data.py --check
python Gazebo_simulation/rl_training/privileged/collect_data.py
```

配置在采集脚本顶部：`WORLDS` 设置地图列表，`COLLECTION_SECONDS` 设置每轮仿真秒数，
`COLLECTION_ROUNDS` 设置每张地图的轮数。默认依次采集四张地图，每张三轮，
每轮最多 180 秒；同一地图多轮数据合并为一份 CSV，再生成随机将约 5% 非零雷达点
置零的增强副本。原始数据和增强数据数量为 1:1。

`Gazebo_simulation/results/datasets/<批次>/` 和 `dataset/simulation/<批次>/`
都使用 `raw/<地图名>_raw.csv`、`dropout/<地图名>_dropout.csv` 分开存放。
仅原始和增强 CSV 复制到训练目录；采集元信息、逐行时间戳及日志保留在 Gazebo 原始目录。
采集不执行数据清理、K 特征选择或随机森林训练。

后续训练统一从 `dataset/` 递归读取 `physical/`、`simulation/`。
训练前需统一实车/仿真标签含义，允许增强数据中的零值，并将同一回合的原始/增强
文件放入相同的训练/验证分组。详见
[采集说明](Gazebo_simulation/rl_training/privileged/README.md#采集随机森林训练数据)。

## 数据训练与模型部署

训练数据位于 `dataset/simulation/<批次>/raw` 与 `dropout`，每行 200 个距离加一个标签。
正式入口 `software/MLcode/train_model.py` 默认使用明确指定的最新批次，完整保留 200 列，
将 `ellipse_002` 留作验证地图。`DATA_VARIANT` 默认 `"dropout"`，也可选 `"raw"` 或 `"both"`。
配置集中在脚本顶部。

```bash
python software/MLcode/train_model.py --check
python software/MLcode/train_model.py
```

模型与报告输出到 `software/ML_model/simulation/`。保存的模型与验证时一致，不用验证地图重训。
仿真标签与旧实车控制指令不同，因此不会同步至实车固件。模型和报告属于生成产物，不提交到 Git。
本机已配置 `python` 使用 Python 3，并安装用户级训练和 Notebook 依赖。
如需补装全部依赖，在项目根目录执行：

```bash
python -m pip install --user -r software/MLcode/requirements-notebook.txt
```

默认需要 `g++` 校验导出模型。
其他环境的安装和配置详见 [训练说明](software/MLcode/README.md)。

想逐步理解数据如何变成模型，可打开 [教学 Notebook](software/MLcode/training_walkthrough.ipynb)。
选择 `/usr/bin/python3` 内核，逐格运行；默认用临时模拟数据，不覆盖正式模型。
