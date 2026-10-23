# 随机森林训练

正式入口为 `train_model.py`，常用配置集中在文件顶部。使用普通 `python`，不需要项目虚拟环境。

```bash
python software/MLcode/train_model.py --check
python software/MLcode/train_model.py
```

默认使用 `dataset/simulation/collection_20261023_092900_850f9f`：前三张训练地图
`train_world3`、`rounded_rectangle_001`、`rounded_rectangle_003` 的 dropout
训练，`ellipse_002` 的 dropout 独立验证。同一地图跨批次始终属于同一侧。
此默认批次是明确固定的，新增采集后修改 `INPUT_BATCHES` 或传 `--batch`。

## 输入与特征

无表头 CSV，每行 `d0,...,d199,command`，前 200 列为毫米距离，末列为动作标签。
默认 `FEATURE_MODE="all"` 完整保留 200 列，不进行 K 筛选；其中 50–150 列是固定零列，
保留它们不代表增加了有效雷达信息。有效扇区里的 dropout 零值也保留。
仿真标签范围 0–14，直行为 7，与旧实车的直行 10 不同，禁止混训或自动部署到旧实车。

每个指定批次的目录结构：

```text
collection_.../
  raw/<map>_raw.csv
  dropout/<map>_dropout.csv
```

`DATA_VARIANT` 可选 `raw`、`dropout`、`both`，默认 `dropout`。单独模式只读取对应目录，
不要求另一个目录存在；训练与验证均使用所选类型。`both` 同时使用原始和增强输入，
并验证每对文件的行数、标签和距离：dropout 只能将原值置零。
格式损坏或配对错误立即中止，避免跳过一行后使后续配对错位。
范围、整数、标签、全零帧等过滤按配置进行，任一配对行不合格时两侧一起排除。
普通的部分零值不会被删除。使用分块读取及临时磁盘数组，避免全部 CSV 转成 Python 对象列表。
报告记录源文件 SHA-256、行数、各项过滤数及标签分布；原始 CSV 不修改。

## 配置与命令

| 配置 | 默认含义 |
| --- | --- |
| `DATA_SOURCE` | `simulation`；切换 `physical` 时需检查标签和数据契约 |
| `INPUT_BATCHES` | 明确列出的批次，避免误混旧采集参数 |
| `DATA_VARIANT` | `"dropout"`；可选 `"raw"` / `"dropout"` / `"both"` |
| `FEATURE_MODE` / `K` | `all` / 8，K 只在 `k_best` 模式生效 |
| `VALIDATION_MAPS` | `("ellipse_002",)`，不参与拟合或特征选择 |
| `N_ESTIMATORS` / `MAX_DEPTH` | 88 / 3，首轮沿用原参数作为基线 |
| `CLASS_WEIGHT` | None，尚未进行类别平衡调参 |
| `READ_CHUNK_ROWS` | 20000，读取及预测分块行数 |
| `SAVE_CLEANED_DATA` | False，避免重复生成大型 CSV |
| `OUTPUT_DIR` | `software/ML_model/simulation` |
| `SYNC_TO_FIRMWARE` | False；仿真模式禁止同步旧实车 |

```bash
# 替换默认批次；可重复 --batch 添加其他兼容批次
python software/MLcode/train_model.py --batch collection_20261023_092900_850f9f
# 可选的 K 筛选实验，写到独立输出目录
python software/MLcode/train_model.py --feature-mode k_best --k 8 --output-dir software/ML_model/simulation_k8
# 仅检查数据、输出清理报告；默认不复制完整清理 CSV
python software/MLcode/train_model.py --clean-only
```

`--input-dir` 指向包含批次的 simulation 根目录。相对路径以 dissertation 为基准。
`--check` 仅检查配置、文件存在与配对关系，不读取 CSV 内容；正式运行才进行逐行验证。
K 筛选仅使用训练地图的数据，排除常量候选列；`both` 模式用 raw 评分，
`dropout` 模式用 dropout 评分。验证地图始终不参与评分。
physical 模式读取独立 physical 目录，多文件按文件分组，单文件按时间留出并设置间隔。
不自动选择、合并或重映射 simulation 与 physical 的标签。

## 输出与评估

- `randomForest.joblib`：分类器、200 列索引、标签、来源及零值约定。
- `randomForest.h`：C++ 推理模型，仅导出，不同步到旧实车。
- `training_report.json`：配置、来源、地图划分、类别分布、评估和导出验证。
- `clean_report.json`：每个文件的校验、过滤统计和 SHA-256。
- `feature_scores.csv`：K 模式的 ANOVA 分数；all 模式只有表头，因为未执行评分。

**保存的模型就是参与验证的模型，不会再用验证地图重训。**
报告所选类型及合并统计的准确率、macro F1、混淆矩阵、各类别召回率、
转向档位 MAE、±1/±2 档准确率及训练集多数类基线。
顶层 macro F1 按验证数据实际出现的类别计算；缺失类别列在 `absent_labels`，不代表已学会。
近邻帧和 dropout 副本使行数很大，但不等于同样数量的独立场景。
稀有动作需补采；最终驾驶效果仍需独立 Gazebo 闭环测试。

C++ 验证覆盖真实样本、部分零值、全零、随机输入和树阈值边界，并比较指令和概率。
验证成功后才发布产物；发布失败回滚，已有头文件另作备份。不会自动烧录开发板。

## 教学 Notebook 与依赖

[training_walkthrough.ipynb](training_walkthrough.ipynb) 使用同一正式函数，演示数据配对、
地图划分、200 列输入、训练评估及 C++ 导出。默认生成小型模拟数据，所有学习产物在临时目录，
不会覆盖正式模型。改成真实数据后仍写临时目录，运行耗时和内存会增加。

环境需要 Python 3.10+、scikit-learn 1.4+ 和 g++。已有依赖时直接运行；需要补装时：

```bash
python -m pip install --user -r software/MLcode/requirements.txt
# Notebook 依赖（包含训练依赖）
python -m pip install --user -r software/MLcode/requirements-notebook.txt
```
